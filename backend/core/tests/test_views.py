from unittest import mock
from datetime import date, timedelta

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Activity, ApprovalLevel, Appropriation, PaymentSchedule

from core.tests.testing_utils import (
    AuthenticatedTestCase,
    BasicTestMixin,
    create_case,
    create_case_as_json,
    create_appropriation,
    create_activity,
    create_appropriation,
    create_payment_schedule,
)
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


class TestCaseViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_history_action_no_history(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["scaling_step"], 1)

    def test_history_action_changed_scaling_steps(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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

    def test_patch_history_change_reason_is_saved(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        # Assert no note is saved initially.
        self.assertEqual(len(response.json()), 1)
        self.assertIsNone(response.json()[0]["history_change_reason"])

        # Update with a history_change_reason.
        reverse_url = reverse("case-detail", kwargs={"pk": case.pk})
        response = self.client.patch(
            reverse_url,
            {"history_change_reason": "history was changed"},
            content_type="application/json",
        )
        # Assert note is now saved
        reverse_url = reverse("case-history", kwargs={"pk": case.pk})
        response = self.client.get(reverse_url)

        self.assertEqual(len(response.json()), 2)
        self.assertEqual(
            response.json()[0]["history_change_reason"], "history was changed"
        )

    def test_patch_is_saved(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )

        self.client.login(username=self.username, password=self.password)

        reverse_url = reverse("case-detail", kwargs={"pk": case.pk})
        response = self.client.get(reverse_url)
        self.assertEqual(response.json()["name"], "Jens Jensen")

        # Update with a new name.
        response = self.client.patch(
            reverse_url, {"name": "new name"}, content_type="application/json"
        )
        # Assert note is now saved
        response = self.client.get(reverse_url)

        self.assertEqual(response.json()["name"], "new name")

    def test_simple_post(self):
        url = reverse("case-list")
        json = create_case_as_json(
            self.case_worker, self.team, self.municipality, self.district
        )
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 201)

    def test_get_expired_filter(self):
        url = reverse("case-list")
        self.client.login(username=self.username, password=self.password)

        now = timezone.now().date()
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # create a main activity with an expired end_date.
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now - timedelta(days=1),
            activity_type=Activity.MAIN_ACTIVITY,
            status=Activity.STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        data = {"expired": True}
        response = self.client.get(url, data)

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], case.id)

        data = {"expired": False}
        response = self.client.get(url, data)
        self.assertEqual(len(response.json()), 0)

    def test_get_non_expired_filter(self):
        url = reverse("case-list")
        self.client.login(username=self.username, password=self.password)

        now = timezone.now().date()
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        # create a main activity with an expired end_date.
        expired_activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=1),
            activity_type=Activity.MAIN_ACTIVITY,
            status=Activity.STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        data = {"expired": False}
        response = self.client.get(url, data)

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], case.id)

        data = {"expired": True}
        response = self.client.get(url, data)
        self.assertEqual(len(response.json()), 0)


class TestAppropriationViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_grant_new(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, status=Appropriation.STATUS_DRAFT
        )
        create_activity(
            case,
            appropriation,
            end_date=date(year=2020, month=12, day=24),
            activity_type=Activity.MAIN_ACTIVITY,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {"approval_level": approval_level.id}
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_grant_discontinued(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY",
            case=case,
            status=Appropriation.STATUS_DISCONTINUED,
        )
        activity = create_activity(  # noqa - it *will* be used.
            case,
            appropriation,
            end_date=date(year=2020, month=12, day=24),
            activity_type=Activity.MAIN_ACTIVITY,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {"approval_level": approval_level.id, "approval_note": "Hej!"}
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_grant_granted(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, status=Appropriation.STATUS_GRANTED
        )
        activity = create_activity(  # noqa - it *will* be used.
            case,
            appropriation,
            end_date=date(year=2020, month=12, day=24),
            status=Activity.STATUS_GRANTED,
            activity_type=Activity.MAIN_ACTIVITY,
        )
        modifying_activity = create_activity(  # noqa - it *will* be used.
            case,
            appropriation,
            end_date=date(year=2022, month=12, day=24),
            status=Activity.STATUS_EXPECTED,
            activity_type=Activity.MAIN_ACTIVITY,
            modifies=activity,
        )
        draft_activity = create_activity(  # noqa - it *will* be used.
            case,
            appropriation,
            end_date=date(year=2023, month=12, day=24),
            status=Activity.STATUS_DRAFT,
            activity_type=Activity.SUPPL_ACTIVITY,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {"approval_level": approval_level.id, "approval_note": "HEJ!"}
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_no_approval_level(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, status=Appropriation.STATUS_DRAFT
        )
        activity = create_activity(  # noqa - it *will* be used.
            case,
            appropriation,
            end_date=date(year=2020, month=12, day=24),
            activity_type=Activity.MAIN_ACTIVITY,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        json = {"approval_note": "Hello!"}
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_grant_granted_no_approval_note_or_level(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, status=Appropriation.STATUS_GRANTED
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        json = {}
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
