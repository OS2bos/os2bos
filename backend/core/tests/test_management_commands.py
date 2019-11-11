from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models import MAIN_ACTIVITY, STATUS_GRANTED
from core.tests.testing_utils import (
    BasicTestMixin,
    create_payment_schedule,
    create_payment,
    create_case,
    create_appropriation,
    create_activity,
)


class TestMarkFictivePaymentsPaid(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_mark_fictive_payments_paid(self):
        payment_schedule = create_payment_schedule(fictive=True)
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        today = timezone.now().date()
        payment = create_payment(payment_schedule, date=today)

        call_command(
            "mark_fictive_payments_paid", "--date=" + today.strftime("%Y%m%d")
        )

        payment.refresh_from_db()
        self.assertTrue(payment.paid)
        self.assertEqual(payment.paid_date, today)
        self.assertEqual(payment.paid_amount, payment.amount)
