from django.test import TestCase

from core.models import ActivityDetails, Activity
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

    def test_validate_end_before_start(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        # start_date > end_date
        data = {
            "start_date": "2019-01-01",
            "end_date": "2018-01-01",
            "details": activity_details.pk,
            "status": Activity.STATUS_EXPECTED,
            "activity_type": Activity.MAIN_ACTIVITY,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "startdato skal være før slutdato",
        )

    def test_validate_start_before_end(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        # start_date < end_date
        data = {
            "start_date": "2018-01-01",
            "end_date": "2019-01-01",
            "details": activity_details.pk,
            "status": Activity.STATUS_EXPECTED,
            "activity_type": Activity.MAIN_ACTIVITY,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})
