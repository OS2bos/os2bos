from collections import Counter

from django.db import migrations
from django.db.models import Count, F


def remove_duplicate_payments(apps, schema_editor):
    PaymentSchedule = apps.get_model("core", "PaymentSchedule")
    # Find payment schedules with more than one payment unique per date.
    affected_payment_schedules = (
        PaymentSchedule.objects.annotate(
            total_unique_payments_count=Count("payments__date", distinct=True)
        )
        .annotate(total_payments_count=Count("payments__date"))
        .exclude(total_unique_payments_count=F("total_payments_count"))
    )
    for payment_schedule in affected_payment_schedules:
        date_values = payment_schedule.payments.values_list("date", flat=True)
        # Count number of unique dates.
        date_counter = Counter(date_values)
        for date, count in date_counter.items():
            # Delete count-1 payments.
            if count > 1:
                to_be_deleted_pks = payment_schedule.payments.filter(
                    date=date
                )[: count - 1].values_list("pk", flat=True)
                payment_schedule.payments.filter(
                    pk__in=to_be_deleted_pks
                ).delete()


class Migration(migrations.Migration):

    dependencies = [("core", "0025_auto_20191127_1142")]

    operations = [migrations.RunPython(remove_duplicate_payments)]
