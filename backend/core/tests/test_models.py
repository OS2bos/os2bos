# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from decimal import Decimal
from datetime import date, timedelta
from unittest import mock

from django import forms
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from parameterized import parameterized

from core.tests.testing_utils import (
    BasicTestMixin,
    create_payment_schedule,
    create_activity,
    create_appropriation,
    create_case,
    create_section,
    create_payment,
    create_account,
    create_service_provider,
)
from core.models import (
    Municipality,
    SchoolDistrict,
    ActivityDetails,
    Account,
    ApprovalLevel,
    Team,
    PaymentSchedule,
    ServiceProvider,
    CASH,
    SD,
    INVOICE,
    INTERNAL,
    Appropriation,
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    STATUS_GRANTED,
    STATUS_EXPECTED,
    STATUS_DRAFT,
)


class AppropriationTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_appropriation_str(self):
        section = create_section()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(section=section, case=case)

        self.assertEqual(str(appropriation), "13212 - ABL-105-2 - 27.45.04")

    def test_total_granted_this_year(self):
        # generate a start and end span of 10 days
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )

        # create main activity with GRANTED.
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
        )

        self.assertEqual(
            activity.appropriation.total_granted_this_year, Decimal("10000")
        )

    def test_total_expected_this_year(self):
        # generate a start and end span of 3 days
        now = timezone.now()
        start_date = now
        end_date = now + timedelta(days=2)
        # create main activity with GRANTED.
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create a GRANTED supplementary activity.
        supplementary_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
        )

        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
        )
        # create an EXPECTED supplementary activity overruling the GRANTED.
        create_activity(
            case,
            appropriation,
            start_date=start_date + timedelta(days=1),
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
            modifies=supplementary_activity,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create a DRAFT supplementary activity which should not be counted.
        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_DRAFT,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create a GRANTED supplementary activity which has
        # modified another that is also GRANTED.
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        supplementary_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=start_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
        )
        create_activity(
            case,
            appropriation,
            start_date=start_date + timedelta(days=1),
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
            modifies=supplementary_activity,
        )

        self.assertEqual(
            appropriation.total_expected_this_year, Decimal("5300")
        )

    def test_total_expected_within_start_end_range(self):
        # generate a start and end span of 10 days
        now = timezone.now()
        start_date = now + timedelta(days=1)
        end_date = now + timedelta(days=10)

        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # create a granted activity
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
        )
        modified_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            payment_plan=payment_schedule,
        )
        # create an expected activity with a (start, end)
        # within the span of the activity it modifies
        modified_start_date = now + timedelta(days=3)
        modified_end_date = now + timedelta(days=6)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("500"),
        )
        create_activity(
            case,
            appropriation,
            start_date=modified_start_date,
            end_date=modified_end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            payment_plan=payment_schedule,
            modifies=modified_activity,
        )
        self.assertEqual(
            appropriation.total_expected_this_year, Decimal("3400")
        )

    def test_total_expected_full_year(self):
        # generate a start and end span of 10 days
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)
        # create main activity with GRANTED.
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create a GRANTED supplementary activity.
        supplementary_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
        )

        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
        )
        # create an EXPECTED supplementary activity overruling the GRANTED.
        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
            modifies=supplementary_activity,
        )

        self.assertEqual(
            activity.appropriation.total_expected_full_year, Decimal("438000")
        )

    def test_main_activity(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case, appropriation, activity_type=MAIN_ACTIVITY
        )

        self.assertEqual(activity, appropriation.main_activity)

    def test_constraint_on_more_than_one_main_activity(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        create_activity(case, appropriation, activity_type=MAIN_ACTIVITY)
        with self.assertRaises(IntegrityError):
            create_activity(case, appropriation, activity_type=MAIN_ACTIVITY)

    def test_constraint_more_than_one_activity(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        create_activity(case, appropriation, activity_type=MAIN_ACTIVITY)
        create_activity(case, appropriation, activity_type=SUPPL_ACTIVITY)
        self.assertEqual(appropriation.activities.count(), 2)

    def test_constraint_more_than_one_activity_with_expected(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case, appropriation, activity_type=MAIN_ACTIVITY
        )
        create_activity(
            case, appropriation, activity_type=MAIN_ACTIVITY, modifies=activity
        )
        self.assertEqual(appropriation.activities.count(), 2)

    def test_supplementary_activities(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case, appropriation, activity_type=SUPPL_ACTIVITY
        )
        self.assertEqual(
            activity, next(appropriation.supplementary_activities)
        )

    def test_appropriation_grant_sets_appropriation_date(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_DRAFT
        )
        now = timezone.now()
        start_date = now + timedelta(days=6)
        end_date = now + timedelta(days=12)
        create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )

        appropriation.grant(
            approval_level.id, "note til bevillingsgodkendelse"
        )

        today = now.date()
        self.assertEqual(appropriation.appropriation_date, today)

    def test_appropriation_grant_on_already_granted_one_time(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        now = timezone.now().date()
        start_date = now + timedelta(days=6)
        end_date = start_date
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
        )
        modified_start_date = start_date
        modified_end_date = end_date
        # let the granted activity be modified by another expected activity.
        modifies_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            start_date=modified_start_date,
            status=STATUS_EXPECTED,
            end_date=modified_end_date,
            modifies=activity,
            payment_plan=modifies_payment_schedule,
        )

        appropriation.grant(
            approval_level.id, "note til bevillingsgodkendelse"
        )
        activity.refresh_from_db()
        modifies_activity.refresh_from_db()
        self.assertEqual(activity.end_date, modified_end_date)
        # expected status should be granted with the
        # start_date of the new activity.
        self.assertEqual(modifies_activity.status, STATUS_GRANTED)
        self.assertEqual(modifies_activity.start_date, modified_start_date)
        # the payments of the old activity should be deleted for
        # a one time payment.
        self.assertEqual(activity.payment_plan.payments.count(), 0)
        self.assertEqual(modifies_activity.payment_plan.payments.count(), 1)

        # assert payments are generated correctly.
        self.assertEqual(
            modifies_activity.payment_plan.payments.first().amount,
            Decimal("600.0"),
        )

    def test_appropriation_grant_on_already_granted_daily(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now + timedelta(days=12)
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        modified_start_date = now + timedelta(days=1)
        modified_end_date = end_date + timedelta(days=6)
        # let the granted activity be modified by another expected activity.
        modifies_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            start_date=modified_start_date,
            status=STATUS_EXPECTED,
            end_date=modified_end_date,
            modifies=activity,
            payment_plan=modifies_payment_schedule,
        )

        appropriation.grant(
            approval_level.id, "note til bevillingsgodkendelse"
        )
        activity.refresh_from_db()
        modifies_activity.refresh_from_db()
        # the old activity should expire the day before
        # the start_date of the new one.
        self.assertEqual(
            activity.end_date, modified_start_date - timedelta(days=1)
        )
        # expected status should be granted with the
        # start_date of the new activity.
        self.assertEqual(modifies_activity.status, STATUS_GRANTED)
        self.assertEqual(modifies_activity.start_date, modified_start_date)
        # the payments of the old activity should expire
        # before the new end_date.
        activity_payments = activity.payment_plan.payments
        self.assertTrue(
            activity_payments.order_by("date").first().date
            < modified_start_date
        )
        # the payments of the new activity should start after today.
        modifies_payments = modifies_activity.payment_plan.payments

        self.assertTrue(
            modifies_payments.order_by("date").first().date
            >= modified_start_date
        )
        # assert payments are generated correctly.
        self.assertSequenceEqual(
            [
                x.date
                for x in (activity_payments.all() | modifies_payments.all())
            ],
            [start_date + timedelta(days=x) for x in range(25)],
        )

    def test_appropriation_grant_on_already_granted_weekly(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now + timedelta(days=12)
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        modified_start_date = start_date + timedelta(days=7)
        modified_end_date = end_date + timedelta(days=12)
        # let the granted activity be modified by another expected activity.
        modifies_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            start_date=modified_start_date,
            status=STATUS_EXPECTED,
            end_date=modified_end_date,
            modifies=activity,
            payment_plan=modifies_payment_schedule,
        )

        appropriation.grant(
            approval_level.id, "note til bevillingsgodkendelse"
        )
        activity.refresh_from_db()
        modifies_activity.refresh_from_db()
        # the old activity should expire the day before
        # the start_date of the new one.
        self.assertEqual(
            activity.end_date, modified_start_date - timedelta(days=1)
        )
        # expected status should be granted with the new start_date.
        self.assertEqual(modifies_activity.status, STATUS_GRANTED)
        self.assertEqual(modifies_activity.start_date, modified_start_date)
        # the payments of the old activity should expire today or before.
        activity_payments = activity.payment_plan.payments
        self.assertTrue(
            activity_payments.order_by("date").first().date
            < modified_start_date
        )
        # the payments of the new activity should start today or after.
        modifies_payments = modifies_activity.payment_plan.payments

        self.assertTrue(
            modifies_payments.order_by("date").first().date
            >= modified_start_date
        )
        # assert payments are generated correctly.
        self.assertSequenceEqual(
            [
                x.date
                for x in (activity_payments.all() | modifies_payments.all())
            ],
            [start_date + timedelta(days=7 * x) for x in range(5)],
        )

    def test_appropriation_grant_validate_expected_false(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now + timedelta(days=12)
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        modifies_payment_schedule = create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        modified_start_date = start_date
        modified_end_date = end_date + timedelta(days=12)
        # expected activity has an invalid start_date.
        create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            start_date=modified_start_date,
            status=STATUS_EXPECTED,
            end_date=modified_end_date,
            modifies=activity,
            payment_plan=modifies_payment_schedule,
        )

        with self.assertRaises(forms.ValidationError):
            appropriation.grant(
                approval_level.id, "note til bevillingsgodkendelse"
            )


class ServiceProviderTestCase(TestCase):
    def test_service_provider_str(self):
        service_provider = create_service_provider(
            cvr_number="12345678", name="Test Leverandør"
        )

        self.assertEqual(str(service_provider), "12345678 - Test Leverandør")


class MunicipalityTestCase(TestCase):
    def test_municipality_str(self):
        municipality = Municipality.objects.create(name="København")

        self.assertEqual(str(municipality), "København")


class SchoolDistrictTestCase(TestCase):
    def test_school_district_str(self):
        school_district = SchoolDistrict.objects.create(name="Skovlunde Skole")

        self.assertEqual(str(school_district), "Skovlunde Skole")


class TeamTestCase(TestCase):
    def test_team_str(self):
        user = get_user_model().objects.create(username="Anders And")
        team = Team.objects.create(name="C-BUR", leader=user)

        self.assertEqual(str(team), "C-BUR")


class SectionTestCase(TestCase):
    def test_section_str(self):
        section = create_section()

        self.assertEqual(str(section), "ABL-105-2 - 27.45.04")


class ActivityDetailsTestCase(TestCase):
    def test_activitydetails_str(self):
        details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        self.assertEqual(
            str(details),
            "010001 - Betaling til andre kommuner/region for specialtandpleje",
        )


class ActivityTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule()
        activity = create_activity(
            case,
            appropriation,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )

        self.assertEqual(
            str(activity),
            "000000 - Test aktivitet - hovedaktivitet - bevilget",
        )

    def test_synchronize_payments_on_save(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule()
        activity = create_activity(
            case,
            appropriation,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )

        self.assertEqual(activity.payment_plan.payments.count(), 10)

        activity.end_date = date(year=2019, month=1, day=13)
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 13)

    def test_synchronize_payments_on_save_one_time_payment(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT
        )
        activity = create_activity(
            case,
            appropriation,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )

        self.assertEqual(activity.payment_plan.payments.count(), 1)
        self.assertEqual(
            activity.payment_plan.payments.first().date,
            date(year=2019, month=1, day=1),
        )
        # A new end_date should not affect the one time payment.
        activity.end_date = date(year=2019, month=1, day=13)
        activity.save()

        self.assertEqual(activity.payment_plan.payments.count(), 1)
        self.assertEqual(
            activity.payment_plan.payments.first().date,
            date(year=2019, month=1, day=1),
        )

    def test_regenerate_payments_on_draft_save(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule()
        activity = create_activity(
            case,
            appropriation,
            payment_plan=payment_schedule,
            status=STATUS_DRAFT,
        )

        self.assertEqual(activity.payment_plan.payments.count(), 10)

        payment_schedule.payment_frequency = PaymentSchedule.MONTHLY
        payment_schedule.save()
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 1)

    def test_total_cost_with_service_provider(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        service_provider = ServiceProvider.objects.create(
            name="Test leverandør", vat_factor=Decimal("90")
        )
        payment_schedule = create_payment_schedule()
        activity = create_activity(
            case,
            appropriation,
            payment_plan=payment_schedule,
            service_provider=service_provider,
        )

        self.assertEqual(activity.total_cost, Decimal("4500.0"))

    def test_no_payment_plan_on_save(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(case, appropriation)
        self.assertIsNone(activity.payment_plan)

    def test_total_cost(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule()
        # 10 days, daily payments of 500.
        activity = create_activity(
            case, appropriation, payment_plan=payment_schedule
        )

        self.assertEqual(activity.total_cost, Decimal("5000"))

    def test_total_cost_spanning_years(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule()
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        # 32 days, daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )

        self.assertEqual(activity.total_cost, Decimal("16000"))

    def test_total_cost_this_year(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # 15 days, daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        self.assertEqual(activity.total_cost_this_year, Decimal("7500"))

    def test_total_cost_this_year_spanning_years(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year + 1, month=1, day=1)
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # 31 days, daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        self.assertEqual(activity.total_cost_this_year, Decimal("15500"))

    def test_total_cost_full_year(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # 365 days, daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        self.assertEqual(activity.total_cost_full_year, Decimal("182500"))

    def test_total_cost_for_year_no_payment_plan(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        self.assertEqual(activity.total_cost_full_year, Decimal("0"))

    def test_monthly_payment_plan(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # 32 days, daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        expected = [
            {"date_month": "2019-12", "amount": Decimal("15500")},
            {"date_month": "2020-01", "amount": Decimal("500")},
        ]
        self.assertEqual(
            [entry for entry in activity.monthly_payment_plan], expected
        )

    def test_created_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )
        self.assertEqual(len(mail.outbox), 1)
        email_message = mail.outbox[0]
        self.assertIn("Aktivitet oprettet", email_message.subject)
        self.assertIn("Barnets CPR nummer: 0205891234", email_message.body)
        self.assertIn("Beløb: 500,0", email_message.body)
        self.assertIn("Start dato: 1. december 2019", email_message.body)
        self.assertIn("Slut dato: 1. januar 2020", email_message.body)

    def test_updated_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )
        activity.save()
        self.assertEqual(len(mail.outbox), 2)
        email_message = mail.outbox[1]
        self.assertIn("Aktivitet opdateret", email_message.subject)
        self.assertIn("Barnets CPR nummer: 0205891234", email_message.body)
        self.assertIn("Beløb: 500,0", email_message.body)
        self.assertIn("Start dato: 1. december 2019", email_message.body)
        self.assertIn("Slut dato: 1. januar 2020", email_message.body)

    def test_deleted_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        # Should send a payment deleted email as status is GRANTED.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )
        activity.delete()
        self.assertEqual(len(mail.outbox), 2)
        email_message = mail.outbox[1]
        self.assertIn("Aktivitet udgået", email_message.subject)
        self.assertIn("Barnets CPR nummer: 0205891234", email_message.body)
        self.assertIn("Beløb: 500,0", email_message.body)
        self.assertIn("Start dato: 1. december 2019", email_message.body)
        self.assertIn("Slut dato: 1. januar 2020", email_message.body)

    def test_payment_email_draft_should_not_send(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_DRAFT
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_DRAFT,
        )
        activity.delete()
        self.assertEqual(len(mail.outbox), 0)

    def test_deleted_payment_email_person_cash_should_not_send(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule(
            payment_method=CASH, recipient_type=PaymentSchedule.PERSON
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )
        activity.delete()
        self.assertEqual(len(mail.outbox), 0)

    def test_deleted_payment_email_no_payment_plan_should_not_send(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED
        )
        # Generate an activity with no payment plan.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        activity.delete()
        self.assertEqual(len(mail.outbox), 0)

    def test_account_main_activity(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )

        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        account = create_account(
            main_activity=activity.details,
            supplementary_activity=None,
            section=section,
        )
        self.assertEqual(activity.account, account)

    def test_account_supplementary_activity(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        supplementary_activity_details = ActivityDetails.objects.create(
            name="Tandbørste",
            activity_id="010002",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule()
        supplementary_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
            details=supplementary_activity_details,
        )

        account = create_account(
            main_activity=main_activity.details,
            supplementary_activity=supplementary_activity.details,
            section=section,
        )
        self.assertEqual(supplementary_activity.account, account)

    def test_account_no_account(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )

        self.assertIsNone(main_activity.account)

    def test_validate_expected_true(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        start_date = date.today()
        end_date = date.today() + timedelta(days=7)
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        start_date = start_date + timedelta(days=1)
        end_date = date.today() + timedelta(days=14)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        self.assertTrue(expected_activity.validate_expected())

    def test_validate_expected_false_no_modifies(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        start_date = date.today()
        end_date = date.today() + timedelta(days=7)
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        with self.assertRaises(forms.ValidationError):
            expected_activity.validate_expected()

    def test_validate_expected_false_same_start_date(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        start_date = date.today()
        end_date = date.today() + timedelta(days=7)
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        start_date = start_date
        end_date = date.today() + timedelta(days=14)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        with self.assertRaises(forms.ValidationError):
            expected_activity.validate_expected()

    def test_validate_expected_false_in_the_past_no_next_payment(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        start_date = date.today() - timedelta(days=3)
        end_date = date.today() + timedelta(days=2)
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
        )
        start_date = date.today() - timedelta(days=3)
        end_date = date.today() + timedelta(days=2)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        with self.assertRaises(forms.ValidationError):
            expected_activity.validate_expected()

    def test_validate_expected_true_ongoing_with_next_payment(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        start_date = date.today() + timedelta(days=2)
        end_date = date.today() + timedelta(days=4)
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
        )
        start_date = date.today() + timedelta(days=3)
        end_date = date.today() + timedelta(days=6)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        self.assertTrue(expected_activity.validate_expected())

    def test_validate_expected_false_one_time_with_invalid_start_date(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            case=case, status=Appropriation.STATUS_GRANTED, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
        )
        start_date = date.today()
        end_date = date.today()
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
        )
        start_date = date.today()
        end_date = date.today()
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        with self.assertRaises(forms.ValidationError):
            expected_activity.validate_expected()


class AccountTestCase(TestCase):
    def test_account_str(self):
        section = create_section()
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        supplementary_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010002",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        account = Account.objects.create(
            number="123456",
            section=section,
            main_activity=main_activity_details,
            supplementary_activity=supplementary_activity_details,
        )

        self.assertEqual(
            str(account),
            f"123456 - {main_activity_details} - "
            f"{supplementary_activity_details} - "
            f"{section}",
        )


class ApprovalLevelTestCase(TestCase):
    def test_approvallevel_str(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")

        self.assertEqual(str(approval_level), f"{approval_level.name}")


class PaymentTestCase(TestCase):
    def test_payment_str(self):
        payment_schedule = create_payment_schedule()
        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
            amount=Decimal("500.0"),
        )
        self.assertEqual(str(payment), "Person - Test - 2019-01-01 - 500.0")


class PaymentScheduleTestCase(TestCase):
    @parameterized.expand(
        [
            (
                PaymentSchedule.DAILY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=10),
                10,
            ),
            (
                PaymentSchedule.DAILY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=1),
                1,
            ),
            (
                PaymentSchedule.WEEKLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=2, day=1),
                5,
            ),
            (
                PaymentSchedule.WEEKLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=1),
                1,
            ),
            (
                PaymentSchedule.BIWEEKLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=2, day=1),
                3,
            ),
            (
                PaymentSchedule.BIWEEKLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=1),
                1,
            ),
            (
                PaymentSchedule.MONTHLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=10, day=1),
                10,
            ),
            (
                PaymentSchedule.MONTHLY,
                date(year=2019, month=1, day=1),
                date(year=2019, month=1, day=1),
                1,
            ),
        ]
    )
    def test_create_rrule_frequency(self, frequency, start, end, expected):
        payment_schedule = create_payment_schedule(payment_frequency=frequency)
        rrule = payment_schedule.create_rrule(start=start, end=end)

        self.assertEqual(len(list(rrule)), expected)

    def test_create_rrule_one_time_1_day(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=2, day=1),
        )

        self.assertEqual(len(list(rrule)), 1)
        self.assertEqual(
            list(rrule)[0].date(), date(year=2019, month=1, day=1)
        )

    def test_create_rrule_incorrect_frequency(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency="incorrect frequency",
        )

        with self.assertRaises(ValueError):
            payment_schedule.create_rrule(
                start=date(year=2019, month=1, day=1),
                end=date(year=2019, month=2, day=1),
            )

    @parameterized.expand(
        [
            (
                PaymentSchedule.ONE_TIME_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
                Decimal("100"),
            ),
            (
                PaymentSchedule.RUNNING_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
                Decimal("100"),
            ),
            (
                PaymentSchedule.PER_HOUR_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                5,
                Decimal("100"),
                Decimal("500"),
            ),
            (
                PaymentSchedule.PER_KM_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                10,
                Decimal("100"),
                Decimal("1000"),
            ),
        ]
    )
    def test_calculate_per_payment_amount(
        self,
        payment_type,
        payment_frequency,
        payment_amount,
        payment_units,
        vat_factor,
        expected,
    ):
        payment_schedule = create_payment_schedule(
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_amount=payment_amount,
            payment_units=payment_units,
        )

        amount = payment_schedule.calculate_per_payment_amount(
            vat_factor=vat_factor
        )

        self.assertEqual(amount, expected)

    @parameterized.expand(
        [
            (PaymentSchedule.INTERNAL, CASH),
            (PaymentSchedule.INTERNAL, SD),
            (PaymentSchedule.INTERNAL, INVOICE),
            (PaymentSchedule.PERSON, INTERNAL),
            (PaymentSchedule.PERSON, INVOICE),
            (PaymentSchedule.COMPANY, CASH),
            (PaymentSchedule.COMPANY, SD),
            (PaymentSchedule.COMPANY, INTERNAL),
        ]
    )
    def test_save_with_payment_and_recipient(
        self, recipient_type, payment_method
    ):
        with self.assertRaises(ValueError):
            create_payment_schedule(
                recipient_type=recipient_type, payment_method=payment_method
            )

    def test_calculate_per_payment_amount_invalid_payment_type(self):
        payment_schedule = create_payment_schedule(
            payment_type="ugyldig betalingstype",
            payment_frequency=PaymentSchedule.DAILY,
        )

        with self.assertRaises(ValueError):
            payment_schedule.calculate_per_payment_amount(
                vat_factor=Decimal("100")
            )

    def test_generate_payments(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=1, day=10)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 10)

    def test_generate_payments_no_end_date(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        # Start in January and no end should generate 25 monthly payments
        # (till end of next year)
        payment_schedule.generate_payments(start_date, None)

        self.assertIsNotNone(payment_schedule.payments)
        self.assertEqual(payment_schedule.payments.count(), 24)

    def test_synchronize_payments_no_end_needs_further_payments(self):
        # Test the case where end is unbounded and payments are generated till
        # end of next year then middle of next year is reached
        # and new payments should be generated once again
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None
        # Initial call to generate payments will generate 24 payments.
        payment_schedule.generate_payments(start_date, end_date)
        self.assertEqual(len(payment_schedule.payments.all()), 24)

        # Now we are in the future and we need to generate new payments
        # because end is still unbounded
        with mock.patch("core.models.date") as date_mock:
            date_mock.today.return_value = date(year=2020, month=7, day=1)
            date_mock.max.month = 12
            date_mock.max.day = 31
            payment_schedule.synchronize_payments(start_date, end_date)
        self.assertEqual(payment_schedule.payments.count(), 36)

    def test_synchronize_payments_new_end_date_in_past(self):
        # Test the case where we generate payments for an unbounded end
        # and next the end is set so we need to delete some generated payments.
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=2019, month=6, day=1)
        payment_schedule.synchronize_payments(start_date, new_end_date)

        self.assertEqual(payment_schedule.payments.count(), 6)

    def test_synchronize_payments_new_end_date_in_future(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None

        # Generate payments till 2020-12-1
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=2021, month=2, day=1)
        payment_schedule.synchronize_payments(start_date, new_end_date)

        self.assertEqual(payment_schedule.payments.count(), 26)

    def test_synchronize_payments_same_end_date_no_changes(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=9, day=1)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 9)

        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

    def test_synchronize_payments_no_payments(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 0)

    def test_synchronize_payments_end_date_in_future_for_weekly(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

        end_date = date(year=2019, month=4, day=1)
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 13)

    def test_synchronize_payments_end_date_in_future_for_biweekly(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.BIWEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 5)

        end_date = date(year=2019, month=4, day=1)
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 7)

    def test_synchronize_payments_invalid_frequency(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

        end_date = date(year=2019, month=4, day=1)
        payment_schedule.payment_frequency = "invalid_frequency"
        payment_schedule.save()
        with self.assertRaises(ValueError):
            payment_schedule.synchronize_payments(start_date, end_date)

    @parameterized.expand(
        [
            (PaymentSchedule.PERSON, SD),
            (PaymentSchedule.PERSON, CASH),
            (PaymentSchedule.INTERNAL, INTERNAL),
            (PaymentSchedule.COMPANY, INVOICE),
        ]
    )
    def test_payment_and_recipient_allowed_save(
        self, recipient_type, payment_method
    ):
        payment_schedule = create_payment_schedule()
        payment = create_payment(
            payment_schedule=payment_schedule,
            date=timezone.now(),
            recipient_type=recipient_type,
            payment_method=payment_method,
        )
        self.assertEqual(payment.recipient_type, recipient_type)
        self.assertEqual(payment.payment_method, payment_method)

    @parameterized.expand(
        [
            (PaymentSchedule.PERSON, INTERNAL),
            (PaymentSchedule.PERSON, INVOICE),
            (PaymentSchedule.INTERNAL, CASH),
            (PaymentSchedule.INTERNAL, SD),
            (PaymentSchedule.INTERNAL, INVOICE),
            (PaymentSchedule.COMPANY, INTERNAL),
            (PaymentSchedule.COMPANY, SD),
            (PaymentSchedule.COMPANY, CASH),
        ]
    )
    def test_payment_and_recipient_disallowed_save(
        self, recipient_type, payment_method
    ):
        payment_schedule = create_payment_schedule()
        with self.assertRaises(ValueError):
            create_payment(
                payment_schedule=payment_schedule,
                date=timezone.now(),
                recipient_type=recipient_type,
                payment_method=payment_method,
            )

    def test_next_payment_none(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        # generates payments in the past.
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.next_payment, None)

    def test_next_payment(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date.today()
        end_date = date.today() + timedelta(days=7)
        # generates payments in the past.
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(
            payment_schedule.next_payment.date,
            date.today() + timedelta(days=7),
        )

    def test_str(self):
        payment_schedule = create_payment_schedule()
        self.assertEqual(
            str(payment_schedule),
            "Person - Jens Testersen - Fast beløb, løbende - Dagligt - 500.0",
        )


class CaseTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )

        self.assertEqual(str(case), case.sbsys_id)

    def test_expired_one(self):
        # generate a just expired end_date
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = now.date() - timedelta(days=1)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        self.assertTrue(case.expired)

    def test_expired_none(self):
        # generate an end_date in the future
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = now.date()
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        self.assertFalse(case.expired)

    def test_expired_no_activities(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )

        self.assertFalse(case.expired)

    def test_expired_multiple_main_activities(self):
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = now.date() - timedelta(days=3)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # create an activity with an expired end_date
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        # create an activity with an expired end_date
        start_date = now.date() - timedelta(days=2)
        end_date = now.date() - timedelta(days=1)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        self.assertTrue(case.expired)
