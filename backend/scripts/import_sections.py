# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""
This script imports Sections from the CBUR "Klassifikationer" spreadsheet.

Currently this requires the sheet "Paragraffer" be saved
as "paragraffer.csv" in the current directory.
"""
import csv
import core.models as models

with open("paragraffer.csv") as csvfile:
    reader = csv.reader(csvfile)
    models_list = []
    rows = [row for row in reader]
    for row in rows[1:]:
        key = row[3]
        text = row[4]

        action_tracks = [x.strip() for x in row[11].split(",") if x != ""]
        target_groups = [x.strip() for x in row[12].split(",") if x != ""]
        tracks_to_steps_dict = {
            "Spor 1": [models.STEP_ONE, models.STEP_TWO],
            "Spor 2": [models.STEP_THREE],
            "Spor 3": [models.STEP_FOUR, models.STEP_FIVE, models.STEP_SIX],
        }
        steps_list = []
        if action_tracks:
            for track in action_tracks:
                steps_list.extend(tracks_to_steps_dict[track])
        law_dict = {
            "SFL": "Skatteforvaltningsloven",
            "LAB": "Lov om beskæftigelsesindsatsen",
            "AKL": "Aktivloven",
            "SEL": "Serviceloven",
            "ABL": "Andelsboligloven",
            "SUL": "Sundhedsloven",
            "STU": "Lov om ungdomsuddannelse for unge med særlige behov",
        }
        law_text_name = law_dict.get(key.split("-")[0], "")

        target_group_dict = {
            "Familieafdeling": "FAMILY_DEPT",
            "Handicap": "DISABILITY_DEPT",
        }
        # SFL - Skatteforvaltningsloven
        # LAB - Lov om beskæftigelsesindsatsen
        # AKL - Aktivloven
        # SEL - Serviceloven
        # ABL - Andelsboligloven
        # SUL - Sundhedsloven
        # STU - Lov om ungdomsuddannelse for unge med særlige behov
        models.Section.objects.update_or_create(
            paragraph=key,
            defaults={
                "paragraph": key,
                "text": text,
                "law_text_name": law_text_name,
                "allowed_for_disability_target_group": "Handicap"
                in target_groups,
                "allowed_for_family_target_group": "Familieafdeling"
                in target_groups,
                "allowed_for_steps": steps_list,
            },
        )
