# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os

from django.db import transaction
from django.core.management.base import BaseCommand

from core.models import AccountAliasMapping
from core.utils import parse_account_alias_mapping_data_from_csv_path


class Command(BaseCommand):
    help = """
    This script imports Account Alias Mappings.

    Currently this requires the account alias mapping sheet be saved
    as "account_alias_mappings.csv".
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            help="set the path to read the account_alias_mappings.csv file",
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
                "account_alias_mappings.csv",
            )
        account_alias_data = parse_account_alias_mapping_data_from_csv_path(
            path
        )

        for (
            main_account_number,
            activity_number,
            alias,
        ) in account_alias_data:
            AccountAliasMapping.objects.update_or_create(
                main_account_number=main_account_number,
                activity_number=activity_number,
                defaults={"alias": alias},
            )
