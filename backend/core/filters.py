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
import json

from django.utils import timezone
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta, MO, SU

from django.forms import DateField, Field, ValidationError
from django.utils.translation import gettext

import django_filters as filters
from django_filters.utils import handle_timezone

from core.models import (
    Case,
    Payment,
    Section,
    Appropriation,
)


class DateRangeField(Field):
    """Custom DateRangeField for use in DateFromToRangeFilter."""

    none_value = "None"

    def compress(self, data_list):
        """Override compress to convert dates."""
        if data_list:
            start_date, stop_date = data_list
            if start_date:
                start_date = handle_timezone(
                    datetime.combine(start_date, time.min)
                )
            if stop_date:
                stop_date = handle_timezone(
                    datetime.combine(stop_date, time.max)
                )
            return slice(start_date, stop_date)
        return None

    def clean(self, value):
        """Override clean to enforce "None" or dates."""
        if value:
            clean_data = []
            values = json.loads(value)
            if isinstance(values, (list, tuple)):
                for field_value in values:
                    if field_value == self.none_value:
                        clean_data.append(None)
                    else:
                        clean_data.append(DateField().clean(field_value))
            else:
                raise ValidationError(
                    gettext(
                        "DateRangeField skal være en liste"
                        ' indeholdende datoer eller "None"'
                    )
                )
            return self.compress(clean_data)
        else:
            return self.compress([])


class CustomDateFromToRangeFilter(filters.RangeFilter):
    r"""
    Custom DateFromToRangeFilter.

    Works with our GraphQL API
    (and DRF) and takes a json list of date strings.

    Sadly graphene-django does not support filters.DateFromToRangeFilter.
    https://github.com/graphql-python/graphene-django/issues/92

    Example in GraphQL:
    dstDate:"[\"2016-12-01\",\"2016-12-31\"]"
    or
    dstDate:"[\"None\",\"2016-12-31\"]"
    """

    field_class = DateRangeField


class CaseFilter(filters.FilterSet):
    """Filter cases on the "expired" field."""

    expired = filters.BooleanFilter(
        method="filter_expired", label=gettext("Udgået")
    )

    case_worker__team = filters.NumberFilter(
        label=gettext("Team for Sagsbehandler")
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


class AppropriationFilter(filters.FilterSet):
    """Filter appropriation."""

    main_activity__details__id = filters.NumberFilter(
        label=gettext("Aktivitetsdetalje for hovedaktivitet")
    )

    case__cpr_number = filters.CharFilter(label=gettext("CPR nummer for Sag"))

    case__case_worker = filters.NumberFilter(
        label=gettext("Sagsbehandler for Sag")
    )

    case__sbsys_id = filters.CharFilter(label=gettext("SBSYS ID for Sag"))

    case__case_worker__team = filters.NumberFilter(
        label=gettext("Team for Sagsbehandler for Sag")
    )

    dst_date = CustomDateFromToRangeFilter(
        method="filter_dst_date",
        label=gettext(
            'DST dato fra/til (f.eks. "[\\"2021-01-02\\",\\"None\\"]")'
        ),
    )

    def filter_dst_date(self, queryset, name, value):
        """Filter on DST date ("from_date" and "to_date")."""
        return queryset.appropriations_for_dst_payload(value.start, value.stop)

    class Meta:
        model = Appropriation
        fields = "__all__"


class PaymentFilter(filters.FilterSet):
    """Filter payments on payment plan, activity, case, dates, etc."""

    payment_schedule__payment_id = filters.NumberFilter(
        label=gettext("Betalings-id for Betalingsplan")
    )

    case__cpr_number = filters.CharFilter(
        label=gettext("CPR-nummer for Sag"),
        field_name=(
            "payment_schedule__activity__appropriation__case__cpr_number"
        ),
    )

    activity__status = filters.CharFilter(
        label=gettext("Status for aktivitet"),
        field_name="payment_schedule__activity__status",
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

    generic_time_choices = (
        ("previous", "Forrige"),
        ("current", "Nuværende"),
        ("next", "Næste"),
    )

    paid_date_or_date_week = filters.ChoiceFilter(
        method="filter_paid_date_or_date_week",
        label=gettext("Betalingsdato eller Dato for uge"),
        choices=generic_time_choices,
    )

    paid_date_or_date_month = filters.ChoiceFilter(
        method="filter_paid_date_or_date_month",
        label=gettext("Betalingsdato eller Dato for måned"),
        choices=generic_time_choices,
    )

    paid_date_or_date_year = filters.ChoiceFilter(
        method="filter_paid_date_or_date_year",
        label=gettext("Betalingsdato eller Dato for år"),
        choices=generic_time_choices,
    )

    date_week = filters.ChoiceFilter(
        method="filter_date_week",
        label=gettext("Betalingsdato eller Dato for uge"),
        choices=generic_time_choices,
    )

    date_month = filters.ChoiceFilter(
        method="filter_date_month",
        label=gettext("Betalingsdato eller Dato for måned"),
        choices=generic_time_choices,
    )

    date_year = filters.ChoiceFilter(
        method="filter_date_year",
        label=gettext("Betalingsdato eller Dato for år"),
        choices=generic_time_choices,
    )

    def filter_paid_date_or_date_gte(self, queryset, name, value):
        """Filter on value <= "best known payment date"."""
        return queryset.paid_date_or_date_gte(value)

    def filter_paid_date_or_date_lte(self, queryset, name, value):
        """Filter on value >= "best known payment date"."""
        return queryset.paid_date_or_date_lte(value)

    def filter_paid_date_or_date_week(self, queryset, name, value):
        """Filter best known payment date on previous, current, next week."""
        now = timezone.now().date()
        if value == "previous":
            reference_date = now - relativedelta(weeks=1)
        elif value == "current":
            reference_date = now
        elif value == "next":  # pragma: no branch
            reference_date = now + relativedelta(weeks=1)

        min_date = reference_date - relativedelta(weekday=MO(-1))
        max_date = reference_date + relativedelta(weekday=SU(1))
        return queryset.paid_date_or_date_lte(max_date).paid_date_or_date_gte(
            min_date
        )

    def filter_paid_date_or_date_month(self, queryset, name, value):
        """Filter best known payment date on previous, current, next month."""
        now = timezone.now().date()
        if value == "previous":
            reference_date = now - relativedelta(months=1)
        elif value == "current":
            reference_date = now
        elif value == "next":  # pragma: no branch
            reference_date = now + relativedelta(months=1)

        min_date = reference_date + relativedelta(day=1)
        # day=31 will always return the last day of the month.
        max_date = reference_date + relativedelta(day=31)
        return queryset.paid_date_or_date_lte(max_date).paid_date_or_date_gte(
            min_date
        )

    def filter_paid_date_or_date_year(self, queryset, name, value):
        """Filter best known payment date on previous, current, next year."""
        now = timezone.now().date()
        if value == "previous":
            year = (now - relativedelta(years=1)).year
        elif value == "current":
            year = now.year
        elif value == "next":  # pragma: no branch
            year = (now + relativedelta(years=1)).year

        min_date = date(day=1, month=1, year=year)
        max_date = date(day=31, month=12, year=year)
        return queryset.paid_date_or_date_lte(max_date).paid_date_or_date_gte(
            min_date
        )

    def filter_date_week(self, queryset, name, value):
        """Filter date on previous, current, next week."""
        now = timezone.now().date()
        if value == "previous":
            reference_date = now - relativedelta(weeks=1)
        elif value == "current":
            reference_date = now
        elif value == "next":  # pragma: no branch
            reference_date = now + relativedelta(weeks=1)

        min_date = reference_date - relativedelta(weekday=MO(-1))
        max_date = reference_date + relativedelta(weekday=SU(1))
        return queryset.filter(date__lte=max_date, date__gte=min_date)

    def filter_date_month(self, queryset, name, value):
        """Filter date on previous, current, next month."""
        now = timezone.now().date()
        if value == "previous":
            reference_date = now - relativedelta(months=1)
        elif value == "current":
            reference_date = now
        elif value == "next":  # pragma: no branch
            reference_date = now + relativedelta(months=1)

        min_date = reference_date + relativedelta(day=1)
        # day=31 will always return the last day of the month.
        max_date = reference_date + relativedelta(day=31)
        return queryset.filter(date__lte=max_date, date__gte=min_date)

    def filter_date_year(self, queryset, name, value):
        """Filter date on previous, current, next year."""
        now = timezone.now().date()
        if value == "previous":
            year = (now - relativedelta(years=1)).year
        elif value == "current":
            year = now.year
        elif value == "next":  # pragma: no branch
            year = (now + relativedelta(years=1)).year

        min_date = date(day=1, month=1, year=year)
        max_date = date(day=31, month=12, year=year)
        return queryset.filter(date__lte=max_date, date__gte=min_date)

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
