from django.utils.translation import gettext_lazy as _

import rest_framework_filters as filters

from core.models import Case, PaymentSchedule, Activity, Payment, Section


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

    paid_date__gt = filters.DateFilter(
        field_name="paid_date",
        lookup_expr="gt",
        label=_("Betalingsdato større end"),
    )
    paid_date__lt = filters.DateFilter(
        field_name="paid_date",
        lookup_expr="lt",
        label=_("Betalingsdato mindre end"),
    )

    class Meta:
        model = Payment
        fields = "__all__"


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class AllowedForStepsFilter(filters.FilterSet):
    allowed_for_steps = CharInFilter(
        field_name="allowed_for_steps", lookup_expr="contains"
    )

    class Meta:
        model = Section
        fields = "__all__"
