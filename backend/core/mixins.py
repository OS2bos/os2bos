import logging

from django.utils import timezone

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
        datetime = timezone.now()

        if status_code == 201 and action == "create":
            objid = response.data["id"]
            request_path = f"{request_path}{objid}"
        log_str = (
            f"{datetime} {username} {action} {method} "
            + f"{request_path} {status_code}"
        )
        if request.method.lower() in self.log_methods:
            # Now perform logging.
            if status.is_server_error(status_code):  # pragma: no cover
                self.logger.error(f"SERVER ERROR: {log_str} {response.data}")
            if status.is_client_error(status_code):
                self.logger.error(f"CLIENT ERROR: {log_str} {response.data}")
            else:
                self.logger.info(f"INFO: {log_str}")

        return response
