from rest_framework import viewsets

from core.models import Case  # TODO: , Appropriation, Activity
from core.models import Municipality

from core.serializers import (
    CaseSerializer,
    # AppropriationSerializer,
    # ActivitySerializer,
    MunicipalitySerializer,
)


class CaseViewSet(viewsets.ModelViewSet):
    # TODO: This should depend on the context!
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class MunicipalityViewSet(viewsets.ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
