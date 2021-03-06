# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Views and viewsets exposed by the REST interface."""
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from core.models import (
    Case,
    Appropriation,
    Activity,
    Rate,
    Price,
    PaymentSchedule,
    Payment,
    Municipality,
    RelatedPerson,
    SchoolDistrict,
    Team,
    Section,
    SectionInfo,
    ActivityDetails,
    ServiceProvider,
    PaymentMethodDetails,
    ApprovalLevel,
    EffortStep,
    TargetGroup,
    InternalPaymentRecipient,
    Effort,
    STATUS_DELETED,
    STATUS_DRAFT,
    STATUS_GRANTED,
)

from core.serializers import (
    CaseSerializer,
    ListAppropriationSerializer,
    AppropriationSerializer,
    ActivitySerializer,
    RateSerializer,
    PriceSerializer,
    PaymentScheduleSerializer,
    PaymentSerializer,
    RelatedPersonSerializer,
    MunicipalitySerializer,
    SchoolDistrictSerializer,
    TeamSerializer,
    SectionSerializer,
    SectionInfoSerializer,
    ActivityDetailsSerializer,
    UserSerializer,
    HistoricalCaseSerializer,
    ServiceProviderSerializer,
    PaymentMethodDetailsSerializer,
    ApprovalLevelSerializer,
    EffortStepSerializer,
    TargetGroupSerializer,
    InternalPaymentRecipientSerializer,
    EffortSerializer,
)
from core.filters import (
    CaseFilter,
    AppropriationFilter,
    PaymentFilter,
    AllowedForStepsFilter,
)
from core.utils import get_person_info

from core.mixins import (
    AuditMixin,
    ClassificationViewSetMixin,
    AuditModelViewSetMixin,
)

from core.authentication import CsrfExemptSessionAuthentication

from core.permissions import (
    IsUserAllowed,
    NewPaymentPermission,
    DeletePaymentPermission,
    EditPaymentPermission,
)


serviceplatformen_logger = logging.getLogger(
    "bevillingsplatform.serviceplatformen"
)


# Working models, read/write


class AuditViewSet(AuditMixin, viewsets.ModelViewSet):
    """Superclass for use by all model classes with audit fields.

    All classes that can be written through the REST interface have
    audit fields.
    """

    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsUserAllowed,)


class ReadOnlyViewset(viewsets.ReadOnlyModelViewSet):
    """Superclass for use model classes that are read only through REST."""

    permission_classes = (IsUserAllowed,)


class CaseViewSet(AuditModelViewSetMixin, AuditViewSet):
    """Viewset exposing Case in the REST API.

    Note the custom actions ``history`` and ``change_case_worker``.
    """

    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filterset_class = CaseFilter

    def get_queryset(self):
        """Avoid Django's default lazy loading to improve performance."""
        queryset = Case.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    def perform_create(self, serializer):
        """Create new case - customized to set user."""
        current_user = self.request.user
        serializer.save(
            case_worker=current_user,
            user_created=current_user.username,
        )

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        """Fetch history of HistoricalCases which we use as assessments."""
        case = self.get_object()
        serializer = HistoricalCaseSerializer(case.history.all(), many=True)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=False, methods=["patch"])
    def change_case_worker(self, request):
        """
        Change the case_worker of several Cases.

        :param case_pks: A list of case pks.
        :param case_worker_pk: the case worker pk to change to.

        """
        case_pks = request.data.get("case_pks", [])
        case_worker_pk = request.data.get("case_worker_pk", None)
        if not case_pks or not case_worker_pk:
            return Response(
                {
                    "errors": [
                        _("case_pks eller case_worker_pk argument mangler")
                    ]
                },
                status.HTTP_400_BAD_REQUEST,
            )
        user_qs = get_user_model().objects.filter(id=case_worker_pk)
        if not user_qs.exists():
            return Response(
                {"errors": [_("bruger med case_worker_pk findes ikke")]},
                status.HTTP_400_BAD_REQUEST,
            )
        user = user_qs.first()
        cases = Case.objects.filter(pk__in=case_pks)
        for case in cases:
            case.case_worker = user
            case.save()
        CaseSerializer = self.get_serializer_class()
        return Response(CaseSerializer(cases, many=True).data)


class AppropriationViewSet(AuditModelViewSetMixin, AuditViewSet):
    """Expose appropriations in REST API.

    Note the custom action ``grant`` for approving an appropriation and
    all its activities.
    """

    serializer_action_classes = {
        "list": ListAppropriationSerializer,
        "retrieve": AppropriationSerializer,
    }
    filterset_class = AppropriationFilter

    def get_serializer_class(self):
        """Use a different Serializer depending on the action."""
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return AppropriationSerializer

    def get_queryset(self):
        """Avoid Django's default lazy loading to improve performance."""
        queryset = Appropriation.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)

        # We need to be able to show and filter on the
        # main activity details id.
        queryset = queryset.annotate_main_activity_details_id()
        return queryset

    @action(detail=True, methods=["patch"])
    def grant(self, request, pk=None):
        """Grant the specified activities on this appropriation."""
        appropriation = self.get_object()
        approval_level = request.data.get("approval_level", None)
        approval_note = request.data.get("approval_note", "")
        activity_pks = request.data.get("activities", [])
        try:
            activities = appropriation.activities.filter(pk__in=activity_pks)
            if len(activities) != len(activity_pks):
                raise RuntimeError(
                    _("Du kan kun godkende ydelser på den samme bevilling")
                )
            appropriation.grant(
                activities, approval_level, approval_note, request.user
            )
            # Success!
            response = Response("OK", status.HTTP_200_OK)
        except Exception as e:
            response = Response(
                {"errors": [str(e)]}, status.HTTP_400_BAD_REQUEST
            )
        return response


class ActivityViewSet(AuditModelViewSetMixin, AuditViewSet):
    """Expose activities in REST API."""

    serializer_class = ActivitySerializer

    filterset_fields = "__all__"

    def get_queryset(self):
        """Avoid Django's default lazy loading to improve performance."""
        queryset = Activity.objects.exclude(status=STATUS_DELETED)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Handle deletion according to their business logic.

        Drafts are deleted, expectations are logically deleted, granted
        activities cannot be deleted.
        """
        activity = self.get_object()
        try:
            if activity.status == STATUS_DRAFT:
                activity.delete()
            elif activity.status == STATUS_GRANTED:
                raise RuntimeError(_("Du kan ikke slette en bevilget ydelse."))

            else:
                activity.status = STATUS_DELETED
                activity.save()
            # Success!
            response = Response("OK", status.HTTP_204_NO_CONTENT)
        except Exception as e:
            response = Response(
                {"errors": [str(e)]}, status.HTTP_400_BAD_REQUEST
            )
        return response


class PaymentMethodDetailsViewSet(AuditViewSet):
    """Expose payment method details in REST API."""

    queryset = PaymentMethodDetails.objects.all()
    serializer_class = PaymentMethodDetailsSerializer


class PriceViewSet(AuditViewSet):
    """Expose Price objects in REST API."""

    queryset = Price.objects.all()
    serializer_class = PriceSerializer


class PaymentScheduleViewSet(AuditViewSet):
    """Expose payment schedules in REST API."""

    serializer_class = PaymentScheduleSerializer

    def get_queryset(self):
        """Avoid Django's default lazy loading to improve performance."""
        queryset = PaymentSchedule.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class PaymentViewSet(AuditViewSet):
    """Expose payments in REST API.

    Note, this viewset supports pagination.
    """

    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (
        EditPaymentPermission,
        DeletePaymentPermission,
        NewPaymentPermission,
    )

    filterset_class = PaymentFilter
    filterset_fields = "__all__"


class RelatedPersonViewSet(AuditModelViewSetMixin, AuditViewSet):
    """Expose related persons - typically family relations - in REST API."""

    queryset = RelatedPerson.objects.all()
    serializer_class = RelatedPersonSerializer

    filterset_fields = "__all__"

    @action(detail=False, methods=["get"])
    def fetch_from_serviceplatformen(self, request):
        """Fetch relations for a person using the CPR from Serviceplatformen.

        Returns the data as serialized RelatedPersons data.

        GET params: cpr
        """
        cpr = request.query_params.get("cpr")
        serviceplatformen_logger.info(
            f"fetch_from_serviceplatformen: {cpr} - {request.user}"
        )
        if not cpr:
            return Response(
                {"errors": _("Intet CPR nummer angivet")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cpr_data = get_person_info(cpr)

        if not cpr_data:
            return Response(
                {
                    "errors": [
                        _("Fejl i CPR eller forbindelse til Serviceplatformen")
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        person = RelatedPerson.serviceplatformen_to_related_person(cpr_data)
        person["relations"] = []
        for relation in cpr_data["relationer"]:
            person["relations"].append(
                RelatedPerson.serviceplatformen_to_related_person(relation)
            )

        return Response(person, status.HTTP_200_OK)


# Master data, read only.


class MunicipalityViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose municipalities in REST API."""

    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    filterset_fields = "__all__"


class SchoolDistrictViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose school districts in REST API."""

    queryset = SchoolDistrict.objects.all()
    serializer_class = SchoolDistrictSerializer
    filterset_fields = "__all__"


class TeamViewSet(ReadOnlyViewset):
    """Expose teams in REST API."""

    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class RateViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose rates in REST API."""

    queryset = Rate.objects.all()
    serializer_class = RateSerializer


class SectionViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose law sections in REST API."""

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filterset_class = AllowedForStepsFilter


class SectionInfoViewSet(ReadOnlyViewset):
    """Expose section infos in REST API."""

    queryset = SectionInfo.objects.all()
    serializer_class = SectionInfoSerializer
    filterset_fields = "__all__"


class ActivityDetailsViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose activity details in REST API."""

    queryset = ActivityDetails.objects.all()
    serializer_class = ActivityDetailsSerializer
    filterset_fields = "__all__"


class UserViewSet(ReadOnlyViewset):
    """Expose users in REST API."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class ServiceProviderViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose service providers in REST API."""

    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    filterset_fields = "__all__"


class ApprovalLevelViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose approval levels in REST API."""

    queryset = ApprovalLevel.objects.all()
    serializer_class = ApprovalLevelSerializer
    filterset_fields = "__all__"


class EffortStepViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose effort steps in REST API."""

    queryset = EffortStep.objects.all()
    serializer_class = EffortStepSerializer
    filterset_fields = "__all__"


class TargetGroupViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose target groups in REST API."""

    queryset = TargetGroup.objects.all()
    serializer_class = TargetGroupSerializer


class InternalPaymentRecipientViewSet(ReadOnlyViewset):
    """Expose internal payment recipients in REST API."""

    queryset = InternalPaymentRecipient.objects.all()
    serializer_class = InternalPaymentRecipientSerializer


class EffortViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose efforts in REST API."""

    queryset = Effort.objects.all()
    serializer_class = EffortSerializer
    filterset_fields = "__all__"


class IsEditingPastPaymentsAllowed(APIView):
    """Expose the ALLOW_EDIT_OF_PAST_PAYMENTS setting in the API."""

    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, format=None):
        """Return the Django setting allowing changes to the past."""
        is_enabled = settings.ALLOW_EDIT_OF_PAST_PAYMENTS
        return Response(is_enabled)
