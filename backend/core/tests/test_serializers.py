from django.test import TestCase

from core.models import ActivityDetails, Activity
from core.models import FAMILY_DEPT, DISABILITY_DEPT, CASH, PaymentSchedule
from core.tests.testing_utils import (
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_payment_schedule,
)
from core.serializers import (
    ActivitySerializer,
    CaseSerializer,
    PaymentScheduleSerializer,
)


class ActivitySerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_validate_end_before_start(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # start_date > end_date
        data = {
            "start_date": "2019-01-01",
            "end_date": "2018-01-01",
            "details": activity_details.pk,
            "status": Activity.STATUS_EXPECTED,
            "activity_type": Activity.MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # start_date < end_date
        data = {
            "start_date": "2018-01-01",
            "end_date": "2019-01-01",
            "details": activity_details.pk,
            "status": Activity.STATUS_EXPECTED,
            "activity_type": Activity.MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})

    def test_validate_no_end(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # no end_date
        data = {
            "start_date": "2018-01-01",
            "details": activity_details.pk,
            "status": Activity.STATUS_EXPECTED,
            "activity_type": Activity.MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})


class CaseSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_validate_error_no_district_for_family_dept(self):
        # Create initial valid case
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )

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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        data = CaseSerializer(case).data
        data["target_group"] = DISABILITY_DEPT
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)

    def test_validate_error_family_dept_partial(self):
        # Create initial valid case
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        data = CaseSerializer(case).data
        # no target_group for partial update
        data.pop("target_group")
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data, partial=True)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)


class PaymentScheduleSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_validate_payment_and_recipient_allowed(self):
        payment_schedule = create_payment_schedule(
            payment_method=CASH, recipient_type=PaymentSchedule.PERSON
        )
        data = PaymentScheduleSerializer(payment_schedule).data
        serializer = PaymentScheduleSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_error_payment_and_recipient_not_allowed(self):
        payment_schedule = create_payment_schedule()
        data = PaymentScheduleSerializer(payment_schedule).data
        data["payment_method"] = CASH
        data["recipient_type"] = PaymentSchedule.INTERNAL
        serializer = PaymentScheduleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "ugyldig betalingsmetode for betalingsmodtager",
            serializer.errors["non_field_errors"][0],
        )
