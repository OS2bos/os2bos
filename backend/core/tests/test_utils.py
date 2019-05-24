# -*- coding: utf-8 -*-
from unittest import mock
from django.test import TestCase
from core.utils import get_cpr_data


class GetCPRDataTestCase(TestCase):

    def test_get_cpr_data_empty_certificate(self):
        with self.settings(SERVICEPLATFORM_CERTIFICATE_PATH=""):
            result = get_cpr_data("1234567890")
        self.assertIsNone(result)

    @mock.patch("core.utils.os.path")
    def test_get_cpr_data_invalid_uuids(self, path_mock):
        path_mock.is_file = lambda str: False
        test_uuids = {
            "service_agreement": "1234",
            "user_system": "1234",
            "user": "1234",
            "service": "1234"
        }
        with self.settings(SERVICEPLATFORM_UUIDS=test_uuids):
            result = get_cpr_data("1234567890")