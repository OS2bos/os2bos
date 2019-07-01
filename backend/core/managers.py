from django.db import models
from django.db.models import Sum, CharField, Value
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
        Annotate each Payment with a date_str = YYYY - MM
        """
        return self.annotate(
            date_str=Concat(
                Cast(ExtractYear("date"), CharField()),
                Value("-", CharField()),
                LPad(Cast(ExtractMonth("date"), CharField()), 2, fill_text=Value("0")),
            )
        ).values("date_str").order_by("date_str").annotate(Sum("amount"))
