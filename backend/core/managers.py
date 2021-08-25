# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Custom query set managers."""
import datetime

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
    OuterRef,
    Subquery,
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
    paid_date_or_date_case = Case(
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

    def annotate_paid_date_or_date(self):
        """Annotate all payments with paid date or payment date."""
        return self.annotate(paid_date_or_date=self.paid_date_or_date_case)

    def paid_date_or_date_gte(self, date):
        """Return all payments with paid date or payment date >= date."""
        return self.annotate_paid_date_or_date().filter(
            paid_date_or_date__gte=date
        )

    def paid_date_or_date_lte(self, date):
        """Return all payments with paid date or payment date <= date."""
        return self.annotate_paid_date_or_date().filter(
            paid_date_or_date__lte=date
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

    def in_year(self, year=None):
        """ Filter payments for a year."""
        if not year:
            year = timezone.now().year

        return self.exclude(
            ~Q(paid_date__year=year), paid_date__isnull=False
        ).exclude(~Q(date__year=year), paid_date__isnull=True)


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
                    Cast(
                        ExtractYear(self.paid_date_or_date_case), CharField()
                    ),
                    Value("-", CharField()),
                    LPad(
                        Cast(
                            ExtractMonth(self.paid_date_or_date_case),
                            CharField(),
                        ),
                        2,
                        fill_text=Value("0"),
                    ),
                )
            )
            .values("date_month")
            .order_by("date_month")
            .annotate(amount=Sum(self.amount_case))
        )

    def expected_payments_for_report_list(self):
        """Filter payments for a report of granted AND expected payments."""
        from core.models import STATUS_GRANTED, STATUS_EXPECTED, Activity

        current_year = timezone.now().year
        two_years_ago = current_year - 2
        beginning_of_two_years_ago = datetime.date.min.replace(
            year=two_years_ago
        )

        expected_activities = Activity.objects.filter(
            Q(status=STATUS_GRANTED) | Q(status=STATUS_EXPECTED)
        )
        payment_ids = [
            payment.id
            for activity in expected_activities
            for payment in activity.applicable_payments
        ]
        return (
            self.filter(id__in=payment_ids)
            .paid_date_or_date_gte(beginning_of_two_years_ago)
            .select_related(
                "payment_schedule__activity__appropriation__case",
                "payment_schedule__activity__appropriation__section",
                "payment_schedule__activity__details",
            )
        )

    def granted_payments_for_report_list(self):
        """Filter payments for a report of only granted payments."""
        from core.models import STATUS_GRANTED, Activity

        current_year = timezone.now().year
        two_years_ago = current_year - 2
        beginning_of_two_years_ago = datetime.date.min.replace(
            year=two_years_ago
        )

        granted_activities = Activity.objects.filter(status=STATUS_GRANTED)
        payment_ids = granted_activities.values_list(
            "payment_plan__payments__pk", flat=True
        )

        return (
            self.filter(id__in=payment_ids)
            .paid_date_or_date_gte(beginning_of_two_years_ago)
            .select_related(
                "payment_schedule__activity__appropriation__case",
                "payment_schedule__activity__appropriation__section",
                "payment_schedule__activity__details",
            )
        )


class ActivityQuerySet(models.QuerySet):
    """QuerySet and Manager for the Activity model."""

    def ongoing(self):
        """Only include ongoing, i.e. non-expired Activities."""
        # On activity level we only care about end_date.
        today = timezone.now().date()
        return self.filter(Q(end_date__isnull=True) | Q(end_date__gte=today))

    def expired(self):
        """Only include expired activities."""
        # On activity level we only care about end_date.
        today = timezone.now().date()
        return self.filter(end_date__lt=today)


class AppropriationQuerySet(models.QuerySet):
    """QuerySet and Manager for the Appropriation model."""

    def ongoing(self):
        """Only include ongoing, i.e. non-expired Appropriations."""
        expired_ids = self.expired().values_list("id", flat=True)
        return self.exclude(id__in=expired_ids)

    def expired(self):
        """Only include expired Appropriations."""
        from core.models import MAIN_ACTIVITY

        today = timezone.now().date()

        main_expired_q = Q(
            activities__end_date__lt=today,
            activities__activity_type=MAIN_ACTIVITY,
        )
        main_q = Q(activities__activity_type=MAIN_ACTIVITY)
        # exclude appropriations with no activities and filter for activities
        # where the number of main activities and expired main activities
        # are the same
        return (
            self.exclude(activities__isnull=True)
            .annotate(
                expired_main_activities_count=Count(
                    "activities", filter=main_expired_q
                )
            )
            .annotate(main_activities_count=Count("activities", filter=main_q))
            .exclude(expired_main_activities_count=0, main_activities_count=0)
            .filter(expired_main_activities_count=F("main_activities_count"))
        ).distinct()

    def annotate_main_activity_details_id(self):
        """Annotate the main_activity__details__id as a subquery."""
        from core.models import Activity, MAIN_ACTIVITY

        main_activity = Activity.objects.filter(
            appropriation=OuterRef("id")
        ).filter(activity_type=MAIN_ACTIVITY, modifies__isnull=True)

        return self.annotate(
            main_activity__details__id=Subquery(
                main_activity.values("details__id")[:1]
            )
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

    def expected_cases_for_report_list(self):
        """Filter cases for a report of granted AND expected cases."""
        from core.models import STATUS_GRANTED, STATUS_EXPECTED

        cases = self.filter(
            Q(appropriations__activities__status=STATUS_GRANTED)
            | Q(appropriations__activities__status=STATUS_EXPECTED)
        ).distinct()

        return cases
