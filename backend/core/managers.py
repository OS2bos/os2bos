from django.db import models
from django.db.models import Sum, CharField, Value, F
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
        return self.aggregate(amount_sum=Coalesce(Sum("amount"), 0))

    def is_paid(self):
        return self.filter(paid=True)

    def bin_in_monthly_amounts(self):
        """
        Bin in monthly amounts.

        The output will look like this:
        [
            {'date_month': '2019-07', 'amount': Decimal('3000.00')},
            {'date_month': '2019-08', 'amount': Decimal('1500.00')}
        ]
        """
        return self.annotate(
            date_month=Concat(
                Cast(ExtractYear("date"), CharField()),
                Value("-", CharField()),
                LPad(Cast(ExtractMonth("date"), CharField()), 2, fill_text=Value("0")),
            )
        ).values("date_month").order_by("date_month").annotate(amount=Sum("amount"))


    def bin_in_monthly_amounts_per_status(self):
        """
        Bin in monthly amounts per Activity status.

        The output will look like this:
        [
            {'status': 'EXPECTED', 'date_month': '2019-07', 'amount': Decimal('3000.00')}
            {'status': 'GRANTED', 'date_month': '2019-07', 'amount': Decimal('1200.00')}
        ]
        """
        return self.annotate(
            date_month=Concat(
                Cast(ExtractYear("date"), CharField()),
                Value("-", CharField()),
                LPad(Cast(ExtractMonth("date"), CharField()), 2, fill_text=Value("0")),
            )
        ).values(
            "date_month",
            status=F("payment_schedule__activity__status")
        ).order_by(
            "date_month",
            "status"
        ).annotate(amount=Sum("amount"))
