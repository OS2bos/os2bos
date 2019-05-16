# -*- coding: utf-8 -*-
from django.test import TestCase

from core.models import Municipality, SchoolDistrict, Sections


class MunicipalityTestCase(TestCase):
    def test_municipality_str(self):
        municipality = Municipality.objects.create(name="København")

        self.assertEqual(str(municipality), "København")


class SchoolDistrictTestCase(TestCase):
    def test_school_district_str(self):
        school_district = SchoolDistrict.objects.create(name="Skovlunde Skole")

        self.assertEqual(str(school_district), "Skovlunde Skole")


class SectionsTestCase(TestCase):
    def test_sections_str(self):
        sections = Sections.objects.create(
            paragraph="ABL-105-2",
            kle_number="27.45.04",
            text="Lov om almene boliger"
        )

        self.assertEqual(str(sections), "ABL-105-2 - 27.45.04")
