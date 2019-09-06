# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""
This script imports ActivityDetails from the CBUR "Klassifikationer"
spreadsheet.

Currently this requires the sheet "Aktiviteter v2" be saved
as "aktiviteter.csv" in the current directory.

NOTE: This requires the Section models to have been populated first.
"""
from core.models import ActivityDetails, Section
from collections import defaultdict
import csv

with open("aktiviteter.csv") as csvfile:
    reader = csv.reader(csvfile)
    models_list = []
    rows = [row for row in reader]
    # dict with (activity_id, set of main activity ids) pairs.
    main_activity_dict = defaultdict(set)
    section_main_dict = defaultdict(set)
    section_supplementary_dict = defaultdict(set)
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
        suppl_activity_on = row[5]
        if suppl_activity_on:
            section_supplementary_dict[activity_id].add(suppl_activity_on)
        main_activity = row[8]
        if main_activity:
            main_activity_dict[activity_id].add(main_activity)

        try:
            ad, created = ActivityDetails.objects.update_or_create(
                name=name,
                activity_id=activity_id,
                max_tolerance_in_percent=tolerance_percent,
                max_tolerance_in_dkk=tolerance_dkk,
            )
        except Exception as e:
            print(f"Import of activity {activity_id} failed: {e}")
            continue

    # Make another pass at ActivityDetails inserting the main activities.
    for details_obj in ActivityDetails.objects.all():

        for activity_id in main_activity_dict[details_obj.activity_id]:
            related_details = ActivityDetails.objects.filter(
                activity_id=activity_id
            )
            if not related_details.exists():
                print(f"activity details with id {activity_id} does not exist")
            else:
                related_details = related_details.first()
                details_obj.main_activities.add(related_details)

        for paragraph in section_main_dict[details_obj.activity_id]:
            main_activity_for = Section.objects.filter(paragraph=paragraph)
            if main_activity_for.exists():
                main_activity_for = main_activity_for.first()
                details_obj.main_activity_for.add(main_activity_for)

        for paragraph in section_supplementary_dict[details_obj.activity_id]:
            supplementary_activity_for = Section.objects.filter(
                paragraph=paragraph
            )
            if supplementary_activity_for.exists():
                supplementary_activity_for = supplementary_activity_for.first()
                details_obj.supplementary_activity_for.add(
                    supplementary_activity_for
                )
