# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import csv
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from core.utils import (
    generate_expected_payments_report_list,
    generate_granted_payments_report_list,
)


logger = logging.getLogger("bevillingsplatform.generate_payments_report")


class Command(BaseCommand):
    help = "Generate granted and expected payments reports as CSV"

    def handle(self, *args, **options):
        granted_payments_list = generate_granted_payments_report_list()
        expected_payments_list = generate_expected_payments_report_list()

        report_dir = settings.PAYMENTS_REPORT_DIR

        try:
            with open(
                os.path.join(report_dir, "granted_payments.csv"), "w"
            ) as csvfile:
                if granted_payments_list:
                    logger.info(
                        f"Created granted payments report "
                        f"for {len(granted_payments_list)} payments"
                    )
                    writer = csv.DictWriter(
                        csvfile, fieldnames=granted_payments_list[0].keys()
                    )

                    writer.writeheader()
                    for payment_dict in granted_payments_list:
                        writer.writerow(payment_dict)

            with open(
                os.path.join(report_dir, "expected_payments.csv"), "w"
            ) as csvfile:
                if expected_payments_list:
                    logger.info(
                        f"Created expected payments report "
                        f" for {len(expected_payments_list)} expected payments"
                    )
                    writer = csv.DictWriter(
                        csvfile, fieldnames=expected_payments_list[0].keys()
                    )

                    writer.writeheader()
                    for payment_dict in expected_payments_list:
                        writer.writerow(payment_dict)
        except Exception:
            logger.exception(
                "An error occurred during generation of payments reports"
            )
