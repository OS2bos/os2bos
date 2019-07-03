from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from core.models import (
    Case,
    Appropriation,
    Activity,
    RelatedPerson,
    Municipality,
    PaymentSchedule,
    PaymentMethodDetails,
    Payment,
    SchoolDistrict,
    Section,
    ActivityDetails,
    Account,
    HistoricalCase,
    ServiceProvider,
    ApprovalLevel,
    Team,
    FAMILY_DEPT,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "cases"]


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = "__all__"

    def validate(self, data):
        # check that if target_group is family, district is given
        if (
            "target_group" in data and data["target_group"] == FAMILY_DEPT
        ) and ("district" not in data or not data["district"]):
            raise serializers.ValidationError(
                _("En sag med familie målgruppe skal have et distrikt")
            )
        return data


class HistoricalCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalCase
        # include history_date (date saved)
        # and history_user (user responsible for saving).
        fields = (
            "case_worker",
            "effort_step",
            "scaling_step",
            "history_date",
            "history_user",
        )


class SupplementaryActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


class ActivitySerializer(serializers.ModelSerializer):
    monthly_payment_plan = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    total_cost_this_year = serializers.ReadOnlyField()

    supplementary_activities = SupplementaryActivitySerializer(
        many=True, read_only=True
    )

    def validate(self, data):
        # Check that start_date is before end_date
        if (
            "end_date" in data
            and data["end_date"]
            and data["start_date"] > data["end_date"]
        ):
            raise serializers.ValidationError(
                _("startdato skal være før slutdato")
            )
        return data

    class Meta:
        model = Activity
        fields = "__all__"


class AppropriationSerializer(serializers.ModelSerializer):
    total_granted_this_year = serializers.ReadOnlyField()
    total_expected_this_year = serializers.ReadOnlyField()

    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Appropriation
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class PaymentMethodDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodDetails
        fields = "__all__"


class PaymentScheduleSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentSchedule
        fields = "__all__"


class RelatedPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedPerson
        fields = "__all__"


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class SchoolDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolDistrict
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class ActivityDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityDetails
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class ServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = "__all__"


class ApprovalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalLevel
        fields = "__all__"
