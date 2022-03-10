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

from core.utils import import_sbsys_appropriation

logger = logging.getLogger(__name__)

# from django_stomp.services.consumer import Payload


def receive_sbsys_event(payload):
    """Receive notification from SBSYS event queue."""
    sbsys_data = payload.body

    try:
        case_id = sbsys_data["SagId"]

        # Do stuff

        # Disable warnings about unsafe SSL if we need to use it.
        # XXX: Not recommended in production.
        if settings.SBSYS_VERIFY_TLS is False:
            import urllib3

            urllib3.disable_warnings()
        else:
            # This should always happen in production.
            pass
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
        appropriation_json = r.json()
        # Now extract info and import to BOS
        if sbsys_data["ForloebtypeId"] == 1:
            # Import SBSYS case - this will always correspond to an
            # Appropriation in OS2bos.

            # In order to do this, we also need to get the corresponding
            # Hovedsag from SBSYS - at the very least, we need its number to
            # look up in BOS.
            #
            # The Case mush have KLE Number 27.24.00 and facet G01, i.e. its
            # number must start with "27.24.00-G01".
            cpr_number = appropriation_json["PrimaryPart"]["CPRnummer"]
            search_query = {
                "PrimaerPerson": {"CprNummer": cpr_number},
                "NummerInterval": {
                    "From": "27.24.00-G01",
                    "To": "27.24.00-G02",
                },
                "SagsStatusId": 9,
            }
            r = requests.post(
                f"{settings.SBSYS_API_URL}/sag/search",
                data=search_query,
                headers=access_headers,
                verify=verify_tls,
            )
            search_data = r.json()
            if search_data["TotalNumberOfResults"] == 0:
                raise RuntimeError(
                    "No Hovedsag found, can't import appropriation"
                )
            case_json = search_data["Results"]["0"]
            import_sbsys_appropriation(appropriation_json, case_json)

        # All went well!
        payload.ack()

    except Exception:
        # Something went wrong.
        payload.nack()
        logger.exception("Handling of SBSYS event failed.")
