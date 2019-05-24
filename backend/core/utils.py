import os
import requests
from django.conf import settings

from service_person_stamdata_udvidet import get_citizen


def get_cpr_data(cpr):
    if not os.path.isfile(settings.SERVICEPLATFORM_CERTIFICATE_PATH):
        return None
    try:
        result = get_citizen(
            service_uuids=settings.SERVICEPLATFORM_UUIDS,
            certificate=settings.SERVICEPLATFORM_CERTIFICATE_PATH,
            cprnr=cpr
        )
        return result
    except requests.exceptions.HTTPError:
        return None
