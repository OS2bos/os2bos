from datetime import date, timedelta
from decimal import Decimal

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Q
from django.contrib.postgres import fields
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from django_audit_fields.models import AuditModelMixin
from simple_history.models import HistoricalRecords

from core.utils import send_activity_deleted_email
from core.managers import PaymentQuerySet
from core.utils import send_appropriation

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


class Municipality(models.Model):
    """Represents a Danish municipality."""

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class SchoolDistrict(models.Model):
    """Represents a Danish school district."""

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class PaymentMethodDetails(models.Model):
    tax_card_choices = (
        ("MAIN_CARD", _("Hovedkort")),
        ("SECONDARY_CARD", _("Bikort")),
    )

    tax_card = models.CharField(
        max_length=128,
        verbose_name=(_("skattekort")),
        choices=tax_card_choices,
    )


class User(AbstractUser):
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
        User, on_delete=models.PROTECT, related_name="managed_teams"
    )

    def __str__(self):
        return f"{self.name}"


class PaymentSchedule(models.Model):
    """Schedule a payment for an Activity."""

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
    # TODO: namechange - this refers actually to the recipient CPR
    recipient_id = models.CharField(max_length=128, verbose_name=_("ID"))
    recipient_name = models.CharField(max_length=128, verbose_name=_("Navn"))

    payment_method = models.CharField(
        max_length=128,
        verbose_name=_("betalingsmåde"),
        choices=payment_method_choices,
    )
    payment_method_details = models.ForeignKey(
        PaymentMethodDetails, null=True, blank=True, on_delete=models.SET_NULL
    )
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    payment_frequency_choices = (
        (DAILY, _("Dagligt")),
        (WEEKLY, _("Ugentligt")),
        (MONTHLY, _("Månedligt")),
    )
    payment_frequency = models.CharField(
        max_length=128,
        verbose_name=_("betalingsfrekvens"),
        choices=payment_frequency_choices,
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

    @staticmethod
    def is_payment_method_and_recipient_type_allowed(
        payment_method, recipient_type
    ):
        allowed = {
            PaymentSchedule.INTERNAL: [INTERNAL],
            PaymentSchedule.PERSON: [CASH, SD],
            PaymentSchedule.COMPANY: [INVOICE],
        }
        return payment_method in allowed[recipient_type]

    def triggers_payment_email(self):
        """
        Trigger a payment email only in the (recipient_type->payment_method) case
        of Internal->Internal or Person->SD.
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
        if not self.is_payment_method_and_recipient_type_allowed(
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
        elif self.payment_frequency == self.MONTHLY:
            # If monthly, choose the first day of the month.
            rrule_frequency = rrule.rrule(
                rrule.MONTHLY, dtstart=start, until=end, bymonthday=1
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

        # The new start_date should be based on the newest payment date
        # and the payment frequency.
        if self.payment_frequency == PaymentSchedule.DAILY:
            new_start = newest_payment.date + relativedelta(days=1)
        elif self.payment_frequency == PaymentSchedule.WEEKLY:
            new_start = newest_payment.date + relativedelta(weeks=1)
        elif self.payment_frequency == PaymentSchedule.MONTHLY:
            new_start = newest_payment.date + relativedelta(months=1)
        else:
            raise ValueError(_("ukendt betalingsfrekvens"))

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


class Payment(models.Model):
    """Represents an amount paid to a supplier - amount, recpient, date.

    These may be entered manually, but ideally they should be imported
    from an accounts payable system."""

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
        PaymentSchedule, on_delete=models.CASCADE, related_name="payments"
    )

    def save(self, *args, **kwargs):
        if not self.payment_schedule.is_payment_method_and_recipient_type_allowed(
            self.payment_method, self.recipient_type
        ):
            raise ValueError(
                _("ugyldig betalingsmetode for betalingsmodtager")
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.amount}"


class Case(AuditModelMixin, models.Model):
    """A case, covering one child - corresponding to a Hovedsag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, max_length=128, verbose_name=_("SBSYS-ID")
    )
    cpr_number = models.CharField(max_length=12, verbose_name=_("cpr-nummer"))
    name = models.CharField(max_length=128, verbose_name=_("Navn"))
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
        null=True,
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
    refugee_integration = models.BooleanField(
        verbose_name=_("integrationsindsatsen"), default=False
    )
    cross_department_measure = models.BooleanField(
        verbose_name=_("tværgående ungeindsats"), default=False
    )
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
        ]
    )


class ApprovalLevel(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class Section(models.Model):
    """Law sections and the corresponding KLE codes.

    Each section is associated with the target group for which it is
    allowed as well as the action steps allowed.
    """

    paragraph = models.CharField(max_length=128, verbose_name=_("paragraf"))
    kle_number = models.CharField(max_length=128, verbose_name=_("KLE-nummer"))
    text = models.TextField(verbose_name=_("forklarende tekst"))
    allowed_for_family_target_group = models.BooleanField(
        verbose_name=_("tilladt for familieafdelingen"), default=False
    )
    allowed_for_disability_target_group = models.BooleanField(
        verbose_name=_("tilladt for handicapafdelingen"), default=False
    )
    allowed_for_steps = fields.ArrayField(
        models.CharField(max_length=128, choices=effort_steps_choices), size=6
    )
    law_text_name = models.CharField(
        max_length=128, verbose_name=_("lov tekst navn")
    )
    sbsys_template_id = models.CharField(
        max_length=128,
        verbose_name=_("SBSYS skabelon-id"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.paragraph} - {self.kle_number}"


class Appropriation(AuditModelMixin, models.Model):
    """An appropriation of funds in a Case - corresponds to a Sag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, max_length=128, verbose_name=_("SBSYS-ID")
    )
    section = models.ForeignKey(
        Section,
        related_name="appropriations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Status - definitions and choice list.
    STATUS_DRAFT = "DRAFT"
    STATUS_BUDGETED = "BUDGETED"
    STATUS_GRANTED = "GRANTED"
    STATUS_DISCONTINUED = "DISCONTINUED"
    status_choices = (
        (STATUS_DRAFT, _("kladde")),
        (STATUS_BUDGETED, _("disponeret")),
        (STATUS_GRANTED, _("bevilget")),
        (STATUS_DISCONTINUED, _("udgået")),
    )
    status = models.CharField(
        verbose_name=_("status"), max_length=16, choices=status_choices
    )

    approval_level = models.ForeignKey(
        ApprovalLevel,
        related_name="appropriations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    approval_note = models.TextField(
        verbose_name=_("evt. bemærkning"), blank=True
    )

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, related_name="appropriations"
    )

    @property
    def total_granted_this_year(self):
        """
        Retrieve total amount granted this year for payments related to
        this Appropriation (both main and supplementary activities).
        """
        granted_activities = self.activities.all().filter(
            status=Activity.STATUS_GRANTED
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

        all_activities = self.activities.filter(
            Q(status=Activity.STATUS_GRANTED, modified_by__isnull=True)
            | Q(status=Activity.STATUS_EXPECTED)
        )

        this_years_payments = Payment.objects.filter(
            payment_schedule__activity__in=all_activities
        ).in_this_year()

        return this_years_payments.amount_sum()

    @property
    def main_activity(self):
        """Return main activity, if any."""
        f = self.activities.filter(activity_type=Activity.MAIN_ACTIVITY)
        if f.exists():
            # Invariant: There is only one main activity.
            return f.first()

    @property
    def supplementary_activities(self):
        """Return all non-main activities."""
        f = self.activities.filter(activity_type=Activity.SUPPL_ACTIVITY)
        return (a for a in f)

    @property
    def payment_plan(self):
        # TODO:
        pass  # pragma: no cover

    def grant(self, approval_level, approval_note):
        """Grant this app - change state and all Activities to GRANTED."""
        if self.status in [self.STATUS_DRAFT, self.STATUS_BUDGETED]:
            # This hasn't been granted yet.
            if approval_level is None:
                raise RuntimeError(_("Angiv venligst bevillingskompetence"))

            approval_level = ApprovalLevel.objects.get(id=approval_level)
            self.approval_level = approval_level
            self.approval_note = approval_note

            self.status = self.STATUS_GRANTED
            for a in self.activities.all():
                # We could do this with an update, but we need to activate the
                # save() method on each activity.
                a.status = a.STATUS_GRANTED
                a.save()
            self.save()
        elif self.status == self.STATUS_GRANTED:
            # Grant all non-granted activities.
            # Merge and delete expectations that modify other activities.
            if approval_level:
                self.approval_level = ApprovalLevel.objects.get(
                    id=approval_level
                )
            if approval_note:
                self.approval_note = approval_note
            if approval_level or approval_note:
                self.save()
            # Now go through the activities.
            for a in self.activities.exclude(status=Activity.STATUS_GRANTED):
                # If a modifies another, merge -
                # else just set status = GRANTED.
                if a.modifies:
                    # "Merge" by ending current activity today
                    # and granting the new one from tomorrow.
                    a.modifies.end_date = date.today()
                    a.start_date = date.today() + timedelta(days=1)
                    a.status = a.STATUS_GRANTED
                    a.modifies.save()
                    a.save()
                else:
                    a.status = a.STATUS_GRANTED
                    a.save()

        else:
            raise RuntimeError(
                _("Kan ikke bevilge en udløbet foranstaltning.")
            )
        # Everything went fine, we can send to SBSYS.
        send_appropriation(self)

    def __str__(self):
        return f"{self.sbsys_id} - {self.section}"


class ServiceProvider(models.Model):
    """
    Class containing information for a specific service provider.
    """

    cvr_number = models.CharField(max_length=8, blank=True)
    name = models.CharField(max_length=128, blank=False)
    vat_factor = models.DecimalField(
        default=100.0,
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )


class ActivityDetails(models.Model):
    """Class containing all services offered by this municipality.

    Each service is associated with the legal articles for which it is
    allowed as well as a price range.
    """

    name = models.CharField(max_length=128, verbose_name=_("Navn"))
    activity_id = models.CharField(
        max_length=128, verbose_name=_("Aktivitets ID")
    )
    max_tolerance_in_percent = models.PositiveSmallIntegerField(
        verbose_name=_("Max tolerance i procent")
    )
    max_tolerance_in_dkk = models.PositiveIntegerField(
        verbose_name=_("Max tolerance i DKK")
    )
    main_activity_for = models.ManyToManyField(
        Section, related_name="main_activities"
    )
    supplementary_activity_for = models.ManyToManyField(
        Section, related_name="supplementary_activities"
    )
    service_providers = models.ManyToManyField(
        ServiceProvider, related_name="supplied_activities"
    )

    def __str__(self):
        return f"{self.activity_id} - {self.name}"


class Activity(AuditModelMixin, models.Model):
    """An activity is a specific service provided within an appropriation."""

    # The details object contains the name, tolerance, etc. of the service.
    details = models.ForeignKey(ActivityDetails, on_delete=models.PROTECT)

    # Status - definitions and choice list.
    STATUS_DRAFT = "DRAFT"
    STATUS_EXPECTED = "EXPECTED"
    STATUS_GRANTED = "GRANTED"
    status_choices = (
        (STATUS_DRAFT, _("kladde")),
        (STATUS_EXPECTED, _("forventet")),
        (STATUS_GRANTED, _("bevilget")),
    )
    status = models.CharField(
        verbose_name=_("status"), max_length=128, choices=status_choices
    )

    start_date = models.DateField(verbose_name=_("startdato"))
    end_date = models.DateField(
        verbose_name=_("slutdato"), null=True, blank=True
    )

    # Activity types and choice list.
    MAIN_ACTIVITY = "MAIN_ACTIVITY"
    SUPPL_ACTIVITY = "SUPPL_ACTIVITY"
    type_choices = (
        (MAIN_ACTIVITY, _("hovedaktivitet")),
        (SUPPL_ACTIVITY, _("følgeaktivitet")),
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
        Appropriation, related_name="activities", on_delete=models.CASCADE
    )

    service_provider = models.ForeignKey(
        ServiceProvider,
        null=True,
        blank=True,
        related_name="activities",
        on_delete=models.SET_NULL,
    )

    note = models.TextField(null=True, blank=True, max_length=1000)

    @property
    def monthly_payment_plan(self):
        payments = Payment.objects.filter(payment_schedule__activity=self)
        return payments.group_by_monthly_amounts()

    @property
    def total_cost_this_year(self):
        now = timezone.now()
        payments = Payment.objects.filter(
            payment_schedule__activity=self
        ).filter(date__year=now.year)

        return payments.amount_sum()

    @property
    def total_cost(self):
        payments = Payment.objects.filter(payment_schedule__activity=self)
        return payments.amount_sum()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        vat_factor = Decimal("100")
        if self.service_provider:
            vat_factor = self.service_provider.vat_factor

        if self.payment_plan:
            if self.payment_plan.payments.exists():
                self.payment_plan.synchronize_payments(
                    self.start_date, self.end_date, vat_factor
                )
            else:
                self.payment_plan.generate_payments(
                    self.start_date, self.end_date, vat_factor
                )

    def delete(self, *args, **kwargs):
        send_activity_deleted_email(self)
        super().delete(*args, **kwargs)


class RelatedPerson(models.Model):
    """A person related to a Case, e.g. as a parent or sibling."""

    relation_type = models.CharField(
        max_length=128, verbose_name=_("relation")
    )
    cpr_number = models.CharField(
        max_length=12, verbose_name=_("cpr-nummer"), blank=True
    )
    name = models.CharField(max_length=128, verbose_name=_("navn"))
    related_case = models.CharField(
        max_length=128, verbose_name=_("SBSYS-sag"), blank=True
    )

    main_case = models.ForeignKey(
        Case, related_name="related_persons", on_delete=models.CASCADE
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

    Should have a different number for each (ActivityDetails, Section) pair.
    """

    number = models.CharField(max_length=128)
    activity = models.ForeignKey(
        ActivityDetails, null=False, on_delete=models.CASCADE
    )
    section = models.ForeignKey(Section, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} - {self.activity} - {self.section}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "section"], name="unique_account_number"
            )
        ]
