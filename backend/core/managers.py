from django.utils import timezone
from django.db import models
from django.db.models import Sum, CharField, Value, Q
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
        Return all ongoing (non-expired) Cases.
        """
        from core.models import Activity

        today = timezone.now().date()
        all_ongoing_main_activities = Activity.objects.filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True),
            activity_type=Activity.MAIN_ACTIVITY,
        )
        ongoing_cases = self.filter(
            Q(appropriations__isnull=True)
            | Q(appropriations__activities__isnull=True)
            | Q(appropriations__activities__in=all_ongoing_main_activities)
        ).distinct()

        return ongoing_cases

    def expired(self):
        """
        Return all expired Cases.
        """
        return self.difference(self.ongoing())
