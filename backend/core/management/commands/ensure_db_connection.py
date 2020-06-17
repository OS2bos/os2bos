# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import sys
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings
from django.db.utils import OperationalError
from bevillingsplatform.initialize import initialize


class Command(BaseCommand):
    help = "Check the connection to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "-w",
            "--wait",
            default=1,
            type=int,
            help="Retry the connection for every second for WAIT seconds.",
        )

    def handle(self, *args, **options):
        for i in range(0, options["wait"]):
            attempt = "%02d/%02d " % (i + 1, options["wait"])
            try:
                connections["default"].ensure_connection()
                self.stdout.write("%s Connected to database." % attempt)
                if getattr(settings, 'INITIALIZE_DATABASE', False) is True:
                    initialize()
                    self.stdout.write("Initialized database with test data")
                sys.exit(0)

            except OperationalError as e:
                self.stdout.write(str(e))
                self.stdout.write(
                    "%s Unable to connect to database." % attempt
                )
                if i < options["wait"] - 1:
                    time.sleep(1)
        self.stdout.write("%s Giving up." % attempt)
        sys.exit(1)
