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
    STATUS_GRANTED,
)


class PaymentQuerySetTestCase(TestCase):
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
        now = timezone.now()
        payment_schedule = create_payment_schedule()
        payment = create_payment(
            payment_schedule,
            date=date(year=now.year - 1, month=12, day=31),
            paid_date=date(year=now.year, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        self.assertIn(payment, Payment.objects.in_this_year())

    def test_in_this_year_false_paid_date(self):
        now = timezone.now()
        payment_schedule = create_payment_schedule()
        payment = create_payment(
            payment_schedule,
            date=date(year=now.year, month=1, day=1),
            paid_date=date(year=now.year - 1, month=1, day=1),
            paid_amount=Decimal("500.0"),
            paid=True,
        )

        self.assertNotIn(payment, Payment.objects.in_this_year())

    def test_amount_sum(self):
        payment_schedule = create_payment_schedule()
        create_payment(payment_schedule, amount=Decimal("1000"))
        create_payment(payment_schedule, amount=Decimal("100"))
        create_payment(payment_schedule, amount=Decimal("50"))

        self.assertEqual(Payment.objects.amount_sum(), Decimal("1150"))

    def test_amount_sum_paid_amount_overrides(self):
        today = timezone.now().date()
        payment_schedule = create_payment_schedule()
        create_payment(payment_schedule, amount=Decimal("1000"))
        create_payment(
            payment_schedule,
            amount=Decimal("100"),
            paid_amount=Decimal("150"),
            paid=True,
            paid_date=today,
        )
        create_payment(
            payment_schedule,
            amount=Decimal("50"),
            paid_amount=Decimal("250"),
            paid=True,
            paid_date=today,
        )

        self.assertEqual(Payment.objects.amount_sum(), Decimal("1400"))

    def test_strict_amount_sum_paid_amount_does_not_override(self):
        today = timezone.now().date()
        payment_schedule = create_payment_schedule()
        create_payment(payment_schedule, amount=Decimal("1000"))
        create_payment(
            payment_schedule,
            amount=Decimal("100"),
            paid_amount=Decimal("150"),
            paid=True,
            paid_date=today,
        )
        create_payment(
            payment_schedule,
            amount=Decimal("50"),
            paid_amount=Decimal("250"),
            paid=True,
            paid_date=today,
        )

        self.assertEqual(Payment.objects.strict_amount_sum(), Decimal("1150"))

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
        payment_schedule = create_payment_schedule()
        create_payment(
            payment_schedule,
            amount=Decimal("1000"),
            paid_amount=Decimal("1200"),
            date=date(year=2019, month=1, day=1),
            paid_date=date(year=2019, month=3, day=1),
            paid=True,
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
            {"date_month": "2019-02", "amount": Decimal("100")},
            {"date_month": "2019-03", "amount": Decimal("1250")},
        ]
        self.assertEqual(
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
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=3),
            end_date=now_date - timedelta(days=2),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an ongoing main activity
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=1),
            end_date=now_date + timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            modifies=activity,
        )
        # create a second appropriation
        appropriation = create_appropriation(case=case, sbsys_id="6521")
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=3),
            end_date=now_date - timedelta(days=2),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an ongoing main activity
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=1),
            end_date=now_date + timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            modifies=activity,
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
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=4),
            end_date=now_date - timedelta(days=3),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an expired main activity
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=2),
            end_date=now_date - timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            modifies=activity,
        )
        # create a second appropriation
        appropriation = create_appropriation(case=case, sbsys_id="6521")
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an expired main activity
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=10),
            end_date=now_date - timedelta(days=9),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        # create an expired main activity
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now_date - timedelta(days=8),
            end_date=now_date - timedelta(days=7),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            modifies=activity,
        )

        expired_cases = Case.objects.all().expired()
        ongoing_cases = Case.objects.all().ongoing()
        self.assertEqual(expired_cases.count(), 1)
        self.assertEqual(ongoing_cases.count(), 0)
