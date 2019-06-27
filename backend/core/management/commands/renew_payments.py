from django.core.management.base import BaseCommand

from core.models import PaymentSchedule


class Command(BaseCommand):
    help = "Renews Payments for an Activity"

    def handle(self, *args, **options):
        # Find recurring payment schedules which has an associated Activity.
        recurring_schedules = PaymentSchedule.objects.filter(
            activity__is_null=False
        ).exclude(payment_type=PaymentSchedule.ONE_TIME_PAYMENT)

        for schedule in recurring_schedules:
            schedule.synchronize_payments()
