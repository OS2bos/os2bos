from unittest import mock
from datetime import datetime, date, timedelta

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from django.db import IntegrityError
from django.db.utils import OperationalError
from django.core import mail

from freezegun import freeze_time

from core.models import (
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    STATUS_GRANTED,
    STATUS_EXPECTED,
    PaymentSchedule,
    ActivityDetails,
    Account,
    ServiceProvider,
    Section,
)
from core.tests.testing_utils import (
    BasicTestMixin,
    create_payment_schedule,
    create_payment,
    create_case,
    create_appropriation,
    create_activity,
    create_section,
)


class TestMarkFictivePaymentsPaid(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_mark_fictive_payments_paid(self):
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
        payment_schedule = create_payment_schedule(
            activity=activity, fictive=True
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
        payment_schedule = create_payment_schedule(
            fictive=True, activity=activity
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        # Should generate payments to 2019-12-01.
        with freeze_time("2018-01-01"):
            activity = create_activity(
                case=case,
                appropriation=appropriation,
                activity_type=MAIN_ACTIVITY,
                status=STATUS_GRANTED,
                start_date=date(year=2018, month=1, day=1),
                end_date=None,
            )
            payment_schedule = create_payment_schedule(
                payment_frequency=PaymentSchedule.MONTHLY,
                payment_type=PaymentSchedule.RUNNING_PAYMENT,
                activity=activity,
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

    @override_settings(INITIALIZE_DATABASE=True)
    @mock.patch("core.management.commands.initialize_database.initialize")
    def test_ensure_db_connection_success_and_initialize(self, initialize_mock):
        # default settings should be able to connect to a database.
        with self.assertRaises(SystemExit) as cm:
            call_command("ensure_db_connection")
        self.assertEqual(cm.exception.code, 0)
        self.assertTrue(initialize_mock.called)

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

    def test_ensure_db_connection_fail_with_wait(self):
        # Mock the ensure_connection method to raise an OperationalError.
        db_mock = mock.MagicMock()
        db_mock.ensure_connection.side_effect = OperationalError
        db_dict = {"default": db_mock}

        with mock.patch(
            "core.management.commands.ensure_db_connection.connections",
            db_dict,
        ):
            with self.assertRaises(SystemExit) as cm:
                call_command("ensure_db_connection", "--wait=2")

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

    def test_send_expired_emails_success(self):
        today = timezone.now().date()

        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        # Only created email should be sent initially.
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Aktivitet oprettet")

        call_command("send_expired_emails")
        # Then expired email.
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Aktivitet udgået")

    def test_send_expired_emails_doesnt_trigger_email(self):
        today = timezone.now().date()

        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
        )

        call_command("send_expired_emails")
        # No emails should be sent.
        self.assertEqual(len(mail.outbox), 0)


class TestExportToPrism(TestCase):
    @mock.patch("core.management.commands.export_to_prism.logger")
    @mock.patch(
        "core.management.commands.export_to_prism."
        "export_prism_payments_for_date"
    )
    def test_export_to_prism_success(
        self, export_prism_payments_mock, logger_mock
    ):
        export_prism_payments_mock.return_value = None

        call_command("export_to_prism")

        export_prism_payments_mock.assert_called_with(None)
        logger_mock.info.assert_called_with(
            "No records found for export to PRISME."
        )

    @mock.patch(
        "core.management.commands.export_to_prism."
        "export_prism_payments_for_date"
    )
    def test_export_to_prism_success_with_date(
        self, export_prism_payments_mock
    ):
        yesterday = timezone.now() - timedelta(days=1)
        call_command(
            "export_to_prism", "--date=" + yesterday.strftime("%Y%m%d")
        )

        export_prism_payments_mock.assert_called_with(
            datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0)
        )

    @mock.patch("core.management.commands.export_to_prism.os")
    @mock.patch("core.management.commands.export_to_prism.logger")
    @mock.patch(
        "core.management.commands.export_to_prism."
        "export_prism_payments_for_date"
    )
    def test_export_to_prism_success_with_file(
        self, export_prism_payments_mock, logger_mock, os_mock
    ):
        os_mock.path.isfile.return_value = True
        export_prism_payments_mock.return_value = "/test/path"

        call_command("export_to_prism")

        logger_mock.info.assert_called_with(
            "Success: PRISME records were exported to /test/path"
        )

    @mock.patch("core.management.commands.export_to_prism.os")
    @mock.patch("core.management.commands.export_to_prism.logger")
    @mock.patch(
        "core.management.commands.export_to_prism."
        "export_prism_payments_for_date"
    )
    def test_export_to_prism_error_invalid_filepath(
        self, export_prism_payments_mock, logger_mock, os_mock
    ):
        os_mock.path.isfile.return_value = False
        export_prism_payments_mock.return_value = "/test/path"

        call_command("export_to_prism")

        logger_mock.error.assert_called_with(
            "Export of records to PRISME failed!"
        )

    @mock.patch("core.management.commands.export_to_prism.logger")
    @mock.patch(
        "core.management.commands.export_to_prism."
        "export_prism_payments_for_date"
    )
    def test_export_to_prism_error_invalid_date(
        self, export_prism_payments_mock, logger_mock
    ):
        with self.assertRaises(SystemExit) as cm:
            call_command("export_to_prism", "--date=wrong_date")
            self.assertEqual(cm.code, 1)

        export_prism_payments_mock.assert_not_called()
        logger_mock.error.assert_called_with(
            "Invalid date input wrong_date - should parse as 'YYYYMMDD'"
        )

    @mock.patch("core.management.commands.export_to_prism.logger")
    @mock.patch(
        "core.management.commands.export_to_prism."
        "export_prism_payments_for_date"
    )
    def test_export_to_prism_error_failed_export(
        self, export_prism_payments_mock, logger_mock
    ):
        export_prism_payments_mock.side_effect = OSError("test")

        call_command("export_to_prism")

        logger_mock.exception.assert_called_with(
            "An exception occurred during export to PRISME"
        )


class TestGeneratePaymentsReports(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    @override_settings(PAYMENTS_REPORT_DIR="/tmp/")
    @mock.patch("core.management.commands.generate_payments_report.logger")
    def test_generate_payments_report_success(self, logger_mock):
        section = create_section()

        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case, section=section)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=2, day=1),
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        another_activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_EXPECTED,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=2, day=1),
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=another_activity,
        )

        call_command("generate_payments_report")

        logger_mock.info.assert_has_calls(
            [
                mock.call("Created granted payments report for 2 payments"),
                mock.call(
                    "Created expected payments report for 4 expected payments"
                ),
            ]
        )

    @override_settings(PAYMENTS_REPORT_DIR="/tmp/")
    @mock.patch("core.management.commands.generate_payments_report.logger")
    def test_generate_payments_report_no_payments(self, logger_mock):

        call_command("generate_payments_report")

        logger_mock.info.assert_not_called()
        logger_mock.exception.assert_not_called()

    @override_settings(PAYMENTS_REPORT_DIR="/invalid_dir/")
    @mock.patch("core.management.commands.generate_payments_report.logger")
    def test_generate_payments_report_exception_raised(self, logger_mock):

        call_command("generate_payments_report")

        logger_mock.exception.assert_called_with(
            "An error occurred during generation of payments reports"
        )


class TestImportActivityDetails(TestCase):
    def test_import_activity_details(self):
        self.assertEqual(ActivityDetails.objects.count(), 0)

        # Import sections first which are used when importing activity details.
        call_command("import_sections")
        call_command("import_activity_details")

        self.assertEqual(ActivityDetails.objects.count(), 82)

    def test_import_activity_details_with_path(self):
        self.assertEqual(ActivityDetails.objects.count(), 0)

        # CSV data with headers and a single activity details entry.
        csv_data = (
            "Aktivitet,Aktivitetnavn,Tollerance,MaxAfvigelse,"
            "Hovedaktivitet på,Følgeudgift på ,Kle nr.,SBSYS id,"
            "Hovedaktivitet,Hovedaktivitetsnavn,Kont1,Konto2,Konto3,"
            "Kontering,PGF betegnelse,Helle,Kolonne1,Leif\n"
            "015031,Soc.pæd. opholdssteder,10%,5000,SEL-52-3.7,,"
            "27.27.42,882,, ,528201003,,15031,528201003-15031,"
            "SEL-52-3.7 Anbringelse udenfor hjemmet,,,\n"
        )
        open_mock = mock.mock_open(read_data=csv_data)

        with mock.patch(
            "core.management.commands.import_activity_details.open", open_mock
        ):
            call_command("import_activity_details", "--path=/tmp/test")

        open_mock.assert_called_with("/tmp/test")
        self.assertEqual(ActivityDetails.objects.count(), 1)

    def test_import_activity_details_with_invalid_main_activity(self):
        self.assertEqual(ActivityDetails.objects.count(), 0)

        # CSV data with headers and a single activity details entry.
        csv_data = (
            # Headers.
            "Aktivitet,Aktivitetnavn,Tollerance,MaxAfvigelse,"
            "Hovedaktivitet på,Følgeudgift på ,Kle nr.,SBSYS id,"
            "Hovedaktivitet,Hovedaktivitetsnavn,Kont1,Konto2,Konto3,"
            "Kontering,PGF betegnelse,Helle,Kolonne1,Leif\n"
            # 1st entry.
            "015031,Soc.pæd. opholdssteder,10%,5000,SEL-52-3.7,,"
            "27.27.42,882,, ,528201003,,15031,528201003-15031,"
            "SEL-52-3.7 Anbringelse udenfor hjemmet,,,\n"
            # 2nd entry with invalid main activity id 015033.
            "015032,Soc.pæd. opholdssteder,10%,5000,,SEL-52-3.7,"
            "27.27.42,882,015033,000000,528201003,,15031,528201003-15031,"
            "SEL-52-3.7 Anbringelse udenfor hjemmet,,,\n"
        )
        open_mock = mock.mock_open(read_data=csv_data)

        with mock.patch(
            "core.management.commands.import_activity_details.open", open_mock
        ):
            call_command("import_activity_details", "--path=/tmp/test")

        self.assertEqual(ActivityDetails.objects.count(), 2)

    @mock.patch(
        "core.management.commands.import_activity_details.ActivityDetails"
    )
    def test_import_activity_details_exception_raised(self, details_mock):
        self.assertEqual(ActivityDetails.objects.count(), 0)

        details_mock.objects.update_or_create.side_effect = IntegrityError()

        call_command("import_activity_details")

        self.assertEqual(ActivityDetails.objects.count(), 0)


class TestImportAccounts(TestCase):
    def test_import_accounts(self):
        # The import_accounts script requires activity details and sections
        # to have been populated first.
        call_command("import_sections")
        call_command("import_activity_details")

        self.assertEqual(Account.objects.count(), 0)

        call_command("import_accounts")

        self.assertEqual(Account.objects.count(), 870)

    def test_import_accounts_with_path(self):
        call_command("import_sections")
        call_command("import_activity_details")

        self.assertEqual(Account.objects.count(), 0)

        csv_data = (
            # Headers.
            "Aktivitet,Aktivitetnavn,Tollerance,MaxAfvigelse,"
            "Hovedaktivitet på,Følgeudgift på ,Kle nr.,SBSYS id,"
            "Hovedaktivitet,Hovedaktivitetsnavn,Kont1,Konto2,Konto3,"
            "Kontering,PGF betegnelse,Helle,Kolonne1,Leif\n"
            # 1st entry.
            "015031,Soc.pæd. opholdssteder,10%,5000,SEL-52-3.7,,27.27.42,"
            "882,, ,528201003,,15031,528201003-15031,"
            "SEL-52-3.7 Anbringelse udenfor hjemmet,,,\n"
        )
        open_mock = mock.mock_open(read_data=csv_data)
        with mock.patch(
            "core.management.commands.import_accounts.open", open_mock
        ):
            call_command("import_accounts", "--path=/tmp/test")

        open_mock.assert_called_with("/tmp/test")
        self.assertEqual(Account.objects.count(), 1)

    def test_import_accounts_no_activity_id(self):
        call_command("import_sections")
        call_command("import_activity_details")

        self.assertEqual(Account.objects.count(), 0)

        csv_data = (
            # Headers.
            "Aktivitet,Aktivitetnavn,Tollerance,MaxAfvigelse,"
            "Hovedaktivitet på,Følgeudgift på ,Kle nr.,SBSYS id,"
            "Hovedaktivitet,Hovedaktivitetsnavn,Kont1,Konto2,Konto3,"
            "Kontering,PGF betegnelse,Helle,Kolonne1,Leif\n"
            # Entry with no activity id.
            ",Soc.pæd. opholdssteder,10%,5000,SEL-52-3.7,,27.27.42,"
            "882,, ,528201003,,15031,528201003-15031,"
            "SEL-52-3.7 Anbringelse udenfor hjemmet,,,\n"
        )
        open_mock = mock.mock_open(read_data=csv_data)
        with mock.patch(
            "core.management.commands.import_accounts.open", open_mock
        ):
            call_command("import_accounts")

        self.assertEqual(Account.objects.count(), 0)

    def test_import_accounts_no_activity_details(self):
        call_command("import_sections")
        # Don't import activity details to hit DoesNotExist cases.

        self.assertEqual(Account.objects.count(), 0)

        call_command("import_accounts")

        self.assertEqual(Account.objects.count(), 0)


class TestImportServiceProviders(TestCase):
    def test_import_service_providers(self):
        self.assertEqual(ServiceProvider.objects.count(), 0)

        call_command("import_service_providers")

        self.assertEqual(ServiceProvider.objects.count(), 422)

    def test_import_service_providers_with_path(self):
        self.assertEqual(ServiceProvider.objects.count(), 0)

        # CSV data with headers and a single service provider entry.
        csv_data = (
            "CVR,Firma,Akiv,Type,Postnummer,Momsfaktor,Afdeling\n"
            '12345678,Testhus,07/16/2018,Opholdssted,4300,"95,4%",01008\n'
        )
        open_mock = mock.mock_open(read_data=csv_data)

        with mock.patch(
            "core.management.commands.import_service_providers.open", open_mock
        ):
            call_command("import_service_providers", "--path=/tmp/test")

        open_mock.assert_called_with("/tmp/test")
        self.assertEqual(ServiceProvider.objects.count(), 1)


class TestImportSections(TestCase):
    def test_import_sections(self):
        self.assertEqual(Section.objects.count(), 0)

        call_command("import_sections")

        self.assertEqual(Section.objects.count(), 146)

    def test_import_sections_with_path(self):
        self.assertEqual(Section.objects.count(), 0)

        # CSV data with headers and a single section entry.
        csv_data = (
            "Lgl,Paragraf,Stykke,Nøgle,B&V-tekst,Betegnelse,KLE nr.,"
            "SBSYS KLE nr.,SBSYS skabelonid.,KMD Sag-tekst,Afsnit,"
            "Indsatstrappen,Målgruppe,Kolonne1\nSEL,10,,SEL-10,"
            '"Rådgivning, kommunal","SEL-10 Rådgivning,'
            'kommunal",27.12.04,,,"Rådgivning, enhver",Kommunens rådgivning'
            ",,,\n"
        )
        open_mock = mock.mock_open(read_data=csv_data)

        with mock.patch(
            "core.management.commands.import_sections.open", open_mock
        ):
            call_command("import_sections", "--path=/tmp/test")

        open_mock.assert_called_with("/tmp/test")
        self.assertEqual(Section.objects.count(), 1)
