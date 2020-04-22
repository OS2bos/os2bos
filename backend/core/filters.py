# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Filters and filtersets for filtering in REST API.

Filters allow us to do basic search for objects on allowed field without
adding the complexity of an entire search engine nor of custom queries.
"""


from django.utils.translation import gettext

import rest_framework_filters as filters

from core.models import (
    Case,
    PaymentSchedule,
    Activity,
    Payment,
    Section,
    Appropriation,
    MAIN_ACTIVITY,
)


class CaseFilter(filters.FilterSet):
    """Filter cases on the "expired" field."""

    expired = filters.BooleanFilter(
        method="filter_expired", label=gettext("Udgået")
    )

    class Meta:
        model = Case
        fields = "__all__"

    def filter_expired(self, queryset, name, value):
        """Filter out cases according to value."""
        if value:
            return queryset.expired()
        else:
            return queryset.ongoing()


class CaseForPaymentFilter(filters.FilterSet):
    """Filter cases on CPR number."""

    class Meta:
        model = Case
        fields = {"cpr_number": ["exact"]}


class CaseForAppropriationFilter(filters.FilterSet):
    """Filter cases on CPR number."""

    class Meta:
        model = Case
        fields = {
            "cpr_number": ["exact"],
            "team": ["exact"],
            "case_worker": ["exact"],
        }


class AppropriationFilter(filters.FilterSet):
    """Filter appropriation."""

    case = filters.RelatedFilter(
        CaseForAppropriationFilter,
        field_name="case",
        label=Case._meta.verbose_name.title(),
        queryset=Case.objects.all(),
    )

    main_activity = filters.ModelChoiceFilter(
        queryset=Activity.objects.filter(
            activity_type=MAIN_ACTIVITY, modifies__isnull=True
        ),
        label=gettext("Hovedaktivitet"),
        field_name="activities",
    )

    class Meta:
        model = Appropriation
        fields = "__all__"


class PaymentScheduleFilter(filters.FilterSet):
    """Filter payment plans on ID."""

    class Meta:
        model = PaymentSchedule
        fields = {"payment_id": ["exact"]}


class ActivityFilter(filters.FilterSet):
    """Filter activities on status."""

    class Meta:
        model = Activity
        fields = {"status": ["exact"]}


class PaymentFilter(filters.FilterSet):
    """Filter payments on payment plan, activity, case, dates, etc."""

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
        label=gettext("Betalingsdato større eller lig med"),
    )
    paid_date__lte = filters.DateFilter(
        field_name="paid_date",
        lookup_expr="lte",
        label=gettext("Betalingsdato mindre eller lig med"),
    )

    date__gte = filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        label=gettext("Dato større eller lig med"),
    )
    date__lte = filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        label=gettext("Dato mindre eller lig med"),
    )

    paid_date_or_date__gte = filters.DateFilter(
        method="filter_paid_date_or_date_gte",
        label=gettext("Betalingsdato eller Dato større eller lig med"),
    )
    paid_date_or_date__lte = filters.DateFilter(
        method="filter_paid_date_or_date_lte",
        label=gettext("Betalingsdato eller Dato mindre eller lig med"),
    )

    def filter_paid_date_or_date_gte(self, queryset, name, value):
        """Filter on value <= "best known payment date"."""
        return queryset.paid_date_or_date_gte(value)

    def filter_paid_date_or_date_lte(self, queryset, name, value):
        """Filter on value >= "best known payment date"."""
        return queryset.paid_date_or_date_lte(value)

    class Meta:
        model = Payment
        fields = "__all__"


class AllowedForStepsFilter(filters.FilterSet):
    """Filter sections on allowed effort steps."""

    allowed_for_steps = filters.NumberFilter(
        field_name="allowed_for_steps", method="filter_allowed_for_steps"
    )

    class Meta:
        model = Section
        fields = "__all__"

    def filter_allowed_for_steps(self, qs, name, value):
        """Filter on "allowed_for_steps" relation."""
        return qs.filter(allowed_for_steps__number=value)
