from datetime import date

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import (
    Payment,
    PaymentSchedule,
    ActivityDetails,
    Account,
    TargetGroup,
    Section,
)
from core.admin import (
    PaymentAdmin,
    PaymentScheduleAdmin,
    AccountAdmin,
    TargetGroupAdmin,
    ClassificationAdmin,
)
from core.tests.testing_utils import (
    AuthenticatedTestCase,
    BasicTestMixin,
    create_payment,
    create_payment_schedule,
    create_account,
    create_section,
    create_target_group,
)

User = get_user_model()


class MockRequest:
    pass


class TestPaymentAdmin(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_payment_id(self):
        payment_schedule = create_payment_schedule()

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
        )
        site = AdminSite()
        payment_admin = PaymentAdmin(Payment, site)
        self.assertEqual(
            payment_admin.payment_id(payment),
            payment.payment_schedule.payment_id,
        )

    def test_account_string(self):
        payment_schedule = create_payment_schedule()

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
        )
        site = AdminSite()
        payment_admin = PaymentAdmin(Payment, site)
        self.assertEqual(
            payment_admin.account_string(payment), payment.account_string
        )

    def test_account_string_new(self):
        payment_schedule = create_payment_schedule()

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
        )
        site = AdminSite()
        payment_admin = PaymentAdmin(Payment, site)
        self.assertEqual(
            payment_admin.account_string_new(payment),
            payment.account_string_new,
        )

    def test_payment_schedule_str(self):
        payment_schedule = create_payment_schedule()

        payment = create_payment(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
        )
        site = AdminSite()
        payment_admin = PaymentAdmin(Payment, site)

        self.assertIn(
            f"/api/admin/core/paymentschedule/{payment_schedule.id}/change/",
            payment_admin.payment_schedule_str(payment),
        )

    def test_admin_changelist_not_admin_user_disallowed(self):
        url = reverse("admin:core_payment_changelist")
        self.user.is_staff = True
        self.user.profile = User.WORKFLOW_ENGINE
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_admin_changelist_admin_user_allowed(self):
        url = reverse("admin:core_payment_changelist")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.profile = User.ADMIN
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class TestPaymentScheduleAdmin(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_account_string(self):
        payment_schedule = create_payment_schedule()

        site = AdminSite()
        payment_schedule_admin = PaymentScheduleAdmin(PaymentSchedule, site)
        self.assertEqual(
            payment_schedule_admin.account_string(payment_schedule),
            payment_schedule.account_string,
        )

    def test_admin_changelist_not_admin_user_disallowed(self):
        url = reverse("admin:core_paymentschedule_changelist")
        self.user.is_staff = True
        self.user.profile = User.WORKFLOW_ENGINE
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_admin_changelist_admin_user_allowed(self):
        url = reverse("admin:core_paymentschedule_changelist")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.profile = User.ADMIN
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class TestAppropriationAdmin(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_admin_changelist_not_admin_user_disallowed(self):
        url = reverse("admin:core_appropriation_changelist")
        self.user.is_staff = True
        self.user.profile = User.WORKFLOW_ENGINE
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_admin_changelist_admin_user_allowed(self):
        url = reverse("admin:core_appropriation_changelist")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.profile = User.ADMIN
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class TestCaseAdmin(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_admin_changelist_not_admin_user_disallowed(self):
        url = reverse("admin:core_case_changelist")
        self.user.is_staff = True
        self.user.profile = User.WORKFLOW_ENGINE
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_admin_changelist_admin_user_allowed(self):
        url = reverse("admin:core_case_changelist")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.profile = User.ADMIN
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class TestActivityAdmin(AuthenticatedTestCase, BasicTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.basic_setup()

    def test_admin_changelist_not_admin_user_disallowed(self):
        url = reverse("admin:core_activity_changelist")
        self.user.is_staff = True
        self.user.profile = User.WORKFLOW_ENGINE
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_admin_changelist_admin_user_allowed(self):
        url = reverse("admin:core_activity_changelist")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.profile = User.ADMIN
        self.user.save()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class TestAccountAdmin(TestCase):
    def test_account_number(self):
        section = create_section()
        main_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        supplementary_activity_details = ActivityDetails.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010002",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        account = create_account(
            section=section,
            main_activity=main_activity_details,
            supplementary_activity=supplementary_activity_details,
        )

        site = AdminSite()
        account_admin = AccountAdmin(Account, site)

        self.assertEqual(account_admin.number(account), account.number)


class TestTargetGroupAdmin(TestCase):
    def test_target_group_required_fields_for_case_initial(self):
        target_group = create_target_group(
            name="familieafdelingen", required_fields_for_case=["district"]
        )
        site = AdminSite()
        request = MockRequest()
        target_group_admin = TargetGroupAdmin(TargetGroup, site)
        target_group_form_class = target_group_admin.get_form(
            request, target_group
        )
        target_group_form = target_group_form_class(instance=target_group)
        initial_required_fields = target_group_form.get_initial_for_field(
            target_group_form.fields["required_fields_for_case"],
            "required_fields_for_case",
        )

        self.assertEqual(initial_required_fields, ["district"])


class TestClassificationAdmin(TestCase):
    def test_has_view_permissions_grant_user_false(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.GRANT)
        self.assertFalse(classification_admin.has_view_permission(request))

    def test_has_add_permission_grant_user_false(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.GRANT)
        self.assertFalse(classification_admin.has_add_permission(request))

    def test_has_change_permission_grant_user_false(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.GRANT)
        self.assertFalse(classification_admin.has_change_permission(request))

    def test_has_delete_permission_grant_user_false(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.GRANT)
        self.assertFalse(classification_admin.has_delete_permission(request))

    def test_has_module_permission_grant_user_false(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.GRANT)
        self.assertFalse(classification_admin.has_module_permission(request))

    def test_has_view_permissions_workflow_engine_user_true(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.WORKFLOW_ENGINE)
        self.assertTrue(classification_admin.has_view_permission(request))

    def test_has_add_permission_workflow_engine_user_true(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.WORKFLOW_ENGINE)
        self.assertTrue(classification_admin.has_add_permission(request))

    def test_has_change_permission_workflow_engine_user_true(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.WORKFLOW_ENGINE)
        self.assertTrue(classification_admin.has_change_permission(request))

    def test_has_delete_permission_workflow_engine_user_true(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.WORKFLOW_ENGINE)
        self.assertTrue(classification_admin.has_delete_permission(request))

    def test_has_module_permission_workflow_engine_user_true(self):
        site = AdminSite()
        classification_admin = ClassificationAdmin(Section, site)
        request = MockRequest()

        request.user = User.objects.create(profile=User.WORKFLOW_ENGINE)
        self.assertTrue(classification_admin.has_module_permission(request))
