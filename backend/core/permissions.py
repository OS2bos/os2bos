# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from rest_framework import permissions

from core.models import User


class IsUserAllowed(permissions.BasePermission):
    """Allow everything in the frontend."""

    def has_permission(self, request, view):
        """Allow depending on operation and user's profile."""
        profile = request.user.profile
        if profile == User.READONLY:
            return request.method in permissions.SAFE_METHODS
        elif profile == User.EDIT:
            # TODO: Find out how to figure out if this is a GRANT
            return True
        elif profile in [User.GRANT, User.ADMIN]:
            # This user can do everything in the frontend.
            return True
        else:
            # No recognized profile, no access
            return False
