# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Mixins to use in view classes."""


import logging

from rest_framework import status


class AuditMixin:
    """Allow audit logging by intercepting all API requests."""

    # By default log all calls that change data. Change e.g. by adding
    # "get" as needed.
    log_methods = ("post", "put", "patch", "delete")
    logger = logging.getLogger("bevillingsplatform.audit")

    def finalize_response(self, request, response, *args, **kwargs):
        """Perform logging and continue normal operations."""
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        status_code = response.status_code

        username = request.user.username
        action = self.action
        method = request.method
        status_code = status_code
        request_path = request.path

        if status_code == 201 and action == "create":
            objid = response.data["id"]
            request_path = f"{request_path}{objid}"
        log_str = f"{username} {action} {method} {request_path} {status_code}"
        if request.method.lower() in self.log_methods:
            # Now perform logging.
            if status.is_server_error(status_code):  # pragma: no cover
                self.logger.error(f"SERVER: {log_str} {response.data}")
            if status.is_client_error(status_code):
                self.logger.error(f"CLIENT: {log_str} {response.data}")
            else:
                self.logger.info(log_str)

        return response


class ClassificationViewSetMixin:
    """Superclass for Classifications only exposing the active."""

    def get_queryset(self):
        """Only expose active objects if user is not workflow or admin."""
        user = self.request.user
        if user.is_authenticated and user.is_workflow_engine_or_admin():
            return self.queryset
        return self.queryset.filter(active=True)
