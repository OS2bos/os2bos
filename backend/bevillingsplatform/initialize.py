# -*- coding: utf-8 -*-

from core.data.municipalities import municipalities
from core.models import Municipality


def initialize():
    """Main script for initializing all the basic data we want at start.

    Should be able to be run multiple times over without generating duplicates.
    """
    initialize_municipalities()


def initialize_municipalities():
    """Initialize all the danish municipalities."""
    for name in municipalities:
        Municipality.objects.get_or_create(name=name)
