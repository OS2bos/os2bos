# -*- coding: utf-8 -*-
from django.test import TestCase

from bevillingsplatform.initialize import initialize
from core.models import Municipality


class InitializeTestCase(TestCase):
    def test_initialize_generates_municipalities(self):
        initialize()
        municipality_count = Municipality.objects.count()
        self.assertEqual(municipality_count, 98)
