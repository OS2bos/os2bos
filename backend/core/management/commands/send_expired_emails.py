# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Activity, STATUS_GRANTED
from core.utils import send_activity_expired_email
from core.decorators import log_to_prometheus

logger = logging.getLogger("bevillingsplatform.send_expired_emails")


class Command(BaseCommand):
    help = (
        "Sends emails for activities that have "
        "expired in the last number of days."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-l",
            "--last-days",
            default=1,
            type=int,
            help=(
                "Send expired emails for activities that are --last-days old."
            ),
        )

    @log_to_prometheus("send_expired_emails")
    def handle(self, *args, **options):
        logger.info("sending expired emails")
        last_days = options["last_days"]
        now_date = timezone.now().date()

        activities = Activity.objects.filter(
            end_date__gte=now_date - timedelta(days=last_days),
            end_date__lt=now_date,
            status=STATUS_GRANTED,
        )

        for activity in activities:
            if not activity.triggers_payment_email:
                continue
            logger.info("sending expired email for %s", activity.id)
            send_activity_expired_email(activity)
