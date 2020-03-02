# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.core.management.base import BaseCommand

from core.models import PaymentSchedule, ONE_TIME_PAYMENT


class Command(BaseCommand):
    help = "Renews Payments for an Activity"

    def handle(self, *args, **options):
        # Find recurring payment schedules which has an associated Activity.
        recurring_schedules = PaymentSchedule.objects.filter(
            activity__is_null=False
        ).exclude(payment_type=ONE_TIME_PAYMENT)

        for schedule in recurring_schedules:
            activity = schedule.activity
            vat_factor = activity.vat_factor
            schedule.synchronize_payments(
                activity.start_date, activity.end_date, vat_factor
            )
