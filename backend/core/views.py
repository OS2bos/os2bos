# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

import rest_framework_filters as filters

from core.models import (
    Case,
    Appropriation,
    Activity,
    PaymentSchedule,
    Payment,
    Municipality,
    RelatedPerson,
    SchoolDistrict,
    Team,
    Section,
    SectionInfo,
    ActivityDetails,
    Account,
    ServiceProvider,
    PaymentMethodDetails,
    ApprovalLevel,
    STATUS_DELETED,
    STATUS_DRAFT,
    STATUS_GRANTED,
)

from core.serializers import (
    CaseSerializer,
    AppropriationSerializer,
    ActivitySerializer,
    PaymentScheduleSerializer,
    PaymentSerializer,
    RelatedPersonSerializer,
    MunicipalitySerializer,
    SchoolDistrictSerializer,
    TeamSerializer,
    SectionSerializer,
    SectionInfoSerializer,
    ActivityDetailsSerializer,
    AccountSerializer,
    UserSerializer,
    HistoricalCaseSerializer,
    ServiceProviderSerializer,
    PaymentMethodDetailsSerializer,
    ApprovalLevelSerializer,
)

from core.utils import get_person_info

from core.mixins import AuditMixin

from core.authentication import CsrfExemptSessionAuthentication

from core.permissions import IsUserAllowed


# Working models, read/write


class CaseFilter(filters.FilterSet):
    expired = filters.BooleanFilter(method="filter_expired", label=_("Udgået"))

    class Meta:
        model = Case
        fields = "__all__"

    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.expired()
        else:
            return queryset.ongoing()


class AuditViewSet(AuditMixin, viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsUserAllowed,)


class ReadOnlyViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsUserAllowed,)


class CaseViewSet(AuditViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filterset_class = CaseFilter

    def perform_create(self, serializer):
        current_user = self.request.user
        team = current_user.team
        serializer.save(case_worker=current_user, team=team)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        """
        Fetch history of HistoricalCases which we use as assessments.
        """
        case = self.get_object()
        serializer = HistoricalCaseSerializer(case.history.all(), many=True)
        return Response(serializer.data)


class AppropriationViewSet(AuditViewSet):
    serializer_class = AppropriationSerializer

    filterset_fields = "__all__"

    def get_queryset(self):
        queryset = Appropriation.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
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


class ActivityViewSet(AuditViewSet):
    serializer_class = ActivitySerializer

    filterset_fields = "__all__"

    def get_queryset(self):
        queryset = Activity.objects.exclude(status=STATUS_DELETED)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    def destroy(self, request, *args, **kwargs):
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
    queryset = PaymentMethodDetails.objects.all()
    serializer_class = PaymentMethodDetailsSerializer


class PaymentScheduleViewSet(AuditViewSet):
    serializer_class = PaymentScheduleSerializer

    def get_queryset(self):
        queryset = PaymentSchedule.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class CaseFilter(filters.FilterSet):
    class Meta:
        model = Case
        fields = {"cpr_number": ["exact"]}


class PaymentScheduleFilter(filters.FilterSet):
    class Meta:
        model = PaymentSchedule
        fields = {"payment_id": ["exact"]}


class ActivityFilter(filters.FilterSet):
    class Meta:
        model = Activity
        fields = {"status": ["exact"]}


class PaymentFilter(filters.FilterSet):
    payment_schedule = filters.RelatedFilter(
        PaymentScheduleFilter,
        field_name="payment_schedule",
        queryset=PaymentSchedule.objects.all(),
    )
    case = filters.RelatedFilter(
        CaseFilter,
        field_name="payment_schedule__activity__appropriation__case",
        label=Case._meta.verbose_name.title(),
        queryset=Case.objects.all(),
    )
    activity = filters.RelatedFilter(
        ActivityFilter,
        field_name="payment_schedule__activity",
        label=Activity._meta.verbose_name.title(),
        queryset=Activity.objects.all(),
    )

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentViewSet(AuditViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    filter_class = PaymentFilter
    filterset_fields = "__all__"


class RelatedPersonViewSet(AuditViewSet):
    queryset = RelatedPerson.objects.all()
    serializer_class = RelatedPersonSerializer

    filterset_fields = "__all__"

    @action(detail=False, methods=["get"])
    def fetch_from_serviceplatformen(self, request):
        """
        Fetch relations for a person using the CPR from Serviceplatformen.

        Returns the data as serialized RelatedPersons data.
        """
        cpr = request.query_params.get("cpr")
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


class MunicipalityViewSet(ReadOnlyViewset):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer


class SchoolDistrictViewSet(ReadOnlyViewset):
    queryset = SchoolDistrict.objects.all()
    serializer_class = SchoolDistrictSerializer


class TeamViewSet(ReadOnlyViewset):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class AllowedForStepsFilter(filters.FilterSet):
    allowed_for_steps = CharInFilter(
        field_name="allowed_for_steps", lookup_expr="contains"
    )

    class Meta:
        model = Section
        fields = "__all__"


class SectionViewSet(ReadOnlyViewset):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filterset_class = AllowedForStepsFilter


class SectionInfoViewSet(ReadOnlyViewset):
    queryset = SectionInfo.objects.all()
    serializer_class = SectionInfoSerializer
    filterset_fields = "__all__"


class ActivityDetailsViewSet(ReadOnlyViewset):
    queryset = ActivityDetails.objects.all()
    serializer_class = ActivityDetailsSerializer
    filterset_fields = "__all__"


class AccountViewSet(ReadOnlyViewset):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filterset_fields = "__all__"


class UserViewSet(ReadOnlyViewset):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class ServiceProviderViewSet(ReadOnlyViewset):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer


class ApprovalLevelViewSet(ReadOnlyViewset):
    queryset = ApprovalLevel.objects.all()
    serializer_class = ApprovalLevelSerializer
