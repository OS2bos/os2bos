# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import decimal
from decimal import Decimal
import csv

from django.db import transaction
from django.core.management.base import BaseCommand

from core.models import ServiceProvider


class Command(BaseCommand):
    help = """
    This script imports ServiceProviders from the CBUR "Klassifikationer"
    spreadsheet.

    Currently this requires the sheet "Leverandør" be saved
    as "serviceproviders.csv".
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            help="set the path to read the serviceproviders.csv file",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = options["path"]
        # if no path is given use a default relative path.
        if not path:
            path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "data",
                "serviceproviders.csv",
            )
        with open(path) as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
            for row in rows[1:]:
                cvr = row[0]
                name = row[1]
                vat_factor = (
                    Decimal(float(row[5][:-1].replace(",", ".")))
                    if row[5][:-1]
                    else 100.00
                )
                try:
                    ServiceProvider.objects.update_or_create(
                        cvr_number=cvr,
                        defaults={"name": name, "vat_factor": vat_factor},
                    )
                except decimal.InvalidOperation:
                    print(cvr, name, vat_factor)
