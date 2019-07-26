# -*- coding: utf-8 -*-
from django.test import TestCase

from bevillingsplatform.initialize import initialize
from core.models import (
    Municipality,
    SchoolDistrict,
    Section,
    Account,
    ActivityDetails,
)


class InitializeTestCase(TestCase):
    def test_initialize_generates_municipalities(self):
        initialize()
        municipality_count = Municipality.objects.count()
        self.assertEqual(municipality_count, 98)

    def test_initialize_generates_school_districts(self):
        initialize()
        school_district_count = SchoolDistrict.objects.count()
        self.assertEqual(school_district_count, 5)

    def test_initialize_generates_sections(self):
        initialize()
        sections_count = Section.objects.count()
        self.assertEqual(sections_count, 146)

    def test_initialize_generates_activity_details(self):
        initialize()
        details_count = ActivityDetails.objects.count()
        self.assertEqual(details_count, 86)

    def test_initialize_generates_accounts(self):
        initialize()
        accounts_count = Account.objects.count()
        self.assertEqual(accounts_count, 883)
