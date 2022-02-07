# Copyright (C) 2022 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Consumers for ActiveMQ/STOMP subscriptions."""

import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)

# from django_stomp.services.consumer import Payload


def receive_sbsys_event(payload):
    """Receive notification from SBSYS event queue."""
    sbsys_data = payload.body
    print(str(sbsys_data))

    try:

        case_id = sbsys_data["SagId"]
        print(case_id)

        # Do stuff

        # Disable warnings about unsafe SSL if we need to use it.
        # XXX: Not recommended in production.
        if settings.SBSYS_VERIFY_TLS is False:
            import urllib3

            urllib3.disable_warnings()
        # Get SBSYS API token.
        sbsys_token_url = settings.SBSYS_TOKEN_URL
        verify_tls = settings.SBSYS_VERIFY_TLS
        token_payload = {
            "client_id": settings.SBSYS_CLIENT_ID,
            "client_secret": settings.SBSYS_CLIENT_SECRET,
            "grant_type": settings.SBSYS_GRANT_TYPE,
        }
        r = requests.post(
            sbsys_token_url, data=token_payload, verify=verify_tls
        )
        token = r.json()["access_token"]
        access_headers = {"Authorization": f"bearer {token}"}

        # Now get case info from SBSYS.
        r = requests.get(
            f"{settings.SBSYS_API_URL}/sag/{case_id}",
            headers=access_headers,
            verify=verify_tls,
        )
        case_json = r.json()
        print(str(case_json))
        # Now extract info and import to BOS
        if sbsys_data["ForloebtypeId"] == 1:
            # Create new case, possibly an Appropriation - etc.
            pass
        # All went well!
        payload.ack()

    except Exception:
        logger.info("Handling of SBSYS event failed.")
        # Something went wrong.
        payload.nack()
