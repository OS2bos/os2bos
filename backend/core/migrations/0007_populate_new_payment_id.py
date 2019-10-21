from django.db import migrations
from django.db.models import F


def populate_payment_id(apps, schema_editor):
    PaymentSchedule = apps.get_model("core", "PaymentSchedule")
    # Initially update all models payment_id with their id.
    PaymentSchedule.objects.update(payment_id=F("id"))
    # Then start from the top level expected ones and update the lower
    # with the first payment_id.
    modified_by_payment_schedules = PaymentSchedule.objects.filter(
        activity__modified_by__isnull=False, activity__modifies__isnull=True
    )
    for payment_schedule in modified_by_payment_schedules:
        modified_by = payment_schedule.activity.modified_by
        while modified_by.exists():
            modified_by_activity = modified_by.first()
            modified_by_payment_schedule = modified_by_activity.payment_plan
            modified_by_payment_schedule.payment_id = payment_schedule.id
            modified_by_payment_schedule.save()
            modified_by = modified_by_activity.modified_by


class Migration(migrations.Migration):

    dependencies = [("core", "0006_add_new_payment_id")]

    operations = [migrations.RunPython(populate_payment_id)]
