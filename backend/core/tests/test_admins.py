from datetime import date

from django.test import TestCase
from django.contrib.admin.sites import AdminSite

from core.models import (
    Payment,
    PaymentSchedule,
    ActivityDetails,
    Account,
    TargetGroup,
)
from core.admin import (
    PaymentAdmin,
    PaymentScheduleAdmin,
    AccountAdmin,
    TargetGroupAdmin,
)
from core.tests.testing_utils import (
    create_payment,
    create_payment_schedule,
    create_account,
    create_section,
    create_target_group,
)


class MockRequest:
    pass


request = MockRequest()


class TestPaymentAdmin(TestCase):
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


class TestPaymentScheduleAdmin(TestCase):
    def test_account_string(self):
        payment_schedule = create_payment_schedule()

        site = AdminSite()
        payment_schedule_admin = PaymentScheduleAdmin(PaymentSchedule, site)
        self.assertEqual(
            payment_schedule_admin.account_string(payment_schedule),
            payment_schedule.account_string,
        )


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
            name="familieafdelingen", required_fields_for_case="['district']"
        )
        site = AdminSite()
        target_group_admin = TargetGroupAdmin(TargetGroup, site)
        target_group_form = target_group_admin.get_form(request, target_group)
        target_group_form_instance = target_group_form(instance=target_group)
        initial_required_fields_for_case = target_group_form_instance.get_initial_for_field(
            target_group_form_instance.fields["required_fields_for_case"],
            "required_fields_for_case",
        )

        self.assertEqual(initial_required_fields_for_case, ["district"])
