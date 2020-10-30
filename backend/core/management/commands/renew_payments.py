# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.core.management.base import BaseCommand

from core.models import PaymentSchedule
from core.decorators import log_to_prometheus


class Command(BaseCommand):
    help = "Renews payments for an unbounded Activity"

    @log_to_prometheus("renew_payments")
    def handle(self, *args, **options):
        # Find recurring unbounded payment schedules
        # which has an associated Activity.
        recurring_schedules = PaymentSchedule.objects.filter(
            activity__isnull=False, activity__end_date__isnull=True
        ).exclude(payment_type=PaymentSchedule.ONE_TIME_PAYMENT)

        for schedule in recurring_schedules:
            activity = schedule.activity
            vat_factor = activity.vat_factor
            schedule.synchronize_payments(
                activity.start_date, activity.end_date, vat_factor
            )
