# -*- coding: utf-8 -*-
from django.test import TestCase

from core.models import (
    Municipality,
    SchoolDistrict,
    Sections,
    ActivityCatalog,
    Account,
    ApprovalLevel,
    Team,
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
        team = Team.objects.create(name="C-BUR")

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
