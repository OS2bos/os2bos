# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from unittest import mock
from datetime import date, timedelta

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import (
    ApprovalLevel,
    PaymentSchedule,
    Payment,
    EffortStep,
    MAIN_ACTIVITY,
    SUPPL_ACTIVITY,
    STATUS_GRANTED,
    STATUS_DRAFT,
    STATUS_EXPECTED,
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
)


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
            "relations": [
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
            ],
        }
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
        # team should be set on the user and also saved on the case.
        self.user.team = self.team
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["team"], self.team.id)

    def test_different_profiles(self):
        url = reverse("case-list")
        # Readonly user
        json = create_case_as_json(
            self.case_worker, self.team, self.municipality, self.district
        )
        self.user.team = self.team
        self.user.profile = "readonly"
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 403)
        # User can edit
        json = create_case_as_json(
            self.case_worker, self.team, self.municipality, self.district
        )
        self.user.profile = "edit"
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(url, json)
        self.assertEqual(response.status_code, 201)
        # No profile
        json = create_case_as_json(
            self.case_worker, self.team, self.municipality, self.district
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
            self.case_worker, self.team, self.municipality, self.district
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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

        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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

        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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

        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT
        )
        # Create a suppl activity without setting its allowed main_activities.
        suppl_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
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
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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

        payment_schedule = create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT
        )
        # Create a suppl activity without setting its allowed main_activities.
        suppl_activity = create_activity(
            case,
            appropriation,
            start_date=now - timedelta(days=5),
            end_date=now - timedelta(days=5),
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
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

    @mock.patch("core.models.send_appropriation")
    def test_grant_one_time_in_past_included(self, send_appropriation_mock):
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

    def test_grant_granted(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        section = create_section()
        appropriation = create_appropriation(
            sbsys_id="XXX-YYY", case=case, section=section
        )
        start_date = timezone.now().date()
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=date(year=2020, month=12, day=24),
            status=STATUS_GRANTED,
            activity_type=MAIN_ACTIVITY,
            payment_plan=payment_schedule,
        )
        section.main_activities.add(activity.details)
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        modifying_activity = create_activity(
            case,
            appropriation,
            start_date=start_date + timedelta(days=1),
            end_date=date(year=2022, month=12, day=24),
            status=STATUS_EXPECTED,
            activity_type=MAIN_ACTIVITY,
            modifies=activity,
            payment_plan=payment_schedule,
        )
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        draft_activity = create_activity(
            case,
            appropriation,
            start_date=start_date,
            end_date=date(year=2023, month=12, day=24),
            status=STATUS_DRAFT,
            activity_type=SUPPL_ACTIVITY,
            payment_plan=payment_schedule,
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

    def test_no_approval_level(self):
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
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
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        now = timezone.now()
        create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )

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
        payment_schedule = create_payment_schedule()
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)

        now = timezone.now()
        create_activity(
            case=case,
            appropriation=appropriation,
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
            start_date=date(year=now.year, month=1, day=1),
            end_date=date(year=now.year, month=1, day=1),
        )

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


class TestActivityViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_get(self):
        now = timezone.now().date()
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_GRANTED,
            payment_plan=payment_schedule,
        )
        url = reverse("activity-list")
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["id"], activity.id)

    def test_delete(self):
        now = timezone.now().date()
        payment_schedule = create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY,
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
        )
        case = create_case(
            self.case_worker, self.team, self.municipality, self.district
        )
        appropriation = create_appropriation(case=case)
        activity1 = create_activity(
            case=case,
            appropriation=appropriation,
            start_date=now - timedelta(days=6),
            end_date=now + timedelta(days=6),
            activity_type=MAIN_ACTIVITY,
            status=STATUS_DRAFT,
            payment_plan=payment_schedule,
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
            payment_plan=create_payment_schedule(),
        )
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
            payment_plan=create_payment_schedule(),
        )
        url = reverse("activity-detail", kwargs={"pk": activity3.pk})
        # Delete.
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 400)
        # Check it's still there.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestSectionViewSet(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_allowed_for_steps_filter(self):
        url = reverse("section-list")
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url, data={"allowed_for_steps": 1})
        self.assertEqual(response.status_code, 200)
