from django.utils import timezone
from django.db import models
from django.db.models import (
    Sum,
    CharField,
    Value,
    Q,
    Case,
    When,
    BooleanField,
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
    def annotate_expired(self):
        from core.models import Activity

        today = timezone.now().date()
        all_ongoing_main_activities = Activity.objects.filter(
            Q(end_date__gte=today) | Q(end_date__isnull=True),
            activity_type=Activity.MAIN_ACTIVITY,
        )
        # return self.annotate(
        #     expired=Case(
        #         When(appropriations__isnull=True, then=Value(False)),
        #         When(
        #             appropriations__activities__isnull=True, then=Value(False)
        #         ),
        #         When(
        #             appropriations__activities__in=all_ongoing_main_activities,
        #             then=Value(False),
        #         ),
        #         default=Value(True),
        #         output_field=BooleanField(),
        #     )
        # )
        ongoing_cases = self.filter(
            appropriations__isnull=True,
            appropriations__activities__isnull=True,
            appropriations__activities__in=all_ongoing_main_activities,
        ).distinct()
        expired_cases = self.difference(ongoing_cases).distinct()

        return ongoing_cases.annotate(
            expired=Value(False, BooleanField())
        ) | expired_cases.annotate(expired=Value(True, BooleanField()))
