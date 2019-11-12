# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django import forms

from rest_framework import serializers

from drf_writable_nested import WritableNestedModelSerializer

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
    SectionInfo,
    ActivityDetails,
    Account,
    HistoricalCase,
    ServiceProvider,
    ApprovalLevel,
    Team,
    FAMILY_DEPT,
    STATUS_DELETED,
)


class UserSerializer(serializers.ModelSerializer):
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
    expired = serializers.ReadOnlyField()

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
    account_string = serializers.ReadOnlyField()
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
    is_payable_manually = serializers.ReadOnlyField()

    def validate(self, data):
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
        exclude = ("saved_account_string",)


class PaymentScheduleSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    account = serializers.ReadOnlyField()

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related("payments")
        return queryset

    def validate(self, data):
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
                    "En betalingtype der ikke er en engangsbetaling "
                    "skal have en betalingsfrekvens"
                )
            )
        elif one_time_payment and payment_frequency:
            raise serializers.ValidationError(
                _("En engangsbetaling må ikke have en betalingsfrekvens")
            )

        return data

    class Meta:
        model = PaymentSchedule
        fields = "__all__"


class ActivitySerializer(WritableNestedModelSerializer):
    monthly_payment_plan = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    total_cost_this_year = serializers.ReadOnlyField()
    total_cost_full_year = serializers.ReadOnlyField()
    total_granted_this_year = serializers.ReadOnlyField()
    total_expected_this_year = serializers.ReadOnlyField()

    payment_plan = PaymentScheduleSerializer(partial=True, required=False)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related("payment_plan")
        return queryset

    def validate(self, data):
        # Check that start_date is before end_date
        if (
            "end_date" in data
            and data["end_date"]
            and data["start_date"] > data["end_date"]
        ):
            raise serializers.ValidationError(
                _("startdato skal være før eller identisk med slutdato")
            )

        # one time payments should have the same start and end date.
        is_one_time_payment = (
            data["payment_plan"]["payment_type"]
            == PaymentSchedule.ONE_TIME_PAYMENT
        )
        if is_one_time_payment and (
            "end_date" not in data or data["end_date"] != data["start_date"]
        ):
            raise serializers.ValidationError(
                _("startdato og slutdato skal være ens for engangsbetaling")
            )

        if "modifies" in data and data["modifies"]:
            # run the validate_expected flow.
            data_copy = data.copy()
            data_copy["payment_plan"] = PaymentSchedule(
                **data_copy.pop("payment_plan")
            )
            instance = Activity(**data_copy)
            try:
                instance.validate_expected()
            except forms.ValidationError as e:
                raise serializers.ValidationError(e.message)
        return data

    class Meta:
        model = Activity
        fields = "__all__"


class AppropriationSerializer(serializers.ModelSerializer):
    total_granted_this_year = serializers.ReadOnlyField()
    total_expected_this_year = serializers.ReadOnlyField()
    total_expected_full_year = serializers.ReadOnlyField()
    granted_from_date = serializers.ReadOnlyField()
    granted_to_date = serializers.ReadOnlyField()

    activities = serializers.SerializerMethodField()

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related("activities")
        return queryset

    def get_activities(self, appropriation):
        activities = appropriation.activities.exclude(status=STATUS_DELETED)
        serializer = ActivitySerializer(
            instance=activities, many=True, read_only=True
        )
        return serializer.data

    class Meta:
        model = Appropriation
        fields = "__all__"


class PaymentMethodDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodDetails
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


class SectionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionInfo
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
