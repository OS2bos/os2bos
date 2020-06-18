# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.core.management.base import BaseCommand
from bevillingsplatform.initialize import initialize
from django.conf import settings


class Command(BaseCommand):
    """
    Initialize database.
    Helper command to seed database with (static) basic data.

    :Reference: :mod:`bevillingsplatform.initialize`

    Should be able to be run multiple times over without generating duplicates.

    Example:

        $ python manage.py initialize_database

    """

    help = "Call initialize function to seed the database"

    def handle(self, *args, **options):
        if settings.INITIALIZE_DATABASE is not True:
            return

        # Display action
        print("Seed database with (static) basic data")

        # Run script
        initialize()

        # Inform user that the operation is complete
        # Assuming that if any of the underlying functions fail
        # the process is stopped/caught in place
        print("Database seeded with (static) basic data")
