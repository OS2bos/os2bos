from django.test import TestCase

from core.tests.testing_mixins import ActivityMixin, PaymentScheduleMixin
from core.serializers import ActivitySerializer


class ActivitySerializerTestCase(
    TestCase, ActivityMixin, PaymentScheduleMixin
):
    def test_get_total_amount(self):
        activity = self.create_activity()
        payment_schedule = self.create_payment_schedule()
        activity.payment_plan = payment_schedule
        activity.save()
        payment_schedule.generate_payments(
            activity.start_date, activity.end_date
        )
        data = ActivitySerializer(activity).data
        self.assertEqual(data["total_amount"], activity.total_amount())
