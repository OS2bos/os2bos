# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Custom permissions used by this app."""

from rest_framework import permissions

from core.models import User, PaymentSchedule, STATUS_DRAFT, STATUS_EXPECTED


class IsUserAllowed(permissions.BasePermission):
    """Determine user's frontend permissions i.e., in all API operations."""

    def has_permission(self, request, view):
        """Allow depending on operation and user's profile."""
        try:
            profile = request.user.profile
        except AttributeError:
            # This should not happen except for anonymous Django users
            # which have no profile and should have no access either.
            return False
        if profile == User.READONLY:
            return request.method in permissions.SAFE_METHODS
        elif profile == User.EDIT:
            return view.get_view_name() != "Grant"
        elif profile in [User.GRANT, User.WORKFLOW_ENGINE, User.ADMIN]:
            # This user can do everything in the frontend.
            return True
        else:
            # No recognized profile, no access
            return False


class NewPaymentPermission(IsUserAllowed):
    """Check if adding a new payment is allowed."""

    def has_permission(self, request, view):
        """Allow for individual payment plan and appropriation not granted."""
        is_permitted = super().has_permission(request, view)

        if is_permitted and request.method == "POST":
            schedule_id = request.POST.get("payment_plan")
            if schedule_id:
                ps = PaymentSchedule.objects.get(id=schedule_id)
                a = ps.activity.appropriation
                is_permitted = (
                    ps.payment_type == PaymentSchedule.INDIVIDUAL_PAYMENT
                    and a.status in [STATUS_EXPECTED, STATUS_DRAFT]
                )

        return is_permitted
