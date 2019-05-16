# -*- coding: utf-8 -*-

from core.data.municipalities import municipalities
from core.data.sections import sections
from core.models import Municipality, Sections


def initialize():
    """Main script for initializing all the basic data we want at start.

    Should be able to be run multiple times over without generating duplicates.
    """
    initialize_municipalities()
    initialize_sections()


def initialize_municipalities():
    """Initialize all the danish municipalities."""
    for name in municipalities:
        Municipality.objects.get_or_create(name=name)


def initialize_sections():
    """Initialize all the relevant law sections."""
    for section in sections:
        paragraph = section["paragraph"]
        kle_number = section["kle_number"]
        text = section["text"]
        Sections.objects.get_or_create(
            paragraph=paragraph,
            kle_number=kle_number,
            text=text
        )
