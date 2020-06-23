# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from core.tests.testing_utils import (
    create_payment,
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_payment_schedule,
    create_activity,
)
from core.models import (
    Payment,
    PaymentSchedule,
    Case,
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    STATUS_GRANTED,
    Activity,
    Appropriation,
)


class PaymentQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_in_this_year_true(self):
        payment_schedule = create_payment_schedule()
        payment = create_payment(payment_schedule)
        self.assertIn(payment, Payment.objects.in_this_year())

    def test_in_this_year_false(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule()
        payment = create_payment(
            payment_schedule, date=date(year=now.year - 1, month=1, day=1)
        )

        self.assertNotIn(payment, Payment.objects.in_this_year())

    def test_in_this_year_true_paid_date(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()
        payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=31),
            paid_date=date(year=now.year, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        self.assertIn(payment, Payment.objects.in_this_year())

    def test_paid_date_or_date_gte(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()

        # should be included
        paid_date_gte_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=29),
            paid_date=date(year=now.year, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should be included
        date_gte_payment = create_payment(
            payment_schedule, date=date(year=now.year, month=1, day=1)
        )

        # should not be included
        paid_date_lt_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=30),
            paid_date=date(year=now.year - 1, month=12, day=31),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should not be included
        date_lt_payment = create_payment(
            payment_schedule, date=date(year=now.year - 1, month=12, day=31)
        )

        self.assertIn(
            paid_date_gte_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertIn(
            date_gte_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )
        self.assertNotIn(
            paid_date_lt_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertNotIn(
            date_lt_payment,
            Payment.objects.paid_date_or_date_gte(
                date(year=now.year, month=1, day=1)
            ),
        )

    def test_paid_date_or_date_lte(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()

        # should be included
        paid_date_lte_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=29),
            paid_date=date(year=now.year, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should be included
        date_lte_payment = create_payment(
            payment_schedule, date=date(year=now.year, month=1, day=1)
        )

        # should not be included
        paid_date_gt_payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=30),
            paid_date=date(year=now.year, month=1, day=2),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        # should not be included
        date_gt_payment = create_payment(
            payment_schedule, date=date(year=now.year, month=1, day=2)
        )

        self.assertIn(
            paid_date_lte_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertIn(
            date_lte_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )
        self.assertNotIn(
            paid_date_gt_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )

        self.assertNotIn(
            date_gt_payment,
            Payment.objects.paid_date_or_date_lte(
                date(year=now.year, month=1, day=1)
            ),
        )

    def test_in_this_year_false_paid_date(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        payment_schedule = create_payment_schedule(activity=activity)

        now = timezone.now()
        payment = create_payment(
            payment_schedule,
            date=date(year=now.year, month=1, day=1),
            paid_date=date(year=now.year - 1, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        self.assertNotIn(payment, Payment.objects.in_this_year())

    def test_amount_sum(self):
        now = timezone.now()

        payment_schedule = create_payment_schedule()
        create_payment(
            payment_schedule,
            amount=Decimal("1000"),
            date=date(year=now.year, month=1, day=1),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("100"),
            date=date(year=now.year, month=1, day=2),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("50"),
            date=date(year=now.year, month=1, day=3),
        )

        self.assertEqual(Payment.objects.amount_sum(), Decimal("1150"))

    def test_amount_sum_paid_amount_overrides(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # Default 10 days of 500DKK.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        # mark last payment paid with 1000.
        last_payment = Payment.objects.last()
        last_payment.paid = True
        last_payment.paid_date = date(year=2019, month=1, day=10)
        last_payment.paid_amount = Decimal(1000)
        last_payment.save()

        self.assertEqual(Payment.objects.amount_sum(), Decimal("5500"))

    def test_strict_amount_sum_paid_amount_does_not_override(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # Default 10 days of 500DKK.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity)

        # mark last payment paid with 700.
        last_payment = Payment.objects.last()
        last_payment.paid = True
        last_payment.paid_date = date(year=2019, month=1, day=10)
        last_payment.paid_amount = Decimal(700)
        last_payment.save()

        self.assertEqual(Payment.objects.strict_amount_sum(), Decimal("5000"))

    def test_group_by_monthly_amounts(self):
        payment_schedule = create_payment_schedule()
        create_payment(
            payment_schedule,
            amount=Decimal("1000"),
            date=date(year=2019, month=1, day=1),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("100"),
            date=date(year=2019, month=2, day=1),
        )
        create_payment(
            payment_schedule,
            amount=Decimal("50"),
            date=date(year=2019, month=3, day=1),
        )

        expected = [
            {"date_month": "2019-01", "amount": Decimal("1000")},
            {"date_month": "2019-02", "amount": Decimal("100")},
            {"date_month": "2019-03", "amount": Decimal("50")},
        ]
        self.assertEqual(
            [entry for entry in Payment.objects.group_by_monthly_amounts()],
            expected,
        )

    def test_group_by_monthly_amounts_paid(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # 4 payments of 500DKK.
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2019, month=2, day=27),
            end_date=date(year=2019, month=3, day=2),
        )
        create_payment_schedule(activity=activity)
        # Mark one March payment paid with 700.
        last_payment = activity.payment_plan.payments.get(
            date=date(year=2019, month=3, day=2)
        )
        last_payment.paid = True
        last_payment.paid_date = date(year=2019, month=3, day=1)
        last_payment.paid_amount = Decimal(700)
        last_payment.save()

        # Expected are two payments in February of 500
        # and two payments in March of 500 and 700.
        expected = [
            {"date_month": "2019-02", "amount": Decimal("1000")},
            {"date_month": "2019-03", "amount": Decimal("1200")},
        ]
        self.assertCountEqual(
            [entry for entry in Payment.objects.group_by_monthly_amounts()],
            expected,
        )


class CaseQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_expired_one_expired_one_ongoing(self):
        now_date = timezone.now().date()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=3),
            end_date=now_date - timedelta(days=2),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an ongoing main activity
        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=1),
            end_date=now_date + timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=ongoing_activity,
        )
        # create a second appropriation
        appropriation = create_appropriation(case=case, sbsys_id="6521")

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=3),
            end_date=now_date - timedelta(days=2),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an ongoing main activity
        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=1),
            end_date=now_date + timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=ongoing_activity,
        )
        expired_cases = Case.objects.all().expired()
        ongoing_cases = Case.objects.all().ongoing()
        self.assertEqual(expired_cases.count(), 0)
        self.assertEqual(ongoing_cases.count(), 1)

    def test_expired_all_expired(self):
        now_date = timezone.now().date()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=4),
            end_date=now_date - timedelta(days=3),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an expired main activity
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=2),
            end_date=now_date - timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=expired_activity,
        )
        # create a second appropriation
        appropriation = create_appropriation(case=case, sbsys_id="6521")

        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=10),
            end_date=now_date - timedelta(days=9),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        # create an expired main activity
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=8),
            end_date=now_date - timedelta(days=7),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=expired_activity,
        )

        expired_cases = Case.objects.all().expired()
        ongoing_cases = Case.objects.all().ongoing()
        self.assertEqual(expired_cases.count(), 1)
        self.assertEqual(ongoing_cases.count(), 0)


class ActivityQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_expired(self):
        today = timezone.now().date()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(expired_activity, Activity.objects.all().expired())
        self.assertNotIn(ongoing_activity, Activity.objects.all().expired())

    def test_ongoing(self):
        today = timezone.now().date()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        # create an expired main activity
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertNotIn(expired_activity, Activity.objects.all().ongoing())
        self.assertIn(ongoing_activity, Activity.objects.all().ongoing())

    def test_ongoing_no_end_date(self):
        today = timezone.now().date()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        ongoing_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(ongoing_activity, Activity.objects.all().ongoing())


class AppropriationQuerySetTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_ongoing(self):
        today = timezone.now().date()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        self.assertIn(appropriation, Appropriation.objects.ongoing())

        # create an expired supplementary activity
        # but an ongoing main activity.
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(appropriation, Appropriation.objects.ongoing())

    def test_expired(self):
        today = timezone.now().date()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        self.assertNotIn(appropriation, Appropriation.objects.expired())

        # create an expired supplementary activity
        # and an expired main activity.
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=3),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )

        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=today - timedelta(days=4),
            end_date=today - timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )

        self.assertIn(appropriation, Appropriation.objects.expired())
