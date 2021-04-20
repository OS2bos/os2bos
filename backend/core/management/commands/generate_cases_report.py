# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from django.core.management.base import BaseCommand

from core.utils import (
    generate_cases_report,
)
from core.decorators import log_to_prometheus

logger = logging.getLogger("bevillingsplatform.generate_cases_report")


class Command(BaseCommand):
    help = "Generate expected cases reports as CSV"

    @log_to_prometheus("generate_cases_report")
    def handle(self, *args, **options):
        try:
            cases_reports = generate_cases_report()
            if cases_reports:
                logger.info(f"Created cases reports: {cases_reports}")
            else:
                logger.info("No cases reports generated")
        except Exception:
            logger.exception(
                "An error occurred during generation of the cases report"
            )
