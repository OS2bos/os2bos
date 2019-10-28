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
    CASH,
    User,
    Team,
)
from core.utils import (
    get_cpr_data,
    get_person_info,
    get_cpr_data_mock,
    send_appropriation,
    saml_before_login,
    saml_create_user,
    send_records_to_prism,
)
from core.tests.testing_utils import (
    BasicTestMixin,
    create_case,
    create_appropriation,
    create_activity,
    create_section,
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=end_date,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        # This will generate three payments on the payment plan, and one
        # of them will be for today.
        records = []

        def my_writer(record):
            records.append(record)

        send_records_to_prism(writer=my_writer)
        self.assertEqual(len(records), 1)
