# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from parameterized import parameterized

from core.tests.testing_mixins import PaymentScheduleMixin
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


class PaymentScheduleTestCase(TestCase, PaymentScheduleMixin):
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

    @parameterized.expand(
        [
            (
                PaymentSchedule.ONE_TIME_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
            ),
            (
                PaymentSchedule.RUNNING_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                0,
                Decimal("100"),
            ),
            (
                PaymentSchedule.PER_HOUR_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                5,
                Decimal("500"),
            ),
            (
                PaymentSchedule.PER_KM_PAYMENT,
                PaymentSchedule.DAILY,
                Decimal("100"),
                10,
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
        expected,
    ):
        payment_schedule = self.create_payment_schedule(
            payment_type=payment_type,
            payment_frequency=payment_frequency,
            payment_amount=payment_amount,
            payment_units=payment_units,
        )

        amount = payment_schedule.calculate_per_payment_amount()

        self.assertEqual(amount, expected)
