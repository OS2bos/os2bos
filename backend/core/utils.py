import os
import logging
import requests

from django.conf import settings
from dateutil import rrule

from service_person_stamdata_udvidet import get_citizen


logger = logging.getLogger(__name__)


def get_person_info(cpr):
    """
    Get CPR data on a person and his/her relations.
    """
    # TODO: switch out these mock calls with the real ones.
    result = get_cpr_data_mock(cpr)
    if not result:
        return None
    for relation in result["relationer"]:
        relation_cpr = relation["cprnr"]
        relation_data = get_cpr_data_mock(relation_cpr)
        if relation_data:
            relation.update(relation_data)
    return result


def get_cpr_data(cpr):
    """
    Get CPR data from Serviceplatformen.
    """
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
            cprnr=cpr,
        )
        return result
    except requests.exceptions.HTTPError:
        logger.exception("get_cpr_data requests error")
        return None


def get_cpr_data_mock(cpr):
    """
    Use test data in place of the real 'get_cpr_data' for now.
    """
    result = {
        "statsborgerskab": "5100",
        "efternavn": "Jensen",
        "postdistrikt": "Næstved",
        "foedselsregistreringssted": "Myndighedsnavn for landekode: 5902",
        "boernUnder18": "false",
        "civilstandsdato": "1991-03-21+01:00",
        "adresseringsnavn": "Jens Jensner Jensen",
        "fornavn": "Jens Jensner",
        "tilflytningsdato": "2001-12-01+01:00",
        "markedsfoeringsbeskyttelse": "true",
        "vejkode": "1759",
        "standardadresse": "Sterkelsvej 17 A,2",
        "etage": "02",
        "koen": "M",
        "status": "80",
        "foedselsdato": "1978-04-27+01:00",
        "vejnavn": "Sterkelsvej",
        "statsborgerskabdato": "1991-09-23+02:00",
        "adressebeskyttelse": "false",
        "stilling": "Sygepl ske",
        "gaeldendePersonnummer": "2704785263",
        "vejadresseringsnavn": "Sterkelsvej",
        "civilstand": "G",
        "alder": "59",
        "relationer": [
            {"cprnr": "0123456780", "relation": "aegtefaelle"},
            {"cprnr": "1123456789", "relation": "barn"},
            {"cprnr": "2123456789", "relation": "barn"},
            {"cprnr": "3123456789", "relation": "barn"},
            {"cprnr": "0000000000", "relation": "mor"},
            {"cprnr": "0000000000", "relation": "far"},
        ],
        "postnummer": "4700",
        "husnummer": "017A",
        "vejviserbeskyttelse": "true",
        "kommunekode": "370",
    }
    return result


def compute_exclude_rruleset(rrule_set, start):
    # Exclude Saturday, Sunday.
    rrule_set.exrule(
        rrule.rrule(
            rrule.YEARLY, byweekday=(rrule.SA, rrule.SU), dtstart=start
        )
    )

    # Exclude 'static holidays'
    # Exclude Christmas days
    rrule_set.exrule(
        rrule.rrule(
            rrule.YEARLY, bymonth=12, bymonthday=[24, 25, 26], dtstart=start
        )
    )
    # Exclude Grundlovsdag
    rrule_set.exrule(
        rrule.rrule(rrule.YEARLY, bymonth=6, bymonthday=5, dtstart=start)
    )
    # Exclude New Years days
    rrule_set.exrule(
        rrule.rrule(rrule.YEARLY, bymonth=12, bymonthday=31, dtstart=start)
    )
    rrule_set.exrule(
        rrule.rrule(rrule.YEARLY, bymonth=1, bymonthday=1, dtstart=start)
    )

    # Exclude Easter and dependant holidays
    holidays_offset_from_easter = [
        -7,  # Palmesøndag
        -3,  # Skærtorsdag
        -2,  # Langfredag
        0,  # Påskedag
        1,  # 2. Påskedag
        7 * 7,  # Pinsedag
        (7 * 7) + 1,  # 2. Pinsedag
        (4 * 7) - 2,  # Store bededag
        (-3) + 6 * 7,  # Kristi himmelfartsdag
    ]
    rrule_set.exrule(
        rrule.rrule(
            rrule.YEARLY, byeaster=holidays_offset_from_easter, dtstart=start
        )
    )

    return rrule_set
