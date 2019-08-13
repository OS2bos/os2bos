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
