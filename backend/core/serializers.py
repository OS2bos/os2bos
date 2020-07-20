# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Data serializers used by the REST API."""

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django import forms

from rest_framework import serializers

from drf_writable_nested import WritableNestedModelSerializer

from core.models import (
    Case,
    Price,
    Rate,
    RatePerDate,
    Appropriation,
    Activity,
    RelatedPerson,
    Municipality,
    PaymentSchedule,
    PaymentMethodDetails,
    Payment,
    SchoolDistrict,
    Section,
    SectionInfo,
    ActivityDetails,
    HistoricalCase,
    ServiceProvider,
    ApprovalLevel,
    Team,
    EffortStep,
    TargetGroup,
    InternalPaymentRecipient,
    Effort,
    STATUS_DELETED,
    STATUS_DRAFT,
    STATUS_EXPECTED,
)
from core.utils import create_rrule


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "cases",
            "team",
            "profile",
        )


class CaseSerializer(serializers.ModelSerializer):
    """Serializer for the Case model.

    Note validation to ensure that cases are always valid
    according to required_fields_for_case
    """

    expired = serializers.ReadOnlyField()
    num_ongoing_appropriations = serializers.SerializerMethodField()
    num_ongoing_draft_or_expected_appropriations = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = Case
        fields = "__all__"

    def get_num_ongoing_appropriations(self, case):
        """Get number of related ongoing appropriations."""
        return case.appropriations.ongoing().count()

    def get_num_ongoing_draft_or_expected_appropriations(self, case):
        """Get number of related expected or draft ongoing appropriations."""
        return len(
            [
                appr
                for appr in case.appropriations.ongoing()
                if (
                    appr.status == STATUS_EXPECTED
                    or appr.status == STATUS_DRAFT
                )
            ]
        )

    def validate(self, data):
        """Check if required fields for case are present."""
        if (
            "target_group" in data
            and data["target_group"].required_fields_for_case
        ):
            required_fields_for_case = data[
                "target_group"
            ].required_fields_for_case
            for field in required_fields_for_case:
                if (
                    self.partial
                    and not getattr(self.instance, field)
                    and (field not in data or not data[field])
                ) or (
                    not self.partial and (field not in data or not data[field])
                ):
                    serializer_fields = self.get_fields()
                    field_label = serializer_fields[field].label
                    raise serializers.ValidationError(
                        _(
                            f"En sag med den givne "
                            f"målgruppe skal have feltet {field_label}"
                        )
                    )
        return data


class HistoricalCaseSerializer(serializers.ModelSerializer):
    """Serializer for the historic/temporal dimension of a Case."""

    class Meta:
        model = HistoricalCase
        # include history_date (date saved),
        # history_user (user responsible for saving),
        # and assessment comment (optional, additional info).
        fields = (
            "case_worker",
            "effort_step",
            "scaling_step",
            "assessment_comment",
            "history_date",
            "history_user",
        )


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model.

    Note the many options for filtering as well as the non-trivial
    validate function.
    """

    account_string = serializers.ReadOnlyField()
    account_alias = serializers.ReadOnlyField()
    payment_schedule__payment_id = serializers.ReadOnlyField(
        source="payment_schedule.payment_id", default=None
    )
    case__cpr_number = serializers.ReadOnlyField(
        source="payment_schedule.activity.appropriation.case.cpr_number"
    )
    activity__id = serializers.ReadOnlyField(
        source="payment_schedule.activity.id"
    )
    activity__status = serializers.ReadOnlyField(
        source="payment_schedule.activity.status"
    )
    activity__details__id = serializers.ReadOnlyField(
        source="payment_schedule.activity.details.id"
    )
    payment_schedule__fictive = serializers.ReadOnlyField(
        source="payment_schedule.fictive"
    )
    is_payable_manually = serializers.ReadOnlyField(default=False)

    def validate(self, data):
        """Validate this payment.

        The payment method must be allowed for this recipient, etc.
        """
        payment_method = (
            data.get("payment_method", None) or self.instance.payment_method
        )
        recipient_type = (
            data.get("recipient_type", None) or self.instance.recipient_type
        )
        paid = data.get("paid", None) or self.instance.paid
        payment_schedule = (
            data.get("payment_schedule", None)
            or self.instance.payment_schedule
        )

        paid_allowed = self.Meta.model.paid_allowed_for_payment_and_recipient(
            payment_method, recipient_type
        )

        if paid and (
            not paid_allowed
            or payment_schedule.fictive
            or not payment_schedule.can_be_paid
        ):
            raise serializers.ValidationError(
                _("Denne betaling må ikke markeres betalt manuelt")
            )
        return data

    class Meta:
        model = Payment
        exclude = ("saved_account_string", "saved_account_alias")


class RatePerDateSerializer(serializers.ModelSerializer):
    """Serializer for the RatePerDate model."""

    class Meta:
        model = RatePerDate
        fields = ("rate", "start_date", "end_date")


class RateSerializer(serializers.ModelSerializer):
    """Serializer for the Rate model."""

    rates_per_date = RatePerDateSerializer(many=True, read_only=True)

    class Meta:
        model = Rate
        fields = "__all__"


class PriceSerializer(WritableNestedModelSerializer):
    """Serializer for the Price model."""

    rates_per_date = RatePerDateSerializer(many=True, read_only=True)

    class Meta:
        model = Price
        exclude = ("payment_schedule",)

    current_amount = serializers.ReadOnlyField(source="rate_amount")
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True
    )
    start_date = serializers.DateField(required=False, write_only=True)
    end_date = serializers.DateField(required=False, write_only=True)

    def create(self, validated_data):
        """Set rate amount on Price."""
        amount = validated_data.pop("amount")
        start_date = validated_data.pop("start_date", None)
        end_date = validated_data.pop("end_date", None)
        instance = super().create(validated_data)
        instance.set_rate_amount(
            amount=amount, start_date=start_date, end_date=end_date
        )
        return instance

    def update(self, instance, validated_data):
        """Update rate amount on Price for dates."""
        amount = validated_data.pop("amount")
        start_date = validated_data.pop("start_date", None)
        end_date = validated_data.pop("end_date", None)
        instance = super().update(instance, validated_data)
        instance.set_rate_amount(
            amount=amount, start_date=start_date, end_date=end_date
        )
        return instance


class PaymentScheduleSerializer(WritableNestedModelSerializer):
    """Serializer for the PaymentSchedule model."""

    payments = PaymentSerializer(many=True, read_only=True)
    price_per_unit = PriceSerializer(required=False, allow_null=True)

    class Meta:
        model = PaymentSchedule
        exclude = ("activity",)

    @staticmethod
    def setup_eager_loading(queryset):
        """Set up eager loading for improved performance."""
        queryset = queryset.prefetch_related("payments")
        return queryset

    def validate(self, data):
        """Validate this payment schedule.

        As for Payment, payment method, recipient type and various other
        things need to fit together.
        """
        if not self.Meta.model.is_payment_and_recipient_allowed(
            data["payment_method"], data["recipient_type"]
        ):
            raise serializers.ValidationError(
                _("ugyldig betalingsmetode for betalingsmodtager")
            )

        one_time_payment = (
            data["payment_type"] == PaymentSchedule.ONE_TIME_PAYMENT
        )
        payment_frequency = (
            "payment_frequency" in data and data["payment_frequency"]
        )
        if not one_time_payment and not payment_frequency:
            raise serializers.ValidationError(
                _(
                    "En betalingstype der ikke er en engangsbetaling "
                    "skal have en betalingsfrekvens"
                )
            )
        elif one_time_payment and payment_frequency:
            raise serializers.ValidationError(
                _("En engangsbetaling må ikke have en betalingsfrekvens")
            )

        # Validate payment/rate/unit info
        payment_cost_type = data["payment_cost_type"]
        instance = self.instance
        if not instance and self.parent:
            # XXX: Get instance from parent form data, we need it.
            instance_id = self.parent.initial_data["payment_plan"].get("id")
            if instance_id:
                instance = PaymentSchedule.objects.get(id=instance_id)

        if payment_cost_type == PaymentSchedule.FIXED_PRICE:
            # Payment amount needs to be given, apart from that s'all
            # good.
            if not (data.get("payment_amount", None)):
                raise serializers.ValidationError(
                    _("Beløb skal udfyldes ved fast beløb")
                )
            # Rate can't be given.
            if data.get("payment_rate", None):
                raise serializers.ValidationError(
                    _("Takst skal ikke angives ved fast beløb")
                )
            # Price data can't be given.
            if data.get("price_per_unit") and data["price_per_unit"].get(
                "amount", None
            ):
                raise serializers.ValidationError(
                    _("Beløb pr. enhed skal ikke angives ved fast takst")
                )
            # Units can't be given.
            if data.get("payment_units", None):
                raise serializers.ValidationError(
                    _("Enheder skal ikke angives ved fast beløb")
                )
        elif payment_cost_type == PaymentSchedule.PER_UNIT_PRICE:
            # Units need to be given.
            if not data.get("payment_units", None):
                if not instance or instance.payment_units is None:
                    raise serializers.ValidationError(
                        _("Enheder skal angives ved pris pr. enhed")
                    )
            # Price data needs to be given.
            # If not given, start and end date default to None.
            if (
                not data.get("price_per_unit", None)
                or data["price_per_unit"].get("amount", None) is None
            ):
                if not instance or not instance.price_per_unit:
                    raise serializers.ValidationError(
                        _("Beløb pr. enhed skal angives")
                    )
            # Rate can't be given.
            if data.get("payment_rate", None):
                raise serializers.ValidationError(
                    _("Takst skal ikke angives ved pris pr. enhed")
                )
            # Payment amount can't be given.
            if data.get("payment_amount", None):
                raise serializers.ValidationError(
                    _("Beløbsfeltet skal ikke udfyldes ved pris pr. enhed")
                )
        elif (
            payment_cost_type == PaymentSchedule.GLOBAL_RATE_PRICE
        ):  # pragma: no cover
            # Units need to be given.
            if not data.get("payment_units", None):
                raise serializers.ValidationError(
                    _("Enheder skal angives ved fast takst")
                )
            # Rate needs to be given.
            if not data.get("payment_rate", None):
                raise serializers.ValidationError(_("Takst skal angives"))
            # Payment amount can't be given.
            if data.get("payment_amount", None):
                raise serializers.ValidationError(
                    _("Beløbsfeltet skal ikke udfyldes ved fast takst")
                )
            # Price data can't be given.
            if data.get("price_per_unit") and data["price_per_unit"].get(
                "amount", None
            ):
                raise serializers.ValidationError(
                    _("Beløb pr. enhed skal ikke angives ved fast takst")
                )

        return data


class ActivitySerializer(WritableNestedModelSerializer):
    """Serializer for the Activity model."""

    monthly_payment_plan = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    total_cost_this_year = serializers.ReadOnlyField()
    total_cost_full_year = serializers.ReadOnlyField()
    total_granted_this_year = serializers.ReadOnlyField()
    total_expected_this_year = serializers.ReadOnlyField()

    payment_plan = PaymentScheduleSerializer(partial=True, required=False)
    details__name = serializers.ReadOnlyField(source="details.name")

    @staticmethod
    def setup_eager_loading(queryset):
        """Set up eager loading for improved performance."""
        queryset = queryset.select_related("payment_plan", "details")
        return queryset

    def validate(self, data):
        """Validate this activity - check end date is after start date, etc."""
        # Check that start_date is before end_date
        if (
            "end_date" in data
            and data["end_date"]
            and data["start_date"] > data["end_date"]
        ):
            raise serializers.ValidationError(
                _("Startdato skal være før eller identisk med slutdato")
            )

        # One time payments should have a payment date in the payment plan.
        is_one_time_payment = (
            data["payment_plan"]["payment_type"]
            == PaymentSchedule.ONE_TIME_PAYMENT
        )
        if is_one_time_payment and (
            "payment_date" not in data["payment_plan"]
            or data["payment_plan"]["payment_date"] is None
        ):
            raise serializers.ValidationError(
                _("der skal angives en betalingsdato for engangsbetaling")
            )

        # Monthly payments that are not expected adjustments should have a
        # valid start_date, end_date and day_of_month that results in payments.
        is_monthly_payment = (
            "payment_frequency" in data["payment_plan"]
            and data["payment_plan"]["payment_frequency"]
            == PaymentSchedule.MONTHLY
        )
        if (
            is_monthly_payment
            and ("end_date" in data and data["end_date"])
            and not ("modifies" in data and data["modifies"])
        ):
            start_date = data["start_date"]
            end_date = data["end_date"]
            payment_type = data["payment_plan"]["payment_type"]
            payment_frequency = data["payment_plan"]["payment_frequency"]
            payment_day_of_month = data["payment_plan"]["payment_day_of_month"]
            has_payments = list(
                create_rrule(
                    payment_type,
                    payment_frequency,
                    payment_day_of_month,
                    start_date,
                    until=end_date,
                )
            )
            if not has_payments:
                raise serializers.ValidationError(
                    _("Betalingsparametre resulterer ikke i nogen betalinger")
                )

        # Cash payments that are not fictive should have a "valid" start_date
        # based on payment date exclusions.
        data_copy = data.copy()

        if (
            "price_per_unit" in data_copy["payment_plan"]
            and data_copy["payment_plan"]["price_per_unit"]
        ):
            data_copy["payment_plan"]["price_per_unit"] = PriceSerializer(
                data=data_copy["payment_plan"]["price_per_unit"]
            ).instance
        data_copy["payment_plan"] = PaymentSchedule(
            **data_copy.pop("payment_plan")
        )
        instance = Activity(**data_copy)

        is_valid_start_date = instance.is_valid_activity_start_date()
        if not is_valid_start_date:
            raise serializers.ValidationError(
                _(
                    "Startdato skal være i fremtiden og "
                    "der skal være mindst to udbetalingsdage i række"
                    " fra nu og til startdatoen"
                )
            )

        if "modifies" in data and data["modifies"]:
            # run the validate_expected flow.
            try:
                instance.validate_expected()
            except forms.ValidationError as e:
                raise serializers.ValidationError(e.message)
        return data

    class Meta:
        model = Activity
        fields = "__all__"


class BaseAppropriationSerializer(serializers.ModelSerializer):
    """Base Serializer for the Appropriation model."""

    status = serializers.ReadOnlyField()
    total_granted_this_year = serializers.ReadOnlyField()
    total_granted_full_year = serializers.ReadOnlyField()
    total_expected_this_year = serializers.ReadOnlyField()
    total_expected_full_year = serializers.ReadOnlyField()
    total_cost_expected = serializers.ReadOnlyField()
    total_cost_granted = serializers.ReadOnlyField()

    granted_from_date = serializers.ReadOnlyField()
    granted_to_date = serializers.ReadOnlyField()
    case__cpr_number = serializers.ReadOnlyField(source="case.cpr_number")
    case__name = serializers.ReadOnlyField(source="case.name")
    case__sbsys_id = serializers.ReadOnlyField(source="case.sbsys_id")
    main_activity__details__id = serializers.ReadOnlyField(
        source="main_activity.details.id", default=None
    )

    num_ongoing_draft_or_expected_activities = (
        serializers.SerializerMethodField()
    )
    num_ongoing_activities = serializers.SerializerMethodField()

    @staticmethod
    def setup_eager_loading(queryset):
        """Set up eager loading for improved performance."""
        queryset = queryset.prefetch_related("case", "activities")
        return queryset

    def get_num_ongoing_draft_or_expected_activities(self, appropriation):
        """Get number of ongoing related draft or expected activities."""
        return (
            appropriation.activities.filter(
                Q(status=STATUS_DRAFT) | Q(status=STATUS_EXPECTED),
                modified_by__isnull=True,
            )
            .ongoing()
            .count()
        )

    def get_num_ongoing_activities(self, appropriation):
        """Get number of ongoing activities."""
        return (
            appropriation.activities.filter(modified_by__isnull=True)
            .exclude(status=STATUS_DELETED)
            .ongoing()
            .count()
        )

    class Meta:
        model = Appropriation
        fields = "__all__"


class ListAppropriationSerializer(BaseAppropriationSerializer):
    """Serializer for the Appropriation model for a list."""

    pass


class AppropriationSerializer(BaseAppropriationSerializer):
    """Serializer for a single Appropriation model."""

    main_activity = ActivitySerializer(read_only=True)
    activities = serializers.SerializerMethodField()

    def get_activities(self, appropriation):
        """Get activities on appropriation."""
        activities = appropriation.activities.exclude(status=STATUS_DELETED)
        serializer = ActivitySerializer(
            instance=activities, many=True, read_only=True
        )
        return serializer.data


class PaymentMethodDetailsSerializer(serializers.ModelSerializer):
    """Serializer for the PaymentMethodDetails model."""

    class Meta:
        model = PaymentMethodDetails
        fields = "__all__"


class RelatedPersonSerializer(serializers.ModelSerializer):
    """Serializer for the RelatedPerson model."""

    class Meta:
        model = RelatedPerson
        fields = "__all__"


class MunicipalitySerializer(serializers.ModelSerializer):
    """Serializer for the Municipality model."""

    class Meta:
        model = Municipality
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for the Team model."""

    class Meta:
        model = Team
        fields = "__all__"


class SchoolDistrictSerializer(serializers.ModelSerializer):
    """Serializer for the SchoolDistrict model."""

    class Meta:
        model = SchoolDistrict
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for the Section model."""

    class Meta:
        model = Section
        fields = "__all__"


class SectionInfoSerializer(serializers.ModelSerializer):
    """Serializer for the SectionInfo model."""

    class Meta:
        model = SectionInfo
        fields = "__all__"


class ActivityDetailsSerializer(serializers.ModelSerializer):
    """Serializer for the ActivityDetails model."""

    class Meta:
        model = ActivityDetails
        fields = "__all__"


class ServiceProviderSerializer(serializers.ModelSerializer):
    """Serializer for the ServiceProvider model."""

    class Meta:
        model = ServiceProvider
        fields = "__all__"


class ApprovalLevelSerializer(serializers.ModelSerializer):
    """Serializer for the ApprovalLevel model."""

    class Meta:
        model = ApprovalLevel
        fields = "__all__"


class EffortStepSerializer(serializers.ModelSerializer):
    """Serializer for the EffortStep model."""

    class Meta:
        model = EffortStep
        fields = "__all__"


class TargetGroupSerializer(serializers.ModelSerializer):
    """Serializer for the TargetGroup model."""

    class Meta:
        model = TargetGroup
        fields = "__all__"


class InternalPaymentRecipientSerializer(serializers.ModelSerializer):
    """Serializer for the InternalPaymentRecipient model."""

    class Meta:
        model = InternalPaymentRecipient
        fields = "__all__"


class EffortSerializer(serializers.ModelSerializer):
    """Serializer for the Effort model."""

    class Meta:
        model = Effort
        fields = "__all__"
