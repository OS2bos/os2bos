# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging

from django.core.management.base import BaseCommand

from core.models import PaymentDateExclusion

from core.utils import generate_payment_date_exclusion_dates


logger = logging.getLogger(
    "bevillingsplatform.generate_payment_date_exclusions"
)


class Command(BaseCommand):
    help = "Generate payment exclusion dates for a number of years."

    def add_arguments(self, parser):
        parser.add_argument(
            "years",
            default=None,
            type=int,
            nargs="*",
            help=("years as YYYY YYYY"),
        )

    def handle(self, *args, **options):
        """Parse years, generate dates and create payment date exclusions."""
        years = options["years"]
        try:
            dates = generate_payment_date_exclusion_dates(years)
            for date in dates:
                PaymentDateExclusion.objects.get_or_create(date=date)

            logger.info(
                f"Success: {len(dates)} Payment Exclusion Dates"
                f" were generated for {years}"
            )
        except Exception:
            logger.exception(
                "An exception occurred during "
                "payment exclusion date generation"
            )
