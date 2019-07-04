from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from core.tests.testing_utils import create_payment_schedule, create_payment
from core.models import Payment


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
