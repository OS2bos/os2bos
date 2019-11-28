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
from core.models import Payment, STATUS_GRANTED, SD

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
            fictive_payments = Payment.objects.filter(
                date=date,
                payment_schedule__fictive=True,
                paid=False,
                payment_schedule__activity__status=STATUS_GRANTED,
            )
            sd_payments = Payment.objects.filter(
                date=date,
                payment_schedule__payment_method=SD,
                paid=False,
                payment_schedule__activity__status=STATUS_GRANTED,
            )
            payments = list(fictive_payments) + list(sd_payments)
            payment_ids = [payment.id for payment in payments]
            for payment in payments:
                print(payment)
                payment.paid = True
                payment.paid_amount = payment.amount
                payment.paid_date = date
                payment.save()
            logger.info(
                f"{len(payments)} payment(s) with ids: "
                f"{payment_ids} were marked paid on {date}"
            )
        except Exception:
            logger.exception(
                "An exception occurred during marking payments fictive."
            )
