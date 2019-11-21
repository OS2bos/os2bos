# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from decimal import Decimal
from datetime import timedelta, date

from django.test import TestCase
from django.utils import timezone

from core.models import (
    ActivityDetails,
    FAMILY_DEPT,
    DISABILITY_DEPT,
    CASH,
    INTERNAL,
    MAIN_ACTIVITY,
    STATUS_EXPECTED,
    STATUS_GRANTED,
    STATUS_DELETED,
    PaymentSchedule,
)
from core.tests.testing_utils import (
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_payment_schedule,
    create_activity,
    create_payment,
)
from core.serializers import (
    ActivitySerializer,
    CaseSerializer,
    PaymentScheduleSerializer,
    AppropriationSerializer,
    PaymentSerializer,
)


class AppropriationSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_get_activities_excludes_deleted(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            payment_plan=payment_schedule,
        )
        activity.status = STATUS_DELETED
        activity.save()
        serializer = AppropriationSerializer(instance=appropriation)
        data = serializer.data

        # assert deleted activity is not included.
        self.assertEqual(len(data["activities"]), 0)


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
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "startdato skal være før eller identisk med slutdato",
        )

    def test_validate_start_before_end(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        # start_date < end_date
        data = {
            "start_date": "2018-01-01",
            "end_date": "2019-01-01",
            "details": activity_details.pk,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
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
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )

        # no end_date
        data = {
            "start_date": "2018-01-01",
            "details": activity_details.pk,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})

    def test_validate_monthly_starts_on_first(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.MONTHLY,
        )

        # no end_date
        data = {
            "start_date": "2018-01-01",
            "details": activity_details.pk,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }
        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

    def test_validate_expected_success(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now + timedelta(days=12)
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            details=details,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        modified_start_date = start_date + timedelta(days=7)
        modified_end_date = end_date + timedelta(days=12)
        # let the granted activity be modified by another expected activity.
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": modified_start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": modified_end_date,
            "modifies": activity.id,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(
                modifies_payment_schedule
            ).data,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})

    def test_validate_expected_invalid_date(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now + timedelta(days=12)
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            details=details,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        modified_start_date = start_date
        modified_end_date = end_date + timedelta(days=12)
        # let the granted activity be modified by another expected activity.
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": modified_start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": modified_end_date,
            "modifies": activity.id,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(
                modifies_payment_schedule
            ).data,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()

    def test_validate_expected_no_modifies_end_date(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        now = timezone.now().date()
        start_date = now + timedelta(1)
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # create an already granted activity with no end_date.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=None,
            details=details,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        modified_start_date = start_date + timedelta(days=1)
        # let the granted activity be modified by another expected activity.
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": modified_start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": None,
            "modifies": activity.id,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(
                modifies_payment_schedule
            ).data,
        }
        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)

    def test_validate_expected_no_next_payment(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        start_date = date.today() - timedelta(days=3)
        end_date = date.today() + timedelta(days=2)
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            details=details,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        start_date = date.today() - timedelta(days=3)
        end_date = date.today() + timedelta(days=2)
        # let the granted activity be modified by another expected activity.
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": end_date,
            "modifies": activity.id,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(
                modifies_payment_schedule
            ).data,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()

    def test_validate_expected_true_ongoing_with_next_payment(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        start_date = date.today() + timedelta(days=2)
        end_date = date.today() + timedelta(days=4)
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            details=details,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        start_date = date.today() + timedelta(days=3)
        end_date = date.today() + timedelta(days=6)
        # let the granted activity be modified by another expected activity.
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": end_date,
            "modifies": activity.id,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(
                modifies_payment_schedule
            ).data,
        }
        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

    def test_validate_one_time_payment_with_payment_frequency(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency="",
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        start_date = date.today()
        end_date = date.today()
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": end_date,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }
        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

    def test_validate_one_time_payment_different_dates(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency="",
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        start_date = date.today()
        end_date = date.today() + timedelta(days=1)
        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": end_date,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }
        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)


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


class PaymentSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_validate_paid_success(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule(
            payment_method=INTERNAL, recipient_type=PaymentSchedule.INTERNAL
        )
        create_activity(
            case=case,
            appropriation=appropriation,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )
        payment = create_payment(
            payment_schedule,
            recipient_type=PaymentSchedule.INTERNAL,
            payment_method=INTERNAL,
        )
        today = date.today()
        data = PaymentSerializer(payment).data
        data["paid"] = True
        data["paid_amount"] = Decimal("100.0")
        data["paid_date"] = today

        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_error_paid_not_allowed(self):
        payment_schedule = create_payment_schedule(
            payment_method=CASH, recipient_type=PaymentSchedule.PERSON
        )
        payment = create_payment(
            payment_schedule,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
        )
        today = date.today()
        data = PaymentSerializer(payment).data
        data["paid"] = True
        data["paid_amount"] = Decimal("100.0")
        data["paid_date"] = today

        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "Denne betaling må ikke markeres betalt manuelt",
            serializer.errors["non_field_errors"][0],
        )

    def test_validate_error_paid_not_allowed_fictive(self):
        payment_schedule = create_payment_schedule(
            payment_method=INTERNAL,
            recipient_type=PaymentSchedule.INTERNAL,
            fictive=True,
        )
        payment = create_payment(
            payment_schedule,
            recipient_type=PaymentSchedule.INTERNAL,
            payment_method=INTERNAL,
        )
        today = date.today()
        data = PaymentSerializer(payment).data
        data["paid"] = True
        data["paid_amount"] = Decimal("100.0")
        data["paid_date"] = today

        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "Denne betaling må ikke markeres betalt manuelt",
            serializer.errors["non_field_errors"][0],
        )

    def test_validate_error_paid_not_allowed_activity_status_not_granted(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule(
            payment_method=INTERNAL, recipient_type=PaymentSchedule.INTERNAL
        )
        create_activity(
            case=case,
            appropriation=appropriation,
            payment_plan=payment_schedule,
            status=STATUS_EXPECTED,
        )
        payment = create_payment(
            payment_schedule,
            recipient_type=PaymentSchedule.INTERNAL,
            payment_method=INTERNAL,
        )
        today = date.today()
        data = PaymentSerializer(payment).data
        data["paid"] = True
        data["paid_amount"] = Decimal("100.0")
        data["paid_date"] = today

        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            "Denne betaling må ikke markeres betalt manuelt",
            serializer.errors["non_field_errors"][0],
        )
