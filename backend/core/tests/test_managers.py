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

    def test_amount_sum(self):
        payment_schedule = create_payment_schedule()
        create_payment(payment_schedule, amount=Decimal("1000"))
        create_payment(payment_schedule, amount=Decimal("100"))
        create_payment(payment_schedule, amount=Decimal("50"))

        self.assertEqual(Payment.objects.amount_sum(), Decimal("1150"))

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
