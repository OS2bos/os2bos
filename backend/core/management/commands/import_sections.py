# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import csv

from django.core.management.base import BaseCommand

import core.models as models


class Command(BaseCommand):
    help = """
    This script imports Sections from the CBUR "Klassifikationer" spreadsheet.

    Currently this requires the sheet "Paragraffer" be saved
    as "paragraphs.csv" in the current directory.
    """

    def handle(self, *args, **options):
        with open("paragraphs.csv") as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
            for row in rows[1:]:
                key = row[3]
                text = row[4]

                action_steps = [
                    x.strip() for x in row[11].split(",") if x != ""
                ]
                target_groups = [
                    x.strip() for x in row[12].split(",") if x != ""
                ]
                steps_dict = {
                    "Trin 1": models.STEP_ONE,
                    "Trin 2": models.STEP_TWO,
                    "Trin 3": models.STEP_THREE,
                    "Trin 4": models.STEP_FOUR,
                    "Trin 5": models.STEP_FIVE,
                    "Trin 6": models.STEP_SIX,
                }
                steps_list = []
                if action_steps:
                    for step in action_steps:
                        steps_list.append(steps_dict[step])
                law_dict = {
                    "SFL": "Skatteforvaltningsloven",
                    "LAB": "Lov om beskæftigelsesindsatsen",
                    "AKL": "Aktivloven",
                    "SEL": "Serviceloven",
                    "ABL": "Andelsboligloven",
                    "SUL": "Sundhedsloven",
                    "STU": (
                        "Lov om ungdomsuddannelse for "
                        "unge med særlige behov"
                    ),
                }
                law_text_name = law_dict.get(key.split("-")[0], "")

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
