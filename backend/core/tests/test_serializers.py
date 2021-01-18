# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from decimal import Decimal
from datetime import timedelta, date

from freezegun import freeze_time

from django.test import TestCase
from django.utils import timezone

from rest_framework import serializers

from core.models import (
    ActivityDetails,
    CASH,
    INVOICE,
    INTERNAL,
    MAIN_ACTIVITY,
    STATUS_EXPECTED,
    STATUS_DRAFT,
    STATUS_GRANTED,
    STATUS_DELETED,
    PaymentSchedule,
    Rate,
)
from core.tests.testing_utils import (
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_payment_schedule,
    create_activity,
    create_payment,
    create_target_group,
)
from core.serializers import (
    ActivitySerializer,
    CaseSerializer,
    PaymentScheduleSerializer,
    AppropriationSerializer,
    PaymentSerializer,
    TargetGroupSerializer,
)


class AppropriationSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_get_activities_excludes_deleted(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(case=case, appropriation=appropriation)
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=activity,
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
            "Startdato skal være før eller identisk med slutdato",
        )

    def test_has_per_unit_price(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_amount": 0,
                "payment_cost_type": "PER_UNIT",
                "payment_frequency": "BIWEEKLY",
                "payment_method": "INVOICE",
                "payment_type": "RUNNING_PAYMENT",
                "payment_units": "6",
                "price_per_unit": {
                    "amount": "180",
                    "start_date": "2020-06-19",
                },
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": "DRAFT",
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()
        # Test creation of Price instance.
        instance = serializer.save()
        self.assertIsNotNone(instance.payment_plan.price_per_unit)

    def test_validate_start_before_end(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=activity,
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

    def test_validate_no_start_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=activity,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        # let the granted activity be modified by another expected activity.
        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "modifies": activity.id,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(
                modifies_payment_schedule
            ).data,
        }
        serializer = ActivitySerializer(data=data)
        serializer.is_valid()

    def test_validate_expected_invalid_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=activity,
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=activity,
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=activity,
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=activity,
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
            payment_date=date.today(),
        )
        case = create_case(self.case_worker, self.municipality, self.district)
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

        self.assertTrue(serializer.is_valid())

    def test_validate_one_time_payment_different_dates(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_date=date.today(),
            payment_frequency="",
        )
        case = create_case(self.case_worker, self.municipality, self.district)
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

        self.assertTrue(serializer.is_valid())

    def test_validate_one_time_payment_no_payment_date(self):
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency="",
        )
        payment_schedule_data = PaymentScheduleSerializer(
            payment_schedule
        ).data

        case = create_case(self.case_worker, self.municipality, self.district)
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
            "payment_plan": payment_schedule_data,
        }
        serializer = ActivitySerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_validate_monthly_payment_with_invalid_parameters(self):
        # Create an "invalid" monthly activity with start and end date 1st
        # but a payment_day_of_month of 31st.
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_day_of_month=31,
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        start_date = date(2020, 1, 1)
        end_date = date(2020, 1, 1)
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

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Betalingsparametre resulterer ikke i nogen betalinger",
        )

    def test_validate_monthly_payment_with_valid_parameters(self):
        # Create a "valid" monthly activity with payment_day_of_month
        # in start - end range

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_day_of_month=31,
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        start_date = date(2020, 1, 1)
        end_date = date(2020, 2, 1)
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

    @freeze_time("2020-01-01")
    def test_validate_monthly_payment_with_for_expected_adjustment(self):
        # Create an "invalid" expected adjustment monthly activity with start
        # and end date on the 23rd and a payment_day_of_month on the 1st.
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )

        modified_activity = create_activity(
            case=case,
            appropriation=appropriation,
            status=STATUS_GRANTED,
            start_date=date(2020, 1, 1),
            end_date=date(2020, 3, 1),
            details=details,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_day_of_month=1,
            activity=modified_activity,
        )

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_day_of_month=1,
        )
        start_date = date(2020, 2, 23)
        end_date = date(2020, 2, 23)

        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "status": STATUS_EXPECTED,
            "activity_type": MAIN_ACTIVITY,
            "end_date": end_date,
            "details": details.id,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
            "modifies": modified_activity.id,
        }
        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

    @freeze_time("2020-01-09")
    def test_validate_cash_payment_with_exclusions_disallowed(self):
        # Create an activity with a start_date within two days
        # of a future payment exclusion date.
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # The 11th is a Saturday.
        start_date = date(2020, 1, 11)
        end_date = date(2020, 1, 13)

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
        )

        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "end_date": end_date,
            "details": details.id,
            "status": STATUS_GRANTED,
            "activity_type": MAIN_ACTIVITY,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }

        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Startdato skal være i fremtiden og "
            "der skal være mindst to udbetalingsdage"
            " fra nu og til startdatoen",
        )

    @freeze_time("2020-01-09")
    def test_validate_cash_payment_in_the_past_disallowed(self):
        # Create an activity with a start_date in the past
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # The 11th is a Saturday.
        start_date = date(2020, 1, 8)
        end_date = date(2020, 1, 13)

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
        )

        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "end_date": end_date,
            "details": details.id,
            "status": STATUS_GRANTED,
            "activity_type": MAIN_ACTIVITY,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }

        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Startdato skal være i fremtiden og "
            "der skal være mindst to udbetalingsdage"
            " fra nu og til startdatoen",
        )

    @freeze_time("2020-01-08")
    def test_validate_cash_payment_with_exclusions_allowed(self):
        # Create an activity with a start_date not within two days
        # of a future payment exclusion date.
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )
        # The 10th is a Friday.
        start_date = date(2020, 1, 10)
        end_date = date(2020, 1, 13)

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
        )

        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "end_date": end_date,
            "details": details.id,
            "status": STATUS_GRANTED,
            "activity_type": MAIN_ACTIVITY,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }

        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

    @freeze_time("2020-01-08")
    def test_validate_cash_payment_tomorrow_disallowed(self):
        # Create an activity with a start_date of tomorrow
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )

        start_date = date(2020, 1, 9)
        end_date = date(2020, 1, 13)

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
        )

        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "end_date": end_date,
            "details": details.id,
            "status": STATUS_GRANTED,
            "activity_type": MAIN_ACTIVITY,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }

        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Startdato skal være i fremtiden og "
            "der skal være mindst to udbetalingsdage"
            " fra nu og til startdatoen",
        )

    @freeze_time("2020-01-08")
    def test_validate_cash_payment_one_time_tomorrow_disallowed(self):
        # Create an activity with a start_date of tomorrow
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )

        start_date = date(2020, 1, 1)
        end_date = date(2020, 2, 1)

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency=None,
            payment_method=CASH,
            payment_date=date(2020, 1, 9),
            recipient_type=PaymentSchedule.PERSON,
        )

        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "end_date": end_date,
            "details": details.id,
            "status": STATUS_GRANTED,
            "activity_type": MAIN_ACTIVITY,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }

        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Startdato skal være i fremtiden og "
            "der skal være mindst to udbetalingsdage"
            " fra nu og til startdatoen",
        )

    @freeze_time("2020-10-15")
    def test_validate_cash_payment_with_two_non_exclusion_days_allowed(self):
        # Today is a Thursday, an activity with a start_date
        # of Monday is allowed.
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        details, unused = ActivityDetails.objects.get_or_create(
            activity_id="000000",
            name="Test aktivitet",
            max_tolerance_in_percent=10,
            max_tolerance_in_dkk=1000,
        )

        start_date = date(2020, 10, 19)
        end_date = date(2020, 10, 22)

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
        )

        data = {
            "case": case.id,
            "appropriation": appropriation.id,
            "start_date": start_date,
            "end_date": end_date,
            "details": details.id,
            "status": STATUS_GRANTED,
            "activity_type": MAIN_ACTIVITY,
            "payment_plan": PaymentScheduleSerializer(payment_schedule).data,
        }

        serializer = ActivitySerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

    def test_individual_payment_disallow_payment_frequency(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_frequency": "BIWEEKLY",
                "payment_method": "INVOICE",
                "payment_type": "INDIVIDUAL_PAYMENT",
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": "DRAFT",
        }
        serializer = ActivitySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["payment_plan"]["non_field_errors"][0],
            "En engangsbetaling eller individuel betaling må"
            " ikke have en betalingsfrekvens",
        )

    def test_individual_payment_disallow_payment_amount(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_amount": 500,
                "payment_method": "INVOICE",
                "payment_type": "INDIVIDUAL_PAYMENT",
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": "DRAFT",
        }
        serializer = ActivitySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["payment_plan"]["non_field_errors"][0],
            "En individuel betaling må ikke have et beløb",
        )

    def test_individual_payment_disallow_payment_cost_type(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_cost_type": "FIXED",
                "payment_method": "INVOICE",
                "payment_type": "INDIVIDUAL_PAYMENT",
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": "DRAFT",
        }
        serializer = ActivitySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["payment_plan"]["non_field_errors"][0],
            "En individuel betaling må ikke have en betalingspristype",
        )

    def test_individual_payment_disallow_payment_day_of_month(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_day_of_month": 1,
                "payment_method": "INVOICE",
                "payment_type": "INDIVIDUAL_PAYMENT",
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": "DRAFT",
        }
        serializer = ActivitySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["payment_plan"]["non_field_errors"][0],
            "En individuel betaling må ikke have en månedlig betalingsdato",
        )

    def test_individual_payment_disallow_payment_units(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_units": 10,
                "payment_method": "INVOICE",
                "payment_type": "INDIVIDUAL_PAYMENT",
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": "DRAFT",
        }
        serializer = ActivitySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["payment_plan"]["non_field_errors"][0],
            "en individuel betaling må ikke have betalingsenheder",
        )

    def test_individual_payment_allow_modifies(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case, appropriation=appropriation, status=STATUS_GRANTED
        )
        create_payment_schedule(activity=activity)

        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_method": "INVOICE",
                "payment_type": "INDIVIDUAL_PAYMENT",
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": STATUS_EXPECTED,
            "modifies": activity.id,
        }
        serializer = ActivitySerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_individual_payment_success(self):
        activity_details = ActivityDetails.objects.create(
            max_tolerance_in_percent=10, max_tolerance_in_dkk=1000
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        data = {
            "activity_type": MAIN_ACTIVITY,
            "appropriation": appropriation.pk,
            "details": activity_details.pk,
            "payment_plan": {
                "payment_method": "INVOICE",
                "payment_type": "INDIVIDUAL_PAYMENT",
                "recipient_id": "75736215",
                "recipient_name": "AKTIV WEEKEND",
                "recipient_type": "COMPANY",
            },
            "start_date": date.today(),
            "status": "DRAFT",
        }
        serializer = ActivitySerializer(data=data)

        self.assertTrue(serializer.is_valid())


class CaseSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_validate_error_no_district_for_family_dept(self):
        # Create initial valid case
        case = create_case(self.case_worker, self.municipality, self.district)
        target_group = create_target_group(
            name="Familieafdelingen", required_fields_for_case="district"
        )
        data = CaseSerializer(case).data
        data["target_group"] = target_group.id
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "En sag med den givne målgruppe skal have feltet Skoledistrikt",
        )

    def test_validate_success_no_district_for_handicap_dept(self):
        # Create initial valid case
        case = create_case(self.case_worker, self.municipality, self.district)
        target_group = create_target_group(
            name="Handicapafdelingen", required_fields_for_case=""
        )
        data = CaseSerializer(case).data
        data["target_group"] = target_group.id
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)

    def test_validate_error_family_dept_partial(self):
        # Create initial valid case
        case = create_case(self.case_worker, self.municipality, self.district)
        data = CaseSerializer(case).data
        # no target_group for partial update
        data.pop("target_group")
        data["district"] = None
        data["sbsys_id"] = "12356789"
        serializer = CaseSerializer(data=data, partial=True)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)

    def test_validate_success_effort_step_partial(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        target_group = case.target_group
        target_group.required_fields_for_case = "effort_step"
        target_group.save()

        data = CaseSerializer(case).data
        data.pop("effort_step")

        serializer = CaseSerializer(case, data=data, partial=True)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)

    def test_validate_error_effort_step_partial(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        case.effort_step = None
        case.save()

        target_group = case.target_group
        target_group.required_fields_for_case = "effort_step"
        target_group.save()

        data = CaseSerializer(case).data
        data.pop("effort_step")

        serializer = CaseSerializer(case, data=data, partial=True)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)


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
            "payment_cost_type": PaymentSchedule.FIXED_PRICE,
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "En engangsbetaling eller individuel betaling"
            " må ikke have en betalingsfrekvens",
        )

    def test_validate_error_non_one_time_payment_without_frequency(self):
        # Create an invalid running payment, no frequency combination.
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
            "En betalingstype der ikke er en engangsbetaling"
            " eller individuel betaling skal have en betalingsfrekvens",
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
            "payment_cost_type": PaymentSchedule.FIXED_PRICE,
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
        valid = serializer.is_valid()
        self.assertTrue(valid)

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

    def test_payment_cost_type_per_unit_price(self):
        """Create a valid running payment, monthly combination."""
        data = {
            "payment_type": PaymentSchedule.RUNNING_PAYMENT,
            "payment_frequency": PaymentSchedule.MONTHLY,
            "payment_units": 1,
            "payment_cost_type": PaymentSchedule.PER_UNIT_PRICE,
            "recipient_type": PaymentSchedule.PERSON,
            "recipient_id": "123456789",
            "recipient_name": "Jens Test",
            "payment_method": CASH,
            "price_per_unit": {
                "amount": 100,
                "start_date": "2020-06-09",
                "end_date": "2030-06-01",
            },
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertTrue(is_valid)
        # Test creation of Price instance.
        instance = serializer.save()
        self.assertTrue(instance.price_per_unit is not None)
        # Test update of Price instance.
        data["price_per_unit"]["amount"] = 150
        data["price_per_unit"]["start_date"] = date.today()
        data["price_per_unit"]["end_date"] = date.today() + timedelta(days=7)

        new_serializer = PaymentScheduleSerializer(data=data)
        is_valid = new_serializer.is_valid()
        self.assertTrue(is_valid)
        new_serializer.save()

        self.assertEqual(instance.price_per_unit.rate_amount, 150)

        new_data = {
            "payment_type": PaymentSchedule.RUNNING_PAYMENT,
            "payment_frequency": PaymentSchedule.MONTHLY,
            "payment_units": 3,
            "payment_cost_type": PaymentSchedule.PER_UNIT_PRICE,
            "recipient_type": PaymentSchedule.PERSON,
            "recipient_id": "123456789",
            "recipient_name": "Jens Test",
            "payment_method": CASH,
        }

        no_price_serializer = PaymentScheduleSerializer(
            data=new_data, instance=new_serializer.instance
        )
        self.assertTrue(no_price_serializer.is_valid())
        updated_instance = no_price_serializer.save()
        self.assertEqual(updated_instance.price_per_unit.rate_amount, 150)
        self.assertEqual(updated_instance.payment_units, 3)
        # Update an existing instance with no payment units, provoking
        # an error.
        del new_data["payment_units"]
        no_units_serializer = PaymentScheduleSerializer(
            data=new_data, instance=no_price_serializer.instance
        )
        # Having no units is OK because the instance already has them.
        self.assertTrue(no_units_serializer.is_valid())

    def test_rate_validation_errors(self):
        data = {
            "payment_type": PaymentSchedule.RUNNING_PAYMENT,
            "payment_frequency": PaymentSchedule.MONTHLY,
            "payment_units": 1,
            "payment_cost_type": PaymentSchedule.FIXED_PRICE,
            "recipient_type": PaymentSchedule.PERSON,
            "recipient_id": "123456789",
            "recipient_name": "Jens Test",
            "payment_method": CASH,
            "price_per_unit": {
                "amount": 100,
                "start_date": "2020-06-09",
                "end_date": "2030-06-01",
            },
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        # Amount needs to be there for fixed price.
        self.assertFalse(is_valid)
        self.assertEqual(
            "Beløb skal udfyldes ved fast beløb",
            serializer.errors["non_field_errors"][0],
        )
        # No rate for fixed price.
        rate = Rate.objects.create(name="test rate")
        data["payment_amount"] = 100
        data["payment_rate"] = rate

        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Takst skal ikke angives ved fast beløb",
            serializer.errors["non_field_errors"][0],
        )
        del data["payment_rate"]

        # No price per unit for fixed price.
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Beløb pr. enhed skal ikke angives ved fast takst",
            serializer.errors["non_field_errors"][0],
        )
        del data["price_per_unit"]
        # No units when price is fixed.
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Enheder skal ikke angives ved fast beløb",
            serializer.errors["non_field_errors"][0],
        )

        data["payment_cost_type"] = PaymentSchedule.PER_UNIT_PRICE
        del data["payment_units"]
        # Units are necessary for per unit price.
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Enheder skal angives ved pris pr. enhed",
            serializer.errors["non_field_errors"][0],
        )

        # Price object is necessary.
        data["payment_units"] = 1
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Beløb pr. enhed skal angives",
            serializer.errors["non_field_errors"][0],
        )
        # Don't have a rate.
        data["payment_rate"] = rate
        data["price_per_unit"] = {
            "amount": 100,
            "start_date": "2020-06-09",
            "end_date": "2030-06-01",
        }

        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Takst skal ikke angives ved pris pr. enhed",
            serializer.errors["non_field_errors"][0],
        )
        del data["payment_rate"]

        # Don't specify payment amount.
        data["payment_amount"] = 100
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Beløbsfeltet skal ikke udfyldes ved pris pr. enhed",
            serializer.errors["non_field_errors"][0],
        )

        data["payment_cost_type"] = PaymentSchedule.GLOBAL_RATE_PRICE
        # Do specify units.
        del data["payment_units"]
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Enheder skal angives ved fast takst",
            serializer.errors["non_field_errors"][0],
        )

        data["payment_units"] = 1
        # Do specify rate.
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Takst skal angives", serializer.errors["non_field_errors"][0]
        )

        data["payment_rate"] = rate
        data["payment_amount"] = 100
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Beløbsfeltet skal ikke udfyldes ved fast takst",
            serializer.errors["non_field_errors"][0],
        )

        del data["payment_amount"]
        data["price_per_unit"] = {
            "amount": 100,
            "start_date": "2020-06-09",
            "end_date": "2030-06-01",
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(
            "Beløb pr. enhed skal ikke angives ved fast takst",
            serializer.errors["non_field_errors"][0],
        )
        # Always hit all branches
        del data["price_per_unit"]
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)

        data["payment_cost_type"] = "wrong"
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)

    def test_validate_error_company_recipient_id_not_cvr(self):
        # Create an invalid cvr as recipient_id for recipient_type COMPANY.
        data = {
            "payment_type": PaymentSchedule.RUNNING_PAYMENT,
            "payment_amount": Decimal("500.0"),
            "payment_units": 0,
            "recipient_type": PaymentSchedule.COMPANY,
            "recipient_id": "123456789",
            "recipient_name": "Jens Test",
            "payment_method": INVOICE,
        }
        serializer = PaymentScheduleSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            serializer.errors["non_field_errors"][0],
            "Ugyldigt CVR nummer for firma",
        )


class PaymentSerializerTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_validate_paid_success(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case, appropriation=appropriation, status=STATUS_GRANTED
        )
        payment_schedule = create_payment_schedule(
            payment_method=INTERNAL,
            recipient_type=PaymentSchedule.INTERNAL,
            activity=activity,
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

    def test_validate_two_payments_same_date_not_allowed(self):
        payment_schedule = create_payment_schedule(
            payment_method=CASH, recipient_type=PaymentSchedule.PERSON
        )
        payment = create_payment(
            payment_schedule,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
        )
        data = PaymentSerializer(payment).data
        del data["id"]
        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        try:
            serializer.save()
        except serializers.ValidationError as e:
            self.assertEqual(
                "En ydelse kan kun have én betaling på en given dato",
                str(e.get_full_details()[0]["message"]),
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
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case, appropriation=appropriation, status=STATUS_EXPECTED
        )
        payment_schedule = create_payment_schedule(
            payment_method=INTERNAL,
            recipient_type=PaymentSchedule.INTERNAL,
            activity=activity,
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

    def test_create_individual_payment(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        start_date = date.today() - timedelta(days=1)
        end_date = date.today() + timedelta(days=1)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            status=STATUS_DRAFT,
            start_date=start_date,
            end_date=end_date,
        )
        payment_schedule = create_payment_schedule(
            activity=activity,
            payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT,
            payment_frequency=None,
            payment_amount=None,
            payment_cost_type=None,
        )
        today = timezone.now().date()

        data = {
            "date": today,
            "recipient_type": PaymentSchedule.INTERNAL,
            "recipient_id": "test",
            "recipient_name": "test",
            "payment_method": INTERNAL,
            "amount": Decimal("500"),
            "payment_schedule": payment_schedule.id,
            "paid": False,
        }
        serializer = PaymentSerializer(data=data)

        self.assertTrue(serializer.is_valid())

        date_outside_activity = date.today() + timedelta(days=10)
        data["date"] = date_outside_activity

        failing_serializer = PaymentSerializer(data=data)
        self.assertFalse(failing_serializer.is_valid())

        del data["date"]
        nodate_serializer = PaymentSerializer(data=data)
        self.assertFalse(nodate_serializer.is_valid())

    def test_create_individual_payment_modifies(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=10)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
        )
        payment_schedule = create_payment_schedule(
            activity=activity,
            payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT,
            payment_frequency=None,
            payment_amount=None,
            payment_cost_type=None,
        )

        data = {
            "date": start_date + timedelta(days=5),
            "recipient_type": PaymentSchedule.INTERNAL,
            "recipient_id": "test",
            "recipient_name": "test",
            "payment_method": INTERNAL,
            "amount": Decimal("500"),
            "payment_schedule": payment_schedule.id,
            "paid": False,
        }
        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        data["date"] = start_date + timedelta(days=1)
        older_serializer = PaymentSerializer(data=data)
        self.assertTrue(older_serializer.is_valid())
        older_serializer.save()

        expectation = create_activity(
            case=case,
            appropriation=appropriation,
            status=STATUS_EXPECTED,
            start_date=start_date + timedelta(days=5),
            end_date=end_date,
            modifies=activity,
        )
        payment_schedule = create_payment_schedule(
            activity=expectation,
            payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT,
            payment_frequency=None,
            payment_amount=None,
            payment_cost_type=None,
        )

    def test_edit_granted_payment_not_allowed(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=10)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
        )
        payment_schedule = create_payment_schedule(
            activity=activity,
            payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT,
            payment_frequency=None,
            payment_amount=None,
            payment_cost_type=None,
        )

        data = {
            "date": start_date + timedelta(days=5),
            "recipient_type": PaymentSchedule.INTERNAL,
            "recipient_id": "test",
            "recipient_name": "test",
            "payment_method": INTERNAL,
            "amount": Decimal("500"),
            "payment_schedule": payment_schedule.id,
            "paid": False,
        }
        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        data["amount"] = Decimal(600)
        serializer = PaymentSerializer(payment, data=data)
        # You're not allowed to do change the amount of a granted
        # payment.
        self.assertFalse(serializer.is_valid())


class TargetGroupSerializerTestCase(TestCase):
    def test_to_representation(self):
        tg = create_target_group()
        serializer = TargetGroupSerializer(tg)
        serializer.to_representation(tg)
