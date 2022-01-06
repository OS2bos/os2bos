# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from datetime import timedelta, date
from decimal import Decimal
from unittest import mock

from lxml import etree
from freezegun import freeze_time
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
    STATUS_DRAFT,
    CASH,
    User,
    Team,
    Payment,
    SectionInfo,
    Case,
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
    generate_payments_report_list_v0,
    generate_cases_report_list_v0,
    generate_payment_date_exclusion_dates,
    validate_cvr,
    get_company_info_from_cvr,
    get_company_info_from_search_term,
    generate_dst_payload_preventive_measures,
    generate_dst_payload_handicap,
)
from core.tests.testing_utils import (
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_activity,
    create_section,
    create_section_info,
    create_payment_schedule,
    create_activity_details,
    create_payment_date_exclusion,
    create_effort_step,
    create_related_person,
    create_approval_level,
    create_municipality,
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


class GetCompanyInfoTestCase(TestCase):
    @override_settings(USE_VIRK=True)
    @mock.patch("core.utils.get_org_info_from_cvr")
    def test_get_company_info_from_cvr(self, virk_mock):
        cvr = "25052943"
        test_service_providers = [
            {
                "cvr_no": "25052943",
                "navn": "MAGENTA ApS",
                "vejnavn": "Pilestræde",
                "husnr": "43",
                "postnr": "1112",
                "branchekode": "620200",
                "status": "NORMAL",
            }
        ]
        virk_mock.return_value = test_service_providers

        result = get_company_info_from_cvr(cvr)

        self.assertEqual(result, test_service_providers)

    @override_settings(USE_VIRK=True)
    @mock.patch("core.utils.get_org_info_from_cvr_p_number_or_name")
    def test_get_company_info_from_search_term(self, virk_mock):
        search_term = "25052943"
        test_service_providers = [
            {
                "cvr_no": "25052943",
                "navn": "MAGENTA ApS",
                "vejnavn": "Pilestræde",
                "husnr": "43",
                "postnr": "1112",
                "branchekode": "620200",
                "status": "NORMAL",
            }
        ]
        virk_mock.return_value = test_service_providers

        result = get_company_info_from_search_term(search_term)

        self.assertEqual(result, test_service_providers)

    @override_settings(USE_VIRK=True)
    @mock.patch("core.utils.get_org_info_from_cvr", lambda cvr: None)
    def test_get_company_info_from_cvr_none(self):
        cvr = "25052943"

        result = get_company_info_from_cvr(cvr)

        self.assertIsNone(result)

    @override_settings(USE_VIRK=True)
    @mock.patch(
        "core.utils.get_org_info_from_cvr_p_number_or_name",
        lambda search_term: None,
    )
    def test_get_company_info_from_search_term_none(self):
        search_term = "25052943"

        result = get_company_info_from_search_term(search_term)

        self.assertIsNone(result)

    @override_settings(USE_VIRK=True)
    @mock.patch("core.utils.virk_logger")
    @mock.patch("core.utils.get_org_info_from_cvr")
    def test_get_company_info_from_cvr_http_error(
        self, virk_mock, virk_logger_mock
    ):
        cvr = "25052943"
        virk_mock.side_effect = requests.exceptions.HTTPError

        result = get_company_info_from_cvr(cvr)

        self.assertIsNone(result)
        virk_logger_mock.exception.assert_called_with(
            "get_cvr_data requests error"
        )

    @override_settings(USE_VIRK=True)
    @mock.patch("core.utils.virk_logger")
    @mock.patch(
        "core.utils.get_org_info_from_cvr_p_number_or_name",
    )
    def test_get_company_info_from_search_term_http_error(
        self, virk_mock, virk_logger_mock
    ):
        search_term = "25052943"
        virk_mock.side_effect = requests.exceptions.HTTPError

        result = get_company_info_from_search_term(search_term)
        self.assertIsNone(result)
        virk_logger_mock.exception.assert_called_with(
            "get_cvr_data requests error"
        )

    @override_settings(USE_VIRK=False)
    def test_get_company_info_from_search_term_no_virk(self):
        search_term = "25052943"
        test_service_providers = [
            {
                "cvr_no": "25052943",
                "navn": "MAGENTA ApS",
                "vejnavn": "Pilestræde",
                "husnr": "43",
                "postnr": "1112",
                "postdistrikt": "København K",
                "branchekode": "620200",
                "branchetekst": (
                    "Konsulentbistand vedrørende informationsteknologi"
                ),
                "status": "NORMAL",
            }
        ]

        result = get_company_info_from_search_term(search_term)

        self.assertEqual(result, test_service_providers)

    @override_settings(USE_VIRK=False)
    def test_get_company_info_from_cvr_no_virk(self):
        cvr = "25052943"
        test_service_providers = [
            {
                "cvr_no": "25052943",
                "navn": "MAGENTA ApS",
                "vejnavn": "Pilestræde",
                "husnr": "43",
                "postnr": "1112",
                "postdistrikt": "København K",
                "branchekode": "620200",
                "branchetekst": (
                    "Konsulentbistand vedrørende informationsteknologi"
                ),
                "status": "NORMAL",
            }
        ]

        result = get_company_info_from_cvr(cvr)

        self.assertEqual(result, test_service_providers)


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
        case = create_case(self.case_worker, self.municipality, self.district)
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

        one_time_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=one_time_activity,
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
        case = create_case(self.case_worker, self.municipality, self.district)
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

        suppl_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=suppl_activity,
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

    @mock.patch("core.utils.HTML")
    @mock.patch("core.utils.EmailMessage")
    @mock.patch("core.utils.get_template")
    def test_send_appropriation_variables_included(
        self, get_template_mock, html_mock, message_mock
    ):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()

        appropriation = create_appropriation(
            sbsys_id="27.69.20-Ø36-23-19", case=case, section=section
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

        section_info = SectionInfo.objects.get(
            activity_details=activity.details, section=section
        )
        section_info.sbsys_template_id = "900"
        section_info.save()

        create_payment_schedule(
            activity=activity,
        )
        send_appropriation(
            appropriation, Activity.objects.filter(pk=activity.pk)
        )
        # Retrieve the mocked template.render call.
        render_call_args = get_template_mock.return_value.render.call_args[1]
        # Assert the correct variables was given.
        self.assertEqual(render_call_args["context"]["kle_number"], "27.69.20")
        self.assertEqual(
            render_call_args["context"]["sbsys_case_file_number"],
            "27.69.20-Ø36-23-19",
        )
        self.assertEqual(
            render_call_args["context"]["sbsys_template_id"], "900"
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
        now = timezone.now().date()
        start_date = now - timedelta(days=1)
        end_date = now + timedelta(days=1)

        # Create an activity etc which is required.

        case_cpr_number = "1234567890"
        case = create_case(
            self.case_worker,
            self.municipality,
            self.district,
            cpr_number=case_cpr_number,
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = create_activity_details(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
        )
        create_section_info(
            details=main_activity_details,
            section=section,
            main_activity_main_account_number="12345",
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
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
        now = timezone.now().date()
        start_date = now - timedelta(days=1)
        end_date = now + timedelta(days=1)
        # Create an activity etc which is required.
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = create_activity_details(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
        )
        create_section_info(
            main_activity_details,
            section,
            main_activity_main_account_number="1234",
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            details=main_activity_details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
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

    @freeze_time("2020-05-13")
    def test_export_prism_payments_with_exclusions_wednesday(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=14)
        # Create an activity etc which is required.
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = create_activity_details()
        create_section_info(
            main_activity_details,
            section,
            main_activity_main_account_number="1234",
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )

        # Generate payment exclusion dates and export.
        exclusion_dates = generate_payment_date_exclusion_dates(years=[2020])
        for exclusion_date in exclusion_dates:
            create_payment_date_exclusion(date=exclusion_date)

        export_prism_payments_for_date(date=None)

        # Assert Wednesday only includes Thursday.
        self.assertCountEqual(
            payment_schedule.payments.filter(paid=True).values_list(
                "date", flat=True
            ),
            [date(2020, 5, 14)],  # Thursday
        )

    @freeze_time("2020-06-04")
    def test_export_prism_payments_with_exclusions_thursday_with_weekend(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=14)
        # Create an activity etc which is required.
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = create_activity_details()
        create_section_info(
            main_activity_details,
            section,
            main_activity_main_account_number="1234",
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )

        # Generate payment exclusion dates and export.
        exclusion_dates = generate_payment_date_exclusion_dates(years=[2020])
        for exclusion_date in exclusion_dates:
            create_payment_date_exclusion(date=exclusion_date)

        export_prism_payments_for_date(date=None)

        # Assert Thursday includes Friday + weekend + Monday.
        self.assertCountEqual(
            payment_schedule.payments.filter(paid=True).values_list(
                "date", flat=True
            ),
            [
                date(2020, 6, 5),  # Friday
                date(2020, 6, 6),  # Saturday
                date(2020, 6, 7),  # Sunday
                date(2020, 6, 8),  # Monday
            ],
        )

    @freeze_time("2024-12-19")
    def test_export_prism_payments_with_exclusions_christmas_2024(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=14)
        # Create an activity etc which is required.
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = create_activity_details()
        create_section_info(
            main_activity_details,
            section,
            main_activity_main_account_number="1234",
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )

        # Generate payment exclusion dates and export.
        exclusion_dates = generate_payment_date_exclusion_dates(
            years=[2024, 2025]
        )
        for exclusion_date in exclusion_dates:
            create_payment_date_exclusion(date=exclusion_date)
        # Create Christmas Eve and New Years Eve as well.
        create_payment_date_exclusion(date=date(2024, 12, 24))
        create_payment_date_exclusion(date=date(2024, 12, 31))

        export_prism_payments_for_date(date=None)

        # Assert Thursday includes Friday + weekend + Monday.
        self.assertCountEqual(
            payment_schedule.payments.filter(paid=True).values_list(
                "date", flat=True
            ),
            [
                date(2024, 12, 20),  # Friday
                date(2024, 12, 21),  # Saturday
                date(2024, 12, 22),  # Sunday
                date(2024, 12, 23),  # Monday
                date(2024, 12, 24),  # Christmas Eve
                date(2024, 12, 25),  # Christmas Day
                date(2024, 12, 26),  # 2nd Christmas Day
                date(2024, 12, 27),  # Friday
                date(2024, 12, 28),  # Saturday
                date(2024, 12, 29),  # Sunday
                date(2024, 12, 30),  # Monday
                date(2024, 12, 31),  # New Years Eve
                date(2025, 1, 1),  # New Years Day
                date(2025, 1, 2),  # First day after exclusion dates.
            ],
        )

    @freeze_time("2020-04-07")
    def test_export_prism_payments_with_exclusions_easter_2020(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=14)
        # Create an activity etc which is required.
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        main_activity_details = create_activity_details()
        create_section_info(
            main_activity_details,
            section,
            main_activity_main_account_number="1234",
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            details=main_activity_details,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )
        # Generate payment exclusion dates and export.
        exclusion_dates = generate_payment_date_exclusion_dates(years=[2020])
        for exclusion_date in exclusion_dates:
            create_payment_date_exclusion(date=exclusion_date)

        export_prism_payments_for_date(date=None)

        # Assert 2020-04-07 includes weekend + easter days.
        self.assertCountEqual(
            payment_schedule.payments.filter(paid=True).values_list(
                "date", flat=True
            ),
            [
                date(2020, 4, 8),  # "Normal" day
                date(2020, 4, 9),  # Maundy Thursday - holiday
                date(2020, 4, 10),  # Good Friday - holiday
                date(2020, 4, 11),  # Saturday - weekend
                date(
                    2020, 4, 12
                ),  # Easter Sunday - holiday / Sunday - weekend
                date(2020, 4, 13),  # Easter Monday
                date(2020, 4, 14),  # Should be paid 2 "normal" days prior
            ],
        )


class TestGeneratePaymentDateExclusionDates(TestCase):
    @mock.patch("core.utils.extra_payment_date_exclusion_tuples", [])
    def test_generate_payment_date_exclusion_dates(self):
        # Generate exclusion dates for 2019, 2020, 2021, and 2022.
        years = [2019, 2020, 2021, 2022]
        dates = generate_payment_date_exclusion_dates(years)

        self.assertTrue(all([date.year in years for date in dates]))
        self.assertEqual(len(dates), 448)

    @mock.patch("core.utils.extra_payment_date_exclusion_tuples", [])
    @freeze_time("2020-01-01")
    def test_generate_payment_date_exclusion_dates_no_params(self):
        # Generate exclusion dates with no params so default
        # is current year and current year + 1.
        dates = generate_payment_date_exclusion_dates()

        self.assertTrue(all([date.year in [2020, 2021] for date in dates]))
        self.assertEqual(len(dates), 223)

    @mock.patch(
        "core.utils.extra_payment_date_exclusion_tuples",
        [(1, 5), (5, 6), (24, 12), (31, 12)],
    )
    @freeze_time("2020-01-01")
    def test_generate_payment_date_exclusion_dates_with_extra_tuples(self):
        dates = generate_payment_date_exclusion_dates()

        self.assertTrue(all([date.year in [2020, 2021] for date in dates]))
        extra_dates = [
            date(year=2020, month=5, day=1),
            date(year=2020, month=6, day=5),
            date(year=2020, month=12, day=24),
            date(year=2020, month=12, day=31),
            date(year=2021, month=5, day=1),
            date(year=2021, month=6, day=5),
            date(year=2021, month=12, day=24),
            date(year=2021, month=12, day=31),
        ]
        for extra_date in extra_dates:
            self.assertIn(extra_date, dates)
        self.assertEqual(len(dates), 229)


class GeneratePaymentsReportTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_generate_payments_report_list(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)

        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, "far test", "far", "1111111111")
        create_related_person(case, "mor test", "mor", "2222222222")
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
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )
        payments = payment_schedule.payments.all()
        payments[0].paid_amount = Decimal(666)
        payments[0].paid_date = now - timedelta(days=10)
        report_list = generate_payments_report_list_v0(payments)
        self.assertEqual(len(report_list), 6)
        first_elem = report_list[0]
        # Assert that the following dict is a subset of the first element.
        expected_data = {
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
            "fictive": False,
            "activity__details__name": "Test aktivitet",
            "activity__details__activity_id": "000000",
            "sbsys_id": "XXX-YYY",
            "cpr_number": "0205891234",
            "name": "Jens Jensen",
            "effort_step": "Trin 1: Tidlig indsats i almenområdet",
            "paying_municipality": "København",
            "acting_municipality": "København",
            "residence_municipality": "København",
            "section": "ABL-105-2",
            "scaling_step": "1",
            "case_worker": "Orla Frøsnapper",
            "leader": "Orla Frøsnapper",
            "team": "FCK",
            "target_group": case.target_group,
            "activity_type": "MAIN_ACTIVITY",
            "main_activity_id": (
                appropriation.main_activity.details.activity_id
            ),
            "father_cpr": "1111111111",
            "mother_cpr": "2222222222",
        }
        self.assertTrue(expected_data.items() <= first_elem.items())
        self.assertIsNotNone(first_elem["id"])
        self.assertIsNotNone(first_elem["activity_start_date"])
        self.assertIsNotNone(first_elem["activity_end_date"])
        self.assertIsNotNone(first_elem["date"])

    def test_generate_payments_report_list_missing_activity(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
        )

        payment_schedule.generate_payments(start_date, end_date)
        payments = payment_schedule.payments.all()

        report_list = generate_payments_report_list_v0(payments)

        self.assertEqual(len(report_list), 0)

    def test_generate_payments_report_list_none(self):
        payments = Payment.objects.none()

        report_list = generate_payments_report_list_v0(payments)

        self.assertEqual(len(report_list), 0)

    def test_generate_payments_report_list_expected_payments(self):
        now = timezone.now().date()
        # Create a granted activity.
        start_date = now
        end_date = now + timedelta(days=5)

        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        # Create an expected activity.
        start_date = now + timedelta(days=4)
        end_date = now + timedelta(days=8)

        expected_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_EXPECTED,
            modifies=granted_activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(800),
            activity=expected_activity,
        )
        payments = Payment.objects.expected_payments_for_report_list()
        report_list = generate_payments_report_list_v0(payments)

        self.assertEqual(len(report_list), 9)
        self.assertEqual(
            sum([x["amount"] for x in report_list]), Decimal("6664")
        )

    def test_generate_payments_report_list_use_historical_case(self):
        # Pay payments on 2020-01-01.
        with freeze_time("2020-01-01"):
            now = timezone.now().date()
            start_date = now
            end_date = now + timedelta(days=5)
            case = create_case(
                self.case_worker, self.municipality, self.district
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
            )
            payment_schedule = create_payment_schedule(
                payment_frequency=PaymentSchedule.DAILY,
                payment_type=PaymentSchedule.RUNNING_PAYMENT,
                recipient_type=PaymentSchedule.PERSON,
                payment_method=CASH,
                payment_amount=Decimal(666),
                activity=granted_activity,
            )
            payment_schedule.payments.update(paid=True)
            payment_schedule.payments.update(paid_date=now)

        self.assertEqual(case.effort_step.number, 1)
        self.assertEqual(case.scaling_step, 1)

        # A day has passed.
        with freeze_time("2020-01-02"):
            effort_step = create_effort_step(name="Trin 2", number=2)
            case.effort_step = effort_step
            case.scaling_step = 2
            case.save()

            report = generate_payments_report_list_v0(
                payment_schedule.payments.all()
            )

            self.assertTrue(
                all(
                    [
                        payment_dict["effort_step"]
                        == "Trin 1: Tidlig indsats i almenområdet"
                        for payment_dict in report
                    ]
                )
            )
            self.assertTrue(
                all(
                    [
                        payment_dict["scaling_step"] == "1"
                        for payment_dict in report
                    ]
                )
            )

    def test_generate_payments_report_list_historical_case_missing(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        case = create_case(self.case_worker, self.municipality, self.district)
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
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        self.assertEqual(case.effort_step.number, 1)
        self.assertEqual(case.scaling_step, 1)

        # Create a second case history entry.
        effort_step = create_effort_step(name="Trin 2", number=2)
        case.effort_step = effort_step
        case.scaling_step = 2
        case.save()

        # Pay payments in the past.
        past_date = date(2020, 1, 1)
        payment_schedule.payments.update(paid=True)
        payment_schedule.payments.update(paid_date=past_date)

        # Exception is not raised:
        # core.models.Case.DoesNotExist: Case had not yet been created.
        report = generate_payments_report_list_v0(
            payment_schedule.payments.all()
        )

        # Payments should use the earliest historical version of the Case.
        self.assertTrue(
            all(
                [
                    payment_dict["effort_step"]
                    == "Trin 1: Tidlig indsats i almenområdet"
                    for payment_dict in report
                ]
            )
        )
        self.assertTrue(
            all(
                [
                    payment_dict["scaling_step"] == "1"
                    for payment_dict in report
                ]
            )
        )


class ValidateCVRTestCase(TestCase):
    def test_validate_cvr_success(self):
        self.assertTrue(validate_cvr("26570514"))

    def test_validate_cvr_with_spaces_success(self):
        self.assertTrue(validate_cvr(" 29244049 "))

    def test_validate_cvr_failure_7_digits(self):
        self.assertFalse(validate_cvr("2924404"))

    def test_validate_cvr_failure_9_digits(self):
        self.assertFalse(validate_cvr("292440494"))


class GenerateCasesReportTestCase(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_generate_cases_report_list(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, "far test", "far", "1111111111")
        create_related_person(case, "mor test", "mor", "2222222222")

        report_list = generate_cases_report_list_v0(Case.objects.all())
        self.assertEqual(len(report_list), 1)
        first_elem = report_list[0]
        # Assert that the following dict is a subset of the first element.
        expected_data = {
            "id": "1",
            "history_id": "1",
            "cpr_number": "0205891234",
            "case_sbsys_id": "27.24.00-G01-99-21",
            "name": "Jens Jensen",
            "target_group": case.target_group,
            "case_worker": "Orla Frøsnapper",
            "team": "FCK",
            "leader": "Orla Frøsnapper",
            "efforts": "",
            "effort_step": "Trin 1: Tidlig indsats i almenområdet",
            "scaling_step": "1",
            "paying_municipality": "København",
            "acting_municipality": "København",
            "residence_municipality": "København",
            "father_cpr": "1111111111",
            "mother_cpr": "2222222222",
        }
        self.assertTrue(set(expected_data) <= set(first_elem))
        self.assertIsNotNone(first_elem["history_date"])


class DSTUtilities(TestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_generate_dst_payload_preventative_initial_load_valid(self):
        now = timezone.now().date()
        start_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_UdsatteBoernOgUngeLeveranceL201U1Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload with no cut-off date
        # should result in a initial_load with a status of "Ny".
        doc = generate_dst_payload_preventive_measures()
        self.assertTrue(xml_schema.validate(doc))

    def test_generate_dst_payload_preventative_one_time_special_case(self):
        now = timezone.now().date()
        payment_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=None,
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
            payment_date=payment_date,
        )
        section.main_activities.add(granted_activity.details)

        section_info = SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        section_info.dst_code = "123"
        section_info.save()

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_UdsatteBoernOgUngeLeveranceL201U1Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        doc = generate_dst_payload_preventive_measures()
        self.assertTrue(xml_schema.validate(doc))

        # One time activities with no start/end use payment_date instead.
        self.assertEqual(
            doc.xpath(
                "x:ForanstaltningStrukturSamling/"
                "x:ForanstaltningStruktur/"
                "x:ForanstaltningStartDato",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            str(payment_date),
        )
        self.assertEqual(
            doc.xpath(
                "x:ForanstaltningStrukturSamling/"
                "x:ForanstaltningStruktur/"
                "x:ForanstaltningSlutDato",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            str(payment_date),
        )

    def test_generate_dst_payload_handicap_initial_load_valid(self):
        now = timezone.now().date()
        start_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
        )
        section.main_activities.add(granted_activity.details)

        section_info = SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        section_info.dst_code = "123"
        section_info.save()

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_BoernMedHandicapLeveranceL231Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload with no cut-off date
        # should result in a initial_load with a status of "Ny".
        doc = generate_dst_payload_handicap()
        self.assertTrue(xml_schema.validate(doc))

        self.assertEqual(
            doc.xpath(
                "x:BoernMedHandicapSagStrukturSamling/"
                "x:BoernMedHandicapSagStruktur/"
                "x:INDBERETNINGSTYPE",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            "Ny",
        )

    def test_generate_dst_payload_handicap_one_time_special_case(self):
        now = timezone.now().date()
        payment_date = now
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        granted_activity = create_activity(
            case,
            appropriation,
            start_date=None,
            end_date=None,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=granted_activity,
            payment_date=payment_date,
        )
        section.main_activities.add(granted_activity.details)

        section_info = SectionInfo.objects.get(
            activity_details=granted_activity.details, section=section
        )
        section_info.dst_code = "123"
        section_info.save()

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_BoernMedHandicapLeveranceL231Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        doc = generate_dst_payload_handicap()
        self.assertTrue(xml_schema.validate(doc))

        # One time activities with no start/end use payment_date instead.
        self.assertEqual(
            doc.xpath(
                "x:BoernMedHandicapSagStrukturSamling/"
                "x:BoernMedHandicapSagStruktur/"
                "x:INDSATS_STARTDATO",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            str(payment_date),
        )
        self.assertEqual(
            doc.xpath(
                "x:BoernMedHandicapSagStrukturSamling/"
                "x:BoernMedHandicapSagStruktur/"
                "x:INDSATS_SLUTDATO",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            str(payment_date),
        )

    @freeze_time("2021-01-01")
    def test_generate_dst_payload_handicap_delta_load_changed(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        # Create a main activity at 2021-01-01 and grant it.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )
        section.main_activities.add(activity.details)

        SectionInfo.objects.get(
            activity_details=activity.details, section=section
        )
        approval_level = create_approval_level()

        activities = Activity.objects.filter(pk=activity.pk)
        appropriation.grant(
            activities, approval_level.id, "note", self.case_worker
        )

        # Next we create a modification to the main activity
        # at 2021-01-03 and grant it.
        with freeze_time("2021-01-03"):
            modifies_activity = create_activity(
                case,
                appropriation,
                start_date=start_date + timedelta(days=2),
                end_date=end_date,
                activity_type=MAIN_ACTIVITY,
                status=STATUS_EXPECTED,
                modifies=activity,
            )
            create_payment_schedule(
                payment_frequency=PaymentSchedule.DAILY,
                payment_type=PaymentSchedule.RUNNING_PAYMENT,
                recipient_type=PaymentSchedule.PERSON,
                payment_method=CASH,
                payment_amount=Decimal(777),
                activity=modifies_activity,
            )
            activities = Activity.objects.filter(pk=modifies_activity.pk)
            appropriation.grant(
                activities, approval_level.id, "note", self.case_worker
            )

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_BoernMedHandicapLeveranceL231Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload from a cut-off date of 2021-01-02
        # For an appropriation containing both main activities before and after
        # should result in a status of "Ændring".
        doc = generate_dst_payload_handicap(from_date=date(2021, 1, 2))

        self.assertTrue(xml_schema.validate(doc))

        self.assertEqual(
            doc.xpath(
                "x:BoernMedHandicapSagStrukturSamling/"
                "x:BoernMedHandicapSagStruktur/"
                "x:INDBERETNINGSTYPE",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            "Ændring",
        )

    @freeze_time("2021-01-02")
    def test_generate_dst_payload_handicap_delta_load_new(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        # Create a main activity at 2021-01-01 and grant it.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )
        section.main_activities.add(activity.details)

        SectionInfo.objects.get(
            activity_details=activity.details, section=section
        )
        approval_level = create_approval_level()

        activities = Activity.objects.filter(pk=activity.pk)
        appropriation.grant(
            activities, approval_level.id, "note", self.case_worker
        )

        # Next we create a modification to the main activity
        # at 2021-01-03 and grant it.
        with freeze_time("2021-01-03"):
            modifies_activity = create_activity(
                case,
                appropriation,
                start_date=start_date + timedelta(days=2),
                end_date=end_date,
                activity_type=MAIN_ACTIVITY,
                status=STATUS_EXPECTED,
                modifies=activity,
            )
            create_payment_schedule(
                payment_frequency=PaymentSchedule.DAILY,
                payment_type=PaymentSchedule.RUNNING_PAYMENT,
                recipient_type=PaymentSchedule.PERSON,
                payment_method=CASH,
                payment_amount=Decimal(777),
                activity=modifies_activity,
            )
            activities = Activity.objects.filter(pk=modifies_activity.pk)
            appropriation.grant(
                activities, approval_level.id, "note", self.case_worker
            )

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_BoernMedHandicapLeveranceL231Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload from a cut-off date of 2021-01-01
        # For an appropriation containing only main activities after
        # should result in a status of "Ny".
        doc = generate_dst_payload_handicap(from_date=date(2021, 1, 1))

        self.assertTrue(xml_schema.validate(doc))

        self.assertEqual(
            doc.xpath(
                "x:BoernMedHandicapSagStrukturSamling/"
                "x:BoernMedHandicapSagStruktur/"
                "x:INDBERETNINGSTYPE",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            "Ny",
        )

    @freeze_time("2021-01-01")
    def test_generate_dst_payload_handicap_delta_load_changed_case(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        # Create a main activity at 2021-01-01 and grant it.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )
        section.main_activities.add(activity.details)

        SectionInfo.objects.get(
            activity_details=activity.details, section=section
        )
        approval_level = create_approval_level()

        activities = Activity.objects.filter(pk=activity.pk)
        appropriation.grant(
            activities, approval_level.id, "note", self.case_worker
        )

        # case gets a new acting municipality in the future.
        with freeze_time("2021-02-01"):
            new_municipality = create_municipality("Ballerup")
            case.acting_municipality = new_municipality
            case.save()

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_BoernMedHandicapLeveranceL231Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload from a cut-off date of 2021-02-01
        # with a case with a changed acting municipality should result
        # in a status of "Ændret".
        doc = generate_dst_payload_handicap(from_date=date(2021, 2, 1))

        self.assertTrue(xml_schema.validate(doc))

        self.assertEqual(
            doc.xpath(
                "x:BoernMedHandicapSagStrukturSamling/"
                "x:BoernMedHandicapSagStruktur/"
                "x:INDBERETNINGSTYPE",
                namespaces={
                    "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                },
            )[0].text,
            "Ændring",
        )

    @freeze_time("2021-01-01")
    def test_generate_dst_payload_handicap_delta_load_no_load(self):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(case, relation_type="far")
        section = create_section(dst_code="123")
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        # Create a main activity at 2021-01-01 and grant it.
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=activity,
        )
        section.main_activities.add(activity.details)

        SectionInfo.objects.get(
            activity_details=activity.details, section=section
        )
        approval_level = create_approval_level()

        activities = Activity.objects.filter(pk=activity.pk)
        appropriation.grant(
            activities, approval_level.id, "note", self.case_worker
        )

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_BoernMedHandicapLeveranceL231Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload from a cut-off date of 2021-02-01
        # with an unchanged activity from 2021-01-01 should result in no
        # load.
        doc = generate_dst_payload_handicap(from_date=date(2021, 2, 1))
        # The doc is not valid due to child elements (approprations) missing.
        self.assertFalse(xml_schema.validate(doc))

        self.assertEqual(
            len(
                doc.xpath(
                    "x:BoernMedHandicapSagStrukturSamling/"
                    "x:BoernMedHandicapSagStruktur",
                    namespaces={
                        "x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"
                    },
                )
            ),
            0,
        )

    def test_generate_dst_payload_preventative_initial_load_consolidation(
        self,
    ):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(
            case, relation_type="far", cpr_number="1234567890"
        )
        section = create_section(dst_code="123")
        first_appropriation = create_appropriation(
            sbsys_id="27.12.06-G01-197-19-gl", case=case, section=section
        )
        first_activity = create_activity(
            case,
            first_appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=first_activity,
        )
        section.main_activities.add(first_activity.details)

        SectionInfo.objects.get(
            activity_details=first_activity.details, section=section
        )

        second_appropriation = create_appropriation(
            sbsys_id="27.12.06-G01-197-19", case=case, section=section
        )
        second_activity = create_activity(
            case,
            second_appropriation,
            start_date=start_date - timedelta(days=10),
            end_date=end_date + timedelta(days=5),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=second_activity,
        )
        section.main_activities.add(second_activity.details)

        SectionInfo.objects.get(
            activity_details=second_activity.details, section=section
        )

        third_appropriation = create_appropriation(
            sbsys_id="27.12.06-G01-197-19-ny", case=case, section=section
        )
        third_activity = create_activity(
            case,
            third_appropriation,
            start_date=start_date - timedelta(days=5),
            end_date=end_date + timedelta(days=10),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=third_activity,
        )
        section.main_activities.add(third_activity.details)

        SectionInfo.objects.get(
            activity_details=third_activity.details, section=section
        )

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_UdsatteBoernOgUngeLeveranceL201U1Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload with no cut-off date
        # should result in a initial_load.
        doc = generate_dst_payload_preventive_measures()
        self.assertTrue(xml_schema.validate(doc))

        # All three appropriations should be consolidated to one entry.
        ns = {"x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"}
        structure_doc = doc.xpath(
            "x:ForanstaltningStrukturSamling/" "x:ForanstaltningStruktur",
            namespaces=ns,
        )
        self.assertEqual(len(structure_doc), 1)
        # Assert elements are properly consolidated.
        self.assertEqual(
            structure_doc[0]
            .xpath("x:UdsatBarnCPRidentifikator", namespaces=ns)[0]
            .text,
            "0205891234",
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:FormynderCPRidentifikator", namespaces=ns)[0]
            .text,
            "1234567890",
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:ForanstaltningId", namespaces=ns)[0]
            .text,
            "27.12.06-G01-197-19",
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:ForanstaltningKode", namespaces=ns)[0]
            .text,
            "123",
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:ForanstaltningStartDato", namespaces=ns)[0]
            .text,
            str(second_activity.start_date),
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:ForanstaltningSlutDato", namespaces=ns)[0]
            .text,
            str(third_activity.end_date),
        )

    def test_generate_dst_payload_handicap_initial_load_consolidation(
        self,
    ):
        now = timezone.now().date()
        start_date = now
        end_date = now + timedelta(days=5)
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(
            case, relation_type="far", cpr_number="1234567890"
        )
        section = create_section(dst_code="123")
        first_appropriation = create_appropriation(
            sbsys_id="27.12.06-G01-197-19-gl", case=case, section=section
        )
        first_activity = create_activity(
            case,
            first_appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=first_activity,
        )
        section.main_activities.add(first_activity.details)

        SectionInfo.objects.get(
            activity_details=first_activity.details, section=section
        )

        second_appropriation = create_appropriation(
            sbsys_id="27.12.06-G01-197-19", case=case, section=section
        )
        second_activity = create_activity(
            case,
            second_appropriation,
            start_date=start_date - timedelta(days=10),
            end_date=end_date + timedelta(days=5),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=second_activity,
        )
        section.main_activities.add(second_activity.details)

        SectionInfo.objects.get(
            activity_details=second_activity.details, section=section
        )

        third_appropriation = create_appropriation(
            sbsys_id="27.12.06-G01-197-19-ny", case=case, section=section
        )
        third_activity = create_activity(
            case,
            third_appropriation,
            start_date=start_date - timedelta(days=5),
            end_date=end_date + timedelta(days=10),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            recipient_type=PaymentSchedule.PERSON,
            payment_method=CASH,
            payment_amount=Decimal(666),
            activity=third_activity,
        )
        section.main_activities.add(third_activity.details)

        SectionInfo.objects.get(
            activity_details=third_activity.details, section=section
        )

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "xml_schemas",
            "DST_BoernMedHandicapLeveranceL231Struktur.xsd",
        )

        with open(schema_path) as f:
            xmlschema_doc = etree.parse(f)
        xml_schema = etree.XMLSchema(xmlschema_doc)

        # Generating a dst payload with no cut-off date
        # should result in a initial_load.
        doc = generate_dst_payload_handicap()
        self.assertTrue(xml_schema.validate(doc))

        # All three appropriations should be consolidated to one entry.
        ns = {"x": "http://rep.oio.dk/dst.dk/xml/schemas/2010/04/16/"}
        structure_doc = doc.xpath(
            "x:BoernMedHandicapSagStrukturSamling/"
            "x:BoernMedHandicapSagStruktur",
            namespaces=ns,
        )
        self.assertEqual(len(structure_doc), 1)
        # Assert elements are properly consolidated.
        self.assertEqual(
            structure_doc[0].xpath("x:CPR", namespaces=ns)[0].text,
            "0205891234",
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:INDSATSFORLOEB_ID", namespaces=ns)[0]
            .text,
            "27.12.06-G01-197-19",
        )
        self.assertEqual(
            structure_doc[0].xpath("x:INDSATS_KODE", namespaces=ns)[0].text,
            "123",
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:INDSATS_STARTDATO", namespaces=ns)[0]
            .text,
            str(second_activity.start_date),
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:INDSATS_SLUTDATO", namespaces=ns)[0]
            .text,
            str(third_activity.end_date),
        )
        self.assertEqual(
            structure_doc[0].xpath("x:SAGSBEHANDLER", namespaces=ns)[0].text,
            "Orla Frøsnapper",
        )
        self.assertEqual(
            structure_doc[0]
            .xpath("x:INDBERETNINGSTYPE", namespaces=ns)[0]
            .text,
            "Ny",
        )
