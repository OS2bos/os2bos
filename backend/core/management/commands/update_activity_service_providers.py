# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    Activity,
    PaymentSchedule,
    ServiceProvider,
)
from core.utils import (
    get_company_info_from_cvr,
)

logger = logging.getLogger(
    "bevillingsplatform.update_activity_service_providers"
)


class Command(BaseCommand):
    help = (
        "Update ongoing company activities with a ServiceProvider"
        "based on the recipient_id (CVR)."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        activities = (
            Activity.objects.filter(
                payment_plan__recipient_type=PaymentSchedule.COMPANY
            )
            .exclude(payment_plan__recipient_id__exact="")
            .ongoing()
        )

        # Instead of updating activities individually
        # we can find the unique cvr_numbers and "bulk update" the activities.
        cvr_numbers = set(
            activities.values_list("payment_plan__recipient_id", flat=True)
        )

        for cvr_number in cvr_numbers:
            company_info_list = get_company_info_from_cvr(cvr_number)

            if not company_info_list:
                # Log activity ids and CVR.
                logger.info(
                    f"Could not retrieve company info"
                    f" for CVR number: {cvr_number}"
                )
                continue

            company_info = company_info_list[0]

            service_provider_info = ServiceProvider.virk_to_service_provider(
                company_info
            )

            service_provider, _ = ServiceProvider.objects.update_or_create(
                cvr_number=cvr_number, defaults=service_provider_info
            )

            to_be_updated = activities.filter(
                payment_plan__recipient_id=cvr_number
            )

            num_updated = to_be_updated.update(
                service_provider=service_provider
            )
            logger.info(
                f"{num_updated} activities updated"
                f" with CVR number: {cvr_number}"
            )
