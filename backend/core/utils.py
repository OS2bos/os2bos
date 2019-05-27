import os
import logging
import requests
from django.conf import settings

from service_person_stamdata_udvidet import get_citizen


logger = logging.getLogger(__name__)


def get_cpr_data(cpr):
    if not os.path.isfile(settings.SERVICEPLATFORM_CERTIFICATE_PATH):
        logger.info(
            "serviceplatform certificate path: %s is not a file",
            settings.SERVICEPLATFORM_CERTIFICATE_PATH,
        )
        return None
    try:
        result = get_citizen(
            service_uuids=settings.SERVICEPLATFORM_UUIDS,
            certificate=settings.SERVICEPLATFORM_CERTIFICATE_PATH,
            cprnr=cpr
        )
        return result
    except requests.exceptions.HTTPError:
        logger.exception("get_cpr_data requests error")
        return None
