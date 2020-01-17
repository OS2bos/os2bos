# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Utilities used by other parts of this app."""


import os
import logging
import requests
import datetime
import itertools

from dateutil.relativedelta import relativedelta

from django.template.loader import get_template
from django.core.mail import EmailMessage

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import strip_tags
from django.db import transaction
from django.db.models import Q

from constance import config

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from service_person_stamdata_udvidet import get_citizen

from core import models


logger = logging.getLogger(__name__)


def get_next_interval(from_date, payment_frequency):
    """Calculate the next date based on start date and payment frequency."""
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
    """Get CPR data on a person and his/her relations."""
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
    """Get CPR data from Serviceplatformen."""
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
    """Use test data in place of the real 'get_cpr_data' for develop/test."""
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
    """Send an email concerning an updated activity."""
    html_message = render_to_string(template, {"activity": activity})
    send_mail(
        subject,
        strip_tags(html_message),
        config.DEFAULT_FROM_EMAIL,
        [config.TO_EMAIL_FOR_PAYMENTS],
        html_message=html_message,
    )


def send_activity_created_email(activity):
    """Send an email because an activity was created."""
    subject = _("Aktivitet oprettet")
    template = "emails/activity_created.html"
    send_activity_email(subject, template, activity)


def send_activity_updated_email(activity):
    """Send an email because an activity was updated."""
    subject = _("Aktivitet opdateret")
    template = "emails/activity_updated.html"
    send_activity_email(subject, template, activity)


def send_activity_expired_email(activity):
    """Send an email because an activity has expired."""
    subject = _("Aktivitet udgået")
    template = "emails/activity_expired.html"
    send_activity_email(subject, template, activity)


def send_appropriation(appropriation, included_activities=None):
    """Generate PDF and XML files from appropriation and send them to SBSYS.

    :param appropriation: the Appropriation from which to generate PDF and XML.
    :param included_activities: Activities which should be explicitly included.

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


def saml_before_login(user_data):  # noqa: D401
    """Hook called after userdata is received from IdP, before login."""
    user_changed = False
    username = user_data["username"][0]
    user = models.User.objects.get(username=username)
    if "team" in user_data:
        # SAML data comes as lists with one element.
        team_name = user_data["team"][0]
        # This is safe, user exists.
        team, _ = models.Team.objects.get_or_create(
            name=team_name, defaults={"leader": user}
        )
        if team != user.team:
            user.team = team
            user_changed = True
    if "bos_profile" in user_data:
        profile = models.User.max_profile(user_data["bos_profile"])
        if profile != user.profile:
            user.profile = profile
            is_admin = profile == models.User.ADMIN
            # Admin status is controlled by these flags.
            user.is_staff = user.is_superuser = is_admin
            user_changed = True
    if user_changed:
        user.save()


def saml_create_user(user_data):  # noqa: D401
    """Hook called after user is created in DB, before login."""
    username = user_data["username"][0]
    user = models.User.objects.get(username=username)
    if "team" in user_data:
        # SAML data comes as lists with one element.
        team_name = user_data["team"][0]
    else:
        team_name = config.DEFAULT_TEAM_NAME

    # This is safe, user exists.
    team, _ = models.Team.objects.get_or_create(
        name=team_name, defaults={"leader": user}
    )
    user.team = team

    if "bos_profile" in user_data:
        profile = models.User.max_profile(user_data["bos_profile"])
        user.profile = profile
        is_admin = profile == models.User.ADMIN
        # Admin status is controlled by these flags.
        user.is_staff = user.is_superuser = is_admin
    user.save()


# Economy integration releated stuff - for the time being, only PRISM.
# TODO: At some point, factor out customer specific third party integrations.


def format_prism_financial_record(payment, line_no, record_no):
    """Format a single financial record for PRISM, on a single line.

    This follows documentation provided by Ballerup Kommune based on
    KMD's interface specification GQ311001Q for financial records (transaction
    type G69).
    """
    # The fields that are hard coded *never* change.
    # We specify them as variables below, but in reality we might as
    # well hardcode them in the actual output.

    reg_location = "000"
    interface_type = "G69"
    org_type = "01"
    post_type = "NOR"
    line_format = "FLYD"

    # Line number is given as 5 chars with leading zeroes, org unit as 4 chars
    # with leading zeroes, as per the specification.
    header = (
        f"{reg_location}{interface_type}{line_no:05d}"
        + f"{config.PRISM_ORG_UNIT:04d}{org_type}{post_type}{line_format}"
    )

    # Now the actual posting fields. These are marked with a leading '&' and
    # must come in increasing order by field number.

    """
    103 - machine number. Here, always '00482'. Number, 5 chars with leading
    zeroes.

    104 - "ekspeditionsløbenr". Enumerating each posting, 1, 2, ... Number, 7
    chars with leading zeroes. The "record_no" parameter.

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

    133 - beneficiary - 10 digits, CPR number.

    153 - posting text.
    """

    case_cpr = payment.payment_schedule.activity.appropriation.case.cpr_number
    fields = {
        "103": f"{config.PRISM_MACHINE_NO:05d}",
        "104": f"{record_no:07d}",
        "110": f"{payment.date.strftime('%Y%m%d')}",
        "111": f"{payment.account_string}",
        "112": f"{int(payment.amount*100):012d} ",
        "113": "D",
        "114": f"{payment.date.year}",
        "132": "02",
        "133": f"{case_cpr}",
        "153": f"{payment.payment_schedule.payment_id}",
    }
    fields["117"] = fields["110"] + fields["103"] + fields["104"]

    field_string = "".join(
        f"&{field_no}{fields[field_no]}" for field_no in sorted(fields)
    )
    # Record id header followed by field string.
    return header + field_string


def format_prism_payment_record(payment, line_no, record_no):
    """Format a single payment record for PRISM, on a single line.

    This follows documentation provided by Ballerup Kommune based on
    KMD's interface specification GF200001Q for creditor records
    (transaction type G68).
    """
    # First, we format the header.
    # The header has the following fields that never change and might as
    # well be hard coded:

    reg_location = "000"
    interface_type = "G68"
    transaction_type = "01"
    line_format = "1"

    header = (
        f"{reg_location}{interface_type}{line_no:05d}"
        + f"{config.PRISM_ORG_UNIT:04d}{transaction_type}{line_format}"
    )

    # Now the mandatory fields. In the file, they are preceded with "&"
    # and must come in non-decreasing order.
    """
    02 - org unit, municipality number - 4 digits with leading zeroes.

    03 - organisation type, always given as '00'. 2 digits.

    08 - amount. 11 digits with leading zeroes.

    09 - sign. '+' for larger than zero, '-' for less. Always '+'.

    10 - ident. code. '02' for CPR number and payment to person.

    11 - payee. CPR number - 10 digits.

    12 - date. 8 digits, 'YYYYMMDD'.

    16 - posteringshenvisningsnummer. As 117 in the finance records -
    date + machine number + record number - 8 chars + 5 chars + 7 chars.

    17 - Payment ID. 20 digits with leading zeroes.

    40 - posting text.
    """

    payment_id = payment.payment_schedule.payment_id
    fields = {
        "02": f"{config.PRISM_ORG_UNIT:04d}",
        "03": "00",
        "08": f"{int(payment.amount*100):011d}",
        "09": "+",
        "10": "02",
        "11": f"{payment.recipient_id}",
        "12": f"{payment.date.strftime('%Y%m%d')}",
        "17": f"{payment_id:020d}",
        "40": f"Fra Ballerup Kommune ref: {payment_id}",
    }
    fields[
        "16"
    ] = f"{fields['12']}{config.PRISM_MACHINE_NO:05d}{record_no:07d}"

    field_string = "".join(
        f"&{field_no}{fields[field_no]}" for field_no in sorted(fields)
    )
    # Record id header followed by field string.
    return header + field_string


def due_payments_for_prism(date):
    """Return payments which are due on date and should be sent to PRISM."""
    return models.Payment.objects.filter(
        date=date,
        recipient_type=models.PaymentSchedule.PERSON,
        payment_method=models.CASH,
        paid=False,
        payment_schedule__activity__status=models.STATUS_GRANTED,
        payment_schedule__fictive=False,
        amount__gt=0,
    )


def generate_records_for_prism(due_payments):
    """Generate the list of records for writing to PRISM file."""
    prism_records = (
        (
            format_prism_financial_record(p, line_no=2 * i - 1, record_no=i),
            format_prism_payment_record(p, line_no=2 * i, record_no=i),
        )
        for i, p in enumerate(due_payments, 1)
    )
    # Flatten for easier handling.
    prism_records = list(itertools.chain(*prism_records))

    return prism_records


@transaction.atomic
def export_prism_payments_for_date(date=None):
    """Process payments and output a file for PRISME."""
    # The output directory is not configurable - this is mapped through Docker.
    output_dir = settings.PRISM_OUTPUT_DIR
    # Date = tomorrow if not given. We need "tomorrow" to set payment date.
    tomorrow = datetime.datetime.now() + relativedelta(day=1)
    if not date:
        date = tomorrow

    # The microseconds are included to avoid accidentally overwriting
    # tomorrow's file.
    filename = f"{output_dir}/{date.strftime('%Y%m%d')}_{tomorrow.microsecond}"
    payments = due_payments_for_prism(date)
    if not payments.exists():
        # No payments
        return
    with open(filename, "w") as f:
        # Generate and write preamble.

        """
        The fields given below never change and might as well be hard coded in
        the output:
        """

        hdisp = " "  # Blank, must be there.
        media_type = "6"  # Don't ask.
        evolbr = "      "  # 6 blanks - once again, don't ask.
        mixed = "1"
        trans_code = "Z300"  # Identifies transaction start.

        user_number = f"{config.PRISM_ORG_UNIT:04d}"  # Org unit.
        day_of_year = tomorrow.timetuple().tm_yday  # Day of year.

        preamble_string = (
            f"{trans_code}{hdisp}{user_number}{media_type}{evolbr}"
            + f"{day_of_year}{mixed}"
        )
        f.write(f"{preamble_string}\n")
        # Generate and write the records.
        prism_records = generate_records_for_prism(payments)
        f.write("\n".join(prism_records))

        # Generate and write the final line.
        cslutd = "SLUTD"  # Don't ask.
        fantrec = f"{len(prism_records):05d}"
        f.write(f"\n{cslutd}{fantrec}\n")
    # Register all payments as paid.
    for p in payments:
        p.paid = True
        p.paid_amount = p.amount
        p.paid_date = tomorrow
        p.save()
    # Return filename for info and verification.
    return filename


def generate_granted_payments_report_list():
    """Generate a payments report of only granted payments."""
    current_year = timezone.now().year
    two_years_ago = current_year - 2

    granted_activities = models.Activity.objects.filter(
        status=models.STATUS_GRANTED,
        start_date__year__gte=two_years_ago,
        end_date__year__lte=current_year,
    )

    payments_report_list = generate_payments_report_list(granted_activities)
    return payments_report_list


def generate_expected_payments_report_list():
    """Generate a payments report of granted AND expected payments."""
    current_year = timezone.now().year
    two_years_ago = current_year - 2

    expected_activities = models.Activity.objects.filter(
        Q(status=models.STATUS_GRANTED) | Q(status=models.STATUS_EXPECTED),
        start_date__year__gte=two_years_ago,
        end_date__year__lte=current_year,
    )

    payments_report_list = generate_payments_report_list(expected_activities)
    return payments_report_list


def generate_payments_report_list(activities):
    """Generate a payments report list of payment dicts from activities."""
    payments_report_list = []
    for activity in activities:
        for payment in activity.applicable_payments:
            case = activity.appropriation.case
            appropriation = activity.appropriation
            payment_schedule = activity.payment_plan

            payment_dict = {
                # payment specific.
                "amount": payment.amount,
                "paid_amount": payment.paid_amount,
                "date": payment.date,
                "paid_date": payment.paid_date,
                "account_string": payment.account_string,
                # payment_schedule specific.
                "payment_schedule__"
                "payment_amount": payment_schedule.payment_amount,
                "payment_schedule__"
                "payment_frequency": payment_schedule.payment_frequency,
                "recipient_type": payment_schedule.recipient_type,
                "recipient_id": payment_schedule.recipient_id,
                "recipient_name": payment_schedule.recipient_name,
                "payment_method": payment_schedule.payment_method,
                # activity specific.
                "details": str(activity.details),
                "activity_start_date": activity.start_date,
                "activity_end_date": activity.end_date,
                # appropriation specific.
                "section": appropriation.section,
                "sbsys_id": appropriation.sbsys_id,
                # case specific.
                "cpr_number": case.cpr_number,
                "name": case.name,
                "effort_step": str(case.effort_step),
                "paying_municipality": str(case.paying_municipality),
            }
            payments_report_list.append(payment_dict)

    return payments_report_list
