# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import sys
from datetime import datetime

from django.core.management.base import BaseCommand

from core.utils import process_payments_for_date


class Command(BaseCommand):
    help = "Exports payments due today or on the give date to PRISME."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--date", default=None, help=("Export payments for date")
        )

    def handle(self, *args, **options):
        """Call export function and that's it!"""
        date = options["date"]
        if not date:
            process_payments_for_date()
        else:
            try:
                date = datetime.strptime(date, "%Y%m%d")
            except ValueError:
                print("Please enter date as 'YYYYMMDD'.")
                sys.exit()
            process_payments_for_date(date)
