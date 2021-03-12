# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import sys
import logging

from datetime import datetime

from django.core.management.base import BaseCommand

from core.utils import export_prism_payments_for_date
from core.decorators import log_to_prometheus

logger = logging.getLogger("bevillingsplatform.export_to_prism")


class Command(BaseCommand):
    help = "Exports payments due today or on the give date to PRISME."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--date", default=None, help=("Export payments for date")
        )

    @log_to_prometheus("export_to_prism")
    def handle(self, *args, **options):
        """Call export function and that's it!"""
        date = options["date"]
        if date is not None:
            try:
                date = datetime.strptime(date, "%Y%m%d")
            except ValueError:
                print("Please enter date as 'YYYYMMDD'.")
                logger.error(
                    f"Invalid date input {date} - should parse as 'YYYYMMDD'"
                )
                sys.exit(1)
        try:
            prism_files = export_prism_payments_for_date(date)

            # This is just a sanity check, if we arrive here everything
            # will have worked out or an exception would have been
            # thrown.
            if not prism_files:
                logger.info("No records found for export to PRISME.")
            elif all(os.path.isfile(file) for file in prism_files):
                logger.info(
                    f"Success: PRISME records were exported to {prism_files}"
                )
            else:
                logger.error(
                    f"Export of records to PRISME failed! {prism_files}"
                )
        except Exception:
            logger.exception("An exception occurred during export to PRISME")
