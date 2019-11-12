from django.utils.translation import gettext_lazy as _

import rest_framework_filters as filters

from core.models import (
    Case,
    PaymentSchedule,
    Activity,
    Payment,
    Section,
    EffortStep,
)


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


class CaseForPaymentFilter(filters.FilterSet):
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
        CaseForPaymentFilter,
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

    paid_date__gte = filters.DateFilter(
        field_name="paid_date",
        lookup_expr="gte",
        label=_("Betalingsdato større eller lig med"),
    )
    paid_date__lte = filters.DateFilter(
        field_name="paid_date",
        lookup_expr="lte",
        label=_("Betalingsdato mindre eller lig med"),
    )

    date__gte = filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        label=_("Dato større eller lig med"),
    )
    date__lte = filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        label=_("Dato mindre eller lig med"),
    )

    paid_date_or_date__gte = filters.DateFilter(
        method="filter_paid_date_or_date_gte",
        label=_("Betalingsdato eller Dato større eller lig med"),
    )
    paid_date_or_date__lte = filters.DateFilter(
        method="filter_paid_date_or_date_lte",
        label=_("Betalingsdato eller Dato mindre eller lig med"),
    )

    def filter_paid_date_or_date_gte(self, queryset, name, value):
        return queryset.paid_date_or_date_gte(value)

    def filter_paid_date_or_date_lte(self, queryset, name, value):
        return queryset.paid_date_or_date_lte(value)

    class Meta:
        model = Payment
        fields = "__all__"


class EffortStepFilter(filters.FilterSet):
    class Meta:
        model = EffortStep
        fields = {"number": ["exact"]}


class AllowedForStepsFilter(filters.FilterSet):
    allowed_for_steps = filters.RelatedFilter(
        EffortStepFilter,
        field_name="allowed_for_steps",
        queryset=Section.objects.all(),
    )

    class Meta:
        model = Section
        fields = "__all__"
