from unittest import mock
from django.urls import reverse
from django.contrib.auth import get_user_model

from .test_utils import AuthenticatedTestCase
from core.tests.testing_mixins import CaseMixin
from core.models import STEP_ONE, STEP_THREE, STEP_FIVE


class TestRelatedPersonsViewSet(AuthenticatedTestCase):
    def test_fetch_from_serviceplatformen_no_cpr(self):
        reverse_url = reverse("relatedperson-fetch-from-serviceplatformen")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"errors": "Intet CPR nummer angivet"}
        )

    @mock.patch("core.views.get_person_info", lambda cpr: None)
    def test_fetch_from_serviceplatformen_wrong_cpr(self):
        reverse_url = reverse("relatedperson-fetch-from-serviceplatformen")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url, data={"cpr": "1234567890"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"errors": ["Fejl i CPR eller forbindelse til Serviceplatformen"]},
        )

    @mock.patch("core.views.get_person_info")
    def test_fetch_from_serviceplatformen_success(self, person_info_mock):
        person_info_data = {
            "adresseringsnavn": "Bo Jensen",
            "relationer": [
                {
                    "cprnr": "0123456780",
                    "relation": "aegtefaelle",
                    "adresseringsnavn": "Iben Jensen",
                },
                {
                    "cprnr": "2123456789",
                    "relation": "barn",
                    "adresseringsnavn": "Ib Jensen",
                },
                {
                    "cprnr": "0000000000",
                    "relation": "mor",
                    "adresseringsnavn": "Ingeborg Jensen",
                },
                {
                    "cprnr": "0000000000",
                    "relation": "far",
                    "adresseringsnavn": "Gunnar Jensen",
                },
            ],
        }
        person_info_mock.return_value = person_info_data
        reverse_url = reverse("relatedperson-fetch-from-serviceplatformen")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url, data={"cpr": "1234567890"})

        self.assertEqual(response.status_code, 200)
        expected_format = [
            {
                "cpr_number": "0123456780",
                "relation_type": "aegtefaelle",
                "name": "Iben Jensen",
            },
            {
                "cpr_number": "2123456789",
                "relation_type": "barn",
                "name": "Ib Jensen",
            },
            {
                "cpr_number": "0000000000",
                "relation_type": "mor",
                "name": "Ingeborg Jensen",
            },
            {
                "cpr_number": "0000000000",
                "relation_type": "far",
                "name": "Gunnar Jensen",
            },
        ]
        self.assertEqual(response.json(), expected_format)


class TestCaseViewSet(AuthenticatedTestCase, CaseMixin):
    def test_history_action_no_history(self):
        case = self.create_case()
        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["scaling_step"], 1)

    def test_history_action_changed_scaling_steps(self):
        case = self.create_case()
        # Change to different scaling steps.
        case.scaling_step = 5
        case.save()
        case.scaling_step = 2
        case.save()

        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        self.assertEqual(len(response.json()), 3)
        # Assert history of scaling steps are preserved.
        self.assertCountEqual(
            [x["scaling_step"] for x in response.json()], [5, 2, 1]
        )

    def test_history_action_changed_effort_steps(self):
        case = self.create_case()
        # Change to different effort steps.
        case.effort_step = STEP_THREE
        case.save()
        case.effort_step = STEP_FIVE
        case.save()

        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        self.assertEqual(len(response.json()), 3)
        # Assert history of scaling steps are preserved.
        self.assertCountEqual(
            [x["effort_step"] for x in response.json()],
            [STEP_ONE, STEP_THREE, STEP_FIVE],
        )

    def test_history_action_changed_case_worker(self):
        case = self.create_case()
        # Change to different effort steps.
        orla = case.case_worker
        leif = get_user_model().objects.create(username="Leif")
        case.case_worker = leif
        case.save()
        lone = get_user_model().objects.create(username="Lone")
        case.case_worker = lone
        case.save()

        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        self.assertEqual(len(response.json()), 3)
        # Assert history of scaling steps are preserved.
        self.assertCountEqual(
            [x["case_worker"] for x in response.json()],
            [orla.id, leif.id, lone.id],
        )

    def test_simple_post(self):
        url = reverse("case-list")
        json = self.create_case_as_json()
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 201)
