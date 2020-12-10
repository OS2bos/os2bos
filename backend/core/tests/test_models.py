# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from decimal import Decimal
from datetime import datetime, date, timedelta
from dateutil import rrule
from unittest import mock
from freezegun import freeze_time

from django import forms
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from parameterized import parameterized
from constance import config

from core.tests.testing_utils import (
    BasicTestMixin,
    create_payment_schedule,
    create_activity,
    create_appropriation,
    create_case,
    create_section,
    create_activity_details,
    create_payment,
    create_service_provider,
    create_section_info,
    create_related_person,
    create_target_group,
    create_variable_rate,
    create_rate,
    create_rate_per_date,
    create_payment_date_exclusion,
    create_account_alias,
)
from core.models import (
    Municipality,
    SchoolDistrict,
    ActivityDetails,
    Activity,
    ApprovalLevel,
    Team,
    PaymentSchedule,
    Price,
    PaymentMethodDetails,
    ServiceProvider,
    EffortStep,
    InternalPaymentRecipient,
    Effort,
    CASH,
    SD,
    INVOICE,
    INTERNAL,
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
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(section=section, case=case)

        self.assertEqual(str(appropriation), "13212 - ABL-105-2")

    def test_section_info_is_none(self):
        section = create_section()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(section=section, case=case)
        si = appropriation.section_info
        self.assertEqual(si, None)
        now = timezone.now().date()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        si = appropriation.section_info
        self.assertEqual(si, None)

    def test_total_granted_this_year(self):
        # generate a start and end span of 10 days
        now = timezone.now().date()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)

        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create main activity with GRANTED.
        new_granted_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=new_granted_activity,
        )
        self.assertEqual(
            activity.appropriation.total_granted_this_year, Decimal("10000")
        )

    def test_total_granted_full_year(self):
        now = timezone.now().date()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)

        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # Create granted activities.
        # Daily payments of 500.00.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # Daily payments of 500.00.
        new_granted_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=new_granted_activity,
        )
        self.assertEqual(
            activity.appropriation.total_granted_full_year,
            Decimal("366000.00"),
        )

    def test_appropriation_status(self):

        now = timezone.now().date()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year + 1, month=1, day=10)

        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        self.assertEqual(appropriation.status, STATUS_DRAFT)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_EXPECTED,
        )

        self.assertEqual(appropriation.status, STATUS_EXPECTED)

        activity.status = STATUS_GRANTED
        activity.save()

        self.assertEqual(appropriation.status, STATUS_GRANTED)

    def test_total_expected_this_year(self):
        # generate a start and end span of 3 days
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=2)
        # create main activity with GRANTED.

        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create a GRANTED supplementary activity.
        supplementary_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=supplementary_activity,
        )

        # create an EXPECTED supplementary activity overruling the GRANTED.
        new_expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date + timedelta(days=1),
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=SUPPL_ACTIVITY,
            modifies=supplementary_activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
            activity=new_expected_activity,
        )

        # create a DRAFT supplementary activity which should not be counted.
        draft_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_DRAFT,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=draft_activity,
        )
        # create a GRANTED supplementary activity which has
        # modified another that is also GRANTED.
        supplementary_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=start_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=supplementary_activity,
        )

        new_granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date + timedelta(days=1),
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
            modifies=supplementary_activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
            activity=new_granted_activity,
        )

        self.assertEqual(
            appropriation.total_expected_this_year, Decimal("5300")
        )

    def test_total_expected_within_start_end_range(self):
        # generate a start and end span of 10 days
        now = timezone.now().date()
        start_date = now + timedelta(days=1)
        end_date = now + timedelta(days=10)

        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create a granted activity

        modified_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
            activity=modified_activity,
        )
        # create an expected activity with a (start, end)
        # within the span of the activity it modifies
        modified_start_date = now + timedelta(days=3)
        modified_end_date = now + timedelta(days=6)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=modified_start_date,
            end_date=modified_end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=modified_activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("500"),
            activity=expected_activity,
        )
        self.assertEqual(
            appropriation.total_expected_this_year, Decimal("3400")
        )

    def test_total_expected_full_year(self):
        # generate a start and end span of 10 days
        now = timezone.now().date()
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)
        # create main activity with GRANTED.
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create a GRANTED supplementary activity.
        supplementary_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=supplementary_activity,
        )

        # create an EXPECTED supplementary activity overruling the GRANTED.
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=SUPPL_ACTIVITY,
            modifies=supplementary_activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_amount=Decimal("700"),
            activity=expected_activity,
        )
        self.assertEqual(
            activity.appropriation.total_expected_full_year,
            activity.total_cost_full_year
            + expected_activity.total_cost_full_year,
        )

    def test_main_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case, appropriation, activity_type=MAIN_ACTIVITY
        )

        self.assertEqual(activity, appropriation.main_activity)

    def test_start_and_end_dates(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        start_date = date(year=now.year, month=1, day=1)
        end_date = date(year=now.year, month=1, day=10)
        activity = create_activity(
            case,
            appropriation,
            activity_type=MAIN_ACTIVITY,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        self.assertEqual(appropriation.granted_from_date, start_date)
        self.assertEqual(appropriation.granted_to_date, end_date)
        activity.status = STATUS_DRAFT
        activity.save()
        self.assertEqual(appropriation.granted_from_date, None)
        self.assertEqual(appropriation.granted_to_date, None)

    def test_constraint_on_more_than_one_main_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        create_activity(case, appropriation, activity_type=MAIN_ACTIVITY)
        with self.assertRaises(IntegrityError):
            create_activity(case, appropriation, activity_type=MAIN_ACTIVITY)

    def test_constraint_more_than_one_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        create_activity(case, appropriation, activity_type=MAIN_ACTIVITY)
        create_activity(case, appropriation, activity_type=SUPPL_ACTIVITY)
        self.assertEqual(appropriation.activities.count(), 2)

    def test_constraint_more_than_one_activity_with_expected(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case, appropriation, activity_type=MAIN_ACTIVITY
        )
        create_activity(
            case, appropriation, activity_type=MAIN_ACTIVITY, modifies=activity
        )
        self.assertEqual(appropriation.activities.count(), 2)

    def test_appropriation_grant_sets_appropriation_date(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        payment_schedule = create_payment_schedule()
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        now = timezone.now().date()
        start_date = now + timedelta(days=6)
        end_date = now + timedelta(days=12)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=start_date,
            end_date=end_date,
            payment_plan=payment_schedule,
        )
        activity.details.main_activity_for.add(section)
        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            appropriation.activities.exclude(status=STATUS_GRANTED),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )

        today = now
        self.assertEqual(
            appropriation.activities.first().appropriation_date, today
        )

    def test_appropriation_grant_no_end_date(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        now = timezone.now().date()
        start_date = now + timedelta(days=6)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=start_date,
            end_date=None,
        )
        activity.details.main_activity_for.add(section)
        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            appropriation.activities.exclude(status=STATUS_GRANTED),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )

    def test_appropriation_suppl_doesnt_cut_date(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        now = timezone.now().date()
        start_date = now + timedelta(days=6)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=start_date,
            end_date=None,
        )
        activity.details.main_activity_for.add(section)
        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            appropriation.activities.exclude(status=STATUS_GRANTED),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )
        suppl_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=start_date,
            end_date=start_date + timedelta(days=2),
        )
        section.supplementary_activities.add(activity.details)
        suppl_activity.details.main_activities.add(activity.details)

        appropriation.grant(
            appropriation.activities.filter(pk=suppl_activity.pk),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )
        suppl_activity.refresh_from_db()
        self.assertEqual(
            suppl_activity.end_date, (start_date + timedelta(days=2))
        )

    def test_grant_no_stop_before_suppl_start(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        now = timezone.now().date()
        start_date = now + timedelta(days=6)
        main_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=start_date,
            end_date=None,
        )
        main_activity.details.main_activity_for.add(section)
        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            appropriation.activities.exclude(status=STATUS_GRANTED),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=start_date + timedelta(days=10),
            end_date=None,
        )
        section.supplementary_activities.add(activity.details)
        activity.details.main_activities.add(activity.details)

        appropriation.grant(
            appropriation.activities.filter(pk=activity.pk),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )
        main_activity.refresh_from_db()
        main_activity.end_date = start_date + timedelta(days=5)
        main_activity.save()

        with self.assertRaises(RuntimeError):
            appropriation.grant(
                appropriation.activities.filter(pk=main_activity.pk),
                approval_level.id,
                "note til bevillingsgodkendelse",
                user,
            )

    def test_appropriation_grant_on_already_granted_one_time(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=activity,
        )
        activity.details.main_activity_for.add(section)

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
        )
        create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=modifies_activity,
        )

        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            appropriation.activities.exclude(status=STATUS_GRANTED),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
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

        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=activity,
        )
        activity.details.main_activity_for.add(section)

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
        )
        create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=modifies_activity,
        )
        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            Activity.objects.filter(pk=modifies_activity.pk),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
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
        self.assertCountEqual(
            [
                x.date
                for x in (activity_payments.all() | modifies_payments.all())
            ],
            [start_date + timedelta(days=x) for x in range(25)],
        )

    def test_appropriation_grant_on_already_granted_weekly(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")

        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
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
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=activity,
        )

        activity.details.main_activity_for.add(section)

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
        )
        create_payment_schedule(
            payment_amount=Decimal("600.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=modifies_activity,
        )

        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            appropriation.activities.exclude(status=STATUS_GRANTED),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
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
        self.assertCountEqual(
            [
                x.date
                for x in (activity_payments.all() | modifies_payments.all())
            ],
            [start_date + timedelta(days=7 * x) for x in range(5)],
        )

    def test_appropriation_grant_on_modifies_suppl_date(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = None
        # create an already granted activity.
        main_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=start_date,
            end_date=end_date,
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=main_activity,
        )
        main_activity.details.main_activity_for.add(section)

        suppl_start_date = start_date + timedelta(days=7)
        suppl_end_date = None
        # let the granted activity be modified by another expected activity.
        suppl_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=SUPPL_ACTIVITY,
            start_date=suppl_start_date,
            status=STATUS_EXPECTED,
            end_date=suppl_end_date,
        )
        create_payment_schedule(
            payment_amount=Decimal("50.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=suppl_activity,
        )
        section.supplementary_activities.add(suppl_activity.details)
        suppl_activity.details.main_activities.add(main_activity.details)

        user = get_user_model().objects.create(username="Anders And")
        appropriation.grant(
            appropriation.activities.exclude(status=STATUS_GRANTED),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )
        modified_start_date = start_date + timedelta(days=7)
        modified_end_date = start_date + timedelta(days=365)
        # let the granted activity be modified by another expected activity.
        new_main_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            start_date=modified_start_date,
            status=STATUS_EXPECTED,
            end_date=modified_end_date,
            modifies=main_activity,
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.WEEKLY,
            activity=new_main_activity,
        )

        appropriation.grant(
            appropriation.activities.filter(pk=new_main_activity.pk),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )
        suppl_activity.refresh_from_db()
        # the old activity should expire the day before
        # the start_date of the new one.
        self.assertEqual(suppl_activity.end_date, modified_end_date)
        new_modified_end_date = modified_end_date - timedelta(3)
        modifies_again = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            start_date=modified_start_date + timedelta(days=7),
            status=STATUS_EXPECTED,
            end_date=new_modified_end_date,
            modifies=new_main_activity,
        )
        create_payment_schedule(activity=modifies_again)

        appropriation.grant(
            appropriation.activities.filter(pk=modifies_again.pk),
            approval_level.id,
            "note til bevillingsgodkendelse",
            user,
        )
        suppl_activity.refresh_from_db()
        self.assertEqual(suppl_activity.end_date, new_modified_end_date)

    def test_appropriation_grant_error_no_main_activity(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now + timedelta(days=12)
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_EXPECTED,
            start_date=start_date,
            end_date=end_date,
        )

        user = get_user_model().objects.create(username="Anders And")
        with self.assertRaises(RuntimeError):
            appropriation.grant(
                appropriation.activities.filter(pk=activity.pk),
                approval_level.id,
                "note til bevillingsgodkendelse",
                user,
            )

    def test_appropriation_grant_error_no_approved_main_activity(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now + timedelta(days=12)
        # Create a main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_EXPECTED,
            start_date=start_date,
            end_date=end_date,
        )
        activity.details.main_activity_for.add(section)
        # create an already granted activity.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_EXPECTED,
            start_date=start_date,
            end_date=end_date,
        )

        user = get_user_model().objects.create(username="Anders And")
        with self.assertRaises(RuntimeError):
            appropriation.grant(
                appropriation.activities.filter(pk=activity.pk),
                approval_level.id,
                "note til bevillingsgodkendelse",
                user,
            )

    def test_appropriation_grant_error_invalid_main_activity(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
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
        )

        user = get_user_model().objects.create(username="Anders And")
        with self.assertRaises(RuntimeError):
            appropriation.grant(
                appropriation.activities.filter(pk=activity.pk),
                approval_level.id,
                "note til bevillingsgodkendelse",
                user,
            )

    def test_appropriation_grant_error_no_activities(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
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
        )
        section.main_activities.add(activity.details)
        user = get_user_model().objects.create(username="Anders And")
        with self.assertRaises(RuntimeError):
            appropriation.grant(
                [], approval_level.id, "note til bevillingsgodkendelse", user
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

        self.assertEqual(str(section), "ABL-105-2")


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
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(
            str(activity),
            "000000 - Test aktivitet - hovedaktivitet - bevilget",
        )

    def test_synchronize_payments_on_save(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(case, appropriation, status=STATUS_GRANTED)
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.payment_plan.payments.count(), 10)

        activity.end_date = date(year=2019, month=1, day=13)
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 13)

    def test_synchronize_payments_on_save_one_time_payment(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(case, appropriation, status=STATUS_GRANTED)
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=activity,
            payment_date=date.today(),
        )

        self.assertEqual(activity.payment_plan.payments.count(), 1)
        self.assertEqual(
            activity.payment_plan.payments.first().date, date.today()
        )
        # A new end_date should not affect the one time payment.
        activity.end_date = date(year=2019, month=1, day=13)
        activity.save()

        self.assertEqual(activity.payment_plan.payments.count(), 1)
        self.assertEqual(
            activity.payment_plan.payments.first().date, date.today()
        )

    def test_grant_already_granted(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(case, appropriation, status=STATUS_GRANTED)
        create_payment_schedule(activity=activity)

        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        user = get_user_model().objects.create(username="Anders And")
        activity.grant(approval_level, "note", user)
        self.assertEqual(activity.status, STATUS_GRANTED)

    def test_grant_on_expected_modifies_sets_payment_schedule_payment_id(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        payment_schedule = create_payment_schedule()
        activity = create_activity(
            case,
            appropriation,
            payment_plan=payment_schedule,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            status=STATUS_GRANTED,
        )
        # Assert payment_id corresponds to payment_plan ID.
        self.assertEqual(
            activity.payment_plan.payment_id, activity.payment_plan.id
        )

        payment_schedule = create_payment_schedule()
        expected_activity = create_activity(
            case,
            appropriation,
            payment_plan=create_payment_schedule(
                payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT
            ),
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=30),
            status=STATUS_EXPECTED,
            modifies=activity,
        )
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")
        user = get_user_model().objects.create(username="Anders And")

        # Assert payment_id corresponds to payment_plan ID.
        self.assertEqual(
            expected_activity.payment_plan.payment_id,
            expected_activity.payment_plan.id,
        )

        # Grant the expected modified activity.
        # This is not allowed as there are no payments on it.
        with self.assertRaises(RuntimeError):
            expected_activity.grant(approval_level, "note", user)

    def test_regenerate_payments_on_draft_save(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(case, appropriation, status=STATUS_DRAFT)
        payment_schedule = create_payment_schedule(activity=activity)

        self.assertEqual(activity.payment_plan.payments.count(), 10)

        payment_schedule.payment_frequency = PaymentSchedule.MONTHLY
        payment_schedule.save()
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 1)

    def test_total_cost_with_service_provider(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        service_provider = ServiceProvider.objects.create(
            name="Test leverandør", vat_factor=Decimal("90")
        )
        activity = create_activity(
            case, appropriation, service_provider=service_provider
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.total_cost, Decimal("4500.0"))

    def test_no_payment_plan_on_save(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(case, appropriation)
        self.assertFalse(hasattr(activity, "payment_plan"))

    def test_total_cost(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # 15 days, daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.total_cost, Decimal("7500"))
        start_date = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=10)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(activity=expected_activity)
        self.assertTrue(expected_activity.validate_expected())

        self.assertEqual(activity.total_cost, Decimal("7500"))

    def test_total_cost_negative_amount(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # 15 days, daily payments of -500.
        activity = create_activity(
            case,
            appropriation,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14),
        )
        create_payment_schedule(
            payment_amount=Decimal("-500"), activity=activity
        )
        self.assertEqual(activity.total_cost, Decimal("-7500"))

    def test_total_cost_spanning_years(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        # 32 days, daily payments of 500.
        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        create_payment_schedule(activity=activity)
        self.assertEqual(activity.total_cost, Decimal("16000"))

    @freeze_time("2019-08-01")
    def test_total_cost_no_payments(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create an activity with daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)
        self.assertEqual(activity.total_cost_this_year, Decimal("500"))
        start_date = date(year=now.year, month=12, day=2)
        end_date = date(year=now.year, month=12, day=2)
        # create an expected activity with no payments.
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(
            payment_amount=Decimal("600"), activity=expected_activity
        )
        # remove the payments
        expected_activity.payment_plan.payments.all().delete()
        self.assertTrue(expected_activity.validate_expected())
        self.assertEqual(activity.total_cost, Decimal("500"))
        self.assertEqual(expected_activity.total_cost, Decimal("0"))

    @freeze_time("2019-08-01")
    def test_total_cost_this_year(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # 15 days, daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.total_cost_this_year, Decimal("7500"))
        start_date = date(year=now.year, month=12, day=2)
        end_date = date(year=now.year, month=12, day=11)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(activity=expected_activity)

        self.assertTrue(expected_activity.validate_expected())
        self.assertEqual(activity.total_cost_this_year, Decimal("500"))

    @freeze_time("2019-08-01")
    def test_total_cost_this_year_multiple_levels(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create an activity with a span of 15 days and daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.total_cost_this_year, Decimal("7500"))
        start_date = date(year=now.year, month=12, day=15)
        end_date = date(year=now.year, month=12, day=15)
        # create an expected activity that overrides
        # the last day of the previous activity.
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(activity=expected_activity)

        self.assertTrue(expected_activity.validate_expected())
        # The total cost of the original activity should be 500 less.
        self.assertEqual(activity.total_cost_this_year, Decimal("7000"))
        self.assertEqual(
            expected_activity.total_cost_this_year, Decimal("500")
        )

        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        # create an expected activity that overrides the full period.
        expected_activity_another_level = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=expected_activity,
        )
        create_payment_schedule(
            payment_amount=Decimal("600"),
            activity=expected_activity_another_level,
        )
        self.assertTrue(expected_activity_another_level.validate_expected())
        #
        self.assertEqual(activity.total_cost_this_year, Decimal("0"))
        self.assertEqual(expected_activity.total_cost_this_year, Decimal("0"))
        self.assertEqual(
            expected_activity_another_level.total_cost_this_year,
            Decimal("9000"),
        )

    @freeze_time("2019-08-01")
    def test_total_cost_this_year_multiple_levels_one_time(self):
        now = timezone.now()

        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create an activity with a one time payment of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=None,
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=activity,
        )

        self.assertEqual(activity.total_cost_this_year, Decimal("500"))
        start_date = date(year=now.year, month=12, day=2)
        end_date = date(year=now.year, month=12, day=2)
        # create an expected activity that overrides the previous with 600.
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=None,
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_amount=Decimal("600"),
            activity=expected_activity,
        )
        self.assertTrue(expected_activity.validate_expected())
        self.assertEqual(activity.total_cost_this_year, Decimal("0"))
        self.assertEqual(
            expected_activity.total_cost_this_year, Decimal("600")
        )

        start_date = date(year=now.year, month=12, day=3)
        end_date = date(year=now.year, month=12, day=3)
        # create an expected activity that overrides the previous with 700.
        expected_activity_another_level = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=expected_activity,
        )
        create_payment_schedule(
            payment_frequency=None,
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_amount=Decimal("700"),
            activity=expected_activity_another_level,
        )
        self.assertTrue(expected_activity_another_level.validate_expected())
        self.assertEqual(activity.total_cost_this_year, Decimal("0"))
        self.assertEqual(expected_activity.total_cost_this_year, Decimal("0"))
        self.assertEqual(
            expected_activity_another_level.total_cost_this_year,
            Decimal("700"),
        )

    @freeze_time("2019-08-01")
    def test_total_cost_this_year_no_payments(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create an activity with daily payments of 500.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.total_cost_this_year, Decimal("500"))
        start_date = date(year=now.year, month=12, day=2)
        end_date = date(year=now.year, month=12, day=2)
        # create an expected activity with no payments.
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(
            payment_amount=Decimal("600"), activity=expected_activity
        )
        # remove the payments
        expected_activity.payment_plan.payments.all().delete()
        self.assertTrue(expected_activity.validate_expected())
        self.assertEqual(activity.total_cost_this_year, Decimal("500"))
        self.assertEqual(expected_activity.total_cost_this_year, Decimal("0"))

    def test_total_granted_this_year_zero_for_draft(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.total_granted_this_year, Decimal(0))

    def test_total_cost_this_year_spanning_years(self):
        now = timezone.now()

        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year + 1, month=1, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # 31 days, daily payments of 500.
        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        create_payment_schedule(activity=activity)

        self.assertEqual(activity.total_cost_this_year, Decimal("15500"))

    def test_total_cost_full_year(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # payments for all days in year, daily payments of 500.
        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        create_payment_schedule(activity=activity)

        days_in_year = len(
            list(
                rrule.rrule(
                    rrule.DAILY,
                    dtstart=date(year=now.year, month=1, day=1),
                    until=date(year=now.year, month=12, day=31),
                )
            )
        )
        self.assertEqual(
            activity.total_cost_full_year, Decimal("500") * days_in_year
        )

    def test_total_cost_full_year_individual_payment(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # There is no way to extrapolate for full year with individual
        # payments so we just return total_cost
        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        payment_schedule = create_payment_schedule(
            activity=activity, payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT
        )

        create_payment(payment_schedule, amount=Decimal("500"))

        self.assertEqual(activity.total_cost_full_year, Decimal("500"))

    def test_total_cost_for_year_no_payment_plan(self):
        now = timezone.now()
        start_date = date(year=now.year, month=12, day=1)
        end_date = date(year=now.year, month=12, day=15)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        self.assertEqual(activity.total_cost_full_year, Decimal("0"))

    def test_monthly_payment_plan(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # 32 days, daily payments of 500.
        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        create_payment_schedule(activity=activity)
        expected = [
            {"date_month": "2019-12", "amount": Decimal("15500")},
            {"date_month": "2020-01", "amount": Decimal("500")},
        ]
        self.assertEqual(
            [entry for entry in activity.monthly_payment_plan], expected
        )

    def test_monthly_payment_plan_negative_amounts(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)

        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # 32 days, daily payments of 500.
        activity = create_activity(
            case, appropriation, start_date=start_date, end_date=end_date
        )
        create_payment_schedule(
            payment_amount=Decimal("-500"), activity=activity
        )
        expected = [
            {"date_month": "2019-12", "amount": Decimal("-15500")},
            {"date_month": "2020-01", "amount": Decimal("-500")},
        ]
        self.assertEqual(
            [entry for entry in activity.monthly_payment_plan], expected
        )

    def test_created_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(activity=activity)

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
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        activity.save()
        self.assertEqual(len(mail.outbox), 2)
        email_message = mail.outbox[1]
        self.assertIn("Aktivitet opdateret", email_message.subject)
        self.assertIn("Barnets CPR nummer: 0205891234", email_message.body)
        self.assertIn("Beløb: 500,0", email_message.body)
        self.assertIn("Start dato: 1. december 2019", email_message.body)
        self.assertIn("Slut dato: 1. januar 2020", email_message.body)

    def test_updated_sd_activity_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(
            self.case_worker, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(activity=activity, payment_method=SD)

        activity.status = STATUS_GRANTED
        activity.save()

        self.assertEqual(len(mail.outbox), 1)
        email_message = mail.outbox[0]
        self.assertIn("Aktivitet opdateret", email_message.subject)
        self.assertIn("Barnets CPR nummer: 0205891234", email_message.body)
        self.assertIn("Beløb: 500,0", email_message.body)
        self.assertIn("Start dato: 1. december 2019", email_message.body)
        self.assertIn("Slut dato: 1. januar 2020", email_message.body)

    def test_updated_one_time_payment_activity_no_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(
            self.case_worker, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            activity=activity,
            payment_method=CASH,
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
        )

        activity.status = STATUS_GRANTED
        activity.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_updated_activity_with_internal_recipient_no_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(
            self.case_worker, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            activity=activity,
            payment_method=INTERNAL,
            recipient_type=PaymentSchedule.INTERNAL,
        )

        activity.status = STATUS_GRANTED
        activity.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_deleted_payment_email(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # Should send a payment deleted email as status is GRANTED.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(activity=activity)

        activity.delete()
        self.assertEqual(len(mail.outbox), 2)
        email_message = mail.outbox[1]
        self.assertIn("Aktivitet slettet", email_message.subject)
        self.assertIn("Barnets CPR nummer: 0205891234", email_message.body)
        self.assertIn("Beløb: 500,0", email_message.body)
        self.assertIn("Start dato: 1. december 2019", email_message.body)
        self.assertIn("Slut dato: 1. januar 2020", email_message.body)

    def test_payment_email_draft_should_not_send(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(activity=activity)

        activity.delete()
        self.assertEqual(len(mail.outbox), 0)

    def test_deleted_payment_email_no_payment_plan_should_not_send(self):
        start_date = date(year=2019, month=12, day=1)
        end_date = date(year=2020, month=1, day=1)
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
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

    def test_validate_expected_true(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        start_date = date.today()
        end_date = date.today() + timedelta(days=7)
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=main_activity,
        )

        start_date = start_date + timedelta(days=1)
        end_date = date.today() + timedelta(days=14)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=expected_activity,
        )

        self.assertTrue(expected_activity.validate_expected())

    def test_validate_expected_false_no_modifies(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        start_date = date.today()
        end_date = date.today() + timedelta(days=7)

        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=expected_activity,
        )
        with self.assertRaises(forms.ValidationError):
            expected_activity.validate_expected()

    def test_validate_expected_false_same_start_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        start_date = date.today()
        end_date = date.today() + timedelta(days=7)
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=main_activity,
        )

        start_date = start_date
        end_date = date.today() + timedelta(days=14)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=expected_activity,
        )

        expected_activity.validate_expected()

    def test_validate_expected_true_ongoing_with_next_payment(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        start_date = date.today() + timedelta(days=2)
        end_date = date.today() + timedelta(days=4)
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=main_activity,
        )

        start_date = date.today() + timedelta(days=3)
        end_date = date.today() + timedelta(days=6)
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )

        create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=expected_activity,
        )

        self.assertTrue(expected_activity.validate_expected())

    def test_validate_expected_false_one_time_with_invalid_start_date(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        start_date = date.today()
        end_date = date.today()
        main_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("500.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=main_activity,
        )

        start_date = date.today()
        end_date = date.today()
        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=main_activity,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=expected_activity,
        )
        expected_activity.validate_expected()

    def test_activity_save_updates_appropriation_modified(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(case=case, appropriation=appropriation)
        self.assertGreaterEqual(appropriation.modified, activity.modified)

    def test_delete_activity_deletes_payment_schedule(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_DRAFT,
            activity_type=MAIN_ACTIVITY,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_amount=Decimal("700.0"),
            payment_frequency=PaymentSchedule.DAILY,
            activity=activity,
        )

        activity.delete()
        with self.assertRaises(PaymentSchedule.DoesNotExist):
            payment_schedule.refresh_from_db()

    def test_account_number_main_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=activity,
        )
        section_info = create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        # account_number should come from ACCOUNT_NUMBER_DEPARTMENT,
        # the section_info of the activity, and ACCOUNT_NUMBER_KIND.
        self.assertEqual(
            activity.account_number,
            f"{section_info.main_activity_main_account_number}-"
            f"{activity.details.activity_id}",
        )

    def test_account_number_main_activity_no_section_info(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=activity,
        )
        # No section info is found.
        self.assertIsNone(activity.account_number)

    def test_account_number_supplementary_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        main_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=main_activity,
        )
        section_info = create_section_info(
            details=main_activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        suppl_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=suppl_activity,
        )
        # account_number should come from ACCOUNT_NUMBER_DEPARTMENT,
        # the section_info of the activity, and ACCOUNT_NUMBER_KIND.
        self.assertEqual(
            suppl_activity.account_number,
            f"{section_info.supplementary_activity_main_account_number}-"
            f"{suppl_activity.details.activity_id}",
        )

    def test_account_number_supplementary_activity_no_section_info(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        main_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=main_activity,
        )
        suppl_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=suppl_activity,
        )
        # No section info is found.
        self.assertIsNone(suppl_activity.account_number)

    def test_account_number_supplementary_activity_no_main_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        suppl_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=suppl_activity,
        )
        # No main activity is found.
        self.assertIsNone(suppl_activity.account_number)

    def test_account_alias_main_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=activity,
        )
        section_info = create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        account_alias = create_account_alias(section_info, activity.details)

        self.assertEqual(activity.account_alias, account_alias.alias)

    def test_account_alias_main_activity_no_section_info(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=activity,
        )
        # No section info is found.
        self.assertIsNone(activity.account_alias)

    def test_account_alias_supplementary_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        main_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=main_activity,
        )
        section_info = create_section_info(
            details=main_activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        suppl_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=suppl_activity,
        )
        account_alias = create_account_alias(
            section_info, main_activity.details
        )

        self.assertEqual(suppl_activity.account_alias, account_alias.alias)

    def test_account_alias_supplementary_activity_no_section_info(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        main_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=main_activity,
        )
        suppl_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=suppl_activity,
        )
        # No section info is found.
        self.assertIsNone(suppl_activity.account_alias)

    def test_account_alias_supplementary_activity_no_main_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        suppl_activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=suppl_activity,
        )
        # No main activity is found.
        self.assertIsNone(suppl_activity.account_alias)

    def test_individual_payment_activity_no_payments(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # payments are not generated.
        activity = create_activity(case, appropriation)
        create_payment_schedule(
            activity=activity, payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT
        )

        self.assertEqual(activity.payment_plan.payments.count(), 0)

        activity.end_date = date(year=2019, month=1, day=13)
        # synchronize_payments is not called either.
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 0)


class ApprovalLevelTestCase(TestCase):
    def test_approvallevel_str(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")

        self.assertEqual(str(approval_level), f"{approval_level.name}")


class PaymentTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_payment_account_default(self):
        # Create a PaymentSchedule with PERSON, CASH
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        payment_schedule = create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=activity,
        )
        section_info = create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=11),
            amount=Decimal("500.0"),
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
        )
        # account_string should come from ACCOUNT_NUMBER_DEPARTMENT,
        # the section_info of the activity, the activity id
        # and ACCOUNT_NUMBER_KIND.
        self.assertEqual(
            payment.account_string,
            f"{config.ACCOUNT_NUMBER_DEPARTMENT}-"
            f"{section_info.main_activity_main_account_number}-"
            f"{activity.details.activity_id}-"
            f"{config.ACCOUNT_NUMBER_KIND}",
        )

    def test_payment_account_new_default(self):
        # Create a PaymentSchedule with PERSON, CASH
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        payment_schedule = create_payment_schedule(
            payment_method=CASH,
            recipient_type=PaymentSchedule.PERSON,
            activity=activity,
        )
        section_info = create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=11),
            amount=Decimal("500.0"),
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
        )
        # Account should come from ACCOUNT_NUMBER_DEPARTMENT,
        # the section_info of the activity, and ACCOUNT_NUMBER_KIND.
        self.assertEqual(
            payment.account_string,
            f"{config.ACCOUNT_NUMBER_DEPARTMENT}-"
            f"{section_info.main_activity_main_account_number}-"
            f"{activity.details.activity_id}-"
            f"{config.ACCOUNT_NUMBER_KIND}",
        )

    def test_payment_account_already_saved(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=11),
            amount=Decimal("500.0"),
            saved_account_string="123-1234-123",
        )
        # Account should come from the saved account.
        self.assertEqual(payment.account_string, "123-1234-123")

    def test_payment_account_with_unset_department_and_kind(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        payment_schedule = create_payment_schedule(
            payment_method=SD,
            recipient_type=PaymentSchedule.PERSON,
            activity=activity,
        )
        create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=11),
            amount=Decimal("500.0"),
        )
        self.assertEqual(payment.account_string, "XXX-12345-000000-XXX")

    def test_payment_save_account_string_saved(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )

        section_info = create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        payment_schedule = create_payment_schedule(activity=activity)

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=11),
            amount=Decimal("500.0"),
        )

        # Account should come from the section info while not paid.
        self.assertEqual(payment.account_string, "XXX-12345-000000-XXX")
        self.assertEqual(payment.saved_account_string, "")

        # Set payment paid which should save the saved_account_string
        payment.paid = True
        payment.paid_date = date(year=2019, month=2, day=1)
        payment.paid_amount = Decimal("500.0")
        payment.save()
        payment.refresh_from_db()
        self.assertEqual(payment.saved_account_string, "XXX-12345-000000-XXX")

        # Change section_info main_account number.
        section_info.main_activity_main_account_number = "67890"
        section_info.save()

        # Payment account_string should use the saved_account_string
        self.assertEqual(payment.account_string, "XXX-12345-000000-XXX")

    def test_payment_save_account_alias_saved(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case,
            appropriation,
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )

        section_info = create_section_info(
            details=activity.details,
            section=section,
            main_activity_main_account_number="12345",
        )
        account_alias = create_account_alias(section_info, activity.details)
        payment_schedule = create_payment_schedule(activity=activity)

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=11),
            amount=Decimal("500.0"),
        )

        # account alias should come from the section info while not paid.
        self.assertEqual(payment.account_alias, "BOS0000001")
        self.assertEqual(payment.saved_account_alias, "")

        # Set payment paid which should save the saved_account_string
        payment.paid = True
        payment.paid_date = date(year=2019, month=2, day=1)
        payment.paid_amount = Decimal("500.0")
        payment.save()
        payment.refresh_from_db()
        self.assertEqual(payment.saved_account_alias, "BOS0000001")

        # Change alias.
        account_alias.alias = "BOS0000002"
        section_info.save()

        # Payment account_string should use the saved_account_string
        self.assertEqual(payment.account_alias, "BOS0000001")

    def test_save_not_all_paid_fields_set(self):
        payment_schedule = create_payment_schedule()

        with self.assertRaises(
            ValueError,
            msg="ved en betalt betaling skal alle betalingsfelter sættes",
        ):
            create_payment(
                payment_schedule=payment_schedule,
                date=date(year=2019, month=1, day=1),
                amount=Decimal("500.0"),
                paid=True,
            )

    def test_save_is_paid_paid_date_not_set(self):
        payment_schedule = create_payment_schedule()

        with self.assertRaises(
            ValueError,
            msg="ved en betalt betaling skal alle betalingsfelter sættes",
        ):
            create_payment(
                payment_schedule=payment_schedule,
                date=date(year=2019, month=1, day=1),
                amount=Decimal("500.0"),
                paid=True,
                paid_amount=Decimal("500.0"),
            )

    def test_save_is_paid_paid_amount_not_set(self):
        today = timezone.now().date()

        payment_schedule = create_payment_schedule()

        with self.assertRaises(
            ValueError,
            msg="ved en betalt betaling skal alle betalingsfelter sættes",
        ):
            create_payment(
                payment_schedule=payment_schedule,
                date=date(year=2019, month=1, day=1),
                amount=Decimal("500.0"),
                paid=True,
                paid_date=today,
            )

    def test_save_is_paid_paid_not_set(self):
        today = timezone.now().date()

        payment_schedule = create_payment_schedule()

        with self.assertRaises(
            ValueError,
            msg="En betaling kan kun betales hvis dens aktivitet er bevilget",
        ):
            create_payment(
                payment_schedule=payment_schedule,
                date=date(year=2019, month=1, day=1),
                amount=Decimal("500.0"),
                paid_date=today,
                paid_amount=Decimal("500"),
            )

    def test_save_is_paid_with_schedule_not_allowing(self):
        today = timezone.now().date()

        payment_schedule = create_payment_schedule()

        with self.assertRaises(ValueError):
            create_payment(
                payment_schedule=payment_schedule,
                date=date(year=2019, month=1, day=1),
                amount=Decimal("500.0"),
                paid=True,
                paid_date=today,
                paid_amount=Decimal("500"),
            )

    def test_payment_str(self):
        payment_schedule = create_payment_schedule()
        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
            amount=Decimal("500.0"),
            payment_method=SD,
            recipient_type=PaymentSchedule.PERSON,
        )
        self.assertEqual(str(payment), "Person - Test - 2019-01-01 - 500.0")


class PaymentMethodDetailsTestCase(TestCase):
    def test_str(self):
        pmd = PaymentMethodDetails.objects.create(tax_card="MAIN_CARD")
        self.assertEqual(str(pmd), "Hovedkort")


class PaymentScheduleTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

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
            (
                PaymentSchedule.MONTHLY,
                date(year=2020, month=1, day=31),
                date(year=2022, month=1, day=1),
                24,
            ),
            (
                PaymentSchedule.MONTHLY,
                date(year=2020, month=1, day=1),
                date(year=2020, month=3, day=31),
                3,
            ),
        ]
    )
    def test_create_rrule_frequency(self, frequency, start, end, expected):
        payment_schedule = create_payment_schedule(payment_frequency=frequency)
        rrule = payment_schedule.create_rrule(start=start, until=end)

        self.assertEqual(len(list(rrule)), expected)

    def test_create_rrule_one_time_1_day(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_date=date.today(),
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            until=date(year=2019, month=2, day=1),
        )

        self.assertEqual(len(list(rrule)), 1)
        self.assertEqual(list(rrule)[0].date(), date.today())

    def test_create_rrule_incorrect_frequency(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency="incorrect frequency",
        )

        with self.assertRaises(ValueError):
            payment_schedule.create_rrule(
                start=date(year=2019, month=1, day=1),
                until=date(year=2019, month=2, day=1),
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
        ]
    )
    def test_calculate_per_payment_amount_for_fixed_price(
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
        today = date.today()
        end = today + timedelta(days=365)
        rrule_frequency = payment_schedule.create_rrule(today, until=end)
        price_date = list(rrule_frequency)[0]
        amount = payment_schedule.calculate_per_payment_amount(
            vat_factor, price_date
        )

        self.assertEqual(amount, expected)

    def test_calculate_per_payment_amount_no_activity(self):
        payment_type = PaymentSchedule.INDIVIDUAL_PAYMENT
        payment_frequency = PaymentSchedule.DAILY
        payment_units = 5

        payment_schedule = create_payment_schedule(
            payment_amount=Decimal(0),
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_units=payment_units,
        )
        payment_schedule.activity = None
        self.assertEqual(payment_schedule.per_payment_amount, Decimal("0"))

    def test_calculate_per_payment_amount_for_perunit_price(self):
        payment_type = PaymentSchedule.RUNNING_PAYMENT
        payment_frequency = PaymentSchedule.DAILY
        price_per_unit = Decimal(199)
        payment_units = 5
        vat_factor = 100
        expected = Decimal(5 * 199)

        payment_schedule = create_payment_schedule(
            payment_amount=None,
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_units=payment_units,
            payment_cost_type=PaymentSchedule.PER_UNIT_PRICE,
        )
        payment_schedule.price_per_unit = Price.objects.create()
        payment_schedule.price_per_unit.set_rate_amount(price_per_unit)
        today = date.today()
        end = today + timedelta(days=365)
        rrule_frequency = payment_schedule.create_rrule(today, until=end)
        price_date = list(rrule_frequency)[0]

        amount = payment_schedule.calculate_per_payment_amount(
            vat_factor, price_date
        )

        self.assertEqual(amount, expected)

    def test_calculate_per_payment_amount_for_rate(self):
        payment_type = PaymentSchedule.RUNNING_PAYMENT
        payment_frequency = PaymentSchedule.DAILY
        price_per_unit = Decimal(237)
        payment_units = 5
        vat_factor = 100
        expected = Decimal(5 * 237)
        rate = create_rate()
        rate.set_rate_amount(price_per_unit)

        payment_schedule = create_payment_schedule(
            payment_amount=None,
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_units=payment_units,
            payment_cost_type=PaymentSchedule.GLOBAL_RATE_PRICE,
            payment_rate=rate,
        )

        today = date.today()
        end = today + timedelta(days=365)
        rrule_frequency = payment_schedule.create_rrule(today, until=end)
        price_date = list(rrule_frequency)[0]

        amount = payment_schedule.calculate_per_payment_amount(
            vat_factor, price_date
        )

        self.assertEqual(amount, expected)

    def test_calculate_per_payment_amount_for_undefined_rate(self):
        payment_type = PaymentSchedule.RUNNING_PAYMENT
        payment_frequency = PaymentSchedule.DAILY
        price_per_unit = Decimal(237)
        payment_units = 5
        vat_factor = 100
        expected = Decimal(0)
        rate = create_rate()
        today = date.today()
        tomorrow = today + timedelta(days=1)
        rate.set_rate_amount(
            price_per_unit, start_date=today, end_date=tomorrow
        )

        payment_schedule = create_payment_schedule(
            payment_amount=None,
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_units=payment_units,
            payment_cost_type=PaymentSchedule.GLOBAL_RATE_PRICE,
            payment_rate=rate,
        )

        start_date = today + timedelta(days=3)
        end = today + timedelta(days=365)
        rrule_frequency = payment_schedule.create_rrule(start_date, until=end)
        price_date = list(rrule_frequency)[0]

        amount = payment_schedule.calculate_per_payment_amount(
            vat_factor, price_date
        )

        self.assertEqual(amount, expected)

    def test_rate_or_price_amount(self):
        payment_type = PaymentSchedule.RUNNING_PAYMENT
        payment_frequency = PaymentSchedule.DAILY
        price_per_unit = Decimal(237)
        payment_units = 5
        rate = create_rate()
        today = date.today()
        tomorrow = today + timedelta(days=1)
        rate.set_rate_amount(
            price_per_unit, start_date=today, end_date=tomorrow
        )

        payment_schedule = create_payment_schedule(
            payment_amount=None,
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_units=payment_units,
            payment_cost_type=PaymentSchedule.GLOBAL_RATE_PRICE,
            payment_rate=rate,
        )

        self.assertEqual(payment_schedule.rate_or_price_amount, Decimal(237))
        payment_schedule = create_payment_schedule(
            payment_amount=None,
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_units=payment_units,
            payment_cost_type=PaymentSchedule.PER_UNIT_PRICE,
        )
        payment_schedule.price_per_unit = Price.objects.create()
        payment_schedule.price_per_unit.set_rate_amount(Decimal(10))
        self.assertEqual(payment_schedule.rate_or_price_amount, Decimal(10))
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(case=case, appropriation=appropriation)
        payment_schedule.activity = activity
        self.assertEqual(payment_schedule.rate_or_price_amount, Decimal(10))

        payment_schedule = create_payment_schedule(
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_amount=Decimal(10),
            payment_units=payment_units,
        )
        self.assertEqual(payment_schedule.rate_or_price_amount, 0)

    def test_datetime_in_set_rate_amount(self):
        rate = create_rate()
        date1 = datetime.today()
        date2 = datetime.today() + timedelta(days=1)
        rate.set_rate_amount(Decimal(100), start_date=date1, end_date=date2)
        self.assertEqual(rate.get_rate_amount(date1), Decimal(100))

    def test_calculate_per_payment_amount_invalid_payment_type(self):
        payment_schedule = create_payment_schedule(
            payment_type="whatever",
            payment_cost_type="ugyldig betalingstype",
            payment_frequency=PaymentSchedule.DAILY,
        )

        payment_schedule.calculate_per_payment_amount(
            vat_factor=Decimal("100"), date=date.today()
        )

    @parameterized.expand(
        [
            (PaymentSchedule.INTERNAL, CASH),
            (PaymentSchedule.INTERNAL, SD),
            (PaymentSchedule.INTERNAL, INVOICE),
            (PaymentSchedule.PERSON, INTERNAL),
            (PaymentSchedule.PERSON, INVOICE),
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

    def test_generate_payments_with_monthly_date(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
            payment_day_of_month=31,
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2020, month=1, day=1)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 12)

    def test_generate_payments_no_end_date(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=now.year, month=1, day=1)
        # Start in January and no end should generate 25 monthly payments
        # (till end of next year)
        payment_schedule.generate_payments(start_date, None)

        self.assertIsNotNone(payment_schedule.payments)
        self.assertEqual(payment_schedule.payments.count(), 24)

    def test_generate_payments_individual_payment(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT,
            payment_frequency=None,
            payment_amount=None,
            payment_cost_type=None,
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=1, day=10)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 0)

    def test_synchronize_payments_no_end_needs_further_payments(self):
        # Test the case where end is unbounded and payments are generated till
        # end of next year then middle of next year is reached
        # and new payments should be generated once again
        now = timezone.now()
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=now.year, month=1, day=1)
        end_date = None
        # Initial call to generate payments will generate 24 payments.
        payment_schedule.generate_payments(start_date, end_date)
        self.assertEqual(len(payment_schedule.payments.all()), 24)

        # Now we are in the future and we need to generate new payments
        # because end is still unbounded
        with mock.patch("core.models.date") as date_mock:
            date_mock.today.return_value = date(
                year=now.year + 1, month=7, day=1
            )
            date_mock.max.month = 12
            date_mock.max.day = 31
            payment_schedule.synchronize_payments(start_date, end_date)
        self.assertEqual(payment_schedule.payments.count(), 36)

    def test_synchronize_payments_new_end_date_in_past(self):
        # Test the case where we generate payments for an unbounded end
        # and next the end is set so we need to delete some generated payments.
        now = timezone.now()
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=now.year, month=1, day=1)
        end_date = None

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=now.year, month=6, day=1)
        payment_schedule.synchronize_payments(start_date, new_end_date)

        self.assertEqual(payment_schedule.payments.count(), 6)

    def test_synchronize_payments_new_end_date_in_future(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=now.year, month=1, day=1)
        end_date = None

        # Generate payments till first of december next year.
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=now.year + 2, month=2, day=1)
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

    def test_synchronize_payments_individual_payment(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.INDIVIDUAL_PAYMENT,
            payment_frequency=None,
            payment_amount=None,
            payment_cost_type=None,
        )
        # No payments should be generated whatsoever.
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 0)

        # No payments should be synchronized either.
        end_date = date(year=2019, month=4, day=1)
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 0)

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

    def test_payment_schedule_save_generates_payment_id(self):
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )

        self.assertEqual(payment_schedule.payment_id, payment_schedule.id)

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
        case = create_case(self.case_worker, self.municipality, self.district)

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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        case = create_case(self.case_worker, self.municipality, self.district)
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
        case = create_case(self.case_worker, self.municipality, self.district)

        self.assertFalse(case.expired)

    def test_expired_multiple_main_activities(self):
        now = timezone.now()
        start_date = date(year=now.year, month=1, day=1)
        end_date = now.date() - timedelta(days=3)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(self.case_worker, self.municipality, self.district)
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


class SectionInfoTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        details = create_activity_details()
        section = create_section()
        section_info = create_section_info(details, section)

        self.assertEqual(str(section_info), f"{details} - {section}")

    def test_get_main_activity_main_account_number(self):
        details = create_activity_details()
        section = create_section()
        section_info = create_section_info(
            details, section, main_activity_main_account_number="1234"
        )

        self.assertEqual(
            section_info.get_main_activity_main_account_number(), "1234"
        )

    def test_get_supplementary_activity_main_account_number_default(self):
        details = create_activity_details()
        section = create_section()
        section_info = create_section_info(
            details,
            section,
            main_activity_main_account_number="1234",
            supplementary_activity_main_account_number="5678",
        )

        self.assertEqual(
            section_info.get_supplementary_activity_main_account_number(),
            "5678",
        )

    def test_get_supplementary_activity_main_account_number_main(self):
        details = create_activity_details()
        section = create_section()
        section_info = create_section_info(
            details,
            section,
            main_activity_main_account_number="1234",
            supplementary_activity_main_account_number="",
        )

        self.assertEqual(
            section_info.get_supplementary_activity_main_account_number(),
            "1234",
        )

    def test_duplicate_activity_details_section_disallowed(self):
        details = create_activity_details()
        section = create_section()
        create_section_info(details, section)
        with self.assertRaises(IntegrityError):
            create_section_info(details, section)


class RelatedPersonTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        related_person = create_related_person(case)
        self.assertEqual(
            str(related_person),
            f"{related_person.name} - "
            f"{related_person.cpr_number} - "
            f"{related_person.main_case}",
        )


class EffortStepTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        effort_step = EffortStep.objects.create(name="Name", number=127)

        self.assertEqual(str(effort_step), "Name")


class TargetGroupTestCase(TestCase):
    def test_str(self):
        target_group = create_target_group(
            name="familieafdelingen", required_fields_for_case="district"
        )
        self.assertEqual(str(target_group), "familieafdelingen")

    def test_get_required_fields_for_case(self):
        target_group = create_target_group(
            name="familieafdelingen", required_fields_for_case="district"
        )

        self.assertEqual(
            target_group.get_required_fields_for_case(), ["district"]
        )

    def test_get_required_fields_for_case_empty(self):
        target_group = create_target_group(
            name="familieafdelingen", required_fields_for_case=""
        )

        self.assertEqual(target_group.get_required_fields_for_case(), [])


class InternalPaymentRecipientTestCase(TestCase):
    def test_str(self):
        internal_payment_recipient = InternalPaymentRecipient.objects.create(
            name="Familiehuset"
        )

        self.assertEqual(str(internal_payment_recipient), "Familiehuset")


class EffortTestCase(TestCase):
    def test_str(self):
        effort = Effort.objects.create(name="Integrationsindsatsen")

        self.assertEqual(str(effort), "Integrationsindsatsen")


class VariableRateTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        variable_rate = create_variable_rate()
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        create_rate_per_date(
            variable_rate, rate=100, start_date=today, end_date=tomorrow
        )

        self.assertEqual(str(variable_rate), f"{today}, {tomorrow}: 100.00")


class RateTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        rate = create_rate()
        rate.set_rate_amount(Decimal(25), start_date=date.today())

        self.assertEqual(rate.rate_amount, Decimal(25))

        self.assertEqual(str(rate), f"{rate.name}")

        tomorrow = date.today() + timedelta(days=1)
        next_week = date.today() + timedelta(days=7)

        rate.set_rate_amount(
            Decimal(30),
            start_date=tomorrow,
            end_date=next_week - timedelta(days=1),
        )
        self.assertEqual(
            rate.get_rate_amount(rate_date=next_week), Decimal(25)
        )

    def test_start_minus_inf(self):
        rate = create_rate()
        rate.set_rate_amount(Decimal(25))

    def test_start_after_end(self):
        rate = create_rate()
        next_week = date.today() + timedelta(days=7)
        with self.assertRaises(
            ValueError, msg="Slutdato skal være mindre end startdato"
        ):
            rate.set_rate_amount(
                Decimal(25), start_date=next_week, end_date=date.today()
            )

    def test_start_rate_updated(self):
        rate = create_rate()
        today = date.today()
        yesterday = today - timedelta(days=1)

        rate.set_rate_amount(Decimal(10), start_date=None, end_date=None)
        rate.set_rate_amount(Decimal(20), start_date=today, end_date=None)

        self.assertEqual(rate.get_rate_amount(yesterday), Decimal(10))
        self.assertEqual(rate.get_rate_amount(today), Decimal(20))

    def test_needs_recalculation(self):
        rate = create_rate()

        self.assertFalse(rate.needs_recalculation)

        rate.set_rate_amount(Decimal(10), start_date=None, end_date=None)
        self.assertTrue(rate.needs_recalculation)


class RatePerDateTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        rate = create_rate(name="test rate")
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        rate_per_date = create_rate_per_date(
            rate, rate=100, start_date=today, end_date=tomorrow
        )

        self.assertEqual(str(rate_per_date), f"100 - {today} - {tomorrow}")


class PaymentDateExclusionTestCase(TestCase):
    def test_str(self):
        payment_date_exclusion = create_payment_date_exclusion()

        self.assertEqual(str(payment_date_exclusion), str(date.today()))


class AccountAliasTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_str(self):
        section = create_section()
        activity_details = create_activity_details()
        section_info = create_section_info(activity_details, section)
        account_alias = create_account_alias(section_info, activity_details)

        self.assertEqual(
            str(account_alias), f"{section_info} - {activity_details}"
        )
