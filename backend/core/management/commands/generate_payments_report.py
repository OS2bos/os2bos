# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from django.core.management.base import BaseCommand

from core.utils import (
    generate_payments_report,
)
from core.decorators import log_to_prometheus

logger = logging.getLogger("bevillingsplatform.generate_payments_report")


class Command(BaseCommand):
    help = "Generate expected payments reports as CSV"

    @log_to_prometheus("generate_payments_report")
    def handle(self, *args, **options):
        try:
            payment_reports = generate_payments_report()
            if payment_reports:
                logger.info(f"Created payments reports: {payment_reports}")
            else:
                logger.info("No payment reports generated")
        except Exception:
            logger.exception(
                "An error occurred during generation of the payments report"
            )
