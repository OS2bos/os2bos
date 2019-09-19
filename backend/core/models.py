# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from datetime import date, timedelta
from decimal import Decimal
import uuid
from dateutil.relativedelta import relativedelta
from dateutil import rrule

from django import forms
from django.db import models, transaction
from django.db.models import Q, F
from django.contrib.postgres import fields as postgres_fields
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django_audit_fields.models import AuditModelMixin
from simple_history.models import HistoricalRecords

from core.managers import PaymentQuerySet, CaseQuerySet
from core.utils import send_appropriation, get_next_interval

# Target group - definitions and choice list.
FAMILY_DEPT = "FAMILY_DEPT"
DISABILITY_DEPT = "DISABILITY_DEPT"
target_group_choices = (
    (FAMILY_DEPT, _("familieafdelingen")),
    (DISABILITY_DEPT, _("handicapafdelingen")),
)

# Effort steps - definitions and choice list.
STEP_ONE = "STEP_ONE"
STEP_TWO = "STEP_TWO"
STEP_THREE = "STEP_THREE"
STEP_FOUR = "STEP_FOUR"
STEP_FIVE = "STEP_FIVE"
STEP_SIX = "STEP_SIX"

effort_steps_choices = (
    (STEP_ONE, _("Trin 1: Tidlig indsats i almenområdet")),
    (STEP_TWO, _("Trin 2: Forebyggelse")),
    (STEP_THREE, _("Trin 3: Hjemmebaserede indsatser")),
    (STEP_FOUR, _("Trin 4: Anbringelse i slægt eller netværk")),
    (STEP_FIVE, _("Trin 5: Anbringelse i forskellige typer af plejefamilier")),
    (STEP_SIX, _("Trin 6: Anbringelse i institutionstilbud")),
)

# Payment methods and choice list.
CASH = "CASH"
SD = "SD"
INVOICE = "INVOICE"
INTERNAL = "INTERNAL"
payment_method_choices = (
    (CASH, _("Udbetaling")),
    (SD, _("SD-LØN")),
    (INVOICE, _("Faktura")),
    (INTERNAL, _("Intern afregning")),
)


# Activity types and choice list.
MAIN_ACTIVITY = "MAIN_ACTIVITY"
SUPPL_ACTIVITY = "SUPPL_ACTIVITY"
type_choices = (
    (MAIN_ACTIVITY, _("hovedaktivitet")),
    (SUPPL_ACTIVITY, _("følgeaktivitet")),
)

# Activity status definitions and choice list.
STATUS_DRAFT = "DRAFT"
STATUS_EXPECTED = "EXPECTED"
STATUS_GRANTED = "GRANTED"
STATUS_DELETED = "DELETED"
# Below, a "virtual" status only relevant for appropriations.
STATUS_EXPIRED = "EXPIRED"

status_choices = (
    (STATUS_DRAFT, _("kladde")),
    (STATUS_EXPECTED, _("forventet")),
    (STATUS_GRANTED, _("bevilget")),
)


class Municipality(models.Model):
    """Represents a Danish municipality."""

    class Meta:
        verbose_name = _("kommune")
        verbose_name_plural = _("kommuner")

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class SchoolDistrict(models.Model):
    """Represents a Danish school district."""

    class Meta:
        verbose_name = _("distrikt")
        verbose_name_plural = _("distrikter")

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class PaymentMethodDetails(models.Model):
    """ Contains extra information about a payment method."""

    class Meta:
        verbose_name = _("betalingsmåde detalje")
        verbose_name_plural = _("betalingsmåde detaljer")

    tax_card_choices = (
        ("MAIN_CARD", _("Hovedkort")),
        ("SECONDARY_CARD", _("Bikort")),
    )

    tax_card = models.CharField(
        max_length=128,
        verbose_name=(_("skattekort")),
        choices=tax_card_choices,
    )

    def __str__(self):
        return f"{self.get_tax_card_display()}"


class User(AbstractUser):
    class Meta:
        verbose_name = _("bruger")
        verbose_name_plural = _("brugere")

    team = models.ForeignKey(
        "Team",
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        # Don't allow creation of users with no team through user interface.
        blank=False,
    )


class Team(models.Model):
    """Represents a team in the administration."""

    name = models.CharField(max_length=128, verbose_name=_("navn"))
    leader = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="managed_teams",
        verbose_name=_("leder"),
    )

    def __str__(self):
        return f"{self.name}"


class PaymentSchedule(models.Model):
    """Schedule a payment for an Activity."""

    class Meta:
        verbose_name = _("betalingsplan")
        verbose_name_plural = _("betalingsplaner")

    # Recipient types and choice list.
    INTERNAL = "INTERNAL"
    PERSON = "PERSON"
    COMPANY = "COMPANY"
    recipient_choices = (
        (INTERNAL, _("Intern")),
        (PERSON, _("Person")),
        (COMPANY, _("Firma")),
    )
    recipient_type = models.CharField(
        max_length=128,
        verbose_name=_("betalingsmodtager"),
        choices=recipient_choices,
    )
    recipient_id = models.CharField(max_length=128, verbose_name=_("ID"))
    recipient_name = models.CharField(max_length=128, verbose_name=_("navn"))

    payment_method = models.CharField(
        max_length=128,
        verbose_name=_("betalingsmåde"),
        choices=payment_method_choices,
    )
    payment_method_details = models.ForeignKey(
        PaymentMethodDetails,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("betalingsmåde detalje"),
    )
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    payment_frequency_choices = (
        (DAILY, _("Dagligt")),
        (WEEKLY, _("Ugentligt")),
        (BIWEEKLY, _("Hver 2. uge")),
        (MONTHLY, _("Månedligt")),
    )
    payment_frequency = models.CharField(
        max_length=128,
        verbose_name=_("betalingsfrekvens"),
        choices=payment_frequency_choices,
        null=True,
        blank=True,
    )
    # This field only applies to monthly payments.
    # It may be replaced by a more general way of handling payment dates
    # independently of the activity's start date.
    payment_day_of_month = models.IntegerField(
        verbose_name=_("betales d."),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )

    ONE_TIME_PAYMENT = "ONE_TIME_PAYMENT"
    RUNNING_PAYMENT = "RUNNING_PAYMENT"
    PER_HOUR_PAYMENT = "PER_HOUR_PAYMENT"
    PER_DAY_PAYMENT = "PER_DAY_PAYMENT"
    PER_KM_PAYMENT = "PER_KM_PAYMENT"
    payment_type_choices = (
        ((ONE_TIME_PAYMENT), _("Engangsudgift")),
        ((RUNNING_PAYMENT), _("Fast beløb, løbende")),
        ((PER_HOUR_PAYMENT), _("Takst pr. time")),
        ((PER_DAY_PAYMENT), _("Takst pr. døgn")),
        ((PER_KM_PAYMENT), _("Takst pr. kilometer")),
    )
    payment_type = models.CharField(
        max_length=128,
        verbose_name=_("betalingstype"),
        choices=payment_type_choices,
    )
    # number of units to pay, ie. XX kilometres or hours
    payment_units = models.PositiveIntegerField(
        verbose_name=_("betalingsenheder"), blank=True, null=True
    )
    payment_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("beløb"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False)

    @property
    def next_payment(self):
        today = date.today()
        upcoming_payments = self.payments.filter(date__gt=today).order_by(
            "date"
        )
        if not upcoming_payments.exists():
            return None
        else:
            return upcoming_payments.first()

    @staticmethod
    def is_payment_and_recipient_allowed(payment_method, recipient_type):
        allowed = {
            PaymentSchedule.INTERNAL: [INTERNAL],
            PaymentSchedule.PERSON: [CASH, SD],
            PaymentSchedule.COMPANY: [INVOICE, CASH],
        }
        return payment_method in allowed[recipient_type]

    @property
    def triggers_payment_email(self):
        """
        Trigger a payment email only in the (recipient_type->payment_method)
        case of Internal->Internal or Person->SD.
        """
        if (
            self.recipient_type == self.INTERNAL
            and self.payment_method == INTERNAL
        ) or (
            self.recipient_type == self.PERSON and self.payment_method == SD
        ):
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.is_payment_and_recipient_allowed(
            self.payment_method, self.recipient_type
        ):
            raise ValueError(
                _("ugyldig betalingsmetode for betalingsmodtager")
            )
        super().save(*args, **kwargs)

    def create_rrule(self, start, end):
        """
        Create a dateutil.rrule based on payment_type/payment_frequency,
        start and end.
        """
        if self.payment_type == self.ONE_TIME_PAYMENT:
            rrule_frequency = rrule.rrule(rrule.DAILY, count=1, dtstart=start)
        elif self.payment_frequency == self.DAILY:
            rrule_frequency = rrule.rrule(
                rrule.DAILY, dtstart=start, until=end
            )
        elif self.payment_frequency == self.WEEKLY:
            rrule_frequency = rrule.rrule(
                rrule.WEEKLY, dtstart=start, until=end
            )
        elif self.payment_frequency == self.BIWEEKLY:
            rrule_frequency = rrule.rrule(
                rrule.WEEKLY, dtstart=start, until=end, interval=2
            )
        elif self.payment_frequency == self.MONTHLY:
            monthly_date = self.payment_day_of_month
            if monthly_date > 28:
                monthly_date = [d for d in range(28, monthly_date + 1)]
            rrule_frequency = rrule.rrule(
                rrule.MONTHLY,
                dtstart=start,
                until=end,
                bymonthday=monthly_date,
                bysetpos=-1,
            )
        else:
            raise ValueError(_("ukendt betalingsfrekvens"))
        return rrule_frequency

    def calculate_per_payment_amount(self, vat_factor):

        if self.payment_type in [self.ONE_TIME_PAYMENT, self.RUNNING_PAYMENT]:
            return self.payment_amount / 100 * vat_factor
        elif self.payment_type in [
            self.PER_HOUR_PAYMENT,
            self.PER_DAY_PAYMENT,
            self.PER_KM_PAYMENT,
        ]:
            return (
                (self.payment_units * self.payment_amount) / 100 * vat_factor
            )
        else:
            raise ValueError(_("ukendt betalingstype"))

    def generate_payments(self, start, end=None, vat_factor=Decimal("100")):
        """
        Generates payments with a start and end.
        """
        # If no end is specified, choose end of the next year.
        if not end:
            today = date.today()
            end = today.replace(
                year=today.year + 1, month=date.max.month, day=date.max.day
            )

        rrule_frequency = self.create_rrule(start, end)

        dates = list(rrule_frequency)

        for date_obj in dates:
            Payment.objects.create(
                date=date_obj,
                recipient_type=self.recipient_type,
                recipient_id=self.recipient_id,
                recipient_name=self.recipient_name,
                payment_method=self.payment_method,
                amount=self.calculate_per_payment_amount(vat_factor),
                payment_schedule=self,
            )

    def synchronize_payments(self, start, end, vat_factor=Decimal("100")):
        """
        Synchronize an existing number of payments for a new end_date.
        """
        today = date.today()

        # If no existing payments is generated we can't do anything.
        if not self.payments.exists():
            return

        newest_payment = self.payments.order_by("-date").first()

        # One time payment is a special case and should not be handled.
        if self.payment_type == PaymentSchedule.ONE_TIME_PAYMENT:
            return
        # The new start_date should be based on the newest payment date
        # and the payment frequency.
        new_start = get_next_interval(
            newest_payment.date, self.payment_frequency
        )

        # Handle the case where an end_date is set in the future
        # after already having generated payments with no end_date.
        if end and (new_start < end):
            self.generate_payments(new_start, end, vat_factor)

        # Handle the case where an end_date is set in the past after
        # already having generated payments with no end_date
        if end and (newest_payment.date > end):
            self.payments.filter(date__gt=end).delete()

        # If end is unbounded and the newest payment has a date less than
        # 6 months from now we can generate new payments for another period.
        if not end and (newest_payment.date < today + relativedelta(months=6)):
            self.generate_payments(new_start, end, vat_factor)

    def __str__(self):
        recipient_type_str = self.get_recipient_type_display()
        payment_frequency_str = self.get_payment_frequency_display()
        payment_type_str = self.get_payment_type_display()
        return (
            f"{recipient_type_str} - "
            f"{self.recipient_name} - "
            f"{payment_type_str} - "
            f"{payment_frequency_str} - "
            f"{self.payment_amount}"
        )


class Payment(models.Model):
    """Represents an amount paid to a supplier - amount, recpient, date.

    These may be entered manually, but ideally they should be imported
    from an accounts payable system."""

    class Meta:
        verbose_name = _("betaling")
        verbose_name_plural = _("betalinger")

    objects = PaymentQuerySet.as_manager()

    date = models.DateField(verbose_name=_("betalingsdato"))

    recipient_type = models.CharField(
        max_length=128,
        verbose_name=_("betalingsmodtager"),
        choices=PaymentSchedule.recipient_choices,
    )
    recipient_id = models.CharField(max_length=128, verbose_name=_("ID"))
    recipient_name = models.CharField(max_length=128, verbose_name=_("Navn"))

    payment_method = models.CharField(
        max_length=128,
        verbose_name=_("betalingsmåde"),
        choices=payment_method_choices,
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("beløb"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    paid = models.BooleanField(default=False, verbose_name=_("betalt"))

    payment_schedule = models.ForeignKey(
        PaymentSchedule,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("betalingsplan"),
    )

    def save(self, *args, **kwargs):
        if not self.payment_schedule.is_payment_and_recipient_allowed(
            self.payment_method, self.recipient_type
        ):
            raise ValueError(
                _("ugyldig betalingsmetode for betalingsmodtager")
            )
        super().save(*args, **kwargs)

    def __str__(self):
        recipient_type_str = self.get_recipient_type_display()
        return (
            f"{recipient_type_str} - "
            f"{self.recipient_name} - "
            f"{self.date} - "
            f"{self.amount}"
        )


class Case(AuditModelMixin, models.Model):
    """A case, covering one child - corresponding to a Hovedsag in SBSYS."""

    class Meta:
        verbose_name = _("sag")
        verbose_name_plural = _("sager")

    objects = CaseQuerySet.as_manager()

    sbsys_id = models.CharField(
        unique=True, max_length=128, verbose_name=_("SBSYS-ID")
    )
    cpr_number = models.CharField(max_length=10, verbose_name=_("cpr-nummer"))
    name = models.CharField(max_length=128, verbose_name=_("navn"))
    case_worker = models.ForeignKey(
        User,
        verbose_name=_("sagsbehandler"),
        related_name="cases",
        on_delete=models.PROTECT,
    )
    team = models.ForeignKey(
        Team,
        verbose_name=_("team"),
        related_name="cases",
        on_delete=models.PROTECT,
        blank=True,
    )
    district = models.ForeignKey(
        SchoolDistrict,
        related_name="cases",
        verbose_name=_("skoledistrikt"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    paying_municipality = models.ForeignKey(
        Municipality,
        verbose_name=_("betalingskommune"),
        related_name="pays_for",
        on_delete=models.PROTECT,
    )
    acting_municipality = models.ForeignKey(
        Municipality,
        verbose_name=_("handlekommune"),
        related_name="acts_on",
        on_delete=models.PROTECT,
    )
    residence_municipality = models.ForeignKey(
        Municipality,
        verbose_name=_("bopælskommune"),
        related_name="resident_clients",
        on_delete=models.PROTECT,
    )
    target_group = models.CharField(
        max_length=128,
        verbose_name=_("målgruppe"),
        choices=target_group_choices,
    )
    effort_step = models.CharField(
        max_length=128,
        choices=effort_steps_choices,
        verbose_name=_("indsatstrappe"),
    )
    scaling_step = models.PositiveSmallIntegerField(
        verbose_name=_("skaleringstrappe"),
        choices=[(i, i) for i in range(1, 11)],
    )
    assessment_comment = models.TextField(
        verbose_name=_("supplerende oplysninger til vurdering"), blank=True
    )
    refugee_integration = models.BooleanField(
        verbose_name=_("integrationsindsatsen"), default=False
    )
    cross_department_measure = models.BooleanField(
        verbose_name=_("tværgående ungeindsats"), default=False
    )
    note = models.TextField(verbose_name=_("note"), blank=True)

    # We only need to store historical records of
    # effort_step, scaling_step, case_worker,
    # thus we can exclude everything else.
    history = HistoricalRecords(
        excluded_fields=[
            "refugee_integration",
            "cross_department_measure",
            "target_group",
            "residence_municipality",
            "acting_municipality",
            "paying_municipality",
            "district",
            "name",
            "cpr_number",
            "sbsys_id",
            "note",
        ]
    )

    def __str__(self):
        return f"{self.sbsys_id}"

    @property
    def expired(self):
        today = timezone.now().date()
        all_main_activities = Activity.objects.filter(
            activity_type=MAIN_ACTIVITY, appropriation__case=self
        )
        # If no activities exists, we will not consider it expired.
        if not all_main_activities.exists():
            return False

        all_main_expired_activities = all_main_activities.filter(
            end_date__lt=today
        )
        return (
            all_main_activities.count() == all_main_expired_activities.count()
        )


class ApprovalLevel(models.Model):
    class Meta:
        verbose_name = _("bevillingsniveau")
        verbose_name_plural = _("bevillingsniveauer")

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class Section(models.Model):
    """Law sections and the corresponding KLE codes.

    Each section is associated with the target group for which it is
    allowed as well as the action steps allowed.
    """

    class Meta:
        verbose_name = _("paragraf")
        verbose_name_plural = _("paragraffer")

    paragraph = models.CharField(max_length=128, verbose_name=_("paragraf"))
    text = models.TextField(verbose_name=_("forklarende tekst"))
    allowed_for_family_target_group = models.BooleanField(
        verbose_name=_("tilladt for familieafdelingen"), default=False
    )
    allowed_for_disability_target_group = models.BooleanField(
        verbose_name=_("tilladt for handicapafdelingen"), default=False
    )
    allowed_for_steps = postgres_fields.ArrayField(
        models.CharField(max_length=128, choices=effort_steps_choices),
        size=6,
        verbose_name=_("tilladt for trin i indsatstrappen"),
    )
    law_text_name = models.CharField(
        max_length=128, verbose_name=_("lov tekst navn")
    )

    def __str__(self):
        return f"{self.paragraph}"


class Appropriation(AuditModelMixin, models.Model):
    """An appropriation of funds in a Case - corresponds to a Sag in SBSYS."""

    class Meta:
        verbose_name = _("bevilling")
        verbose_name_plural = _("bevillinger")

    sbsys_id = models.CharField(
        unique=True, max_length=128, verbose_name=_("SBSYS-ID")
    )
    section = models.ForeignKey(
        Section,
        related_name="appropriations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("paragraf"),
    )

    @property
    def status(self):
        if not self.activities.exists() or not self.main_activity:
            return STATUS_DRAFT
        # We now know that there is at least one activity and a main activity.
        today = timezone.now().date()
        if self.main_activity.end_date < today:
            return STATUS_EXPIRED
        # Now, the status should follow the main activity's status.
        return self.main_activity.status

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="appropriations",
        verbose_name=_("sag"),
    )
    note = models.TextField(
        verbose_name=_("supplerende oplysninger"), blank=True
    )

    @property
    def total_granted_this_year(self):
        """
        Retrieve total amount granted this year for payments related to
        this Appropriation (both main and supplementary activities).
        """

        granted_activities = self.activities.all().filter(
            status=STATUS_GRANTED
        )

        this_years_payments = Payment.objects.filter(
            payment_schedule__activity__in=granted_activities
        ).in_this_year()

        return this_years_payments.amount_sum()

    @property
    def total_expected_this_year(self):
        """
        Retrieve total amount expected this year for payments related to
        this Appropriation.

        we take into account granted payments but overrule with expected
        if it modifies another activity.
        """

        activities = self.activities.filter(
            Q(status=STATUS_GRANTED) | Q(status=STATUS_EXPECTED)
        )
        return (
            Payment.objects.filter(payment_schedule__activity__in=activities)
            .expected()
            .in_this_year()
            .amount_sum()
        )

    @property
    def total_expected_full_year(self):
        """
        Retrieve total amount expected for the year
        extrapolating for the full year (January 1 - December 31)
        """
        all_activities = self.activities.filter(
            Q(status=STATUS_GRANTED, modified_by__isnull=True)
            | Q(status=STATUS_EXPECTED)
            | Q(status=STATUS_GRANTED, modified_by__status=STATUS_GRANTED)
        )
        return sum(
            activity.total_cost_full_year for activity in all_activities
        )

    @property
    def main_activity(self):
        """Return main activity, if any."""
        f = self.activities.filter(activity_type=MAIN_ACTIVITY)
        if f.exists():
            # Invariant: There is only one main activity.
            return f.first()

    @property
    def section_info(self):
        if self.main_activity and self.section:
            si_filter = self.main_activity.details.sectioninfo_set.filter(
                section=self.section
            )
            if si_filter.exists():
                return si_filter.first()

    @property
    def payment_plan(self):
        # TODO:
        pass  # pragma: no cover

    @transaction.atomic
    def grant(self, activities, approval_level, approval_note, approval_user):
        """Grant all the given Activities."""

        # Please specify approval level.
        if approval_level is None:
            raise RuntimeError(_("Angiv venligst bevillingskompetence"))
        # In order to approve, you need a main activity.
        if not self.main_activity:
            raise RuntimeError(
                _("Kan ikke godkende en bevilling uden en hovedydelse")
            )
        # In order to approve, you must specify a section:
        if not self.section:
            raise RuntimeError(_("Angiv venligst en paragraf"))
        # Make sure that the main activity is valid for this appropriation.
        if not (
            self.main_activity.details in self.section.main_activities.all()
        ):
            raise RuntimeError(
                _("Denne ydelse kan ikke bevilges på den angivne paragraf")
            )
        # Can't approve nothing
        if not activities:
            raise RuntimeError(_("Angiv mindst én aktivitet"))

        # The activities come in as a queryset. Save a copy as a list to
        # be able to append, please.
        to_be_granted = list(activities)
        # If the main activity is being approved, impose its end dates
        # on the other activities.

        if activities.filter(activity_type=MAIN_ACTIVITY).exists():
            main_activity = activities.filter(
                activity_type=MAIN_ACTIVITY
            ).first()
            # Update the end date for all supplementary activities that
            # don't have an end date less than the main activities'.
            if main_activity.end_date:
                for a in self.activities.filter(
                    activity_type=SUPPL_ACTIVITY
                ).exclude(end_date__lte=main_activity.end_date):
                    a.end_date = main_activity.end_date
                    a.save()
                    if a.status == STATUS_GRANTED:
                        # If we're not already granting a modification
                        # of this activity, we need to re-grant it.
                        if not (
                            a.modified_by and a.modified_by in activities
                        ):  # pragma: no cover
                            to_be_granted.append(a)
        else:
            # No main activity. We're only allowed to do this if the
            # main activity is already approved.
            if not self.activities.filter(
                activity_type=MAIN_ACTIVITY, status=STATUS_GRANTED
            ).exists():
                raise RuntimeError(
                    _(
                        "Kan ikke godkende følgeydelser, før"
                        " hovedydelsen er godkendt."
                    )
                )

        approval_level = ApprovalLevel.objects.get(id=approval_level)

        for a in to_be_granted:
            a.grant(approval_level, approval_note, approval_user)

        # Everything went fine, we can send to SBSYS.
        send_appropriation(self)

    def __str__(self):
        return f"{self.sbsys_id} - {self.section}"


class ServiceProvider(models.Model):
    """
    Class containing information for a specific service provider.
    """

    class Meta:
        verbose_name = _("leverandør")
        verbose_name_plural = _("leverandører")

    cvr_number = models.CharField(
        max_length=8, blank=True, verbose_name=_("cvr-nummer")
    )
    name = models.CharField(
        max_length=128, blank=False, verbose_name=_("navn")
    )
    vat_factor = models.DecimalField(
        default=100.0,
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("momsfaktor"),
    )

    def __str__(self):
        return f"{self.cvr_number} - {self.name}"


class ActivityDetails(models.Model):
    """Class containing all services offered by this municipality.

    Each service is associated with the legal articles for which it is
    allowed as well as a price range.
    """

    class Meta:
        verbose_name = _("aktivitetsdetalje")
        verbose_name_plural = _("aktivitetsdetaljer")

    name = models.CharField(max_length=128, verbose_name=_("Navn"))
    activity_id = models.CharField(
        max_length=128, verbose_name=_("aktivitets ID"), unique=True
    )
    max_tolerance_in_percent = models.PositiveSmallIntegerField(
        verbose_name=_("max tolerance i procent")
    )
    max_tolerance_in_dkk = models.PositiveIntegerField(
        verbose_name=_("max tolerance i DKK")
    )
    main_activity_for = models.ManyToManyField(
        Section,
        related_name="main_activities",
        verbose_name=_("hovedaktivitet for paragraffer"),
        blank=True,
        through="SectionInfo",
    )
    supplementary_activity_for = models.ManyToManyField(
        Section,
        related_name="supplementary_activities",
        verbose_name=_("følgeudgift for paragraffer"),
        blank=True,
    )
    service_providers = models.ManyToManyField(
        ServiceProvider,
        related_name="supplied_activities",
        verbose_name=_("leverandører"),
        blank=True,
    )

    main_activities = models.ManyToManyField(
        "self",
        related_name="supplementary_activities",
        symmetrical=False,
        verbose_name=_("tilladte hovedaktiviteter"),
        blank=True,
    )

    def __str__(self):
        return f"{self.activity_id} - {self.name}"


class SectionInfo(models.Model):
    """For a main activity, KLE no. and SBSYS ID for the relevant sections."""

    class Meta:
        # For info about why we do this, see
        # https://code.djangoproject.com/ticket/23034, especially
        # comment #9.
        db_table = "core_activitydetails_main_activity_for"

    activity_details = models.ForeignKey(
        ActivityDetails,
        on_delete=models.CASCADE,
        db_column="activitydetails_id",
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, db_column="section_id"
    )

    kle_number = models.CharField(
        max_length=128, verbose_name=_("KLE-nummer"), blank=True
    )
    sbsys_template_id = models.CharField(
        max_length=128, verbose_name=_("SBSYS skabelon-id"), blank=True
    )


class Activity(AuditModelMixin, models.Model):
    """An activity is a specific service provided within an appropriation."""

    # The details object contains the name, tolerance, etc. of the service.

    class Meta:
        verbose_name = _("aktivitet")
        verbose_name_plural = _("aktiviteter")
        constraints = [
            # Activity start_date should come before end_date.
            models.CheckConstraint(
                check=Q(start_date__lte=F("end_date")),
                name="end_date_after_start_date",
            ),
            # Appropriation can only have a single main activity
            # that does not have an expected activity.
            models.UniqueConstraint(
                fields=["appropriation"],
                condition=Q(activity_type=MAIN_ACTIVITY)
                & Q(modifies__isnull=True),
                name="unique_main_activity",
            ),
        ]

    details = models.ForeignKey(
        ActivityDetails,
        on_delete=models.PROTECT,
        verbose_name=_("aktivitetsdetalje"),
    )

    status = models.CharField(
        verbose_name=_("status"), max_length=128, choices=status_choices
    )

    approval_level = models.ForeignKey(
        ApprovalLevel,
        related_name="approved_activities",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("bevillingsniveau"),
    )
    approval_note = models.TextField(
        verbose_name=_("evt. bemærkning"), blank=True
    )
    approval_user = models.ForeignKey(
        User,
        related_name="approved_activities",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_("bevilget af bruger"),
    )

    appropriation_date = models.DateField(
        verbose_name=_("bevillingsdato"), null=True, blank=True
    )

    start_date = models.DateField(verbose_name=_("startdato"))
    end_date = models.DateField(
        verbose_name=_("slutdato"), null=True, blank=True
    )

    activity_type = models.CharField(
        max_length=128, verbose_name=_("type"), choices=type_choices
    )

    payment_plan = models.OneToOneField(
        PaymentSchedule,
        on_delete=models.CASCADE,
        verbose_name=_("betalingsplan"),
        null=True,
        blank=True,
    )

    # An expected change modifies another actitvity and will eventually
    # be merged with it.
    modifies = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="modified_by",
        on_delete=models.CASCADE,
    )
    # The appropriation that owns this activity.
    appropriation = models.ForeignKey(
        Appropriation,
        related_name="activities",
        on_delete=models.CASCADE,
        verbose_name=_("bevilling"),
    )

    service_provider = models.ForeignKey(
        ServiceProvider,
        null=True,
        blank=True,
        related_name="activities",
        on_delete=models.SET_NULL,
        verbose_name=_("leverandør"),
    )

    note = models.TextField(null=True, blank=True, max_length=1000)

    def __str__(self):
        activity_type_str = self.get_activity_type_display()
        status_str = self.get_status_display()
        return f"{self.details} - {activity_type_str} - {status_str}"

    @transaction.atomic
    def grant(self, approval_level, approval_note, approval_user):
        "Grant this activity - update payment info as needed." ""

        self.appropriation_date = timezone.now().date()
        self.approval_level = approval_level
        self.approval_note = approval_note
        self.approval_user = approval_user

        if self.status == STATUS_GRANTED:
            # Re-granting - nothing more to do.
            pass
        elif not self.modifies:
            # Simple case: Just set status.
            self.status = STATUS_GRANTED
        elif self.validate_expected():  # pragma: no cover
            # "Merge" by ending current activity the day before the new
            # start_date.
            #
            # In case of a one_time_payment we end the on the same day and
            # delete all payments for the old one.
            payment_type = self.modifies.payment_plan.payment_type
            if payment_type == PaymentSchedule.ONE_TIME_PAYMENT:
                self.modifies.payment_plan.payments.all().delete()
                self.modifies.start_date = self.start_date
                # With one time payments, end date and start date must
                # always be the same.
                self.modifies.end_date = self.start_date
            else:
                self.modifies.end_date = self.start_date - timedelta(days=1)
            # In all cases ...
            self.modifies.save()
            self.status = STATUS_GRANTED
        self.save()

    def validate_expected(self):
        """
        Validate this is a correct expected activity.
        """
        if not self.modifies:
            raise forms.ValidationError(
                _("den forventede justering har ingen ydelse at justere")
            )

        if self.modifies.end_date and self.start_date > self.modifies.end_date:

            raise forms.ValidationError(
                _(
                    f"den justerede aktivitets startdato skal være før"
                    f"ydelsens slutdato: {self.modifies.end_date}"
                )
            )
        return True

    @property
    def ongoing(self):
        today = date.today()
        return self.start_date <= today and (
            not self.end_date or self.end_date > today
        )

    @property
    def account(self):
        if self.activity_type == MAIN_ACTIVITY:
            accounts = Account.objects.filter(
                section=self.appropriation.section,
                main_activity=self.details,
                supplementary_activity=None,
            )
        else:
            main_activity = self.appropriation.main_activity
            if not main_activity:
                return None
            accounts = Account.objects.filter(
                section=self.appropriation.section,
                main_activity=main_activity.details,
                supplementary_activity=self.details,
            )
        if accounts.exists():
            account = accounts.first()
        else:
            account = None
        return account

    @property
    def monthly_payment_plan(self):
        payments = Payment.objects.filter(payment_schedule__activity=self)
        return payments.group_by_monthly_amounts()

    @property
    def total_cost_this_year(self):
        if self.status == STATUS_GRANTED and self.modified_by.exists():
            payments = Payment.objects.filter(
                payment_schedule__activity=self
            ).expected()
        else:
            payments = Payment.objects.filter(payment_schedule__activity=self)
        return payments.in_this_year().amount_sum()

    @property
    def total_granted_this_year(self):
        if self.status == STATUS_GRANTED:
            payments = Payment.objects.filter(payment_schedule__activity=self)
            return payments.in_this_year().amount_sum
        else:
            return Decimal(0)

    @property
    def total_expected_this_year(self):
        return self.total_cost_this_year

    @property
    def total_cost(self):
        if self.status == STATUS_GRANTED and self.modified_by.exists():
            payments = Payment.objects.filter(
                payment_schedule__activity=self
            ).expected()
        else:
            payments = Payment.objects.filter(payment_schedule__activity=self)
        return payments.amount_sum()

    @property
    def total_cost_full_year(self):
        """
        Retrieve total amount expected for the year
        extrapolating for the full year (January 1 - December 31)
        """
        if not self.payment_plan:
            return Decimal(0.0)

        vat_factor = self.vat_factor
        now = timezone.now()
        start_date = date(now.year, month=1, day=1)
        end_date = date(now.year, month=12, day=31)
        num_payments = len(
            list(self.payment_plan.create_rrule(start_date, end_date))
        )
        return (
            self.payment_plan.calculate_per_payment_amount(vat_factor)
            * num_payments
        )

    @property
    def triggers_payment_email(self):
        # If activity or appropriation is not granted we don't send an email.
        if not self.status == STATUS_GRANTED:
            return False

        # Don't trigger the email if the payment plan does not exist
        # or does not need a payment email to trigger.
        if not hasattr(self, "payment_plan") or not self.payment_plan:
            return False
        if not self.payment_plan.triggers_payment_email:
            return False
        return True

    @property
    def vat_factor(self):
        vat_factor = Decimal("100")
        if self.service_provider:
            vat_factor = self.service_provider.vat_factor
        return vat_factor


class RelatedPerson(models.Model):
    """A person related to a Case, e.g. as a parent or sibling."""

    class Meta:
        verbose_name = _("relateret person")
        verbose_name_plural = _("relaterede personer")

    relation_type = models.CharField(
        max_length=128, verbose_name=_("relation")
    )
    cpr_number = models.CharField(
        max_length=10, verbose_name=_("cpr-nummer"), blank=True
    )
    name = models.CharField(max_length=128, verbose_name=_("navn"))
    related_case = models.CharField(
        max_length=128, verbose_name=_("SBSYS-sag"), blank=True
    )

    main_case = models.ForeignKey(
        Case,
        related_name="related_persons",
        on_delete=models.CASCADE,
        verbose_name=_("hovedsag"),
    )

    @staticmethod
    def serviceplatformen_to_related_person(data):
        """
        Convert data from Serviceplatformen to our RelatedPerson model data.
        """
        converter_dict = {
            "cprnr": "cpr_number",
            "relation": "relation_type",
            "adresseringsnavn": "name",
        }
        return {
            converter_dict[k]: v
            for (k, v) in data.items()
            if k in converter_dict
        }


class Account(models.Model):
    """Class containing account numbers.

    Should have a number for each
    (main activity, supplementary activity, section) pair.
    """

    number = models.CharField(
        max_length=128, verbose_name=_("konteringsnummer")
    )
    main_activity = models.ForeignKey(
        ActivityDetails,
        null=False,
        on_delete=models.CASCADE,
        related_name="main_accounts",
        verbose_name=_("hovedaktivitet"),
    )
    supplementary_activity = models.ForeignKey(
        ActivityDetails,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="supplementary_accounts",
        verbose_name=_("følgeudgift"),
    )
    section = models.ForeignKey(
        Section,
        null=False,
        on_delete=models.CASCADE,
        related_name="accounts",
        verbose_name=_("paragraf"),
    )

    def __str__(self):
        return (
            f"{self.number} - "
            f"{self.main_activity} - "
            f"{self.supplementary_activity} - "
            f"{self.section}"
        )

    class Meta:
        verbose_name = _("konto")
        verbose_name_plural = _("konti")
        constraints = [
            models.UniqueConstraint(
                fields=["main_activity", "supplementary_activity", "section"],
                name="unique_account_number",
            )
        ]
