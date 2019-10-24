# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import logging
import requests
import datetime

from dateutil.relativedelta import relativedelta

from django.template.loader import get_template
from django.core.mail import EmailMessage

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags

from constance import config

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from service_person_stamdata_udvidet import get_citizen

import core.models as models

logger = logging.getLogger(__name__)


def get_next_interval(from_date, payment_frequency):
    """
    Calculate the next date based on a start date and payment frequency.
    """
    from core.models import PaymentSchedule

    if payment_frequency == PaymentSchedule.DAILY:
        new_start = from_date + relativedelta(days=1)
    elif payment_frequency == PaymentSchedule.WEEKLY:
        new_start = from_date + relativedelta(weeks=1)
    elif payment_frequency == PaymentSchedule.BIWEEKLY:
        new_start = from_date + relativedelta(weeks=2)
    elif payment_frequency == PaymentSchedule.MONTHLY:
        new_start = from_date.replace(day=1) + relativedelta(months=1)
    else:
        raise ValueError(_("ukendt betalingsfrekvens"))
    return new_start


def get_person_info(cpr):
    """
    Get CPR data on a person and his/her relations.
    """
    if settings.USE_SERVICEPLATFORM:
        func = get_cpr_data
    else:
        func = get_cpr_data_mock
    result = func(cpr)
    if not result:
        return None
    for relation in result["relationer"]:
        relation_cpr = relation["cprnr"]
        relation_data = func(relation_cpr)
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
            production=settings.USE_SERVICEPLATFORM_PROD,
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


def send_activity_email(subject, template, activity):
    html_message = render_to_string(template, {"activity": activity})
    send_mail(
        subject,
        strip_tags(html_message),
        config.DEFAULT_FROM_EMAIL,
        [config.TO_EMAIL_FOR_PAYMENTS],
        html_message=html_message,
    )


def send_activity_created_email(activity):
    subject = _("Aktivitet oprettet")
    template = "emails/activity_created.html"
    send_activity_email(subject, template, activity)


def send_activity_updated_email(activity):
    subject = _("Aktivitet opdateret")
    template = "emails/activity_updated.html"
    send_activity_email(subject, template, activity)


def send_activity_expired_email(activity):
    subject = _("Aktivitet udgået")
    template = "emails/activity_expired.html"
    send_activity_email(subject, template, activity)


def send_appropriation(appropriation, included_activities=None):
    """Generate PDF and XML files from appropriation and send them to SBSYS.

    Parameters:
    appropriation: the Appropriation from which to generate the PDF and XML.
    included_activities: Activities which should be explicitly included.
    """

    if included_activities is None:
        included_activities_qs = models.Activity.objects.none()
    else:
        # Convert to queryset.
        included_activities_qs = models.Activity.objects.filter(
            id__in=(a.id for a in included_activities)
        )

    today = datetime.date.today()
    approved_main_activities = (
        appropriation.activities.filter(
            activity_type=models.MAIN_ACTIVITY, status=models.STATUS_GRANTED
        )
        .exclude(end_date__lt=today)
        .union(
            included_activities_qs.filter(activity_type=models.MAIN_ACTIVITY)
        )
    )

    approved_suppl_activities = (
        appropriation.activities.filter(
            activity_type=models.SUPPL_ACTIVITY, status=models.STATUS_GRANTED
        )
        .exclude(end_date__lt=today)
        .union(
            included_activities_qs.filter(activity_type=models.SUPPL_ACTIVITY)
        )
    )

    render_context = {
        "appropriation": appropriation,
        "main_activities": approved_main_activities,
        "supplementary_activities": approved_suppl_activities,
    }

    # Get SBSYS template and KLE number from main activity.
    section_info = appropriation.section_info
    render_context["kle_number"] = section_info.kle_number
    render_context["sbsys_template_id"] = section_info.sbsys_template_id

    # Generate os2forms.xml
    xml_template = get_template(settings.SBSYS_XML_TEMPLATE)
    xml_data = xml_template.render(context=render_context)
    xml_file_name = "os2forms.xml"

    # Generate PDF
    html_template = get_template(settings.SBSYS_APPROPRIATION_TEMPLATE)
    html_data = html_template.render(context=render_context)

    # Configure fonts for correct rendering.
    font_config = FontConfiguration()
    pdf_data = HTML(string=html_data).write_pdf(font_config=font_config)
    pdf_file_name = f"{appropriation.sbsys_id}.pdf"

    # Send as email
    msg = EmailMessage()
    msg.subject = "Bevillingsskrivelse"
    msg.body = ""
    msg.from_email = config.DEFAULT_FROM_EMAIL
    msg.to = [config.SBSYS_EMAIL]
    msg.attachments = [
        (xml_file_name, xml_data, "text/xml"),
        (pdf_file_name, pdf_data, "application/pdf"),
    ]

    msg.send()


def saml_before_login(user_data):
    "Hook called after userdata is received from IdP, before login."
    user_changed = False
    [username] = user_data["username"]
    user = models.User.objects.get(username=username)
    if "team" in user_data:
        # SAML data comes as lists with one element.
        [team_name] = user_data["team"]
        # This is safe, user exists.
        team, _ = models.Team.objects.get_or_create(
            name=team_name, defaults={"leader": user}
        )
        if team != user.team:
            user.team = team
            user_changed = True
    if "bos_profile" in user_data:
        [profile] = user_data["bos_profile"]
        if profile != user.profile:
            user.profile = profile
            is_admin = profile == models.User.ADMIN
            # Admin status is controlled by these flags.
            user.is_staff = user.is_superuser = is_admin
            user_changed = True
    if user_changed:
        user.save()


def saml_create_user(user_data):
    "Hook called after user is created in DB, before login."
    user_changed = False
    [username] = user_data["username"]
    user = models.User.objects.get(username=username)
    if "team" in user_data:
        # SAML data comes as lists with one element.
        [team_name] = user_data["team"]
        # This is safe, user exists.
        team, _ = models.Team.objects.get_or_create(
            name=team_name, defaults={"leader": user}
        )
        user.team = team
        user_changed = True
    if "bos_profile" in user_data:
        [profile] = user_data["bos_profile"]
        user.profile = profile
        is_admin = profile == models.User.ADMIN
        # Admin status is controlled by these flags.
        user.is_staff = user.is_superuser = is_admin
        user_changed = True
    if user_changed:
        user.save()


# Economy integration releated stuff - for the time being, only PRISM.
# TODO: At some point, factor out customer specific third party integrations.


def format_prism_record(payment, line_no):
    """Format a single record, i.e., a single line, for PRISM.

    Note, this follows documentation provided by Ballerup Kommune based on
    KMD's interface specification GQ311001Q for financial records (transaction
    type G69).
    """
    # Note, the fields that are hard coded *never* change.
    # We specify them below, but for clarity we hard code them in the actual
    # output.
    """
    reg_location = '000'
    interface_type = 'G69'
    org_type = "01"
    post_type = "NOR"
    line_format = "FLYD"
    """

    org_unit = 151  # TODO: Move to settings.
    # Line number is given as 5 chars with leading zeroes, or unit as 4 chars
    # with leading zeroes, as per the specification.
    header = f"000G69{line_no:05d}{org_unit:04d}01NORFLYD"

    # Now the actual posting fields. These are marked with a leading '&' and
    # must come in increasing order by field number.

    """
    103 - machine number. What? Maybe payment ID will do. Number, 5 chars
    with leading zeroes.

    104 - "ekspeditionsløbenr". What? Number, 7 chars with leading zeroes.

    110 - posting date, format 'YYYYMMDD'

    111 - account number. Account string for this payment. Number, 10 chars.

    112 - amount. Number, 12 chars with leading zeroes + 1 trailing char for
    the sign ('+' or ' ' for plus, '-' for minus - the latter is not relevant
    here).

    113 - debit or credit; 'D' for debit, 'K' for credit. Will always be 'D'.

    114 - fiscal year. Use the fiscal year of the date parameter.

    117 - udbetalingshenvisningsnummer - date + machine number + expedition
    number.

    132 - recipient number code - always '02' for CPR number.

    133 - recipient - 10 digits, CPR number.

    153 - posting text.
    """

    fields = {
        "103": f"{payment.payment_schedule.payment_id:05d}",
        "104": f"{payment.pk:07d}",
        "110": f"{payment.date.strftime('%Y%m%d')}",
        "112": f"{int(payment.amount*100):12d} ",
        "113": "D",
        "114": f"{payment.date.year}",
        "132": "02",
        "133": payment.recipient_id,
        "153": f"{payment.payment_schedule.activity.details}"[35],
    }
    fields["117"] = fields["110"] + fields["103"] + fields["104"]

    field_string = "".join(
        f"&{field_no}{fields[field_no]}" for field_no in sorted(fields)
    )
    # Record id header followed by field string.
    return header + field_string


def send_records_to_prism(writer, date=None):
    """Send relevant payments to PRISM."""

    # Default to payments due TODAY.
    if not date:
        date = datetime.date.today()

    due_payments = models.Payment.objects.filter(
        date=date,
        recipient_type=models.PaymentSchedule.PERSON,
        payment_method=models.CASH,
        paid=False,
    )
    for i, p in enumerate(due_payments):
        record = format_prism_record(p, i + 1)
        writer(record)
