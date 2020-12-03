# Copyright (C) 2020 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import logging

from django.core.management.base import BaseCommand

from core.models import Rate, PaymentSchedule, Activity
from core.decorators import log_to_prometheus

logger = logging.getLogger("bevillingsplatform.recalculate_on_changed_rate")


class Command(BaseCommand):
    help = "Recalculate payments schedules if they use a rate that has changed"

    @log_to_prometheus("recalculate_on_changed_rate")
    def handle(self, *args, **options):
        """Find rates and corresponding schedules, recalculate."""
        try:
            logger.info("Start recalculating payment schedules.")
            rates = Rate.objects.filter(needs_recalculation=True)
            logger.info("Recalculating rates: {}".format(list(rates)))
            payment_schedules = PaymentSchedule.objects.filter(
                payment_cost_type=PaymentSchedule.GLOBAL_RATE_PRICE,
                payment_rate__in=rates,
                activity__in=Activity.objects.ongoing(),
            )
            for payment_schedule in payment_schedules:
                payment_schedule.recalculate_prices()
                logger.info(
                    f"Recalculated payment schedule: {payment_schedule}"
                )
            rates.update(needs_recalculation=False)
            logger.info("Success: Done recalculating payment schedules.")
        except Exception:
            logger.exception(
                "An exception occurred while recalculating payments"
            )
