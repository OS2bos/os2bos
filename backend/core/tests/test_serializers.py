from decimal import Decimal

from django.test import TestCase

from core.models import (
    ActivityDetails,
    Activity,
    FAMILY_DEPT,
    DISABILITY_DEPT,
    CASH,
    PaymentSchedule,
)
from core.tests.testing_utils import (
    BasicTestMixin,
    create_case,
    create_appropriation,
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

    def test_validate_success_disability_dept_no_scaling_or_effort_step(self):
        # create valid case for DISABILITY_DEPT
        case = create_case(
            self.case_worker,
            self.team,
            self.municipality,
            self.district,
            target_group=DISABILITY_DEPT,
        )

        data = CaseSerializer(case).data
        # new sbys_id, remove effort and scaling step.
        data["sbsys_id"] = "12356789"
        data.pop("effort_step")
        data.pop("scaling_step")
        serializer = CaseSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)

    def test_validate_error_family_dept_no_scaling_or_effort_step(self):
        # create initial valid case for FAMILY_DEPT
        case = create_case(
            self.case_worker,
            self.team,
            self.municipality,
            self.district,
            target_group=FAMILY_DEPT,
        )

        data = CaseSerializer(case).data
        # new sbys_id, remove effort and scaling step.
        data["sbsys_id"] = "12356789"
        data.pop("effort_step")
        data.pop("scaling_step")
        serializer = CaseSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "en sag med familie målgruppe skal have en"
            " indsats- og skaleringstrappe",
        )


class PaymentScheduleSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_validate_error_one_time_payment_with_frequency(self):
        # Create an invalid one time payment, daily combination.
        data = {
            "payment_frequency": PaymentSchedule.DAILY,
            "payment_type": PaymentSchedule.ONE_TIME_PAYMENT,
            "payment_amount": Decimal("500.0"),
            "payment_units": 0,
            "recipient_type": PaymentSchedule.PERSON,
            "recipient_id": "123456789",
            "recipient_name": "Jens Test",
            "payment_method": CASH,
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "En engangsbetaling må ikke have en betalingsfrekvens",
        )

    def test_validate_error_non_one_time_payment_without_frequency(self):
        # Create an invalid running payment, no frequency combiation.
        data = {
            "payment_type": PaymentSchedule.RUNNING_PAYMENT,
            "payment_amount": Decimal("500.0"),
            "payment_units": 0,
            "recipient_type": PaymentSchedule.PERSON,
            "recipient_id": "123456789",
            "recipient_name": "Jens Test",
            "payment_method": CASH,
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "En betalingtype der ikke er en engangsbetaling"
            " skal have en betalingsfrekvens",
        )

    def test_validate_one_time_payment_without_frequency(self):
        # Create a valid running payment, monthly combination.
        data = {
            "payment_type": PaymentSchedule.RUNNING_PAYMENT,
            "payment_frequency": PaymentSchedule.MONTHLY,
            "payment_amount": Decimal("500.0"),
            "payment_units": 0,
            "recipient_type": PaymentSchedule.PERSON,
            "recipient_id": "123456789",
            "recipient_name": "Jens Test",
            "payment_method": CASH,
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
