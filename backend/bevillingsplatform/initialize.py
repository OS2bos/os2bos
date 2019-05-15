# -*- coding: utf-8 -*-

from core.data.municipalities import municipalities
from core.models import Municipality


def initialize():
    initialize_municipalities()


def initialize_municipalities():
    for name in municipalities:
        Municipality.objects.get_or_create(name=name)
