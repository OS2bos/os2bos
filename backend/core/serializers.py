from rest_framework import serializers

from core.models import Case, Appropriation, Activity
from core.models import Municipality


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = "__all__"


class AppropriationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appropriation
        fields = "__all__"


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = "__all__"
