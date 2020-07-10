# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import csv

from django.db import transaction
from django.db.models import Q
from django.core.management.base import BaseCommand

from core.models import ActivityDetails, SectionInfo, AccountAlias


class Command(BaseCommand):
    help = """
    This script imports Account Aliases.

    Currently this requires the account alias mapping sheet be saved
    as "account_aliases.csv".
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            help="set the path to read the account_aliases.csv file",
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
                "account_aliases.csv",
            )
        with open(path) as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]

            for row in rows[1:]:
                account_alias = row[0]
                mapping = row[2].rstrip("-")
                _, account_number, activity_id, _ = mapping.split("-")

                section_info = SectionInfo.objects.filter(
                    Q(main_activity_main_account_number=account_number)
                    | Q(
                        supplementary_activity_main_account_number=account_number
                    )
                )
                if not section_info.exists():
                    print(
                        f"section info with main activity account number: "
                        f"{account_number} does not exist."
                    )
                    continue

                # If the activity_id of the corresponding section info details
                # corresponds to activity id of the alias
                if section_info.activity_details.activity_id == activity_id:
                    AccountAlias.objects.update_or_create(
                        section_info=section_info,
                        activity_details=None,
                        defaults={"alias": account_alias},
                    )
                else:
                    activity_details = ActivityDetails.objects.filter(
                        activity_id=activity_id
                    )
                    if not activity_details.exists():
                        print(
                            f"activity details with activity_id: "
                            f"{activity_id} does not exist."
                        )
                        continue
                    activity_details = activity_details.first()

                section_info = section_info.first()

                AccountAlias.objects.update_or_create(
                    activity_details=activity_details,
                    section_info=section_info,
                    defaults={"alias": account_alias},
                )
