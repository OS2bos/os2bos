# Copyright (C) 2022 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Consumers for ActiveMQ/STOMP subscriptions."""

import logging

logger = logging.getlogger(__name__)

from django_stomp.services.consumer import Payload


def receive_sbsys_event(payload):
    logger.info("Event received from SBSYS queue!")

    sbsys_data = payload.body

    try:

        case_id = sbsys_data.get("SagId")

        # Do stuff

        # All went well!
        payload.ack()

    except Exception:
        logger.info("Handling of SBSYS event failed.")
        # Something went wrong.
        payload.nack()
