# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest import mock

from django.test import TestCase, override_settings

from core.consumers import receive_sbsys_event


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post(*args, **kwargs):
    return MockResponse({"access_token": "12345678"}, 200)


def mocked_requests_get(*args, **kwargs):
    return MockResponse({"SagID": "1234"}, 200)


class ReceiveSBSYSEventTestCase(TestCase):
    @override_settings(SBSYS_VERIFY_TLS=True)
    @mock.patch("django_stomp.services.consumer.Payload")
    @mock.patch("requests.post", side_effect=mocked_requests_post)
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_receive_sbsys_event(
        self, requests_get_mock, requests_post_mock, payload_mock
    ):
        payload_mock.body = {
            "SagId": 1831,
            "ForloebtypeId": 1,
        }
        payload_mock.ack = lambda self: None
        # No tests - this function doesn't return anything.
        # S'all good if it doesn't throw an exception.
        receive_sbsys_event(payload_mock)

    @override_settings(SBSYS_VERIFY_TLS=False)
    @mock.patch("django_stomp.services.consumer.Payload")
    @mock.patch("requests.post", side_effect=mocked_requests_post)
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_receive_sbsys_event_no_tls(
        self, requests_get_mock, requests_post_mock, payload_mock
    ):
        payload_mock.body = {
            "SagId": 1831,
            "ForloebtypeId": 1,
        }
        payload_mock.ack = lambda self: None
        # No tests - this function doesn't return anything.
        # S'all good if it doesn't throw an exception.
        receive_sbsys_event(payload_mock)

    @mock.patch("django_stomp.services.consumer.Payload")
    @mock.patch("requests.post", side_effect=Exception)
    def test_receive_sbsys_event_auth_failed(
        self, requests_post_mock, payload_mock
    ):
        payload_mock.body = {
            "SagId": 1831,
        }
        payload_mock.nack = lambda self: None
        try:
            receive_sbsys_event(payload_mock)
        except Exception:
            pass
