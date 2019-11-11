# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import sys
import logging
from datetime import datetime

from django.db import transaction
from django.core.management.base import BaseCommand
from core.models import Payment

logger = logging.getLogger("bevillingsplatform.mark_fictive_payments_paid")


class Command(BaseCommand):
    help = "Marks fictive payments paid on the given date."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--date",
            help=("Mark payments fictive for date"),
            default=None,
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Mark fictive payments paid for the given date."""
        date = options["date"]
        if date is not None:
            try:
                date = datetime.strptime(date, "%Y%m%d").date()
            except ValueError:
                print("Please enter date as 'YYYYMMDD'.")
                logger.error(
                    f"Invalid date input {date} - should parse as 'YYYYMMDD'"
                )
                sys.exit()
        else:
            date = datetime.now().date()

        try:
            payments = Payment.objects.filter(
                date=date, payment_schedule__fictive=True, paid=False
            )

            for payment in payments:
                payment.paid = True
                payment.paid_amount = payment.amount
                payment.paid_date = date
                payment.save()
            logger.info(
                f"{payments.count()} payment(s) were marked paid on {date}"
            )
        except Exception:
            logger.exception(
                "An exception occurred during marking payments fictive."
            )
