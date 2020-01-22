# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta
from decimal import Decimal
from unittest import mock

import requests
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models import (
    Activity,
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    PaymentSchedule,
    STATUS_GRANTED,
    STATUS_EXPECTED,
    CASH,
    User,
    Team,
    ActivityDetails,
    Payment,
)
from core.utils import (
    get_cpr_data,
    get_person_info,
    get_cpr_data_mock,
    send_appropriation,
    saml_before_login,
    saml_create_user,
    generate_records_for_prism,
    due_payments_for_prism,
    export_prism_payments_for_date,
    generate_payments_report_list,
    generate_granted_payments_report_list,
    generate_expected_payments_report_list,
)
from core.tests.testing_utils import (
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_activity,
    create_section,
    create_account,
    create_payment_schedule,
)


class GetCPRDataTestCase(TestCase):
    def test_get_cpr_data_empty_certificate(self):
        with self.settings(SERVICEPLATFORM_CERTIFICATE_PATH=""):
            result = get_cpr_data("1234567890")
        self.assertIsNone(result)

    @mock.patch("core.utils.os.path.isfile")
    @mock.patch("requests.post")
    def test_get_cpr_data_request_error(self, requests_mock, mock_isfile):
        mock_isfile.return_value = True
        requests_mock.side_effect = requests.exceptions.HTTPError("error")

        with self.assertLogs(level="ERROR") as log:
            result = get_cpr_data("1234567890")

            self.assertIsNone(result)
            self.assertEqual(len(log.output), 1)
            self.assertIn("get_cpr_data requests error", log.output[0])

    @mock.patch("core.utils.os.path.isfile")
    @mock.patch("core.utils.get_citizen")
    def test_get_cpr_data_success(self, get_citizen_mock, mock_isfile):
        mock_isfile.return_value = True
        result_data = {
            "fornavn": "Jens Jensner",
            "efternavn": "Jensen",
            "relationer": [{"cprnr": "0123456780", "relation": "aegtefaelle"}],
        }
        get_citizen_mock.return_value = result_data
        result = get_cpr_data("1234567890")

        self.assertEqual(result["fornavn"], "Jens Jensner")


class GetPersonInfoTestCase(TestCase):
    @mock.patch("core.utils.get_cpr_data_mock", lambda cpr: None)
    def test_get_person_info_no_response(self):
        result = get_person_info("nonexistant")
        self.assertIsNone(result)

    @mock.patch("core.utils.get_cpr_data_mock")
    def test_get_person_info_relation_lookups_fail(
        self, get_cpr_data_mock_mock
    ):
        # Make first call successful and subsequent calls return None.
        get_cpr_data_mock_mock.side_effect = [
            get_cpr_data_mock("1234567890")
        ] + [None] * 10
        result = get_person_info("1234567890")

        self.assertNotIn("adresseringsnavn", result["relationer"][0])

    def test_get_person_info_success(self):
        result = get_person_info("1234567890")

        self.assertIn("relationer", result)
        self.assertIn("adresseringsnavn", result["relationer"][0])

    @override_settings(USE_SERVICEPLATFORM=True)
    @mock.patch("core.utils.get_cpr_data")
    def test_get_person_info_get_cpr_data(self, get_cpr_data_mock):
        get_cpr_data_mock.return_value = {
            "statsborgerskab": "5100",
            "efternavn": "Jensen",
            "postdistrikt": "Næstved",
            "foedselsregistreringssted": "Myndighedsnavn for landekode: 5902",
            "boernUnder18": "false",
            "civilstandsdato": "1991-03-21+01:00",
            "adresseringsnavn": "Jens Jensner Jensen",
            "fornavn": "Jens Jensner",
            "tilflytningsdato": "2001-12-01+01:00",
            "markedsfoeringsbeskyttelse": "true",
            "vejkode": "1759",
            "standardadresse": "Sterkelsvej 17 A,2",
            "etage": "02",
            "koen": "M",
            "status": "80",
            "foedselsdato": "1978-04-27+01:00",
            "vejnavn": "Sterkelsvej",
            "statsborgerskabdato": "1991-09-23+02:00",
            "adressebeskyttelse": "false",
            "stilling": "Sygepl ske",
            "gaeldendePersonnummer": "2704785263",
            "vejadresseringsnavn": "Sterkelsvej",
            "civilstand": "G",
            "alder": "59",
            "relationer": [
                {"cprnr": "0123456780", "relation": "aegtefaelle"},
                {"cprnr": "1123456789", "relation": "barn"},
                {"cprnr": "2123456789", "relation": "barn"},
                {"cprnr": "3123456789", "relation": "barn"},
                {"cprnr": "0000000000", "relation": "mor"},
                {"cprnr": "0000000000", "relation": "far"},
            ],
            "postnummer": "4700",
            "husnummer": "017A",
            "vejviserbeskyttelse": "true",
            "kommunekode": "370",
        }
        result = get_person_info("1234567890")

        self.assertIn("relationer", result)
        self.assertIn("efternavn", result)


class SendAppropriationTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    @mock.patch("core.utils.HTML")
    @mock.patch("core.utils.EmailMessage")
    @mock.patch("core.utils.get_template")
    def test_send_appropriation(
        self, get_template_mock, html_mock, message_mock
    ):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        now = timezone.now().date()
        activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=5),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        section.main_activities.add(activity.details)
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT
        )
        one_time_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )
        send_appropriation(
            appropriation, Activity.objects.filter(pk=one_time_activity.pk)
        )
        # Retrieve the mocked template.render call.
        render_call_args = get_template_mock.return_value.render.call_args[1]
        # Assert the activities was part of the call to render.
        self.assertCountEqual(
            [activity], render_call_args["context"]["main_activities"]
        )
        self.assertCountEqual(
            [one_time_activity],
            render_call_args["context"]["supplementary_activities"],
        )

    @mock.patch("core.utils.HTML")
    @mock.patch("core.utils.EmailMessage")
    @mock.patch("core.utils.get_template")
    def test_send_appropriation_no_included(
        self, get_template_mock, html_mock, message_mock
    ):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        now = timezone.now().date()
        activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=5),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        section.main_activities.add(activity.details)
        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT
        )
        create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
            status=STATUS_GRANTED,
        )
        send_appropriation(appropriation)
        # Retrieve the mocked template.render call.
        render_call_args = get_template_mock.return_value.render.call_args[1]
        # Assert the activities was part of the call to render.

        self.assertCountEqual(
            [activity], render_call_args["context"]["main_activities"]
        )
        self.assertCountEqual(
            [], render_call_args["context"]["supplementary_activities"]
        )


class SamlLoginTestcase(TestCase, BasicTestMixin):
    def test_saml_before_login(self):
        user_data = {
            "team": ["S-DIG"],
            "username": ["dummy"],
            "bos_profile": ["grant"],
        }
        User.objects.create_user("dummy", "dummy", profile="grant")
        saml_before_login(user_data)
        [team_name] = user_data["team"]
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.name, "S-DIG")
        user_data["bos_profile"] = ["admin"]
        saml_before_login(user_data)

    def test_saml_create_user(self):
        user_data = {
            "team": ["S-DIG"],
            "username": ["dummy"],
            "bos_profile": ["grant"],
        }
        User.objects.create_user("dummy", "dummy", profile="grant")
        saml_create_user(user_data)
        [team_name] = user_data["team"]
        team = Team.objects.get(name=team_name)
        self.assertEqual(team.name, "S-DIG")
        saml_create_user(user_data)

    def test_no_team(self):
        User.objects.create_user("dummy", "dummy", profile="grant")
        user_data = {"username": ["dummy"]}
        saml_before_login(user_data)
        saml_create_user(user_data)

    def test_more_profiles(self):
        # This relates to a bug where we received more than one bos_profile and
        # duly crashed.
        user_data = {
            "team": ["S-DIG"],
            "username": ["dummy"],
            "bos_profile": ["grant", "edit"],
        }
        user = User.objects.create_user("dummy", "dummy", profile="readonly")
        saml_before_login(user_data)
        user.refresh_from_db()
        self.assertEqual(user.profile, "grant")

        user_data["bos_profile"].append("admin")
        user_data["username"] = ["dummy1"]
        user = User.objects.create_user("dummy1", "dummy1", profile="readonly")
        saml_create_user(user_data)
        user.refresh_from_db()
        self.assertEqual(user.profile, "admin")
        # Test the case with no user profiles given
        user_data["bos_profile"] = []
        saml_before_login(user_data)
        user.refresh_from_db()
        self.assertEqual(user.profile, "")


class SendToPrismTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_format_prism_financial_record(self):
        # Create a payment that is due today
        now = timezone.now()
        start_date = now - timedelta(days=1)
        end_date = now + timedelta(days=1)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )
        # Create an activity etc which is required.

        case_cpr_number = "1234567890"
        case = create_case(
            self.case_worker,
            self.team,
            self.municipality,
            self.district,
            cpr_number=case_cpr_number,
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        create_account(
            section=section,
            main_activity=main_activity_details,
            supplementary_activity=None,
        )
        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            details=main_activity_details,
        )
        # This will generate three payments on the payment plan, and one
        # of them will be for today.
        due_payments = due_payments_for_prism(now)
        records = generate_records_for_prism(due_payments)
        self.assertEqual(len(records), 2)
        due_payments = due_payments_for_prism(end_date)
        records = generate_records_for_prism(due_payments)
        self.assertEqual(len(records), 2)
        finance_reference = records[0].split("&117")[1][:20]
        payment_reference = records[1].split("&16")[1][:20]
        # These references is what links the two records.
        # This is a simple sanity check.
        self.assertEqual(payment_reference, finance_reference)
        # Check that the CPR number on G69 is the one from the case.
        finance_cpr = records[0].split("&133")[1][:10]
        payment_cpr = records[1].split("&11")[1][:10]
        self.assertEqual(finance_cpr, case_cpr_number)
        self.assertEqual(payment_cpr, payment_schedule.recipient_id)
        self.assertNotEqual(finance_cpr, payment_cpr)

    def test_export_prism_payments_for_date(self):
        # Create a payment that is due today
        now = timezone.now()
        start_date = now - timedelta(days=1)
        end_date = now + timedelta(days=1)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )
        # Create an activity etc which is required.
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        create_account(
            section=section,
            main_activity=main_activity_details,
            supplementary_activity=None,
        )
        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            details=main_activity_details,
        )
        # Check that there's unpaid payments for today.
        due_payments = due_payments_for_prism(start_date)
        self.assertEqual(due_payments.count(), 1)

        export_prism_payments_for_date(date=start_date)

        # Check that there's NO unpaid payments for that date.
        due_payments = due_payments_for_prism(start_date)
        self.assertEqual(due_payments.count(), 0)

        # Also process for today
        export_prism_payments_for_date()

        # Repeat the previous processing to have an example with no due
        # payments.
        export_prism_payments_for_date()


class GeneratePaymentsReportTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_generate_payments_report_list(self):
        now = timezone.now()
        start_date = now
        end_date = now + timedelta(days=5)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )

        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        payments = payment_schedule.payments.all()
        report_list = generate_payments_report_list(payments)
        self.assertEqual(len(report_list), 6)
        first_elem = report_list[0]
        # Assert that the following dict is a subset of the first element.
        self.assertTrue(
            {
                "amount": Decimal("666.00"),
                "paid_amount": None,
                "paid_date": None,
                "account_string": "12345-UKENDT-123",
                "payment_schedule__payment_amount": Decimal("666"),
                "payment_schedule__payment_frequency": "DAILY",
                "recipient_type": "PERSON",
                "recipient_id": "0205891234",
                "recipient_name": "Jens Testersen",
                "payment_method": "CASH",
                "details": "000000 - Test aktivitet",
                "sbsys_id": "XXX-YYY",
                "cpr_number": "0205891234",
                "name": "Jens Jensen",
                "effort_step": "Trin 1: Tidlig indsats i almenområdet",
                "paying_municipality": "København",
                "section": "ABL-105-2",
                "activity": activity.pk,
                "main_activity_id": (
                    appropriation.main_activity.details.activity_id
                ),
                "main_activity": appropriation.main_activity.pk,
            }.items()
            <= first_elem.items()
        )
        self.assertIsNotNone(first_elem["activity_start_date"])
        self.assertIsNotNone(first_elem["activity_end_date"])
        self.assertIsNotNone(first_elem["date"])

    def test_generate_payments_report_list_missing_activity(self):
        now = timezone.now()
        start_date = now
        end_date = now + timedelta(days=5)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )
        # Create an activity etc which is required.
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        activity.delete()

        payment_schedule.refresh_from_db()
        payments = payment_schedule.payments.all()

        report_list = generate_payments_report_list(payments)

        self.assertEqual(len(report_list), 0)

    def test_generate_payments_report_list_none(self):
        payments = Payment.objects.none()

        report_list = generate_payments_report_list(payments)

        self.assertEqual(len(report_list), 0)

    def test_generate_payments_report_list_granted_payments(self):
        now = timezone.now()
        # Create a granted activity.
        start_date = now
        end_date = now + timedelta(days=5)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        # Create an expected activity.
        start_date = now + timedelta(days=4)
        end_date = now + timedelta(days=8)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )

        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_EXPECTED,
            payment_plan=payment_schedule,
            modifies=granted_activity,
        )

        report_list = generate_granted_payments_report_list()

        self.assertEqual(len(report_list), 6)

    def test_generate_payments_report_list_expected_payments(self):
        now = timezone.now()
        # Create a granted activity.
        start_date = now
        end_date = now + timedelta(days=5)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )

        # Create an expected activity.
        start_date = now + timedelta(days=4)
        end_date = now + timedelta(days=8)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(800),
        )

        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_EXPECTED,
            payment_plan=payment_schedule,
            modifies=granted_activity,
        )

        report_list = generate_expected_payments_report_list()

        self.assertEqual(len(report_list), 9)
        self.assertEqual(
            sum([x["amount"] for x in report_list]), Decimal("6664")
        )
