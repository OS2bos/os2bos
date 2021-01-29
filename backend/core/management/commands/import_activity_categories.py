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

from core.models import ActivityDetails, Section, SectionInfo, ActivityCategory


class Command(BaseCommand):
    help = """
    This script imports Account Categories.

    Currently this requires the account category mapping sheet be saved
    as "activity_categories.csv".
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            help="set the path to read the activity_categories.csv file",
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
                "activity_categories.csv",
            )
        with open(path) as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]

            for row in rows[1:]:
                section_paragraph = row[1]
                activity_details_activity_id = row[2][:6]
                activity_category_id = row[3][:6]
                activity_category_name = row[3][6:].strip()

                # Find the relevant Section.
                sections = Section.objects.filter(paragraph=section_paragraph)
                if not sections.exists():
                    print(
                        f"section with paragraph: {section_paragraph}"
                        f" does not exist."
                    )
                    continue
                section = sections.first()

                # Find the relevant ActivityDetails.
                activity_details = ActivityDetails.objects.filter(
                    activity_id=activity_details_activity_id
                )
                if not activity_details.exists():
                    print(
                        f"activity details with activity id: "
                        f"{activity_details_activity_id} does not exist."
                    )
                    continue
                activity_details_obj = activity_details.first()

                # Find the relevant SectionInfos.
                section_infos = SectionInfo.objects.filter(
                    activity_details=activity_details_obj,
                    section=section,
                )
                if not section_infos.exists():
                    print(
                        f"section info with section: {section} and "
                        f"activity_details: {activity_details_obj}"
                        f" does not exist."
                    )
                    continue

                # Create the ActivityCategory and associate it
                # with the SectionInfos.
                obj, _ = ActivityCategory.objects.update_or_create(
                    category_id=activity_category_id,
                    name=activity_category_name,
                )
                section_infos.update(activity_category=obj)
