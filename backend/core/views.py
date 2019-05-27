from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from core.models import (
    Case,
    Appropriation,
    Activity,
    PaymentSchedule,
    Payment,
    Municipality,
    RelatedPerson,
    SchoolDistrict,
    Sections,
    ActivityCatalog,
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
    SectionsSerializer,
    ActivityCatalogSerializer,
)

from core.utils import get_cpr_data

# Working models, read/write


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class AppropriationViewSet(viewsets.ModelViewSet):
    queryset = Appropriation.objects.all()
    serializer_class = AppropriationSerializer
    filterset_fields = "__all__"


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filterset_fields = "__all__"


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class RelatedPersonViewSet(viewsets.ModelViewSet):
    queryset = RelatedPerson.objects.all()
    serializer_class = RelatedPersonSerializer

    @action(detail=False, methods=["get"])
    def fetch_from_serviceplatformen(self, request):
        """
        Fetch relations from a CPR number from Serviceplatformen.

        returns the data as RelatedPersons.
        """
        cpr = request.query_params.get("cpr")
        if not cpr:
            return Response(
                {"errors": _("Intet CPR nummer angivet")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # cpr_data = get_cpr_data(cpr)
        # Use test data for now.
        cpr_data = {
            "relationer": [
                {"cprnr": "0123456780", "relation": "aegtefaelle"},
                {"cprnr": "1123456789", "relation": "barn"},
                {"cprnr": "2123456789", "relation": "barn"},
                {"cprnr": "3123456789", "relation": "barn"},
                {"cprnr": "0000000000", "relation": "mor"},
                {"cprnr": "0000000000", "relation": "far"},
            ]
        }
        if not cpr_data:
            return Response(
                {"errors": [_("Fejl i forbindelse til Serviceplatformen")]},
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


class SectionsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sections.objects.all()
    serializer_class = SectionsSerializer


class ActivityCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityCatalog.objects.all()
    serializer_class = ActivityCatalogSerializer
