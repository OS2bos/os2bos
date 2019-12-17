# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Classes for handling CSRF authentication."""

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Override standard session to exempt request from CSRF validation.

    This is OK from a security perspective since a new SAML token is
    issued with *each* API request.
    """

    def enforce_csrf(self, request):
        """Override this function to do nothing."""
        return  # To not perform the csrf check previously happening
