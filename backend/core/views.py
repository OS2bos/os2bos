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
from django.http import HttpResponse
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    api_view,
)
from rest_framework.request import Request

from lxml import etree

from graphene_django.views import GraphQLView

from constance import config

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
    ActivityCategory,
    DSTPayload,
    STATUS_DELETED,
    STATUS_DRAFT,
    STATUS_GRANTED,
    PREVENTATIVE_MEASURES,
    HANDICAP,
)

from core.serializers import (
    CaseSerializer,
    ListAppropriationSerializer,
    AppropriationSerializer,
    ActivitySerializer,
    ListActivitySerializer,
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
    HistoricalPaymentSerializer,
    ServiceProviderSerializer,
    PaymentMethodDetailsSerializer,
    ApprovalLevelSerializer,
    EffortStepSerializer,
    TargetGroupSerializer,
    InternalPaymentRecipientSerializer,
    EffortSerializer,
    ActivityCategorySerializer,
    DSTPayloadSerializer,
)
from core.filters import (
    CaseFilter,
    AppropriationFilter,
    PaymentFilter,
    AllowedForStepsFilter,
)

from core.utils import (
    get_person_info,
    get_company_info_from_search_term,
    generate_dst_payload_preventive_measures,
    generate_dst_payload_handicap,
)

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


class AuthenticatedGraphQLView(GraphQLView):
    """
    GraphQLView with our Django Rest Framework authentication on top.

    As found on: https://github.com/graphql-python/graphene/issues/249
    """

    def parse_body(self, request):
        """Apparently graphene needs a body attribute."""
        if isinstance(request, Request):  # pragma: no cover
            return request.data
        return super(AuthenticatedGraphQLView, self).parse_body(
            request
        )  # pragma: no cover

    @classmethod
    def as_view(cls, *args, **kwargs):
        """Add the relevant DRF-view logic to the view."""
        view = super(AuthenticatedGraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsUserAllowed,))(view)
        view = authentication_classes((CsrfExemptSessionAuthentication,))(view)
        view = api_view(["GET", "POST"])(view)
        return view


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
            case_worker=current_user, user_created=current_user.username
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
    """
    ## Expose appropriations in REST API.

    ### Actions

    **grant** for approving an appropriation and
    all its activities.

    - approval_level
    - approval_note
    - activity_pks

    **generate_dst_preventative_measures_payload** for generating a DST
    preventative measures payload.

    - sections
    - from_start_date
    - test

    **generate_dst_handicap_payload** for generating a DST handicap payload.

    - sections
    - from_start_date
    - test
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

    @action(detail=False, methods=["get"])
    def generate_dst_preventative_measures_file(self, request):
        """Generate a Preventative Measures payload for DST."""
        from_date = request.query_params.get("from_date", None)
        test = request.query_params.get("test", "true")
        test = True if test == "true" else False

        if "sections" in request.query_params:
            sections_pks = request.query_params.getlist("sections")
            sections = Section.objects.filter(pk__in=sections_pks)
        else:
            sections = Section.objects.filter(default_for_dst_handicap=True)

        doc = etree.tostring(
            generate_dst_payload_preventive_measures(from_date, sections, test)
        )
        payload_type = "T201" if test else "L201"
        municipality_code = config.DST_MUNICIPALITY_CODE
        now = timezone.now()
        period = now.strftime("%YM%m")
        generation_timestamp = now.strftime("%Y%m%dT%H%M%S")
        filename = (
            f"P_{municipality_code}_"
            f"{payload_type}_"
            f"P{period}_"
            f"V01_D{generation_timestamp}.xml"
        )
        # If payload is not a test we save it for later use.
        if not test:
            DSTPayload.objects.create(
                name=filename,
                content=doc.decode("utf-8"),
                from_date=from_date,
                dst_type=PREVENTATIVE_MEASURES,
            )

        response = HttpResponse(doc, content_type="text/xml")
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    @action(detail=False, methods=["get"])
    def generate_dst_handicap_file(self, request):
        """Generate a Handicap payload for DST."""
        from_date = request.query_params.get("from_date", None)
        test = request.query_params.get("test", "true")
        test = True if test == "true" else False

        if "sections" in request.query_params:
            sections_pks = request.query_params.getlist("sections")
            sections = Section.objects.filter(pk__in=sections_pks)
        else:
            sections = Section.objects.filter(default_for_dst_handicap=True)

        doc = etree.tostring(
            generate_dst_payload_handicap(from_date, sections, test)
        )
        payload_type = "T231" if test else "L231"
        municipality_code = config.DST_MUNICIPALITY_CODE
        now = timezone.now()
        period = now.strftime("%YM%m")
        generation_timestamp = now.strftime("%Y%m%dT%H%M%S")
        filename = (
            f"P_{municipality_code}_"
            f"{payload_type}_"
            f"P{period}_"
            f"V01_D{generation_timestamp}.xml"
        )
        # If payload is not a test we save it for later use.
        if not test:
            DSTPayload.objects.create(
                name=filename,
                content=doc.decode("utf-8"),
                from_date=from_date,
                dst_type=HANDICAP,
            )

        response = HttpResponse(doc, content_type="text/xml")
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response


class ActivityViewSet(AuditModelViewSetMixin, AuditViewSet):
    """Expose activities in REST API."""

    serializer_action_classes = {
        "list": ListActivitySerializer,
        "retrieve": ActivitySerializer,
    }
    filterset_fields = "__all__"

    def get_serializer_class(self):
        """Use a different Serializer depending on the action."""
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return ActivitySerializer

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


class PaymentMethodDetailsViewSet(ClassificationViewSetMixin, AuditViewSet):
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

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        """Fetch history of Payment."""
        payment = self.get_object()
        serializer = HistoricalPaymentSerializer(
            payment.history.all(), many=True
        )
        return Response(serializer.data)


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


class TeamViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
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


class SectionInfoViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
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
    filterset_fields = "__all__"


class ServiceProviderViewSet(
    ClassificationViewSetMixin, viewsets.ModelViewSet
):
    """Expose service providers in REST API."""

    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    filterset_fields = "__all__"

    @action(detail=False, methods=["get"])
    def fetch_serviceproviders_from_virk(self, request):
        """Fetch serviceproviders using a generic search term from Virk.

        Returns the data as serialized ServiceProvider data.

        GET params: search_term
        """
        search_term = request.query_params.get("search_term")
        if not search_term:
            return Response(
                {"errors": [_("Der kræves en search_term parameter")]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        company_info = get_company_info_from_search_term(search_term)

        if not company_info:
            return Response(
                {"errors": [_("Fejl i søgning eller forbindelse til Virk")]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service_providers = [
            ServiceProvider.virk_to_service_provider(data)
            for data in company_info
        ]
        return Response(service_providers, status.HTTP_200_OK)


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


class InternalPaymentRecipientViewSet(
    ClassificationViewSetMixin, ReadOnlyViewset
):
    """Expose internal payment recipients in REST API."""

    queryset = InternalPaymentRecipient.objects.all()
    serializer_class = InternalPaymentRecipientSerializer


class EffortViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose efforts in REST API."""

    queryset = Effort.objects.all()
    serializer_class = EffortSerializer
    filterset_fields = "__all__"


class ActivityCategoryViewSet(ClassificationViewSetMixin, ReadOnlyViewset):
    """Expose activity categories in REST API."""

    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer


class DSTPayloadViewSet(ReadOnlyViewset):
    """Expose DST payloads in REST API."""

    queryset = DSTPayload.objects.all()
    serializer_class = DSTPayloadSerializer


class FrontendSettingsView(APIView):
    """Expose a relevant selection of settings to the frontend."""

    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, format=None):
        """Expose the relevant settings."""
        settings_dict = {
            "ALLOW_EDIT_OF_PAST_PAYMENTS": (
                settings.ALLOW_EDIT_OF_PAST_PAYMENTS
            ),
            "ALLOW_SERVICE_PROVIDERS_FROM_VIRK": (
                settings.ALLOW_SERVICE_PROVIDERS_FROM_VIRK
            ),
        }
        return Response(settings_dict)
