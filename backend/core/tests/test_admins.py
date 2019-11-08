from datetime import date

from django.test import TestCase
from django.contrib.admin.sites import AdminSite

from core.models import Payment, PaymentSchedule
from core.admin import PaymentAdmin, PaymentScheduleAdmin
from core.tests.testing_utils import create_payment, create_payment_schedule


class MockRequest:
    pass


request = MockRequest()


class TestPaymentAdmin(TestCase):
    def test_payment_id(self):
        payment_schedule = create_payment_schedule()

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
        )
        site = AdminSite()
        payment_admin = PaymentAdmin(Payment, site)
        self.assertEqual(
            payment_admin.payment_id(payment),
            payment.payment_schedule.payment_id,
        )

    def test_account_string(self):
        payment_schedule = create_payment_schedule()

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
        )
        site = AdminSite()
        payment_admin = PaymentAdmin(Payment, site)
        self.assertEqual(
            payment_admin.account_string(payment), payment.account_string
        )


class TestPaymentScheduleAdmin(TestCase):
    def test_account_string(self):
        payment_schedule = create_payment_schedule()

        site = AdminSite()
        payment_schedule_admin = PaymentScheduleAdmin(PaymentSchedule, site)
        self.assertEqual(
            payment_schedule_admin.account_string(payment_schedule),
            payment_schedule.account_string,
        )
