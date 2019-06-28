from decimal import Decimal
from datetime import date
from unittest import mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from parameterized import parameterized

from core.tests.testing_mixins import PaymentScheduleMixin, ActivityMixin
from core.models import (
    Municipality,
    SchoolDistrict,
    Sections,
    ActivityCatalog,
    Account,
    ApprovalLevel,
    Team,
    Payment,
    PaymentSchedule,
    ServiceProvider,
)


class MunicipalityTestCase(TestCase):
    def test_municipality_str(self):
        municipality = Municipality.objects.create(name="København")

        self.assertEqual(str(municipality), "København")


class SchoolDistrictTestCase(TestCase):
    def test_school_district_str(self):
        school_district = SchoolDistrict.objects.create(name="Skovlunde Skole")

        self.assertEqual(str(school_district), "Skovlunde Skole")


class TeamTestCase(TestCase):
    def test_team_str(self):
        user = get_user_model().objects.create(username="Anders And")
        team = Team.objects.create(name="C-BUR", leader=user)

        self.assertEqual(str(team), "C-BUR")


class SectionsTestCase(TestCase):
    def test_sections_str(self):
        sections = Sections.objects.create(
            paragraph="ABL-105-2",
            kle_number="27.45.04",
            text="Lov om almene boliger",
            allowed_for_steps=[],
            law_text_name="Lov om almene boliger",
        )

        self.assertEqual(str(sections), "ABL-105-2 - 27.45.04")


class ActivityCatalogTestCase(TestCase):
    def test_activitycatalog_str(self):
        catalog = ActivityCatalog.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )

        self.assertEqual(
            str(catalog),
            "010001 - Betaling til andre kommuner/region for specialtandpleje",
        )


class ActivityTestCase(TestCase, ActivityMixin, PaymentScheduleMixin):
    def test_activity_total_amount_no_payment_plan(self):
        activity = self.create_activity()
        total_amount = activity.total_amount()
        self.assertEqual(total_amount, 0)

    def test_activity_synchronize_payments_on_save(self):
        activity = self.create_activity()
        payment_schedule = self.create_payment_schedule()
        activity.payment_plan = payment_schedule
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 10)
        activity.end_date = date(year=2019, month=1, day=13)
        activity.save()
        self.assertEqual(activity.payment_plan.payments.count(), 13)

    def test_activity_total_amount_on_main_activity(self):
        activity = self.create_activity()
        payment_schedule = self.create_payment_schedule()
        activity.payment_plan = payment_schedule
        activity.save()
        self.assertEqual(activity.total_amount(), Decimal("5000.0"))

    def test_activity_total_amount_on_main_supplementary_activities(self):
        # Generate main activity
        activity = self.create_activity()
        payment_schedule = self.create_payment_schedule()
        activity.payment_plan = payment_schedule
        activity.save()
        # Generate first supplementary activity
        supplementary_activity = self.create_activity()
        payment_schedule = self.create_payment_schedule()
        supplementary_activity.payment_plan = payment_schedule
        supplementary_activity.main_activity = activity
        supplementary_activity.save()

        # Generate second supplementary activity without payment schedule.
        supplementary_activity = self.create_activity()
        supplementary_activity.main_activity = activity
        supplementary_activity.save()

        self.assertEqual(activity.total_amount(), Decimal("10000.0"))

    def test_activity_total_amount_on_service_provider(self):
        service_provider = ServiceProvider.objects.create(
            name="Test leverandør", vat_factor=Decimal("90")
        )
        activity = self.create_activity()
        payment_schedule = self.create_payment_schedule()
        activity.payment_plan = payment_schedule
        activity.service_provider = service_provider
        activity.save()
        self.assertEqual(activity.total_amount(), Decimal("4500.0"))


class AccountTestCase(TestCase):
    def test_account_str(self):
        sections = Sections.objects.create(
            paragraph="ABL-105-2",
            kle_number="27.45.04",
            text="Lov om almene boliger",
            allowed_for_steps=[],
            law_text_name="Lov om almene boliger",
        )
        catalog = ActivityCatalog.objects.create(
            name="Betaling til andre kommuner/region for specialtandpleje",
            activity_id="010001",
            max_tolerance_in_dkk=5000,
            max_tolerance_in_percent=10,
        )
        account = Account.objects.create(
            number="123456", section=sections, activity_catalog=catalog
        )

        self.assertEqual(str(account), f"123456 - {catalog} - {sections}")


class ApprovalLevelTestCase(TestCase):
    def test_approvallevel_str(self):
        approval_level = ApprovalLevel.objects.create(name="egenkompetence")

        self.assertEqual(str(approval_level), f"{approval_level.name}")


class PaymentTestCase(TestCase, PaymentScheduleMixin):
    def test_payment_str(self):
        payment_schedule = self.create_payment_schedule()
        payment = Payment.objects.create(
            payment_schedule=payment_schedule,
            date=date(year=2019, month=1, day=1),
            amount=Decimal("500.0"),
        )
        self.assertEqual(str(payment), "2019-01-01 - 500.0")


class PaymentScheduleTestCase(TestCase, PaymentScheduleMixin, ActivityMixin):
    def test_create_rrule_daily_10_days(self):
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=1, day=10),
        )

        self.assertEqual(len(list(rrule)), 10)
        # Assert days from 1-10 are generated.
        self.assertCountEqual(
            [event.day for event in list(rrule)], list(range(1, 11))
        )

    def test_create_rrule_daily_1_days(self):
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.DAILY
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=1, day=1),
        )

        self.assertEqual(len(list(rrule)), 1)

    def test_create_rrule_monthly_10_months(self):
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.MONTHLY
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=10, day=1),
        )

        self.assertEqual(len(list(rrule)), 10)

    def test_create_rrule_monthly_1_months(self):
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.MONTHLY
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=1, day=1),
        )

        self.assertEqual(len(list(rrule)), 1)

    def test_create_rrule_weekly_4_weeks(self):
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.WEEKLY
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=2, day=1),
        )

        self.assertEqual(len(list(rrule)), 5)

    def test_create_rrule_weekly_1_weeks(self):
        payment_schedule = self.create_payment_schedule(
            payment_frequency=PaymentSchedule.WEEKLY
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=1, day=1),
        )

        self.assertEqual(len(list(rrule)), 1)

    def test_create_rrule_one_time_1_day(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.ONE_TIME_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
        )

        rrule = payment_schedule.create_rrule(
            start=date(year=2019, month=1, day=1),
            end=date(year=2019, month=2, day=1),
        )

        self.assertEqual(len(list(rrule)), 1)
        self.assertEqual(
            list(rrule)[0].date(), date(year=2019, month=1, day=1)
        )

    def test_create_rrule_incorrect_frequency(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency="incorrect frequency",
        )

        with self.assertRaises(ValueError):
            payment_schedule.create_rrule(
                start=date(year=2019, month=1, day=1),
                end=date(year=2019, month=2, day=1),
            )

    @parameterized.expand(
        [
            (
                PaymentSchedule.ONE_TIME_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
                Decimal("100"),
            ),
            (
                PaymentSchedule.RUNNING_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
                Decimal("100"),
            ),
            (
                PaymentSchedule.PER_HOUR_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                5,
                Decimal("100"),
                Decimal("500"),
            ),
            (
                PaymentSchedule.PER_KM_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                10,
                Decimal("100"),
                Decimal("1000"),
            ),
        ]
    )
    def test_calculate_per_payment_amount(
        self,
        payment_type,
        payment_frequency,
        payment_amount,
        payment_units,
        vat_factor,
        expected,
    ):
        payment_schedule = self.create_payment_schedule(
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_amount=payment_amount,
            payment_units=payment_units,
        )

        amount = payment_schedule.calculate_per_payment_amount(
            vat_factor=vat_factor
        )

        self.assertEqual(amount, expected)

    def test_calculate_per_payment_amount_invalid_payment_type(self):
        payment_schedule = self.create_payment_schedule(
            payment_type="ugyldig betalingstype",
            payment_frequency=PaymentSchedule.DAILY,
        )

        with self.assertRaises(ValueError):
            payment_schedule.calculate_per_payment_amount(
                vat_factor=Decimal("100")
            )

    def test_generate_payments(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.DAILY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=1, day=10)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 10)

    def test_generate_payments_no_end_date(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        # Start in January and no end should generate 24 monthly payments
        # (till end of next year)
        payment_schedule.generate_payments(start_date, None)

        self.assertIsNotNone(payment_schedule.payments)
        self.assertEqual(payment_schedule.payments.count(), 24)

    def test_synchronize_payments_no_end_needs_further_payments(self):
        # Test the case where end is unbounded and payments are generated till
        # end of next year then middle of next year is reached
        # and new payments should be generated once again
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None
        # Initial call to generate payments will generate 24 payments.
        payment_schedule.generate_payments(start_date, end_date)
        self.assertEqual(len(payment_schedule.payments.all()), 24)

        # Now we are in the future and we need to generate new payments
        # because end is still unbounded
        with mock.patch("core.models.date") as date_mock:
            date_mock.today.return_value = date(year=2020, month=7, day=1)
            date_mock.max.month = 12
            date_mock.max.day = 31
            payment_schedule.synchronize_payments(start_date, end_date)
        self.assertEqual(payment_schedule.payments.count(), 36)

    def test_synchronize_payments_new_end_date_in_past(self):
        # Test the case where we generate payments for an unbounded end
        # and next the end is set so we need to delete some generated payments.
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=2019, month=6, day=1)
        payment_schedule.synchronize_payments(start_date, new_end_date)

        self.assertEqual(payment_schedule.payments.count(), 6)

    def test_synchronize_payments_new_end_date_in_future(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None

        # Generate payments till 2020-12-1
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 24)

        new_end_date = date(year=2021, month=2, day=1)
        payment_schedule.synchronize_payments(start_date, new_end_date)

        self.assertEqual(payment_schedule.payments.count(), 26)

    def test_synchronize_payments_same_end_date_no_changes(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=9, day=1)

        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(len(payment_schedule.payments.all()), 9)

        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

    def test_synchronize_payments_no_payments(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.MONTHLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = None
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 0)

    def test_synchronize_payments_end_date_in_future_for_weeks(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

        end_date = date(year=2019, month=4, day=1)
        payment_schedule.synchronize_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 13)

    def test_synchronize_payments_invalid_frequency(self):
        payment_schedule = self.create_payment_schedule(
            payment_type=PaymentSchedule.RUNNING_PAYMENT,
            payment_frequency=PaymentSchedule.WEEKLY,
            payment_amount=Decimal("100"),
        )
        start_date = date(year=2019, month=1, day=1)
        end_date = date(year=2019, month=3, day=1)
        payment_schedule.generate_payments(start_date, end_date)

        self.assertEqual(payment_schedule.payments.count(), 9)

        end_date = date(year=2019, month=4, day=1)
        payment_schedule.payment_frequency = "invalid_frequency"
        payment_schedule.save()
        with self.assertRaises(ValueError):
            payment_schedule.synchronize_payments(start_date, end_date)
