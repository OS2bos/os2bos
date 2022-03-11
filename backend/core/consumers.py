# Copyright (C) 2022 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Consumers for ActiveMQ/STOMP subscriptions."""

import logging

from core.utils import (
    fetch_sbsys_appropriation_data,
    import_sbsys_appropriation,
)

logger = logging.getLogger(__name__)

# from django_stomp.services.consumer import Payload


def receive_sbsys_event(payload):
    """Receive notification from SBSYS event queue."""
    sbsys_data = payload.body

    try:
        case_id = sbsys_data["SagId"]

        appropriation_json, case_json = fetch_sbsys_appropriation_data(case_id)

        if sbsys_data["ForloebtypeId"] == 1:
            import_sbsys_appropriation(appropriation_json, case_json)

        # All went well!
        payload.ack()

    except Exception:
        # Something went wrong.
        payload.nack()
        logger.exception("Handling of SBSYS event failed.")
