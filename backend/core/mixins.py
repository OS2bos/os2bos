import logging

from rest_framework import status


class AuditMixin:
    """Allow audit logging by intercepting all API requests."""

    # By default log all calls that change data. Change e.g. by adding
    # "get" as needed.
    log_methods = ("post", "put", "patch", "delete")
    logger = logging.getLogger(__name__)

    def finalize_response(self, request, response, *args, **kwargs):
        """Perform logging and continue normal operations."""

        response = super().finalize_response(
            request, response, *args, **kwargs
        )

        if request.method.lower() in self.log_methods:
            # Now perform logging.
            if response.is_error():
                logger.error(f"ERROR: {response.text}")
            else:
                logger.info(f"INFO: {response.text}")
