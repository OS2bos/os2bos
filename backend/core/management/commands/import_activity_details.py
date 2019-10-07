# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""
This script imports ActivityDetails from the CBUR "Klassifikationer"
spreadsheet.

Currently this requires the sheet "Aktiviteter" be saved
as "aktiviteter.csv" in the current directory.

NOTE: This requires the Section models to have been populated first.
"""

from collections import defaultdict
import csv

from django.core.management.base import BaseCommand

from core.models import ActivityDetails, Section, SectionInfo


class Command(BaseCommand):
    help = """
    This script imports Accounts from the CBUR "Klassifikationer"
    spreadsheet.

    Currently this requires the sheet "Aktiviteter" be saved
    as "activities.csv" in the current directory.

    NOTE: This requires the Section models AND
    the ActivityDetails to have been populated first.
    """

    def handle(self, *args, **options):
        with open("activities.csv") as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
            # dict with (activity_id, set of main activity ids) pairs.
            # containing which supplementary activities can have which
            # main activities.
            main_activity_dict = defaultdict(set)

            # dict with (main activity_id) -> (paragraph)
            # containing which sections an activity can be main activity for.
            section_main_dict = defaultdict(set)

            # dict with (supplementary activity_id) -> (paragraph)
            # containing which sections an activity can be supplementary
            # activity for.
            section_supplementary_dict = defaultdict(set)

            # dict with (activity_id, paragraph) -> (kle_number, sbsys_id)
            kle_and_sbsys_dict = {}

            for row in rows[1:]:
                activity_id = row[0]
                if not activity_id:
                    continue
                name = row[1]
                tolerance_percent = row[2][:-1]
                if not tolerance_percent:
                    tolerance_percent = 10
                tolerance_dkk = row[3]
                if not tolerance_dkk:
                    tolerance_dkk = 5000
                main_activity_on = row[4]
                if main_activity_on:
                    section_main_dict[activity_id].add(main_activity_on)
                    kle_number = row[6] or ""
                    sbsys_id = row[7] or ""
                    kle_and_sbsys_dict[activity_id, main_activity_on] = (
                        kle_number,
                        sbsys_id,
                    )
                suppl_activity_on = row[5]
                if suppl_activity_on:
                    section_supplementary_dict[activity_id].add(
                        suppl_activity_on
                    )
                main_activity = row[8]
                if main_activity:
                    main_activity_dict[activity_id].add(main_activity)

                try:
                    ad, created = ActivityDetails.objects.update_or_create(
                        activity_id=activity_id,
                        defaults={
                            "name": name,
                            "max_tolerance_in_percent": tolerance_percent,
                            "max_tolerance_in_dkk": tolerance_dkk,
                        },
                    )
                except Exception as e:
                    print(f"Import of activity {activity_id} failed: {e}")
                    continue

            # Make another pass at ActivityDetails inserting the
            # main activities.
            for details_obj in ActivityDetails.objects.all():

                for activity_id in main_activity_dict[details_obj.activity_id]:
                    related_details = ActivityDetails.objects.filter(
                        activity_id=activity_id
                    )
                    if not related_details.exists():
                        print(
                            f"activity details with id {activity_id}"
                            f" does not exist"
                        )
                    else:
                        related_details = related_details.first()
                        details_obj.main_activities.add(related_details)

                # This is to make the switch to the new "through" model
                details_obj.main_activity_for.clear()
                for paragraph in section_main_dict[details_obj.activity_id]:
                    main_activity_for = Section.objects.filter(
                        paragraph=paragraph
                    )
                    if main_activity_for.exists():
                        main_activity_for = main_activity_for.first()
                        kle_number, sbsys_id = kle_and_sbsys_dict[
                            details_obj.activity_id, paragraph
                        ]
                        SectionInfo.objects.update_or_create(
                            activity_details=details_obj,
                            section=main_activity_for,
                            defaults={
                                "kle_number": kle_number,
                                "sbsys_template_id": sbsys_id,
                            },
                        )

                for paragraph in section_supplementary_dict[
                    details_obj.activity_id
                ]:
                    supplementary_activity_for = Section.objects.filter(
                        paragraph=paragraph
                    )
                    if supplementary_activity_for.exists():
                        supplementary_activity_for = (
                            supplementary_activity_for.first()
                        )
                        details_obj.supplementary_activity_for.add(
                            supplementary_activity_for
                        )
