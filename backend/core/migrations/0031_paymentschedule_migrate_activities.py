from django.db import migrations


def payment_schedule_migrate_activities(apps, schema_editor):
    PaymentSchedule = apps.get_model("core", "PaymentSchedule")

    payment_schedules = PaymentSchedule.objects.all()

    for payment_schedule in payment_schedules:
        payment_schedule.new_activity = payment_schedule.activity
        payment_schedule.save()


class Migration(migrations.Migration):

    dependencies = [("core", "0030_paymentschedule_new_activity")]

    operations = [migrations.RunPython(payment_schedule_migrate_activities)]
