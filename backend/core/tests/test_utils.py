# -*- coding: utf-8 -*-
from unittest import mock
from django.test import TestCase
import requests

from core.utils import get_cpr_data, get_person_info, get_cpr_data_mock


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
