# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import csv

from django.db import transaction
from django.core.management.base import BaseCommand

from core.models import ActivityDetails, Section, Account


class Command(BaseCommand):
    help = """
    This script imports Accounts from the CBUR "Klassifikationer"
    spreadsheet.

    Currently this requires the sheet "Aktiviteter" be saved
    as "activities.csv".

    NOTE: This requires the Section models AND
    the ActivityDetails to have been populated first.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            help="set the path to read the activities.csv file",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = options["path"]
        # if no path is given use a default relative path.
        if not path:
            path = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "activities.csv"
            )
        with open(path) as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
            for row in rows[1:]:
                activity_id = row[0]
                main_activity_section = row[4]
                supplementary_activity_section = row[5]
                paragraph = (
                    supplementary_activity_section
                    if supplementary_activity_section
                    else main_activity_section
                )
                main_activity = row[8]
                account_number = row[13]
                if (
                    not activity_id
                    or not (
                        main_activity_section or supplementary_activity_section
                    )
                    or not account_number
                    or not paragraph
                ):
                    continue
                main_account_number = account_number.split("-")[0]
                activity_number = account_number.split("-")[1]

                # if no main activity column is present
                # we know the row is a main activity.
                if not main_activity:
                    try:
                        main_activity_details = ActivityDetails.objects.get(
                            activity_id=activity_id
                        )
                        suppl_activity_details = None
                    except ActivityDetails.DoesNotExist:
                        print(
                            f"ActivityDetails with id: {activity_id}"
                            f" does not exist"
                        )
                        continue
                else:
                    try:
                        main_activity_details = ActivityDetails.objects.get(
                            activity_id=main_activity
                        )
                        suppl_activity_details = ActivityDetails.objects.get(
                            activity_id=activity_id
                        )
                    except ActivityDetails.DoesNotExist:
                        print(
                            f"ActivityDetails with id: {activity_id}"
                            f" or {main_activity} does not exist"
                        )
                        continue
                section = Section.objects.get(paragraph=paragraph)

                Account.objects.update_or_create(
                    main_activity=main_activity_details,
                    supplementary_activity=suppl_activity_details,
                    section=section,
                    defaults={
                        "main_account_number": main_account_number,
                        "activity_number": activity_number,
                    },
                )
