# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest import mock

from django.test import TestCase

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
    return MockResponse({"SagID", "1234"}, 200)


class ReceiveSBSYSEventTestCase(TestCase):
    @mock.patch("django_stomp.services.consumer.Payload")
    @mock.patch("requests.post", side_effect=mocked_requests_post)
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_receive_sbsys_event(
        self, requests_get_mock, requests_post_mock, payload_mock
    ):
        payload_mock.body = {
            "SagID": 1831,
            "ForloebtypeId": 1,
        }
        payload_mock.ack = lambda self: None

        receive_sbsys_event(payload_mock)
