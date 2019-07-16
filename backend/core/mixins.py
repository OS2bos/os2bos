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

        if request.method.lower() in self.log_methods:
            # Now perform logging.
            if status.is_server_error(status_code):
                self.logger.error(f"SERVER ERROR: {response.data}")
            if status.is_client_error(status_code):
                self.logger.error(f"CLIENT ERROR: {response.data}")
            else:
                self.logger.info(f"INFO: {response.data}")

        return response
