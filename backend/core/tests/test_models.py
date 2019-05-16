# -*- coding: utf-8 -*-
from django.test import TestCase

from core.models import Municipality


class MunicipalityTestCase(TestCase):
    def test_municipality_str(self):
        municipality = Municipality.objects.create(name="København")

        self.assertEqual(str(municipality), "København")
