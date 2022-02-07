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


example_sbsys_data = {
    "SagsTyper": [{"Id": 3, "Navn": "BUSag"}],
    "SagsTitel": "Børn og ungesag v127.9.12 - Åge Test Berggren",
    "Personer": [
        {
            "FoedeDato": "1922-02-11T00:00:00+01:00",
            "Koen": "Mand",
            "CprNummer": "021122-3989",
            "Adresse": {
                "Id": 63,
                "Adresse1": "Testvænget 1",
                "PostNummer": 8000,
                "PostDistrikt": "Aarhus",
                "HusNummer": "3",
                "Etage": "3",
                "DoerBetegnelse": "th",
                "ErBeskyttet": False,
            },
            "CivilstandId": 4,
            "MorCPR": "000000-0000",
            "FarCPR": "000000-0000",
            "TilmeldtDigitalPost": False,
            "Uuid": "4beba82f-3709-488d-aac0-e2be14bebac7",
            "Id": 14,
            "Navn": "Åge Test Berggren",
        }
    ],
    "Firmaer": [],
    "PrimaryPart": {
        "PartId": 14,
        "PartType": "Person",
        "CPRnummer": "021122-3989",
        "Navn": "Åge Test Berggren",
    },
    "Id": 3793,
    "SagIdentity": "f9e19574-196e-4136-89c3-8004445e1a77",
    "Opstaaet": "2022-02-07T14:21:00.61+01:00",
    "Nummer": "27.27.27-I10-2-22",
    "Fagomraade": {
        "Uuid": "b168ec95-d6e4-480a-8c82-30c1cab68209",
        "Id": 1,
        "Navn": "Standard",
    },
    "BevaringId": 10,
    "SenesteStatusAendringKommentar": "Sagsstatus ændret til Opstået",
    "SenesteStatusAendring": "2022-02-07T14:21:00.437+01:00",
    "Oprettet": "2022-02-07T14:21:00.61+01:00",
    "SenestAendret": "2022-02-07T14:21:00.887+01:00",
    "ErBeskyttet": True,
    "ErBesluttet": False,
    "BeslutningHarDeadline": False,
    "SagsNummerId": 3793,
    "Ansaettelsessted": {
        "Uuid": "c2822c97-8e48-4cc7-8e0f-474318c8192a",
        "Id": 5,
        "Navn": "Løn",
    },
    "Behandler": {
        "LogonId": "testbruger01",
        "Uuid": "c713c192-939f-463a-8f71-dc92d699e64e",
        "Id": 2,
        "Navn": "Test Bruger 01",
    },
    "SagsStatus": {
        "Id": 6,
        "Navn": "Opstået",
        "Orden": 1,
        "SagsTilstand": "Aktiv",
        "RequireComments": False,
        "SagsStatusKommentar": "Sagsstatus ændret til Opstået",
    },
    "ArkivAfklaringStatusId": 1,
    "OprettetAf": {
        "LogonId": "testbruger01",
        "Uuid": "c713c192-939f-463a-8f71-dc92d699e64e",
        "Id": 2,
        "Navn": "Test Bruger 01",
    },
    "SenestAendretAf": {
        "LogonId": "testbruger01",
        "Uuid": "c713c192-939f-463a-8f71-dc92d699e64e",
        "Id": 2,
        "Navn": "Test Bruger 01",
    },
    "SecuritySetId": 104742,
    "SagSkabelon": {
        "Uuid": "65e6d2b3-5630-452a-9f95-8ab9e2a0f875",
        "Id": 110,
        "Navn": "Børn og ungesag v127.9.12",
    },
    "SagsNummer": {
        "EmneplanNummer": {
            "Id": 13650,
            "EmneplanID": 90,
            "Nummer": "27.27.27",
            "Navn": "Anbringelse i åbne døgninstitutioner for børn og"
            + "unge med sociale adfærdsproblemer",
            "Beskrivelse": "Nr. 27.27.27\r\n\r\n* Emnet er til sager, hvor"
            + " barnet eller den unge anbringes i en døgninstitution for "
            + "børn og unge med sociale adfærdsproblemer.\r\n\r\nHenvisning"
            + " til andre relevante emner:\r\n\r\n* Anbringelse i sikrede"
            + " døgninstitutioner, se emne 27.27.48\r\n\r\n",
            "Niveau": 2,
            "Oprettet": "2009-05-01T00:00:00+02:00",
            "Rettet": "2017-02-01T00:00:00+01:00",
            "ErUdgaaet": False,
            "AfloserNumre": [],
        },
        "Facet": {
            "ID": 800,
            "FacetTypeID": 1339,
            "Nummer": "I10",
            "Navn": "Kopisager fra andre myndigheder",
            "Beskrivelse": "I10 anvendes til sager, hvor"
            + " afleveringsforpligtelsen i henhold til arkivloven er"
            + " løst/løses af anden myndighed. Handlingsfacetten anvendes"
            + " til sager fra de tidligere amter. Hvis der på baggrund af"
            + " oplysninger fra en af disse sager sker en sagsbehandling, "
            + "skal der oprettes en ny sag, eventuel med en reference til"
            + " I10-sagen.\r\n",
            "BevaringID": 10,
            "Oprettet": "2006-12-01T00:00:00+01:00",
            "Rettet": "2011-02-01T00:00:00+01:00",
        },
        "Aarstal": 2022,
        "SekvensNummer": 2,
    },
}


def mocked_requests_post(*args, **kwargs):
    return MockResponse({"access_token": "12345678"}, 200)


def mocked_requests_get(*args, **kwargs):
    return MockResponse(example_sbsys_data, 200)


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
