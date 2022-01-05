# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest import mock
from datetime import date, timedelta
from decimal import Decimal

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.test import override_settings

from parameterized import parameterized
from freezegun import freeze_time

from core.models import (
    ApprovalLevel,
    PaymentSchedule,
    Payment,
    EffortStep,
    ServiceProvider,
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    STATUS_GRANTED,
    STATUS_DRAFT,
    STATUS_EXPECTED,
    INTERNAL,
)

from core.tests.testing_utils import (
    AuthenticatedTestCase,
    BasicTestMixin,
    create_case,
    create_section,
    create_case_as_json,
    create_appropriation,
    create_activity,
    create_payment_schedule,
    create_user,
    create_activity_details,
    create_service_provider,
    create_related_person,
)

User = get_user_model()


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
        expected_format = {
            "name": "Bo Jensen",
            "from_serviceplatformen": True,
            "relations": [
                {
                    "cpr_number": "0123456780",
                    "relation_type": "aegtefaelle",
                    "name": "Iben Jensen",
                    "from_serviceplatformen": True,
                },
                {
                    "cpr_number": "2123456789",
                    "relation_type": "barn",
                    "name": "Ib Jensen",
                    "from_serviceplatformen": True,
                },
                {
                    "cpr_number": "0000000000",
                    "relation_type": "mor",
                    "name": "Ingeborg Jensen",
                    "from_serviceplatformen": True,
                },
                {
                    "cpr_number": "0000000000",
                    "relation_type": "far",
                    "name": "Gunnar Jensen",
                    "from_serviceplatformen": True,
                },
            ],
        }
        self.assertEqual(response.json(), expected_format)


class TestCaseViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_history_action_no_history(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["scaling_step"], 1)

    def test_history_action_changed_scaling_steps(self):
        case = create_case(self.case_worker, self.municipality, self.district)
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
        case = create_case(self.case_worker, self.municipality, self.district)
        # Change to different effort steps.
        case.effort_step = EffortStep.objects.get(number=3)
        case.save()
        case.effort_step = EffortStep.objects.get(number=5)
        case.save()

        reverse_url = reverse("case-history", kwargs={"pk": case.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        self.assertEqual(len(response.json()), 3)
        # Assert history of scaling steps are preserved.
        """"
        self.assertCountEqual(
            [x["effort_step"] for x in response.json()],
            [1, 2, 3],
        )
        """

    def test_history_action_changed_case_worker(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        # Change to different effort steps.
        orla = case.case_worker
        leif = User.objects.create(username="Leif")
        case.case_worker = leif
        case.save()
        lone = User.objects.create(username="Lone")
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

    def test_patch_is_saved(self):
        case = create_case(self.case_worker, self.municipality, self.district)

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
            self.case_worker, self.municipality, self.district
        )
        # team should be set on the user
        self.user.team = self.team
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)

        self.assertEqual(response.status_code, 201)

    def test_different_profiles(self):
        url = reverse("case-list")
        # Readonly user
        json = create_case_as_json(
            self.case_worker, self.municipality, self.district
        )
        self.user.team = self.team
        self.user.profile = "readonly"
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 403)
        # User can edit
        json = create_case_as_json(
            self.case_worker, self.municipality, self.district
        )
        self.user.profile = "edit"
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 201)
        # No profile
        json = create_case_as_json(
            self.case_worker, self.municipality, self.district
        )
        self.user.profile = ""
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 403)

    def test_no_login(self):
        url = reverse("case-list")
        # Anonymous user
        json = create_case_as_json(
            self.case_worker, self.municipality, self.district
        )
        self.user = None
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 403)

    def test_get_expired_filter(self):
        url = reverse("case-list")
        self.client.login(username=self.username, password=self.password)

        now = timezone.now().date()
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create a main activity with an expired end_date.
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now - timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
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
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        # create a main activity with an expired end_date.
        create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=1),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        data = {"expired": False}
        response = self.client.get(url, data)

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], case.id)

        data = {"expired": True}
        response = self.client.get(url, data)
        self.assertEqual(len(response.json()), 0)

    def test_get_non_expired_filter_no_activities(self):
        url = reverse("case-list")
        self.client.login(username=self.username, password=self.password)

        case = create_case(self.case_worker, self.municipality, self.district)
        create_appropriation(case=case)

        data = {"expired": False}
        response = self.client.get(url, data)

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], case.id)

        data = {"expired": True}
        response = self.client.get(url, data)
        self.assertEqual(len(response.json()), 0)

    def test_get_non_expired_filter_no_appropriations(self):
        url = reverse("case-list")
        self.client.login(username=self.username, password=self.password)
        case = create_case(self.case_worker, self.municipality, self.district)
        data = {"expired": False}
        response = self.client.get(url, data)

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], case.id)

        data = {"expired": True}
        response = self.client.get(url, data)
        self.assertEqual(len(response.json()), 0)

    def test_change_case_worker(self):
        url = reverse("case-change-case-worker")
        self.client.login(username=self.username, password=self.password)

        case = create_case(self.case_worker, self.municipality, self.district)
        new_case_worker = create_user(username="Jens Tester")
        data = {"case_pks": [case.pk], "case_worker_pk": new_case_worker.pk}
        response = self.client.patch(
            url, data=data, content_type="application/json"
        )

        case.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["id"], case.id)
        self.assertEqual(case.case_worker, new_case_worker)

    def test_change_case_worker_missing_case_pks(self):
        url = reverse("case-change-case-worker")
        self.client.login(username=self.username, password=self.password)

        new_case_worker = create_user(username="Jens Tester")
        data = {"case_worker_pk": new_case_worker.pk}
        response = self.client.patch(
            url, data=data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["errors"],
            ["case_pks eller case_worker_pk argument mangler"],
        )

    def test_change_case_worker_missing_case_worker_pk(self):
        url = reverse("case-change-case-worker")
        self.client.login(username=self.username, password=self.password)
        case = create_case(self.case_worker, self.municipality, self.district)
        data = {"case_pks": [case.pk]}
        response = self.client.patch(
            url, data=data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["errors"],
            ["case_pks eller case_worker_pk argument mangler"],
        )

    def test_change_case_worker_non_existant_case_worker(self):
        url = reverse("case-change-case-worker")
        self.client.login(username=self.username, password=self.password)
        case = create_case(self.case_worker, self.municipality, self.district)
        data = {"case_pks": [case.pk], "case_worker_pk": 999}
        response = self.client.patch(
            url, data=data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["errors"],
            ["bruger med case_worker_pk findes ikke"],
        )


class TestAppropriationViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_grant_new(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        activity = create_activity(
            case,
            appropriation,
            end_date=date(year=2020, month=12, day=24),
            activity_type=MAIN_ACTIVITY,
        )
        section.main_activities.add(activity.details)
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "activities": [activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_grant_no_activities(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(sbsys_id="XXX-YYY", case=case)
        create_activity(
            case,
            appropriation,
            end_date=date(year=2020, month=12, day=24),
            activity_type=MAIN_ACTIVITY,
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
        self.assertEqual(response.status_code, 400)

    def test_grant_wrong_activity(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation1 = create_appropriation(sbsys_id="XXX-YYY", case=case)
        appropriation2 = create_appropriation(sbsys_id="YYY-XXX", case=case)
        activity = create_activity(
            case,
            appropriation2,
            end_date=date(year=2020, month=12, day=24),
            activity_type=MAIN_ACTIVITY,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation1.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "activities": [activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_grant_main_activity_not_allowed(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        now = timezone.now().date()
        main_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=5),
            activity_type=MAIN_ACTIVITY,
        )
        section.main_activities.add(main_activity.details)

        # Create a suppl activity without setting its allowed main_activities.
        suppl_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=suppl_activity,
        )
        section.supplementary_activities.add(suppl_activity.details)

        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "activities": [main_activity.pk, suppl_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["errors"][0],
            "En af følgeydelserne kan ikke bevilges"
            " på den angivne hovedaktivitet",
        )

    def test_grant_suppl_activity_not_allowed(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        now = timezone.now().date()
        main_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=5),
            activity_type=MAIN_ACTIVITY,
        )
        section.main_activities.add(main_activity.details)

        # Create a suppl activity without setting its allowed main_activities.
        suppl_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=suppl_activity,
        )
        suppl_activity.details.main_activities.add(main_activity.details)

        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "activities": [main_activity.pk, suppl_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["errors"][0],
            "En af følgeydelserne kan ikke bevilges"
            " på den angivne paragraf",
        )

    def test_grant_no_granted_main_activity_not_allowed(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        now = timezone.now().date()
        main_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now + timedelta(days=5),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        section.main_activities.add(main_activity.details)

        # Create a suppl activity without setting its allowed main_activities.
        suppl_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=suppl_activity,
        )
        section.supplementary_activities.add(suppl_activity.details)
        suppl_activity.details.main_activities.add(main_activity.details)
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "activities": [suppl_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["errors"][0],
            "Kan ikke godkende følgeydelser, før hovedydelsen er godkendt.",
        )

    @mock.patch("core.models.send_appropriation")
    def test_grant_one_time_in_past_included(self, send_appropriation_mock):
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
        )
        section.main_activities.add(activity.details)

        one_time_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            activity=one_time_activity,
        )
        section.supplementary_activities.add(one_time_activity.details)
        one_time_activity.details.main_activities.add(activity.details)

        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "activities": [activity.pk, one_time_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        # Assert one_time_activity was sent in call to send_appropriation.
        self.assertIn(
            one_time_activity, send_appropriation_mock.call_args[0][1]
        )

    @freeze_time("2020-01-01")
    def test_grant_granted(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        start_date = timezone.now().date()
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=date(year=2020, month=12, day=24),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        section.main_activities.add(activity.details)

        modifying_activity = create_activity(
            case,
            appropriation,
            start_date=start_date + timedelta(days=1),
            end_date=date(year=2022, month=12, day=24),
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=modifying_activity,
        )

        draft_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=date(year=2023, month=12, day=24),
            status=STATUS_DRAFT,
            activity_type=SUPPL_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=draft_activity,
        )
        section.supplementary_activities.add(draft_activity.details)
        draft_activity.details.main_activities.add(activity.details)

        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "approval_note": "HEJ!",
            "activities": [modifying_activity.pk, draft_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    @freeze_time("2020-01-01")
    def test_grant_granted_in_future_deletes_old(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        start_date = date(year=2020, month=2, day=1)
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=date(year=2020, month=3, day=1),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        section.main_activities.add(activity.details)

        modifying_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=date(year=2020, month=5, day=1),
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=modifying_activity,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        json = {
            "approval_level": approval_level.id,
            "approval_note": "HEJ!",
            "activities": [modifying_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Assert old activity is deleted and all
        # modifying_activity payments are there.
        with self.assertRaises(ObjectDoesNotExist):
            activity.refresh_from_db()
        self.assertEqual(modifying_activity.payment_plan.payments.count(), 91)

    def test_no_approval_level(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(sbsys_id="XXX-YYY", case=case)
        activity = create_activity(
            case,
            appropriation,
            end_date=date(year=2020, month=12, day=24),
            activity_type=MAIN_ACTIVITY,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        self.client.login(username=self.username, password=self.password)
        json = {"approval_note": "Hello!", "activities": [activity.pk]}
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    @freeze_time("2020-01-01")
    def test_filter_main_activity__details__id(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        section = create_section()
        approval_level, _ = ApprovalLevel.objects.get_or_create(
            name="egenkompetence"
        )
        # Create an appropriation that should have
        # main_activity_details_id = details.id
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        details = create_activity_details(
            name="test aktivitetsdetalje", activity_id="111112"
        )
        expected_details = create_activity_details(
            name="test forventet aktivitetsdetalje", activity_id="111115"
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=1, day=10),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        section.main_activities.add(activity.details, expected_details)

        modifying_activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=7),
            end_date=date(year=2020, month=1, day=20),
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
            details=details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=modifying_activity,
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        json = {
            "approval_level": approval_level.id,
            "approval_note": "HEJ!",
            "activities": [modifying_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        # Create an appropriation that should have
        # main_activity_details_id = expected_details.id
        appropriation = create_appropriation(
            sbsys_id="YYY-XXX", case=case, section=section
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=1, day=10),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=expected_details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        modifying_activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=7),
            end_date=date(year=2020, month=1, day=20),
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
            details=expected_details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=modifying_activity,
        )
        url = reverse("appropriation-grant", kwargs={"pk": appropriation.pk})
        json = {
            "approval_level": approval_level.id,
            "approval_note": "HEJ!",
            "activities": [modifying_activity.pk],
        }
        response = self.client.patch(
            url, json, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        url = reverse("appropriation-list")
        json = {"main_activity__details__id": details.id}
        response = self.client.get(url, json, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["main_activity__details__id"], details.id
        )

        url = reverse("appropriation-list")
        json = {"main_activity__details__id": expected_details.id}
        response = self.client.get(url, json, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["main_activity__details__id"],
            expected_details.id,
        )

    @freeze_time("2022-01-01")
    def test_generate_dst_preventative_measures_file_success(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(main_case=case)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        details = create_activity_details(
            name="test aktivitetsdetalje", activity_id="111112"
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=1, day=10),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("appropriation-generate-dst-preventative-measures-file")

        response = self.client.get(url, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            "attachment; filename=P_151_T201_P2022M01_V01_D20220101T000000.xml"
        )

    @freeze_time("2022-01-01")
    def test_generate_dst_preventative_measures_file_specific_section(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(main_case=case)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        details = create_activity_details(
            name="test aktivitetsdetalje", activity_id="111112"
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=1, day=10),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("appropriation-generate-dst-preventative-measures-file")
        json = {"sections": section.id}
        response = self.client.get(url, json, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            "attachment; filename=P_151_T201_P2022M01_V01_D20220101T000000.xml"
        )

    @freeze_time("2022-01-01")
    def test_generate_dst_handicap_file_success(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(main_case=case)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        details = create_activity_details(
            name="test aktivitetsdetalje", activity_id="111112"
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=1, day=10),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("appropriation-generate-dst-handicap-file")

        response = self.client.get(url, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            "attachment; filename=P_151_T231_P2022M01_V01_D20220101T000000.xml"
        )

    @freeze_time("2022-01-01")
    def test_generate_dst_handicap_file_specific_section(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        create_related_person(main_case=case)
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )

        details = create_activity_details(
            name="test aktivitetsdetalje", activity_id="111112"
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=1, day=10),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            details=details,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )

        self.client.login(username=self.username, password=self.password)
        url = reverse("appropriation-generate-dst-handicap-file")

        json = {"sections": section.id}
        response = self.client.get(url, json, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            "attachment; filename=P_151_T231_P2022M01_V01_D20220101T000000.xml"
        )

class TestPaymentScheduleViewSet(AuthenticatedTestCase):
    def test_get(self):
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        url = reverse("paymentschedule-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["id"], payment_schedule.id)


class TestPaymentViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_get_payment_date_or_date__gte_filter(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        now = timezone.now()
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )
        create_payment_schedule(activity=activity)

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)

        cutoff_date = date(year=now.year, month=1, day=5)
        response = self.client.get(
            url, data={"paid_date_or_date__gte": f"{cutoff_date}"}
        )
        ids_list = [payment["id"] for payment in response.json()["results"]]
        self.assertEqual(response.status_code, 200)
        self.assertSequenceEqual(
            ids_list,
            Payment.objects.paid_date_or_date_gte(cutoff_date).values_list(
                "id", flat=True
            ),
        )

    def test_get_payment_date_or_date__lte_filter(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        now = timezone.now()
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )
        create_payment_schedule(activity=activity)

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)
        cutoff_date = date(year=now.year, month=1, day=5)
        response = self.client.get(
            url, data={"paid_date_or_date__lte": f"{cutoff_date}"}
        )
        ids_list = [payment["id"] for payment in response.json()["results"]]
        self.assertEqual(response.status_code, 200)
        self.assertSequenceEqual(
            ids_list,
            Payment.objects.paid_date_or_date_lte(cutoff_date).values_list(
                "id", flat=True
            ),
        )

    @parameterized.expand(
        [
            (
                "previous",
                [
                    "2019-12-23",
                    "2019-12-24",
                    "2019-12-25",
                    "2019-12-26",
                    "2019-12-27",
                    "2019-12-28",
                    "2019-12-29",
                ],
            ),
            (
                "current",
                [
                    "2019-12-30",
                    "2019-12-31",
                    "2020-01-01",
                    "2020-01-02",
                    "2020-01-03",
                    "2020-01-04",
                    "2020-01-05",
                ],
            ),
            (
                "next",
                [
                    "2020-01-06",
                    "2020-01-07",
                    "2020-01-08",
                    "2020-01-09",
                    "2020-01-10",
                    "2020-01-11",
                    "2020-01-12",
                ],
            ),
        ]
    )
    @freeze_time("2020-01-01")
    def test_filter_paid_date_or_date_week(self, argument, dates):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2019, month=12, day=1),
            end_date=date(year=2020, month=2, day=1),
        )
        payment_schedule = create_payment_schedule(
            activity=activity, payment_frequency=PaymentSchedule.DAILY
        )
        payment_schedule.payments.update(paid_date=F("date"))

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(
            url, data={"paid_date_or_date_week": argument}
        )
        payments = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            dates, [payment["paid_date"] for payment in payments]
        )

    @parameterized.expand(
        [
            (
                "previous",
                [
                    "2019-12-23",
                    "2019-12-24",
                    "2019-12-25",
                    "2019-12-26",
                    "2019-12-27",
                    "2019-12-28",
                    "2019-12-29",
                ],
            ),
            (
                "current",
                [
                    "2019-12-30",
                    "2019-12-31",
                    "2020-01-01",
                    "2020-01-02",
                    "2020-01-03",
                    "2020-01-04",
                    "2020-01-05",
                ],
            ),
            (
                "next",
                [
                    "2020-01-06",
                    "2020-01-07",
                    "2020-01-08",
                    "2020-01-09",
                    "2020-01-10",
                    "2020-01-11",
                    "2020-01-12",
                ],
            ),
        ]
    )
    @freeze_time("2020-01-01")
    def test_filter_date_week(self, argument, dates):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2019, month=12, day=1),
            end_date=date(year=2020, month=2, day=1),
        )
        create_payment_schedule(
            activity=activity, payment_frequency=PaymentSchedule.DAILY
        )

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url, data={"date_week": argument})
        payments = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(dates, [payment["date"] for payment in payments])

    @parameterized.expand(
        [
            ("previous", ["2020-01-01"]),
            ("current", ["2020-02-01"]),
            ("next", ["2020-03-01"]),
        ]
    )
    @freeze_time("2020-02-01")
    def test_filter_paid_date_or_date_month(self, argument, dates):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=4, day=1),
        )
        create_payment_schedule(
            activity=activity, payment_frequency=PaymentSchedule.MONTHLY
        )

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(
            url, data={"paid_date_or_date_month": argument}
        )
        payments = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(dates, [payment["date"] for payment in payments])

    @parameterized.expand(
        [
            ("previous", ["2020-01-01"]),
            ("current", ["2020-02-01"]),
            ("next", ["2020-03-01"]),
        ]
    )
    @freeze_time("2020-02-01")
    def test_filter_date_month(self, argument, dates):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2020, month=1, day=1),
            end_date=date(year=2020, month=4, day=1),
        )
        payment_schedule = create_payment_schedule(
            activity=activity, payment_frequency=PaymentSchedule.MONTHLY
        )
        payment_schedule.payments.update(paid_date=F("date"))

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url, data={"date_month": argument})
        payments = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            dates, [payment["paid_date"] for payment in payments]
        )

    @parameterized.expand(
        [
            ("previous", ["2019-10-01", "2019-11-01", "2019-12-01"]),
            (
                "current",
                [
                    "2020-01-01",
                    "2020-02-01",
                    "2020-03-01",
                    "2020-04-01",
                    "2020-05-01",
                    "2020-06-01",
                    "2020-07-01",
                    "2020-08-01",
                    "2020-09-01",
                    "2020-10-01",
                    "2020-11-01",
                    "2020-12-01",
                ],
            ),
            ("next", ["2021-01-01", "2021-02-01"]),
        ]
    )
    @freeze_time("2020-01-01")
    def test_filter_paid_date_or_date_year(self, argument, dates):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2019, month=10, day=1),
            end_date=date(year=2021, month=2, day=1),
        )
        payment_schedule = create_payment_schedule(
            activity=activity, payment_frequency=PaymentSchedule.MONTHLY
        )
        payment_schedule.payments.update(paid_date=F("date"))

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(
            url, data={"paid_date_or_date_year": argument}
        )
        payments = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            dates, [payment["paid_date"] for payment in payments]
        )

    @parameterized.expand(
        [
            ("previous", ["2019-10-01", "2019-11-01", "2019-12-01"]),
            (
                "current",
                [
                    "2020-01-01",
                    "2020-02-01",
                    "2020-03-01",
                    "2020-04-01",
                    "2020-05-01",
                    "2020-06-01",
                    "2020-07-01",
                    "2020-08-01",
                    "2020-09-01",
                    "2020-10-01",
                    "2020-11-01",
                    "2020-12-01",
                ],
            ),
            ("next", ["2021-01-01", "2021-02-01"]),
        ]
    )
    @freeze_time("2020-01-01")
    def test_filter_date_year(self, argument, dates):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=2019, month=10, day=1),
            end_date=date(year=2021, month=2, day=1),
        )
        create_payment_schedule(
            activity=activity, payment_frequency=PaymentSchedule.MONTHLY
        )

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url, data={"date_year": argument})
        payments = response.json()["results"]

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(dates, [payment["date"] for payment in payments])

    def test_post(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        now = timezone.now()
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )
        create_payment_schedule(activity=activity)

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        payment = response.json()["results"][0]
        payment = {k: v for k, v in payment.items() if v is not None}
        response = self.client.post(url, payment)
        self.assertEqual(response.status_code, 403)
        del payment["payment_schedule"]
        response = self.client.post(url, payment)
        self.assertEqual(response.status_code, 400)

    def test_delete(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        now = timezone.now()
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )
        create_payment_schedule(activity=activity)

        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        payment = response.json()["results"][0]
        payment_pk = payment["id"]
        detail_url = reverse("payment-detail", kwargs={"pk": payment_pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, 403)

    def test_put(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        now = timezone.now()
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )
        create_payment_schedule(
            activity=activity,
            payment_method=INTERNAL,
            recipient_type=PaymentSchedule.INTERNAL,
        )
        url = reverse("payment-list")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        payment = response.json()["results"][0]
        payment_pk = payment["id"]
        detail_url = reverse("payment-detail", kwargs={"pk": payment_pk})
        payment = {k: v for k, v in payment.items() if v is not None}
        response = self.client.put(
            detail_url, payment, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_history_action_no_history(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        now = timezone.now()
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )
        payment_schedule = create_payment_schedule(activity=activity)
        payment = payment_schedule.payments.first()

        reverse_url = reverse("payment-history", kwargs={"pk": payment.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["paid_date"], None)
        self.assertEqual(response.json()[0]["paid"], False)
        self.assertEqual(response.json()[0]["paid_amount"], None)

    def test_history_action_changed_paid_fields(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        now = timezone.now()
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )
        payment_schedule = create_payment_schedule(activity=activity)
        payment = payment_schedule.payments.first()

        # Pay the payment, generating a history object.
        payment.paid = True
        payment.paid_date = now
        payment.paid_amount = Decimal(100.0)
        payment.save()

        reverse_url = reverse("payment-history", kwargs={"pk": payment.pk})

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse_url)

        self.assertEqual(len(response.json()), 2)

        self.assertEqual(response.json()[0]["paid_date"], str(now.date()))
        self.assertEqual(response.json()[0]["paid"], True)
        self.assertEqual(response.json()[0]["paid_amount"], "100.00")
        self.assertIsNotNone(response.json()[0]["history_date"])

        self.assertEqual(response.json()[1]["paid_date"], None)
        self.assertEqual(response.json()[1]["paid"], False)
        self.assertEqual(response.json()[1]["paid_amount"], None)


class TestActivityViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_get(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        url = reverse("activity-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["id"], activity.id)

    def test_delete(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity1 = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity1,
        )
        url = reverse("activity-detail", kwargs={"pk": activity1.pk})
        self.client.login(username=self.username, password=self.password)
        # First, check the activity is there.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Delete.
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        # Now check the activity is gone gone gone!
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        activity2 = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_EXPECTED,
        )
        create_payment_schedule(activity=activity2)
        url = reverse("activity-detail", kwargs={"pk": activity2.pk})
        # Check it's there.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Delete.
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        # Check it's gone.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        activity3 = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_GRANTED,
        )
        create_payment_schedule(activity=activity3)
        url = reverse("activity-detail", kwargs={"pk": activity3.pk})
        # Delete.
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400)
        # Check it's still there.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_with_existing_service_provider(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        details = create_activity_details(
            name="test aktivitetsdetalje", activity_id="111112"
        )
        service_provider = create_service_provider(
            cvr_number="25052943", name="MAGENTA ApS"
        )
        url = reverse("activity-list")
        self.client.login(username=self.username, password=self.password)

        # Create an activity with a service provider that already exists
        # which should update it and assign it to the activity.
        data = {
            "status": "DRAFT",
            "appropriation": str(appropriation.pk),
            "activity_type": "SUPPL_ACTIVITY",
            "details": str(details.pk),
            "service_provider": {
                "cvr_number": "25052943",
                "name": "MAGENTA ApS #2",
                "street": "Pilestræde",
                "street_number": "43",
                "zip_code": "1112",
                "branch_code": "620200",
                "status": "NORMAL",
            },
            "payment_plan": {
                "payment_type": "ONE_TIME_PAYMENT",
                "payment_cost_type": "FIXED",
                "payment_amount": "200",
                "payment_date": "2021-07-20",
                "recipient_type": "COMPANY",
                "recipient_id": "25052943",
                "recipient_name": "MAGENTA ApS",
                "payment_method": "INVOICE",
                "payment_rate": None,
                "price_per_unit": None,
                "payment_units": None,
                "payment_day_of_month": None,
            },
        }
        response = self.client.post(
            url, data=data, content_type="application/json"
        )

        service_provider.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["service_provider"]["id"], service_provider.id
        )
        self.assertEqual(service_provider.name, "MAGENTA ApS #2")

    def test_post_with_new_service_provider(self):
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        details = create_activity_details(
            name="test aktivitetsdetalje", activity_id="111112"
        )
        url = reverse("activity-list")
        self.client.login(username=self.username, password=self.password)

        # Assert we start with no service providers.
        self.assertEqual(ServiceProvider.objects.count(), 0)
        # Create an activity with a service provider
        # that does not already exist.
        data = {
            "status": "DRAFT",
            "appropriation": str(appropriation.pk),
            "activity_type": "SUPPL_ACTIVITY",
            "details": str(details.pk),
            "service_provider": {
                "cvr_number": "25052943",
                "name": "MAGENTA ApS",
                "street": "Pilestræde",
                "street_number": "43",
                "zip_code": "1112",
                "branch_code": "620200",
                "status": "NORMAL",
            },
            "payment_plan": {
                "payment_type": "ONE_TIME_PAYMENT",
                "payment_cost_type": "FIXED",
                "payment_amount": "200",
                "payment_date": "2021-07-20",
                "recipient_type": "COMPANY",
                "recipient_id": "25052943",
                "recipient_name": "MAGENTA ApS",
                "payment_method": "INVOICE",
                "payment_rate": None,
                "price_per_unit": None,
                "payment_units": None,
                "payment_day_of_month": None,
            },
        }
        response = self.client.post(
            url, data=data, content_type="application/json"
        )

        service_provider = ServiceProvider.objects.first()
        self.assertEqual(ServiceProvider.objects.count(), 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["service_provider"]["id"], service_provider.id
        )

    def test_put_with_existing_service_provider(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_DRAFT,
        )
        payment_plan = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        service_provider = create_service_provider(
            cvr_number="25052943", name="MAGENTA ApS"
        )
        url = reverse("activity-detail", kwargs={"pk": activity.pk})
        self.client.login(username=self.username, password=self.password)

        # Create an activity with a service provider that already exists
        # which should update it and assign it to the activity.
        data = {
            "id": activity.id,
            "status": "DRAFT",
            "appropriation": str(appropriation.pk),
            "activity_type": "SUPPL_ACTIVITY",
            "details": str(activity.details.pk),
            "start_date": str(now - timedelta(days=6)),
            "end_date": str(now + timedelta(days=6)),
            "service_provider": {
                "cvr_number": "25052943",
                "name": "MAGENTA ApS #2",
                "street": "Pilestræde",
                "street_number": "43",
                "zip_code": "1112",
                "branch_code": "620200",
                "status": "NORMAL",
            },
            "payment_plan": {
                "id": payment_plan.pk,
                "payment_type": "RUNNING_PAYMENT",
                "payment_frequency": "DAILY",
                "payment_cost_type": "FIXED",
                "payment_amount": "200",
                "payment_date": "2021-07-20",
                "recipient_type": "COMPANY",
                "recipient_id": "25052943",
                "recipient_name": "MAGENTA ApS",
                "payment_method": "INVOICE",
                "payment_rate": None,
                "price_per_unit": None,
                "payment_units": None,
                "payment_day_of_month": None,
            },
        }
        response = self.client.put(
            url, data=data, content_type="application/json"
        )

        service_provider.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["service_provider"]["id"], service_provider.id
        )
        self.assertEqual(service_provider.name, "MAGENTA ApS #2")

    def test_put_with_new_service_provider(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
        )
        payment_plan = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        url = reverse("activity-detail", kwargs={"pk": activity.pk})
        self.client.login(username=self.username, password=self.password)

        # Assert we start with no service providers.
        self.assertEqual(ServiceProvider.objects.count(), 0)
        # Create an activity with a service provider
        # that does not already exist.
        data = {
            "id": activity.id,
            "status": "DRAFT",
            "appropriation": str(appropriation.pk),
            "activity_type": "SUPPL_ACTIVITY",
            "details": str(activity.details.pk),
            "start_date": str(now - timedelta(days=6)),
            "end_date": str(now + timedelta(days=6)),
            "service_provider": {
                "cvr_number": "25052943",
                "name": "MAGENTA ApS",
                "street": "Pilestræde",
                "street_number": "43",
                "zip_code": "1112",
                "branch_code": "620200",
                "status": "NORMAL",
            },
            "payment_plan": {
                "id": payment_plan.pk,
                "payment_type": "RUNNING_PAYMENT",
                "payment_frequency": "DAILY",
                "payment_cost_type": "FIXED",
                "payment_amount": "200",
                "payment_date": "2021-07-20",
                "recipient_type": "COMPANY",
                "recipient_id": "25052943",
                "recipient_name": "MAGENTA ApS",
                "payment_method": "INVOICE",
                "payment_rate": None,
                "price_per_unit": None,
                "payment_units": None,
                "payment_day_of_month": None,
            },
        }
        response = self.client.put(
            url, data=data, content_type="application/json"
        )
        service_provider = ServiceProvider.objects.first()
        self.assertEqual(ServiceProvider.objects.count(), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["service_provider"]["id"], service_provider.id
        )

    def test_patch_with_null_service_provider(self):
        now = timezone.now().date()
        case = create_case(self.case_worker, self.municipality, self.district)
        appropriation = create_appropriation(case=case)
        service_provider = create_service_provider()

        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=SUPPL_ACTIVITY,
            status=STATUS_DRAFT,
            service_provider=service_provider,
        )
        payment_plan = create_payment_schedule(
            payment_cost_type=PaymentSchedule.FIXED_PRICE,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            activity=activity,
        )
        url = reverse("activity-detail", kwargs={"pk": activity.pk})
        self.client.login(username=self.username, password=self.password)

        # Modify an activity removing a service provider from it.
        data = {
            "id": activity.id,
            "status": "DRAFT",
            "appropriation": str(appropriation.pk),
            "activity_type": "SUPPL_ACTIVITY",
            "details": str(activity.details.pk),
            "start_date": str(now - timedelta(days=6)),
            "end_date": str(now + timedelta(days=6)),
            "payment_plan": {
                "id": payment_plan.pk,
                "payment_type": "RUNNING_PAYMENT",
                "payment_frequency": "DAILY",
                "payment_cost_type": "FIXED",
                "payment_amount": "200",
                "payment_date": "2021-07-20",
                "recipient_type": "COMPANY",
                "recipient_id": "25052943",
                "recipient_name": "MAGENTA ApS",
                "payment_method": "INVOICE",
                "payment_rate": None,
                "price_per_unit": None,
                "payment_units": None,
                "payment_day_of_month": None,
            },
            "service_provider": None,
        }
        response = self.client.put(
            url, data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service_provider"], None)


class TestServiceProviderViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_fetch_serviceproviders_from_virk_action_correct_search_term(self):
        url = reverse("serviceprovider-fetch-serviceproviders-from-virk")

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url, data={"search_term": "MAGENTA"})

        test_service_providers = [
            {
                "cvr_number": "25052943",
                "name": "MAGENTA ApS",
                "street": "Pilestræde",
                "street_number": "43",
                "zip_code": "1112",
                "post_district": "København K",
                "business_code": "620200",
                "business_code_text": (
                    "Konsulentbistand vedrørende informationsteknologi"
                ),
                "status": "NORMAL",
            }
        ]
        self.assertEqual(response.json(), test_service_providers)

    def test_fetch_serviceproviders_from_virk_action_no_search_term(self):
        url = reverse("serviceprovider-fetch-serviceproviders-from-virk")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url)

        self.assertEqual(
            response.json(),
            {"errors": ["Der kræves en search_term parameter"]},
        )

    @mock.patch(
        "core.views.get_company_info_from_search_term", lambda search_term: []
    )
    def test_fetch_serviceproviders_from_virk_action_no_company_info(self):
        url = reverse("serviceprovider-fetch-serviceproviders-from-virk")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url, data={"search_term": "MAGENTA"})

        self.assertEqual(
            response.json(),
            {"errors": ["Fejl i søgning eller forbindelse til Virk"]},
        )


class TestSectionViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_allowed_for_steps_filter(self):
        url = reverse("section-list")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url, data={"allowed_for_steps": 1})
        self.assertEqual(response.status_code, 200)


class TestClassificationMixin(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_get_queryset_active_allowed_as_grant_user(self):
        section = create_section(active=True)
        url = reverse("section-list")
        # User has grant permissions.
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.json()[0]["id"], section.id)

    def test_get_queryset_inactive_disallowed_as_grant_user(self):
        create_section(active=False)
        url = reverse("section-list")
        # User has grant permissions.
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.json(), [])

    def test_queryset_active_allowed_as_workflow_user(self):
        self.user.profile = User.WORKFLOW_ENGINE
        self.user.save()

        section = create_section(active=True)
        url = reverse("section-list")
        # User has grant permissions.
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.json()[0]["id"], section.id)

    def test_queryset_inactive_allowed_as_workflow_user(self):
        self.user.profile = User.WORKFLOW_ENGINE
        self.user.save()

        section = create_section(active=False)
        url = reverse("section-list")
        # User has grant permissions.
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.json()[0]["id"], section.id)


class TestAuditModelViewSetMixin(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_case_perform_create(self):
        url = reverse("case-list")
        json = create_case_as_json(
            self.case_worker, self.municipality, self.district
        )
        self.user.team = self.team
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user_created"], self.username)

    def test_case_perform_update(self):
        url = reverse("case-list")
        json = create_case_as_json(
            self.case_worker, self.municipality, self.district
        )
        self.user.team = self.team
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)

        # Assert user_created is set but user_modified is not on creation.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user_created"], self.username)
        self.assertEqual(response.json()["user_modified"], "")
        # Assert user_modified is now set on modification.
        url = reverse("case-detail", kwargs={"pk": response.json()["id"]})
        response = self.client.patch(url, json={"cpr_number": "0123456789"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_modified"], self.username)

    def test_related_person_perform_create(self):
        case = create_case(self.case_worker, self.municipality, self.district)

        url = reverse("relatedperson-list")
        self.client.login(username=self.username, password=self.password)

        json = {"relation_type": "Far", "name": "Test", "main_case": case.id}
        response = self.client.post(url, json)

        # Assert user_created is set but user_modified is not on creation.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user_created"], self.username)
        self.assertEqual(response.json()["user_modified"], "")

    def test_related_person_perform_update(self):
        case = create_case(self.case_worker, self.municipality, self.district)

        url = reverse("relatedperson-list")
        self.client.login(username=self.username, password=self.password)

        json = {"relation_type": "Far", "name": "Test", "main_case": case.id}
        response = self.client.post(url, json)

        # Assert user_created is set but user_modified is not on creation.
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user_created"], self.username)
        self.assertEqual(response.json()["user_modified"], "")

        # Assert user_modified is now set on modification.
        url = reverse(
            "relatedperson-detail", kwargs={"pk": response.json()["id"]}
        )
        response = self.client.patch(url, json={"name": "Test patch"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_modified"], self.username)


class TestFrontendSettingsView(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    @override_settings(ALLOW_EDIT_OF_PAST_PAYMENTS=True)
    @override_settings(ALLOW_SERVICE_PROVIDERS_FROM_VIRK=True)
    def test_frontend_settings(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("frontend-settings")
        response = self.client.get(url)

        expected_response = {
            "ALLOW_EDIT_OF_PAST_PAYMENTS": True,
            "ALLOW_SERVICE_PROVIDERS_FROM_VIRK": True,
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)
