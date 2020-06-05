# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Custom query set managers."""

from django.utils import timezone
from django.db import models
from django.db.models import (
    Case,
    When,
    Sum,
    CharField,
    DecimalField,
    Value,
    Q,
    F,
    Count,
)
from django.db.models.functions import (
    Coalesce,
    Cast,
    Concat,
    ExtractMonth,
    ExtractYear,
    LPad,
)


class PaymentQuerySet(models.QuerySet):
    """Handle payments properly - some are paid and others are not.

    In general we should use the scheduled day and amount for unpaid
    payments and the paid date and paid amount for paid ones.
    """

    # Case for using paid_date if available, else date.
    date_case = Case(
        When(paid_date__isnull=False, then="paid_date"),
        When(date__isnull=False, then="date"),
        default="date",
    )
    # Case for using paid_amount if available, else amount.
    amount_case = Case(
        When(paid_amount__isnull=False, then="paid_amount"),
        When(amount__isnull=False, then="amount"),
        default="amount",
        output_field=DecimalField(),
    )

    def paid_date_or_date_gte(self, date):
        """Return all payments with paid date or payment date >= date."""
        return self.annotate(relevant_date=self.date_case).filter(
            relevant_date__gte=date
        )

    def paid_date_or_date_lte(self, date):
        """Return all payments with paid date or payment date <= date."""
        return self.annotate(relevant_date=self.date_case).filter(
            relevant_date__lte=date
        )

    def strict_amount_sum(self):
        """Sum over Payments amount."""
        return (
            self.aggregate(amount_sum=Coalesce(Sum("amount"), 0))["amount_sum"]
            or 0
        )

    def amount_sum(self):
        """Sum over Payments with paid_amount overruling amount."""
        return (
            self.aggregate(amount_sum=Coalesce(Sum(self.amount_case), 0))[
                "amount_sum"
            ]
            or 0
        )

    def in_this_year(self):
        """Filter Payments only in the current year."""
        now = timezone.now()

        return self.exclude(
            ~Q(paid_date__year=now.year), paid_date__isnull=False
        ).exclude(~Q(date__year=now.year), paid_date__isnull=True)

    def group_by_monthly_amounts(self):
        """
        Group by monthly amounts.

        The output will look like this::

            [
                {'date_month': '2019-07', 'amount': Decimal('3000.00')},
                {'date_month': '2019-08', 'amount': Decimal('1500.00')}
            ]

        """
        return (
            self.annotate(
                date_month=Concat(
                    Cast(ExtractYear(self.date_case), CharField()),
                    Value("-", CharField()),
                    LPad(
                        Cast(ExtractMonth(self.date_case), CharField()),
                        2,
                        fill_text=Value("0"),
                    ),
                )
            )
            .values("date_month")
            .order_by("date_month")
            .annotate(amount=Sum(self.amount_case))
        )


class CaseQuerySet(models.QuerySet):
    """Distinguish between expired and ongoing cases."""

    def ongoing(self):
        """Only include ongoing, i.e. non-expired Cases."""
        expired_ids = self.expired().values_list("id", flat=True)
        return self.exclude(id__in=expired_ids)

    def expired(self):
        """Only include expired Cases."""
        from core.models import MAIN_ACTIVITY

        today = timezone.now().date()

        main_expired_q = Q(
            appropriations__activities__end_date__lt=today,
            appropriations__activities__activity_type=MAIN_ACTIVITY,
        )
        main_q = Q(appropriations__activities__activity_type=MAIN_ACTIVITY)
        # exclude cases with no activities and filter for activities
        # where the number of main activities and expired main activities
        # are the same
        return (
            self.exclude(appropriations__activities__isnull=True)
            .annotate(
                expired_main_activities_count=Count(
                    "appropriations__activities", filter=main_expired_q
                )
            )
            .annotate(
                main_activities_count=Count(
                    "appropriations__activities", filter=main_q
                )
            )
            .exclude(expired_main_activities_count=0, main_activities_count=0)
            .filter(expired_main_activities_count=F("main_activities_count"))
        ).distinct()


class PaymentScheduleManager(models.Manager):
    """Handle prices and rates correctly when updating object."""

    def create(self, *args, **kwargs):
        """Create a new PaymentSchedule."""
        from core.models import PaymentSchedule as P
        payment_pricing_date = kwargs.pop("payment_pricing_date", None)
        payment_schedule = super().create(*args, **kwargs)
        # TODO: Handle this all correctly
        # Note: "requirements" should be handled in serializer's
        # validate function.
        if payment_schedule.payment_cost_type == P.FIXED_PRICE:
            # Payment amount needs to be given, apart from that s'all
            # good. Rate and payment_pricing_date can't be given.
            payment_pricing_date
            pass
        elif payment_schedule.payment_cost_type == P.PER_UNIT_PRICE:
            # Units need to be given.
            # Payment amount needs to be given.
            # Payment pricing date defaults to today.
            # We will create a new price object defaulting to minus
            # infinity to infinity - periods must be edited elsewhere.
            pass
        elif payment_schedule.payment_cost_type == P.GLOBAL_RATE_PRICE:
            # Rate needs to be given.
            # Payment amount should not be given.
            # Units need to be given.
            # Payment pricing date defaults to today.
            # In fact, probably nothing needs to be done.
            pass
        return payment_schedule

    def update(self, *args, **kwargs):
        """Handle rates and prices correctly."""
        return super().update(*args, **kwargs)
