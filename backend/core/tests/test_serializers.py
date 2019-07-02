from django.test import TestCase

from core.models import ActivityDetails, Activity, FAMILY_DEPT, DISABILITY_DEPT
from core.tests.testing_mixins import (
    ActivityMixin,
    CaseMixin,
    PaymentScheduleMixin,
)
from core.serializers import ActivitySerializer, CaseSerializer


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

    def test_validate_no_end(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        # no end_date
        data = {
            "start_date": "2018-01-01",
            "details": activity_details.pk,
            "status": Activity.STATUS_EXPECTED,
            "activity_type": Activity.MAIN_ACTIVITY,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})


class CaseSerializerTestCase(TestCase, CaseMixin):
    def test_validate_error_no_district_for_family_dept(self):
        # Create initial valid case
        case = self.create_case()

        data = CaseSerializer(case).data
        data["target_group"] = FAMILY_DEPT
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "En sag med familie målgruppe skal have et distrikt",
        )

    def test_validate_success_no_district_for_handicap_dept(self):
        # Create initial valid case
        case = self.create_case()
        data = CaseSerializer(case).data
        data["target_group"] = DISABILITY_DEPT
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)

    def test_validate_error_family_dept_partial(self):
        # Create initial valid case
        case = self.create_case()
        data = CaseSerializer(case).data
        # no target_group for partial update
        data.pop("target_group")
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data, partial=True)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
