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

from core.models import PaymentDateExclusion

from core.utils import generate_payment_date_exclusion_dates


logger = logging.getLogger(
    "bevillingsplatform.generate_payment_date_exclusion_dates"
)


class Command(BaseCommand):
    help = "Generate payment exclusion dates for a number of years."

    def add_arguments(self, parser):
        parser.add_argument(
            "-y",
            "--years",
            default=None,
            help=("Generate payment exclusion dates for years"),
        )

    def handle(self, *args, **options):
        """Parse comma-separated years and generate dates."""
        years = options["years"]
        if years is not None:
            try:
                years = years.split(",")
            except ValueError:
                print("Please enter years as comma-separated 'YYYY,YYYY'.")
                logger.error(
                    f"Invalid years input {years} - should parse as 'YYYY,YYYY'"
                )
                sys.exit(1)
        try:
            dates = generate_payment_date_exclusion_dates(years)
            for date in dates:
                PaymentDateExclusion.objects.get_or_create(date=date)

            logger.info(
                f"Success: Payment Exclusion Dates were generated for {years}"
            )
        except Exception:
            logger.exception(
                "An exception occurred during "
                "payment exclusion date generation"
            )
