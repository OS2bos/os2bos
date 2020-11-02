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

from dateutil import rrule
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
from django.db.models import Q, BooleanField
from django.db.models.expressions import Case, When

from constance import config

from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from holidays import Denmark as danish_holidays

from service_person_stamdata_udvidet import get_citizen

from core import models
from core.data.extra_payment_date_exclusion_tuples import (
    extra_payment_date_exclusion_tuples,
)


logger = logging.getLogger(__name__)


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
    cpr_number = activity.appropriation.case.cpr_number
    subject = _("Aktivitet oprettet - %s") % cpr_number
    template = "emails/activity_created.html"
    send_activity_email(subject, template, activity)


def send_activity_updated_email(activity):
    """Send an email because an activity was updated."""
    cpr_number = activity.appropriation.case.cpr_number
    subject = _("Aktivitet opdateret - %s") % cpr_number
    template = "emails/activity_updated.html"
    send_activity_email(subject, template, activity)


def send_activity_expired_email(activity):
    """Send an email because an activity has expired."""
    cpr_number = activity.appropriation.case.cpr_number
    subject = _("Aktivitet udgået - %s") % cpr_number
    template = "emails/activity_expired.html"
    send_activity_email(subject, template, activity)


def send_activity_deleted_email(activity):
    """Send an email because an activity has been deleted."""
    cpr_number = activity.appropriation.case.cpr_number
    subject = _("Aktivitet slettet - %s") % cpr_number
    template = "emails/activity_deleted.html"
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

    # Fetch all currently granted main activities.
    approved_main_activities_ids = (
        appropriation.activities.filter(
            activity_type=models.MAIN_ACTIVITY, status=models.STATUS_GRANTED
        )
        .exclude(end_date__lt=today)
        .values_list("id", flat=True)
    )
    # Fetch all main activities from the explicitly included queryset.
    included_main_activities_ids = included_activities_qs.filter(
        activity_type=models.MAIN_ACTIVITY
    ).values_list("id", flat=True)

    # Annotate is_new so we can highlight them in the template.
    main_activities = models.Activity.objects.filter(
        Q(id__in=approved_main_activities_ids)
        | Q(id__in=included_main_activities_ids)
    ).annotate(
        is_new=Case(
            When(id__in=included_main_activities_ids, then=True),
            default=False,
            output_field=BooleanField(),
        )
    )

    # Fetch all currently granted supplementary activities.
    approved_suppl_activities_ids = appropriation.activities.filter(
        activity_type=models.SUPPL_ACTIVITY, status=models.STATUS_GRANTED
    ).exclude(end_date__lt=today)

    # Fetch all supplementary activities from the explicitly included queryset.
    included_suppl_activities_ids = included_activities_qs.filter(
        activity_type=models.SUPPL_ACTIVITY
    )
    # Annotate is_new so we can highlight them in the template.
    suppl_activities = models.Activity.objects.filter(
        Q(id__in=approved_suppl_activities_ids)
        | Q(id__in=included_suppl_activities_ids)
    ).annotate(
        is_new=Case(
            When(id__in=included_suppl_activities_ids, then=True),
            default=False,
            output_field=BooleanField(),
        )
    )

    render_context = {
        "appropriation": appropriation,
        "main_activities": main_activities,
        "supplementary_activities": suppl_activities,
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
            is_workflow_engine = profile == models.User.WORKFLOW_ENGINE
            # Admin status is controlled by these flags.
            user.is_staff = is_admin or is_workflow_engine
            user.is_superuser = is_admin
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
        is_workflow_engine = profile == models.User.WORKFLOW_ENGINE
        # Admin status is controlled by these flags.
        user.is_staff = is_admin or is_workflow_engine
        user.is_superuser = is_admin
    user.save()


# Economy integration releated stuff - for the time being, only PRISM.
# TODO: At some point, factor out customer specific third party integrations.


def format_prism_financial_record(
    payment, line_no, record_no, use_account_alias=False
):
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
        "111": f"{payment.account_alias}",
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

    17 - The unique Payment pk. 20 digits with leading zeroes.

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
        "17": f"{payment.pk:020d}",
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
            format_prism_financial_record(
                p,
                line_no=2 * i - 1,
                record_no=i,
            ),
            format_prism_payment_record(p, line_no=2 * i, record_no=i),
        )
        for i, p in enumerate(due_payments, 1)
    )
    # Flatten for easier handling.
    prism_records = list(itertools.chain(*prism_records))

    return prism_records


def write_prism_file(date, payments, tomorrow):
    """Write the actual PRISM file."""
    # The output directory is not configurable - this is mapped through Docker.
    output_dir = settings.PRISM_OUTPUT_DIR

    # The microseconds are included to avoid accidentally overwriting
    # tomorrow's file.
    filename = f"{output_dir}/{date.strftime('%Y%m%d')}_{tomorrow.microsecond}"
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
    return filename


@transaction.atomic
def export_prism_payments_for_date(date=None):
    """Process payments and output a file for PRISME.

    Default date for exporting payments is tomorrow.

    We check the day after tomorrow for one or several payment date exclusions
    and include payments for those found.
    """
    # Date = tomorrow if not given. We need "tomorrow" to set payment date.
    tomorrow = datetime.datetime.now() + relativedelta(days=1)
    if not date:
        date = tomorrow

    # Retrieve payments for the default date.
    payment_ids = list(
        due_payments_for_prism(date).values_list("id", flat=True)
    )

    # We include payments until we reach two consecutive days
    # with no exclusions.
    payment_date_exclusions_found = False
    consecutive_days = 1
    days_delta = 1
    while consecutive_days < 2:
        while models.PaymentDateExclusion.objects.filter(
            date=date + relativedelta(days=days_delta)
        ).exists():
            payment_date_exclusions_found = True
            payment_ids.extend(
                list(
                    due_payments_for_prism(
                        date + relativedelta(days=days_delta)
                    ).values_list("id", flat=True)
                )
            )
            days_delta += 1
            consecutive_days = 0

        # Also include payments for the first day after
        # one or more PaymentDateExclusion dates.
        if payment_date_exclusions_found:
            payment_ids.extend(
                list(
                    due_payments_for_prism(
                        date + relativedelta(days=days_delta)
                    ).values_list("id", flat=True)
                )
            )
        consecutive_days += 1
        days_delta += 1
        payment_date_exclusions_found = False

    payments = models.Payment.objects.filter(id__in=payment_ids)
    if not payments.exists():
        # No payments
        return

    filename = write_prism_file(date, payments, tomorrow)

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
    end_of_current_year = datetime.date.max.replace(year=current_year)
    two_years_ago = current_year - 2
    beginning_of_two_years_ago = datetime.date.min.replace(year=two_years_ago)

    granted_activities = models.Activity.objects.filter(
        status=models.STATUS_GRANTED
    )
    payment_ids = granted_activities.values_list(
        "payment_plan__payments__pk", flat=True
    )
    payments = (
        models.Payment.objects.filter(id__in=payment_ids)
        .paid_date_or_date_gte(beginning_of_two_years_ago)
        .paid_date_or_date_lte(end_of_current_year)
        .select_related(
            "payment_schedule__activity__appropriation__case",
            "payment_schedule__activity__appropriation__section",
            "payment_schedule__activity__details",
        )
    )
    payments_report_list = generate_payments_report_list(payments)
    return payments_report_list


def generate_expected_payments_report_list():
    """Generate a payments report of granted AND expected payments."""
    current_year = timezone.now().year
    end_of_current_year = datetime.date.max.replace(year=current_year)
    two_years_ago = current_year - 2
    beginning_of_two_years_ago = datetime.date.min.replace(year=two_years_ago)

    expected_activities = models.Activity.objects.filter(
        Q(status=models.STATUS_GRANTED) | Q(status=models.STATUS_EXPECTED)
    )
    payment_ids = [
        payment.id
        for activity in expected_activities
        for payment in activity.applicable_payments
    ]
    payments = (
        models.Payment.objects.filter(id__in=payment_ids)
        .paid_date_or_date_gte(beginning_of_two_years_ago)
        .paid_date_or_date_lte(end_of_current_year)
        .select_related(
            "payment_schedule__activity__appropriation__case",
            "payment_schedule__activity__appropriation__section",
            "payment_schedule__activity__details",
        )
    )
    payments_report_list = generate_payments_report_list(payments)
    return payments_report_list


def generate_payments_report_list(payments):
    """Generate a payments report list of payment dicts from payments."""
    payments_report_list = []
    for payment in payments:
        activity = payment.payment_schedule.activity
        if not activity:
            logger.exception(
                f"PaymentSchedule {payment.payment_schedule.pk}"
                f" has no activity"
            )
            continue

        case = activity.appropriation.case
        appropriation = activity.appropriation
        payment_schedule = payment.payment_schedule

        main_activity_id = (
            appropriation.main_activity.details.activity_id
            if appropriation.main_activity
            else None
        )

        main_activity_name = (
            appropriation.main_activity.details.name
            if appropriation.main_activity
            else None
        )
        # Get the historical effort_step and scaling_step.
        if payment.paid_date:
            paid_datetime = timezone.make_aware(
                datetime.datetime.combine(
                    payment.paid_date, datetime.time.max
                ),
                timezone=timezone.utc,
            )
            try:
                historical_case = case.history.as_of(paid_datetime)
            except case.DoesNotExist:
                historical_case = case.history.earliest()
            effort_step = historical_case.effort_step
            scaling_step = historical_case.scaling_step
        else:
            effort_step = case.effort_step
            scaling_step = case.scaling_step

        price_per_unit = (
            payment_schedule.price_per_unit.get_rate_amount(payment.date)
            if payment_schedule.payment_cost_type
            == payment_schedule.PER_UNIT_PRICE
            else (
                payment_schedule.payment_rate.get_rate_amount(payment.date)
                if payment_schedule.payment_cost_type
                == payment_schedule.GLOBAL_RATE_PRICE
                else ""
            )
        )

        payment_dict = {
            # payment specific.
            "id": payment.pk,
            "amount": payment.amount,
            "paid_amount": payment.paid_amount,
            "date": payment.date,
            "paid_date": payment.paid_date,
            "account_string": payment.account_string,
            "account_alias": payment.account_alias,
            # payment_schedule specific.
            "payment_schedule__payment_id": payment_schedule.payment_id,
            "payment_schedule__"
            "payment_amount": payment_schedule.payment_amount,
            "payment_schedule__"
            "payment_frequency": payment_schedule.payment_frequency,
            "recipient_type": payment_schedule.recipient_type,
            "recipient_id": payment_schedule.recipient_id,
            "recipient_name": payment_schedule.recipient_name,
            "payment_method": payment_schedule.payment_method,
            "payment_cost_type": payment_schedule.payment_cost_type,
            "price_per_unit": price_per_unit,
            "units": payment_schedule.payment_units,
            # activity specific.
            "activity__details__activity_id": activity.details.activity_id,
            "activity__details__name": activity.details.name,
            "activity_start_date": activity.start_date,
            "activity_end_date": activity.end_date,
            "activity_status": activity.status,
            # appropriation specific.
            "section": appropriation.section.paragraph,
            "section_text": appropriation.section.text,
            "sbsys_id": appropriation.sbsys_id,
            "main_activity_id": main_activity_id,
            "main_activity_name": main_activity_name,
            # case specific.
            "cpr_number": case.cpr_number,
            "name": case.name,
            "target_group": case.target_group,
            "case_worker": str(case.case_worker),
            "team": str(case.team) if case.team else None,
            "leader": str(case.team.leader) if case.team else None,
            "efforts": ",".join([e.name for e in case.efforts.all()]),
            "effort_step": str(effort_step),
            "scaling_step": str(scaling_step),
            "paying_municipality": str(case.paying_municipality),
        }
        payments_report_list.append(payment_dict)

    return payments_report_list


def create_rrule(
    payment_type, payment_frequency, payment_day_of_month, start, **kwargs
):
    """Create a dateutil.rrule to generate dates for a payment schedule.

    The rule should be based on payment_type/payment_frequency and start.
    Takes either "until" or "count" as kwargs.
    """
    # One time payments are a special case with a count of 1 always.
    if payment_type == models.PaymentSchedule.ONE_TIME_PAYMENT:
        rrule_frequency = rrule.rrule(rrule.DAILY, dtstart=start, count=1)
    elif payment_frequency == models.PaymentSchedule.DAILY:
        rrule_frequency = rrule.rrule(rrule.DAILY, dtstart=start, **kwargs)
    elif payment_frequency == models.PaymentSchedule.WEEKLY:
        rrule_frequency = rrule.rrule(rrule.WEEKLY, dtstart=start, **kwargs)
    elif payment_frequency == models.PaymentSchedule.BIWEEKLY:
        rrule_frequency = rrule.rrule(
            rrule.WEEKLY, dtstart=start, interval=2, **kwargs
        )
    elif payment_frequency == models.PaymentSchedule.MONTHLY:
        monthly_date = payment_day_of_month
        if monthly_date > 28:
            monthly_date = [d for d in range(28, monthly_date + 1)]
        rrule_frequency = rrule.rrule(
            rrule.MONTHLY,
            dtstart=start,
            bymonthday=monthly_date,
            bysetpos=-1,
            **kwargs,
        )
    else:
        raise ValueError(_("ukendt betalingsfrekvens"))
    return rrule_frequency


def generate_payment_date_exclusion_dates(years=None):
    """
    Generate "default" dates for payment date exclusions for a number of years.

    The default are danish holidays and weekends.
    """
    if not years:
        current_year = datetime.date.today().year
        years = [current_year, current_year + 1]

    danish_holiday_dates = list(danish_holidays(years=years))

    start_date = datetime.date(min(years), 1, 1)
    end_date = datetime.date(max(years), 12, 31)

    weekend_dates = [
        dt.date()
        for dt in (
            rrule.rrule(
                dtstart=start_date,
                until=end_date,
                freq=rrule.WEEKLY,
                byweekday=(rrule.SA, rrule.SU),
            )
        )
    ]

    extra_payment_date_exclusions = []
    payment_date_exclusion_tuples = extra_payment_date_exclusion_tuples
    for year in years:
        for day, month in payment_date_exclusion_tuples:
            extra_payment_date_exclusions.append(
                datetime.date(day=day, month=month, year=year)
            )

    exclusion_dates = []
    exclusion_dates.extend(danish_holiday_dates)
    exclusion_dates.extend(weekend_dates)
    exclusion_dates.extend(extra_payment_date_exclusions)

    return sorted(list(set(exclusion_dates)))
