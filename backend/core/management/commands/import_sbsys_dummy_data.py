# Copyright (C) 2022 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import logging

from django.core.management.base import BaseCommand

from core.tests.test_consumers import example_sbsys_data, example_search_result

from core.utils import import_sbsys_appropriation

logger = logging.getLogger("bevillingsplatform.sbsys_dummy_import")


class Command(BaseCommand):
    help = "Imports dummy data currently used for testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--date", default=None, help=("Export payments for date")
        )

    def handle(self, *args, **options):
        """Do import."""
        appropriation_json = example_sbsys_data
        case_json = example_search_result["Results"][0]
        case_json["Behandler"]["LogonId"] = "familieraadgiver"

        import_sbsys_appropriation(appropriation_json, case_json)
