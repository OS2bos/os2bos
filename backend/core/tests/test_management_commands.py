from unittest import mock
from datetime import date, timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.db.utils import OperationalError
from django.core import mail

from freezegun import freeze_time

from core.models import (
    MAIN_ACTIVITY,
    STATUS_GRANTED,
    PaymentSchedule,
    ActivityDetails,
    Account,
    ServiceProvider,
    SchoolDistrict,
)
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

    def test_mark_fictive_payments_paid_no_arg(self):
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

        call_command("mark_fictive_payments_paid")

        payment.refresh_from_db()
        self.assertTrue(payment.paid)
        self.assertEqual(payment.paid_date, today)
        self.assertEqual(payment.paid_amount, payment.amount)

    @mock.patch("core.management.commands.mark_fictive_payments_paid.logger")
    def test_mark_fictive_payments_paid_wrong_date(self, logger_mock):
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

        with self.assertRaises(SystemExit):
            call_command("mark_fictive_payments_paid", "--date=wrong_date")

        payment.refresh_from_db()
        self.assertFalse(payment.paid)
        self.assertIsNone(payment.paid_date, today)
        self.assertIsNone(payment.paid_amount, payment.amount)

        self.assertTrue(logger_mock.error.called)

    @mock.patch("core.management.commands.mark_fictive_payments_paid.logger")
    @mock.patch("core.management.commands.mark_fictive_payments_paid.Payment")
    def test_mark_fictive_payments_paid_exception_raised(
        self, payment_mock, logger_mock
    ):
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

        payment_mock.objects.filter.side_effect = IntegrityError

        call_command(
            "mark_fictive_payments_paid", "--date=" + today.strftime("%Y%m%d")
        )

        payment.refresh_from_db()
        self.assertFalse(payment.paid)
        self.assertIsNone(payment.paid_date, today)
        self.assertIsNone(payment.paid_amount, payment.amount)

        self.assertTrue(logger_mock.exception.called)


class TestRenewPayments(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_renew_payments_renewed(self):
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        # Should generate payments to 2019-12-01.
        with freeze_time("2018-01-01"):
            create_activity(
                case=case,
                appropriation=appropriation,
                activity_type=MAIN_ACTIVITY,
                status=STATUS_GRANTED,
                payment_plan=payment_schedule,
                start_date=date(year=2018, month=1, day=1),
                end_date=None,
            )
        self.assertEqual(payment_schedule.payments.count(), 24)

        # Generated payments are not 6 months ahead.
        # So we generate new payments from next payment date:
        # 2020-01-01 till end of next year (2020-12-01).
        with freeze_time("2019-12-01"):
            call_command("renew_payments")

        self.assertEqual(payment_schedule.payments.count(), 36)


class TestEnsureDbConnection(TestCase):
    def test_ensure_db_connection_success(self):
        # default settings should be able to connect to a database.
        with self.assertRaises(SystemExit) as cm:
            call_command("ensure_db_connection")
        self.assertEqual(cm.exception.code, 0)

    def test_ensure_db_connection_fail(self):
        # Mock the ensure_connection method to raise an OperationalError.
        db_mock = mock.MagicMock()
        db_mock.ensure_connection.side_effect = OperationalError
        db_dict = {"default": db_mock}

        with mock.patch(
            "core.management.commands.ensure_db_connection.connections",
            db_dict,
        ):
            with self.assertRaises(SystemExit) as cm:
                call_command("ensure_db_connection")

        self.assertEqual(cm.exception.code, 1)


class TestInitializeDatabase(TestCase):
    @mock.patch("core.management.commands.initialize_database.initialize")
    def test_initialize_database(self, initialize_mock):
        # the initialize function is tested
        # in bevillingsplatform.tests.test_initialize
        # so we can simply test it is called.
        call_command("initialize_database")
        self.assertTrue(initialize_mock.called)


class TestSendExpiredEmails(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_send_expired_emails(self):
        today = timezone.now().date()
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
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
        )
        # Created email should be sent initially.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Aktivitet oprettet")

        call_command("send_expired_emails")
        # Then expired email.
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Aktivitet udgået")
