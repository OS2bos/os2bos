# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import logging

from datetime import datetime

from django.core.management.base import BaseCommand

from core.utils import export_prism_payments_for_date


logger = logging.getLogger("bevillingsplatform.export_to_prism")


class Command(BaseCommand):
    help = "Exports payments due today or on the give date to PRISME."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--date", default=None, help=("Export payments for date")
        )

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
                sys.exit()
        try:
            prism_file = export_prism_payments_for_date(date)
            # This is just a sanity check, if we arrive here everything will
            # have worked out or an exception would have been thrown.
            if prism_file is None:
                logger.info("No records found for export to PRISME.")
            elif os.path.isfile(prism_file):
                logger.info(
                    f"Success: PRISME records were exported to {prism_file}"
                )
            else:
                logger.error("Export of records to PRISME failed!")
        except Exception:
            logger.exception(
                f"An exception occurred during export to PRISME: {e}"
            )
