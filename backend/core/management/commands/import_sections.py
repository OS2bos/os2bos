# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from core import models


class Command(BaseCommand):
    help = """
    This script imports Sections from the CBUR "Klassifikationer" spreadsheet.

    Currently this requires the sheet "Paragraffer" be saved
    as "paragraphs.csv".
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            help="set the path to read the paragraphs.csv file",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = options["path"]
        # if no path is given use a default relative path.
        if not path:
            path = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "paragraphs.csv"
            )
        with open(path) as csvfile:
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
                    "Trin 1": 1,
                    "Trin 2": 2,
                    "Trin 3": 3,
                    "Trin 4": 4,
                    "Trin 5": 5,
                    "Trin 6": 6,
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
                    },
                )
                section = models.Section.objects.get(paragraph=key)
                effort_steps = models.EffortStep.objects.filter(
                    number__in=steps_list
                )
                if effort_steps.exists():
                    section.allowed_for_steps.add(*effort_steps)

                if "Handicap" in target_groups:
                    target_group, _ = models.TargetGroup.objects.get_or_create(
                        name="Handicapafdelingen"
                    )
                    section.allowed_for_target_groups.add(target_group)
                if "Familieafdeling" in target_groups:
                    target_group, _ = models.TargetGroup.objects.get_or_create(
                        name="Familieafdeling"
                    )
                    section.allowed_for_target_groups.add(target_group)
