from datetime import date

from django.db import migrations
from django.utils.translation import gettext_lazy as _

import portion as P


def create_interval(start_date, end_date):
    """create_interval method from current Price model."""
    if start_date is None:
        start_date = -P.inf
    if end_date is None:
        end_date = P.inf
    if not start_date < end_date:
        raise ValueError(_("Slutdato skal være mindre end startdato"))
    return P.closedopen(start_date, end_date)


def set_rate_amount(apps, price, amount, start_date=None, end_date=None):
    """set_rate_amount method from current Price model."""
    RatePerDate = apps.get_model("core", "RatePerDate")
    new_period = create_interval(start_date, end_date)

    existing_periods = price.rates_per_date.all()
    d = P.IntervalDict()
    for period in existing_periods:
        interval = create_interval(period.start_date, period.end_date)
        d[interval] = period.rate

    # We generate all periods from scratch to avoid complicated
    # merging logic.
    existing_periods.delete()

    d[new_period] = amount
    for period in d.keys():
        for interval in list(period):
            # In case of composite intervals
            start = (
                interval.lower if isinstance(interval.lower, date) else None
            )
            end = interval.upper if isinstance(interval.upper, date) else None
            period_rate_dict = d[
                P.closedopen(interval.lower, interval.upper) or date.today()
            ]
            rate = period_rate_dict.values()[0]

            rpd = RatePerDate(
                start_date=start, end_date=end, rate=rate, main_rate=price
            )
            rpd.save()


def migrate_old_prices(apps, schema_editor):
    PaymentSchedule = apps.get_model("core", "PaymentSchedule")
    Price = apps.get_model("core", "Price")

    for payment_schedule in PaymentSchedule.objects.all():
        # Historical PaymentSchedule model does not have attributes
        # so we use the hard-coded values of "payment_type".
        if (
            payment_schedule.payment_type == "ONE_TIME_PAYMENT"
            or payment_schedule.payment_type == "RUNNING_PAYMENT"
        ):
            # These payment types are already handled by setting
            # a default payment_cost_type of FIXED_PRICE
            continue

        elif (
            payment_schedule.payment_type == "PER_HOUR_PAYMENT"
            or payment_schedule.payment_type == "PER_DAY_PAYMENT"
            or payment_schedule.payment_type == "PER_KM_PAYMENT"
        ):
            # These payment types should have a Price with a single period
            # of unbounded start and end.
            price = Price.objects.create(payment_schedule=payment_schedule)
            set_rate_amount(
                apps,
                price,
                payment_schedule.payment_amount,
                start_date=None,
                end_date=None,
            )

            # Set the payment_cost_type and payment_amount.
            payment_schedule.payment_cost_type = "PER_UNIT"
            payment_schedule.payment_amount = None
            payment_schedule.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0067_auto_20200615_1846")]

    operations = [migrations.RunPython(migrate_old_prices)]
