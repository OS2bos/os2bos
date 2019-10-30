# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.core.management.base import BaseCommand

from core.utils import process_payments_for_date


class Command(BaseCommand):
    help = "Exports payments due TODAY to PRISME."

    def handle(self, *args, **options):
        """Call export function and that's it!"""
        process_payments_for_date()
