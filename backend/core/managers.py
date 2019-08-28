# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.utils import timezone
from django.db import models
from django.db.models import Sum, CharField, Value, Q, F, Count
from django.db.models.functions import (
    Coalesce,
    Cast,
    Concat,
    ExtractMonth,
    ExtractYear,
    LPad,
)


class PaymentQuerySet(models.QuerySet):
    def amount_sum(self):
        return self.aggregate(amount_sum=Coalesce(Sum("amount"), 0))[
            "amount_sum"
        ]

    def in_this_year(self):
        now = timezone.now()
        return self.filter(date__year=now.year)

    def group_by_monthly_amounts(self):
        """
        Group by monthly amounts.

        The output will look like this:
        [
            {'date_month': '2019-07', 'amount': Decimal('3000.00')},
            {'date_month': '2019-08', 'amount': Decimal('1500.00')}
        ]
        """
        return (
            self.annotate(
                date_month=Concat(
                    Cast(ExtractYear("date"), CharField()),
                    Value("-", CharField()),
                    LPad(
                        Cast(ExtractMonth("date"), CharField()),
                        2,
                        fill_text=Value("0"),
                    ),
                )
            )
            .values("date_month")
            .order_by("date_month")
            .annotate(amount=Sum("amount"))
        )

    def expected(self):
        """
        This includes granted and expected status payments where we exclude
        the granted which has an expected in its place.

        For one time payments we exclude the old granted payment.
        For recurring payments we only exclude the old granted payments
        ocurring at or after the start_date of the expected activity.
        """
        from core.models import (
            STATUS_EXPECTED,
            STATUS_GRANTED,
            PaymentSchedule,
        )

        return (
            self.filter(
                Q(payment_schedule__activity__status=STATUS_GRANTED)
                | Q(payment_schedule__activity__status=STATUS_EXPECTED)
            )
            .exclude(
                Q(
                    date__gte=F(
                        "payment_schedule__activity__modified_by__start_date"
                    )
                ),
                **{
                    "payment_schedule__activity" "__status": STATUS_GRANTED,
                    "payment_schedule__activity"
                    "__modified_by__isnull": False,
                    "payment_schedule__activity"
                    "__modified_by__status": STATUS_EXPECTED,
                }
            )
            .exclude(
                **{
                    "payment_schedule__"
                    "payment_type": PaymentSchedule.ONE_TIME_PAYMENT,
                    "payment_schedule__activity"
                    "__modified_by__isnull": False,
                    "payment_schedule__activity"
                    "__modified_by__status": STATUS_EXPECTED,
                }
            )
        )


class CaseQuerySet(models.QuerySet):
    def ongoing(self):
        """
        Only include ongoing (non-expired) Cases.
        """
        expired_ids = self.expired().values_list("id", flat=True)
        return self.exclude(id__in=expired_ids)

    def expired(self):
        """
        Only include expired Cases.
        """
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
            .filter(expired_main_activities_count=F("main_activities_count"))
        ).distinct()
