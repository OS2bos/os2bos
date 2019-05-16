from rest_framework import viewsets

from core.models import (
    Case,
    Appropriation,
    Activity,
    PaymentSchedule,
    Payment,
    Municipality,
    RelatedPerson,
)

from core.serializers import (
    CaseSerializer,
    AppropriationSerializer,
    ActivitySerializer,
    MunicipalitySerializer,
    PaymentScheduleSerializer,
    PaymentSerializer,
    RelatedPersonSerializer,
)


# Working models, read/write


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class AppropriationViewSet(viewsets.ModelViewSet):
    queryset = Appropriation.objects.all()
    serializer_class = AppropriationSerializer


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    queryset = PaymentSchedule.objects.all()
    serializer_class = PaymentScheduleSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class RelatedPersonViewSet(viewsets.ModelViewSet):
    queryset = RelatedPerson.objects.all()
    serializer_class = RelatedPersonSerializer


# Master data, read only.


class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
