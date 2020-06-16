from django.db import migrations


def migrate_old_prices(apps, schema_editor):
    PaymentSchedule = apps.get_model("core", "PaymentSchedule")
    Price = apps.get_model("core", "Price")

    for payment_schedule in PaymentSchedule.objects.all():
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
            # Set the payment_cost_type
            payment_schedule.payment_cost_type = "PER_UNIT"
            payment_schedule.save()
            # These payment types should have a Price with a single period.
            price = Price.objects.create(payment_schedule=payment_schedule)
            price.set_rate_amount(
                payment_schedule.payment_amount, start_date=None, end_date=None
            )


class Migration(migrations.Migration):

    dependencies = [("core", "0067_auto_20200615_1846")]

    operations = [migrations.RunPython(migrate_old_prices)]
