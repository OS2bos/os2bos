# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.test import TestCase

from bevillingsplatform.initialize import initialize
from core.models import (
    Municipality,
    SchoolDistrict,
    Section,
    SectionInfo,
    ActivityDetails,
    PaymentMethodDetails,
    RatePerDate,
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
        self.assertEqual(details_count, 82)

    def test_initialize_generates_section_infos(self):
        initialize()
        section_infos = SectionInfo.objects.count()
        self.assertEqual(section_infos, 86)

    def test_initialize_generates_payment_method_details(self):
        initialize()
        payment_method_details_count = PaymentMethodDetails.objects.count()
        self.assertEqual(payment_method_details_count, 2)

    def test_initialize_generates_rates(self):
        initialize()
        rates_per_date_count = RatePerDate.objects.count()
        self.assertEqual(rates_per_date_count, 30)
