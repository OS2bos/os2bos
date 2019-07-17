from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django_filters import rest_framework as filters

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
    ActivityDetails,
    Account,
    ServiceProvider,
    PaymentMethodDetails,
    ApprovalLevel,
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
    pass


class CaseViewSet(AuditViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    filterset_class = CaseFilter

    def perform_create(self, serializer):
        current_user = self.request.user
        team = current_user.team
        serializer.save(case_worker=current_user, team=team)

    def perform_update(self, serializer):
        # save history_change_reason for the Case used for assessments.
        change_reason = None
        if (
            "history_change_reason" in self.request.data
            and self.request.data["history_change_reason"]
        ):
            change_reason = self.request.data.pop("history_change_reason")

        serializer.save(changeReason=change_reason)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        """
        Fetch history of HistoricalCases which we use as assessments.
        """
        case = self.get_object()
        serializer = HistoricalCaseSerializer(case.history.all(), many=True)
        return Response(serializer.data)


class AppropriationViewSet(AuditViewSet):
    queryset = Appropriation.objects.all()
    serializer_class = AppropriationSerializer

    filterset_fields = "__all__"

    @action(detail=True, methods=["patch"])
    def grant(self, request, pk=None):
        """Grant this appropriation."""
        appropriation = self.get_object()
        approval_level = request.data.get("approval_level", None)
        approval_note = request.data.get("approval_note", "")

        try:
            appropriation.grant(approval_level, approval_note)
            response = Response("OK", status.HTTP_200_OK)
        except Exception as e:
            response = Response(
                {"errors": [str(e)]}, status.HTTP_400_BAD_REQUEST
            )
        return response


class ActivityViewSet(AuditViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    filterset_fields = "__all__"


class PaymentMethodDetailsViewSet(AuditViewSet):
    queryset = PaymentMethodDetails.objects.all()
    serializer_class = PaymentMethodDetailsSerializer


class PaymentScheduleViewSet(AuditViewSet):
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleSerializer


class PaymentViewSet(AuditViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


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
        relations = []
        for relation in cpr_data["relationer"]:
            relations.append(
                RelatedPerson.serviceplatformen_to_related_person(relation)
            )

        return Response(relations, status.HTTP_200_OK)


# Master data, read only.


class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer


class SchoolDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SchoolDistrict.objects.all()
    serializer_class = SchoolDistrictSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
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


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filterset_class = AllowedForStepsFilter


class ActivityDetailsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityDetails.objects.all()
    serializer_class = ActivityDetailsSerializer
    filterset_fields = "__all__"


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class ServiceProviderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer


class ApprovalLevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApprovalLevel.objects.all()
    serializer_class = ApprovalLevelSerializer
