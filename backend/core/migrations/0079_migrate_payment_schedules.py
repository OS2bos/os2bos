from django.db import migrations


def migrate_payment_schedules(apps, schema_editor):
    PaymentSchedule = apps.get_model("core", "PaymentSchedule")

    one_time_payments = PaymentSchedule.objects.filter(
        payment_type="ONE_TIME_PAYMENT"
    )
    for payment_schedule in one_time_payments:
        payment_schedule.payment_date = payment_schedule.activity.start_date
        payment_schedule.save()

class Migration(migrations.Migration):

    dependencies = [("core", "0078_paymentschedule_payment_date")]

    operations = [migrations.RunPython(migrate_payment_schedules)]
