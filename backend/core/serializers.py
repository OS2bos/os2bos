from rest_framework import serializers

from core.models import (
    Case,
    Appropriation,
    Activity,
    RelatedPerson,
    Municipality,
    PaymentSchedule,
    Payment,
)


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


class PaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSchedule
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class RelatedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedPerson
        fields = "__all__"
