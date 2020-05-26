# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""These are the Django models, defining the database layout."""

from datetime import date, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta

import portion as P

from django import forms
from django.db import models, transaction
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q, F
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django_audit_fields.models import AuditModelMixin
from simple_history.models import HistoricalRecords
from constance import config

from core.managers import PaymentQuerySet, CaseQuerySet
from core.utils import send_appropriation, create_rrule

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

status_choices = (
    (STATUS_DRAFT, _("kladde")),
    (STATUS_EXPECTED, _("forventet")),
    (STATUS_GRANTED, _("bevilget")),
)


class Classification(models.Model):
    """Abstract base class for Classifications."""

    active = models.BooleanField(default=True, verbose_name=_("aktiv"))

    class Meta:
        abstract = True


class Municipality(Classification):
    """Represents a Danish municipality."""

    class Meta:
        verbose_name = _("kommune")
        verbose_name_plural = _("kommuner")

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class SchoolDistrict(Classification):
    """Represents a Danish school district."""

    class Meta:
        verbose_name = _("distrikt")
        verbose_name_plural = _("distrikter")

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class EffortStep(Classification):
    """Evaluation step for grading the effort deemed necessary in a case."""

    class Meta:
        verbose_name = _("indsatstrappetrin")
        verbose_name_plural = _("indsatstrappe")
        ordering = ["number"]

    name = models.CharField(max_length=128, verbose_name=_("navn"))
    number = models.PositiveIntegerField(verbose_name="Nummer", unique=True)

    def __str__(self):
        return f"{self.name}"


class TargetGroup(Classification):
    """Target group for a case."""

    class Meta:
        verbose_name = _("målgruppe")
        verbose_name_plural = _("målgrupper")

    name = models.CharField(max_length=128, verbose_name=_("navn"))
    required_fields_for_case = ArrayField(
        models.CharField(max_length=128),
        blank=True,
        null=True,
        verbose_name="påkrævede felter på sag",
    )

    def __str__(self):
        return f"{self.name}"


class Effort(Classification):
    """Effort for a case."""

    class Meta:
        verbose_name = _("indsats")
        verbose_name_plural = _("indsatser")

    name = models.CharField(max_length=128, verbose_name=_("navn"))
    description = models.CharField(
        max_length=128, verbose_name=_("beskrivelse"), blank=True
    )
    allowed_for_target_groups = models.ManyToManyField(
        TargetGroup,
        related_name="efforts",
        verbose_name=_("målgrupper"),
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"


class PaymentMethodDetails(models.Model):
    """Contains extra information about a payment method."""

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
    """Customized user for handling login etc."""

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

    # Different permission levels for user profile.

    READONLY = "readonly"
    EDIT = "edit"
    GRANT = "grant"
    WORKFLOW_ENGINE = "workflow_engine"
    ADMIN = "admin"

    @classmethod
    def max_profile(cls, perms):
        """Return the profile (in "perms") with the highest permissions.

        IdPs can send more than one profile when using SAML.  This
        function returns the "maximum" profile in the sense of the one
        with the most far-reaching permissions.
        """
        permission_score = {
            cls.READONLY: 0,
            cls.EDIT: 1,
            cls.GRANT: 2,
            cls.WORKFLOW_ENGINE: 3,
            cls.ADMIN: 4,
        }
        if not perms:
            return ""

        max_score = max(permission_score.get(p, -1) for p in perms)

        return {v: k for k, v in permission_score.items()}.get(max_score, "")

    profile_choices = (
        (READONLY, _("Kun læse")),
        (EDIT, _("Læse og skrive")),
        (GRANT, _("Bevilge")),
        (WORKFLOW_ENGINE, ("Redigere klassifikationer")),
        (ADMIN, _("Admin")),
    )
    profile = models.CharField(
        max_length=128,
        verbose_name=(_("brugerprofil")),
        choices=profile_choices,
        blank=True,
    )

    def is_workflow_engine_or_admin(self):
        """Return if user has workflow or admin permission."""
        if self.profile in [User.WORKFLOW_ENGINE, User.ADMIN]:
            return True
        return False


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


class VariableRate(models.Model):
    """Superclass for time-dependent rates and prices."""

    @staticmethod
    def create_interval(start_date, end_date):
        """Create new interval for rates."""
        if start_date is None:
            start_date = -P.inf
        if end_date is None:
            end_date = P.inf
        if not start_date < end_date:
            raise ValueError(_("Slutdato skal være mindre end startdato"))
        return P.closedopen(start_date, end_date)

    def get_rate_amount(self, rate_date=date.today()):
        """Look up period in RatesPerDate."""
        periods = self.rates_per_date.all()
        d = P.IntervalDict()
        for p in periods:
            i = self.create_interval(p.start_date, p.end_date)
            d[i] = p.rate
        return d.get(rate_date)

    rate_amount = property(get_rate_amount)

    @transaction.atomic
    def set_rate_amount(self, amount, start_date=None, end_date=None):
        """Set amount, merge with existing periods."""
        new_period = self.create_interval(start_date, end_date)

        existing_periods = self.rates_per_date.all()
        d = P.IntervalDict()
        for period in existing_periods:
            interval = self.create_interval(period.start_date, period.end_date)
            d[interval] = period.rate

        # We generate all periods from scratch to avoid complicated
        # merging logic.
        existing_periods.delete()

        d[new_period] = amount
        for period in d.keys():
            for interval in list(period):
                # In case of composite intervals
                start = (
                    interval.lower
                    if isinstance(interval.lower, date)
                    else None
                )
                end = (
                    interval.upper
                    if isinstance(interval.upper, date)
                    else None
                )
                rpd = RatePerDate(
                    start_date=start,
                    end_date=end,
                    rate=d[start or end or date.today()],
                    main_rate=self,
                )
                rpd.save()

    def __str__(self):
        return ";".join(
            f"{r.start_date}, {r.end_date}: {r.rate}"
            for r in self.rates_per_date.all()
        )


class RatePerDate(models.Model):
    """Handle the date variation of VariableRates."""

    rate = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("takst")
    )

    # Date dependency
    start_date = models.DateField(
        null=True, blank=True, verbose_name=_("startdato")
    )
    end_date = models.DateField(
        null=True, blank=True, verbose_name=_("slutdato")
    )
    main_rate = models.ForeignKey(
        VariableRate, on_delete=models.CASCADE, related_name="rates_per_date"
    )


class Price(VariableRate):
    """A price on an individual payment plan."""

    class Meta:
        verbose_name = _("pris")

    payment_schedule = models.OneToOneField(
        "PaymentSchedule",
        on_delete=models.CASCADE,
        verbose_name=_("betalingsplan"),
        related_name="price",
        null=True,
        blank=True,
    )


class Rate(VariableRate):
    """A centrally fixed rate."""

    class Meta:
        verbose_name = _("takst")

    name = models.CharField(max_length=128, verbose_name=_("navn"))
    description = models.TextField(verbose_name=_("beskrivelse"), blank=True)


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

    activity = models.OneToOneField(
        "Activity",
        on_delete=models.CASCADE,
        verbose_name=_("aktivitet"),
        related_name="payment_plan",
        null=True,
        blank=True,
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

    payment_type = models.CharField(
        max_length=128,
        verbose_name=_("betalingstype"),
        choices=payment_type_choices,
    )
    # number of units to pay, ie. XX kilometres or hours
    payment_units = models.DecimalField(
        verbose_name=_("betalingsenheder"),
        blank=True,
        null=True,
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    payment_amount = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("beløb")
    )
    fictive = models.BooleanField(default=False, verbose_name=_("fiktiv"))
    payment_id = models.PositiveIntegerField(
        editable=False, verbose_name=_("betalings-ID"), blank=True, null=True
    )

    @property
    def next_payment(self):
        """Return the next payment due starting from today, if any."""
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
        """Determine if this combination of method and recipient is allowed."""
        allowed = {
            PaymentSchedule.INTERNAL: [INTERNAL],
            PaymentSchedule.PERSON: [CASH, SD],
            PaymentSchedule.COMPANY: [INVOICE, CASH],
        }
        return payment_method in allowed[recipient_type]

    @property
    def can_be_paid(self):
        """Determine whether payments on this schedule can be paid.

        It is only allowed to pay payments associated with an approved
        activity, i.e. status GRANTED.
        """
        if (
            hasattr(self, "activity")
            and self.activity
            and self.activity.status == STATUS_GRANTED
        ):
            return True
        return False

    def save(self, *args, **kwargs):
        """Save this payment schedule after validating payment method."""
        if not self.is_payment_and_recipient_allowed(
            self.payment_method, self.recipient_type
        ):
            raise ValueError(
                _("ugyldig betalingsmetode for betalingsmodtager")
            )
        super().save(*args, **kwargs)

    def create_rrule(self, start, **kwargs):
        """Create a dateutil.rrule for this schedule specifically."""
        return create_rrule(
            self.payment_type,
            self.payment_frequency,
            self.payment_day_of_month,
            start,
            **kwargs,
        )

    def calculate_per_payment_amount(self, vat_factor):
        """Calculate amount from payment type and units."""
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
        """Generate payments with a start and end date."""
        # If no end is specified, choose end of the next year.
        if not end:
            today = date.today()
            end = today.replace(
                year=today.year + 1, month=date.max.month, day=date.max.day
            )

        rrule_frequency = self.create_rrule(start, until=end)

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
        """Synchronize an existing number of payments for a new end_date."""
        today = date.today()

        # If no existing payments is generated we can't do anything.
        if not self.payments.exists():
            return

        newest_payment = self.payments.order_by("-date").first()

        # One time payment is a special case and should not be handled.
        if self.payment_type == self.ONE_TIME_PAYMENT:
            return
        # The new start_date should be based on the next payment date
        # from create_rrule.
        _, new_start = list(self.create_rrule(newest_payment.date, count=2))
        new_start = new_start.date()

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

    @property
    def account_string(self):
        """Calculate account string from activity."""
        if (
            self.recipient_type == PaymentSchedule.PERSON
            and self.payment_method == CASH
        ):
            department = config.ACCOUNT_NUMBER_DEPARTMENT
            kind = config.ACCOUNT_NUMBER_KIND
        else:
            # Set department and kind to 'XXX'
            # to signify they are not used.
            department = "XXX"
            kind = "XXX"

        # Account string is "unknown" when there is no
        # activity or account.
        # The explicit inclusion of "unknown" is a demand due to the
        # PRISME integration.
        if (
            not hasattr(self, "activity")
            or not self.activity
            or not self.activity.account
        ):
            account_number = config.ACCOUNT_NUMBER_UNKNOWN
        else:
            account_number = self.activity.account.number

        return f"{department}-{account_number}-{kind}"

    @property
    def account_string_new(self):
        """Calculate account string from activity.

        TODO: eventually replace account_string with this.
        """
        if (
            self.recipient_type == PaymentSchedule.PERSON
            and self.payment_method == CASH
        ):
            department = config.ACCOUNT_NUMBER_DEPARTMENT
            kind = config.ACCOUNT_NUMBER_KIND
        else:
            # Set department and kind to 'XXX'
            # to signify they are not used.
            department = "XXX"
            kind = "XXX"

        # Account string is "unknown" when there is no
        # activity or account.
        # The explicit inclusion of "unknown" is a demand due to the
        # PRISME integration.
        if (
            not hasattr(self, "activity")
            or not self.activity
            or not self.activity.account_number
        ):
            account_number = config.ACCOUNT_NUMBER_UNKNOWN
        else:
            account_number = self.activity.account_number

        return f"{department}-{account_number}-{kind}"

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
    """Represent an amount paid to a supplier - amount, recipient, date.

    These may be entered manually, but ideally they should be imported
    from an accounts payable system.
    """

    class Meta:
        verbose_name = _("betaling")
        verbose_name_plural = _("betalinger")
        ordering = ("date",)
        constraints = [
            models.UniqueConstraint(
                fields=["payment_schedule", "date"], name="unique_payment_date"
            )
        ]

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
        max_digits=14, decimal_places=2, verbose_name=_("beløb")
    )
    paid_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("betalt beløb"),
        null=True,
        blank=True,
    )
    paid = models.BooleanField(default=False, verbose_name=_("betalt"))
    paid_date = models.DateField(
        verbose_name=_("betalt på dato"), null=True, blank=True
    )
    note = models.TextField(verbose_name=_("note"), blank=True)

    saved_account_string = models.CharField(
        max_length=128, verbose_name=_("gemt kontostreng"), blank=True
    )
    payment_schedule = models.ForeignKey(
        PaymentSchedule,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("betalingsplan"),
    )

    def save(self, *args, **kwargs):
        """Save this payment - validate payment method and completeness."""
        if not self.payment_schedule.is_payment_and_recipient_allowed(
            self.payment_method, self.recipient_type
        ):
            raise ValueError(
                _("ugyldig betalingsmetode for betalingsmodtager")
            )

        paid_fields = (
            self.paid,
            self.paid_date is not None,
            self.paid_amount is not None,
        )
        if any(paid_fields) and not all(paid_fields):
            raise ValueError(
                _("ved en betalt betaling skal alle betalingsfelter sættes")
            )

        if self.paid and not self.payment_schedule.can_be_paid:
            raise ValueError(
                _(
                    "En betaling kan kun betales "
                    "hvis dens aktivitet er bevilget"
                )
            )
        super().save(*args, **kwargs)

    @staticmethod
    def paid_allowed_for_payment_and_recipient(payment_method, recipient_type):
        """Determine whether "paid" can be manually set."""
        disallowed = {PaymentSchedule.PERSON: [CASH, SD]}

        if (
            recipient_type in disallowed
            and payment_method in disallowed[recipient_type]
        ):
            return False
        return True

    @property
    def is_payable_manually(self):
        """Determine whether it is payable manually (in the frontend)."""
        return (
            self.paid_allowed_for_payment_and_recipient(
                self.payment_method, self.recipient_type
            )
            and not self.payment_schedule.fictive
            and self.payment_schedule.can_be_paid
        )

    @property
    def account_string(self):
        """Return saved account string if any, else calculate from schedule."""
        if self.saved_account_string:
            return self.saved_account_string

        return self.payment_schedule.account_string

    @property
    def account_string_new(self):
        """Return saved account string if any, else calculate from schedule.

        TODO: eventually replace account_string with this.
        """
        if self.saved_account_string:
            return self.saved_account_string

        return self.payment_schedule.account_string_new

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
    target_group = models.ForeignKey(
        TargetGroup,
        verbose_name=_("målgruppe"),
        on_delete=models.PROTECT,
        related_name="cases",
        null=True,
    )
    effort_step = models.ForeignKey(
        EffortStep,
        verbose_name=_("indsatstrappe"),
        on_delete=models.PROTECT,
        null=True,
    )
    scaling_step = models.PositiveSmallIntegerField(
        verbose_name=_("skaleringstrappe"),
        choices=[(i, i) for i in range(1, 11)],
    )
    assessment_comment = models.TextField(
        verbose_name=_("supplerende oplysninger til vurdering"), blank=True
    )
    efforts = models.ManyToManyField(
        Effort, related_name="cases", verbose_name=_("indsatser"), blank=True,
    )
    note = models.TextField(verbose_name=_("note"), blank=True)

    # We only need to store historical records of effort_step, scaling_step,
    # case_worker, assessment_comment, team, thus we can exclude everything
    # else.
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
        """Determine if this case has expired.

        A case is considered to be expired if all its associated
        activites have end date in the past. If it does not have any
        associated (non-deleted) activities, it is not considered to be
        expired.
        """
        today = timezone.now().date()
        all_main_activities = Activity.objects.filter(
            activity_type=MAIN_ACTIVITY, appropriation__case=self
        ).exclude(status=STATUS_DELETED)
        # If no activities exists, we will not consider it expired.
        if not all_main_activities.exists():
            return False

        all_main_expired_activities = all_main_activities.filter(
            end_date__lt=today
        )
        return (
            all_main_activities.count() == all_main_expired_activities.count()
        )


class ApprovalLevel(Classification):
    """Organizational level on which an appropriation was approved."""

    class Meta:
        verbose_name = _("bevillingsniveau")
        verbose_name_plural = _("bevillingsniveauer")

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class Section(Classification):
    """Law sections and the corresponding KLE codes.

    Each section is associated with the target group for which it is
    allowed as well as the action steps allowed.
    """

    class Meta:
        verbose_name = _("paragraf")
        verbose_name_plural = _("paragraffer")

    paragraph = models.CharField(max_length=128, verbose_name=_("paragraf"))
    text = models.TextField(verbose_name=_("forklarende tekst"))
    allowed_for_target_groups = models.ManyToManyField(
        TargetGroup,
        related_name="sections",
        verbose_name=_("målgrupper"),
        blank=True,
    )
    allowed_for_steps = models.ManyToManyField(
        EffortStep,
        related_name="sections",
        verbose_name=_("trin i indsatstrappen"),
        blank=True,
    )
    law_text_name = models.CharField(
        max_length=128, verbose_name=_("lov tekst navn")
    )

    def __str__(self):
        return f"{self.paragraph}"


class SectionEffortStepProxy(Section.allowed_for_steps.through):
    """Proxy model for the allowed_for_steps (EffortStep) m2m field on Section.

    We use a proxy so we can override __str__ for use in django admin
    without an explicit through model.
    """

    class Meta:
        proxy = True
        verbose_name = _("paragraf")
        verbose_name_plural = _("paragraf")

    def __str__(self):
        return f"{self.section.paragraph} {self.section.text}"


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
        """Calculate appropriation status from status of activities."""
        if self.activities.filter(status=STATUS_EXPECTED).exists():
            return STATUS_EXPECTED
        if self.activities.filter(status=STATUS_GRANTED).exists():
            return STATUS_GRANTED

        return STATUS_DRAFT

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
    def granted_from_date(self):
        """Retrieve the start date of the main activity, if granted."""
        # The appropriation start date is the start date of the first
        # main activity.
        f = self.activities.filter(
            activity_type=MAIN_ACTIVITY,
            modifies__isnull=True,
            status=STATUS_GRANTED,
        )
        if f.exists():
            # There should be only one - count on that.
            activity = f.first()
            return activity.start_date

    @property
    def granted_to_date(self):
        """Retrieve the end date of the main activity, if granted."""
        # The appropriation start date is the start date of the first
        # main activity.
        f = self.activities.filter(
            activity_type=MAIN_ACTIVITY,
            modified_by__isnull=True,
            status=STATUS_GRANTED,
        )
        if f.exists():
            # There should be only one - count on that.
            activity = f.first()
            return activity.end_date

    @property
    def total_granted_this_year(self):
        """Retrieve total amount granted this year for this Appropriation.

        This includes both main and supplementary activities.
        """
        granted_activities = self.activities.filter(status=STATUS_GRANTED)

        this_years_payments = Payment.objects.filter(
            payment_schedule__activity__in=granted_activities
        ).in_this_year()

        return this_years_payments.amount_sum()

    @property
    def total_granted_full_year(self):
        """Retrieve total amount granted for this year.

        Extrapolate for the full year (January 1 - December 31).
        """
        all_activities = self.activities.filter(status=STATUS_GRANTED)
        return sum(
            activity.total_cost_full_year for activity in all_activities
        )

    @property
    def total_expected_this_year(self):
        """Retrieve total amount expected this year for this Appropriation.

        We take into account granted payments but overrule with expected
        amounts if they modify another activity.
        """
        activities = self.activities.filter(
            Q(status=STATUS_GRANTED) | Q(status=STATUS_EXPECTED)
        )
        return sum(a.total_expected_this_year for a in activities)

    @property
    def total_expected_full_year(self):
        """Retrieve total amount expected for this year.

        Extrapolate for the full year (January 1 - December 31).
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
    def total_cost_expected(self):
        """Retrieve total amount expected."""
        activities = self.activities.filter(
            Q(status=STATUS_GRANTED) | Q(status=STATUS_EXPECTED)
        )
        return sum(activity.total_cost for activity in activities)

    @property
    def total_cost_granted(self):
        """Retrieve total amount granted."""
        all_granted_activities = self.activities.filter(status=STATUS_GRANTED)
        payments = Payment.objects.filter(
            payment_schedule__activity__in=all_granted_activities
        )

        return payments.amount_sum()

    @property
    def main_activity(self):
        """Return main activity, if any."""
        # We define the main activity as the *first* main activity.
        f = self.activities.filter(
            activity_type=MAIN_ACTIVITY, modifies__isnull=True
        )
        if f.exists():
            # Invariant: There is only one main activity.
            return f.first()

    @property
    def supplementary_activities(self):
        """Return supplementary activities, if any."""
        suppl_activities = self.activities.filter(
            activity_type=SUPPL_ACTIVITY, modifies__isnull=True
        )
        return suppl_activities

    @property
    def section_info(self):
        """Return info for law section justifying this appropriation."""
        if self.main_activity and self.section:
            si_filter = self.main_activity.details.sectioninfo_set.filter(
                section=self.section
            )
            if si_filter.exists():
                return si_filter.first()

    @property
    def payment_plan(self):
        """Aggregate payment plans in this appropriation. TBD."""
        # TODO: Implement this in a later phase, maybe. Else delete.
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
        # Make sure that the supplementary activities are valid
        # for this appropriation.
        if not all(
            activity.details in self.section.supplementary_activities.all()
            for activity in self.supplementary_activities
        ):
            raise RuntimeError(
                _(
                    "En af følgeydelserne kan ikke bevilges"
                    " på den angivne paragraf"
                )
            )
        # Make sure that the main activity is valid for the
        # supplementary activities.
        if not all(
            self.main_activity.details
            in activity.details.main_activities.all()
            for activity in self.supplementary_activities
        ):
            raise RuntimeError(
                _(
                    "En af følgeydelserne kan ikke bevilges"
                    " på den angivne hovedaktivitet"
                )
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
                # The end date must not be later than any supplementary
                # activity's start date.
                if (
                    self.activities.filter(
                        start_date__gt=main_activity.end_date,
                        activity_type=SUPPL_ACTIVITY,
                    )
                    .exclude(status=STATUS_DELETED)
                    .exists()
                ):
                    raise RuntimeError(
                        _(
                            "Denne bevilling har følgeydelser, der starter "
                            "efter hovedydelsens slutdato. Slet venligst "
                            "disse eller ryk slutdatoen frem."
                        )
                    )
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
            granted_main_activities = self.activities.filter(
                activity_type=MAIN_ACTIVITY, status=STATUS_GRANTED
            )
            if not granted_main_activities.exists():
                raise RuntimeError(
                    _(
                        "Kan ikke godkende følgeydelser, før"
                        " hovedydelsen er godkendt."
                    )
                )
            # Set end date to the highest end date of all granted main
            # activities.
            granted_end_dates = [a.end_date for a in granted_main_activities]
            end_date = (
                None if None in granted_end_dates else max(granted_end_dates)
            )
            for a in to_be_granted:
                if a.end_date is None or (end_date and a.end_date > end_date):
                    a.end_date = end_date
                    a.save()
        approval_level = ApprovalLevel.objects.get(id=approval_level)
        for a in to_be_granted:
            a.refresh_from_db()
            a.grant(approval_level, approval_note, approval_user)

        # Everything went fine, we can send to SBSYS.
        send_appropriation(self, to_be_granted)

    def __str__(self):
        return f"{self.sbsys_id} - {self.section}"


class ServiceProvider(Classification):
    """Class containing information for a specific service provider."""

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


class ActivityDetails(Classification):
    """Class containing all services offered by this municipality.

    Each service is associated with the legal articles for which it is
    allowed as well as a price range.
    """

    class Meta:
        verbose_name = _("aktivitetsdetalje")
        verbose_name_plural = _("aktivitetsdetaljer")

    name = models.CharField(max_length=128, verbose_name=_("Navn"))
    description = models.TextField(verbose_name=_("beskrivelse"), blank=True)
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
        verbose_name=_("hovedydelser"),
        help_text=_(
            "Denne aktivitetsdetalje kan være følgeudgift for"
            " disse hovedydelser.<br>"
        ),
        blank=True,
    )

    def __str__(self):
        return f"{self.activity_id} - {self.name}"


class ActivityDetailsSectionProxy(
    ActivityDetails.supplementary_activity_for.through
):
    """
    Proxy model for supplementary_activity_for (Section) on ActivityDetails.

    We use a proxy model so we can override __str__ for
    use in django admin without an explicit through model.
    """

    class Meta:
        proxy = True
        verbose_name = _("aktivitetsdetalje")
        verbose_name_plural = _("aktivitetsdetalje")

    def __str__(self):
        return f"{self.activitydetails}"


class SectionInfo(models.Model):
    """For a main activity, KLE no. and SBSYS ID for the relevant sections."""

    class Meta:
        verbose_name = _("paragraf-info")
        verbose_name_plural = _("paragraf-info")

    activity_details = models.ForeignKey(
        ActivityDetails,
        on_delete=models.CASCADE,
        verbose_name=_("aktivitetsdetalje"),
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, verbose_name=_("paragraf")
    )

    kle_number = models.CharField(
        max_length=128, verbose_name=_("KLE-nummer"), blank=True
    )
    sbsys_template_id = models.CharField(
        max_length=128, verbose_name=_("SBSYS skabelon-id"), blank=True
    )

    main_activity_main_account_number = models.CharField(
        max_length=128,
        verbose_name=_("hovedkontonummer for hovedaktivitet"),
        blank=True,
    )
    supplementary_activity_main_account_number = models.CharField(
        max_length=128,
        verbose_name=_("hovedkontonummer for følgeudgift"),
        help_text=_(
            "Et hovedkontonummer der skal bruges, hvis en følgeudgift"
            " har denne aktivitetsdetalje som hovedydelse.<br>"
        ),
        blank=True,
    )

    def get_main_activity_main_account_number(self):
        """Get the main activity main account number."""
        return self.main_activity_main_account_number

    def get_supplementary_activity_main_account_number(self):
        """Get the supplementary activity main account number.

        If no such number exists, take the one for the main activity.
        """
        if self.supplementary_activity_main_account_number:
            return self.supplementary_activity_main_account_number
        return self.main_activity_main_account_number

    def __str__(self):
        return f"{self.activity_details} - {self.section}"


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
            # that does not have an expected activity and is not deleted.
            models.UniqueConstraint(
                fields=["appropriation"],
                condition=Q(activity_type=MAIN_ACTIVITY)
                & Q(modifies__isnull=True)
                & ~Q(status=STATUS_DELETED),
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
        on_delete=models.PROTECT,
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
        """Grant this activity - update payment info as needed."""
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
                while (
                    self.modifies is not None
                    and self.start_date <= self.modifies.start_date
                ):
                    old_activity = self.modifies
                    # Set STATUS_DELETED to circumvent
                    # unique_main_activity constraint.
                    old_activity.status = STATUS_DELETED
                    old_activity.save()
                    # Save with new modifies to not trigger CASCADE deletion.
                    self.modifies = self.modifies.modifies
                    self.save()
                    old_activity.delete()
                # self.start_date > self.modifies.start_date or is None
                if self.modifies:
                    self.modifies.end_date = self.start_date - timedelta(
                        days=1
                    )
            # In all cases ...
            if self.modifies:
                self.modifies.save()
                # When an expected activity that has a modifies is granted,
                # we change the expected activitys payment_id to be that of
                # the modifies activity.
                self.payment_plan.payment_id = (
                    self.modifies.payment_plan.payment_id
                )
                self.payment_plan.save()
            self.status = STATUS_GRANTED
        self.save()

    def validate_expected(self):
        """Validate this is a correct expected activity."""
        today = date.today()

        if not self.modifies:
            raise forms.ValidationError(
                _("den forventede justering har ingen ydelse at justere")
            )

        # Check that this modification is in the future.
        if self.start_date < today:
            raise forms.ValidationError(
                _(
                    "den forventede justerings startdato skal"
                    " være i fremtiden"
                )
            )

        return True

    @property
    def account(self):
        """Calculate the account to use with this activity."""
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
    def account_number(self):
        """Calculate the account_number to use with this activity.

        TODO: eventually replace account.number with this.
        """
        if self.activity_type == MAIN_ACTIVITY:
            section_info = SectionInfo.objects.filter(
                activity_details=self.details,
                section=self.appropriation.section,
            ).first()
            if not section_info:
                return None
            main_account_number = (
                section_info.get_main_activity_main_account_number()
            )
        else:
            main_activity = self.appropriation.main_activity
            if not main_activity:
                return None
            section_info = SectionInfo.objects.filter(
                activity_details=main_activity.details,
                section=self.appropriation.section,
            ).first()
            if not section_info:
                return None
            main_account_number = (
                section_info.get_supplementary_activity_main_account_number()
            )
        return f"{main_account_number}-{self.details.activity_id}"

    @property
    def monthly_payment_plan(self):
        """Calculate the payment plan for this activity, grouped by months."""
        payments = Payment.objects.filter(payment_schedule__activity=self)
        return payments.group_by_monthly_amounts()

    @property
    def applicable_payments(self):
        """Return payments that are not overruled by expected payments."""
        if not hasattr(self, "payment_plan") or not self.payment_plan:
            return Payment.objects.none()

        if self.status == STATUS_GRANTED and self.modified_by.exists():
            # one time payments are always overruled entirely.
            if (
                self.payment_plan.payment_type
                == PaymentSchedule.ONE_TIME_PAYMENT
            ):
                payments = Payment.objects.none()
            else:
                # Find the earliest payment date in the chain of
                # modified_by activities and exclude from that point
                # and onwards.
                modified_by_activities = self.get_all_modified_by_activities()
                min_payment = (
                    Payment.objects.filter(
                        payment_schedule__activity__in=modified_by_activities
                    )
                    .order_by("date")
                    .first()
                )
                if not min_payment:
                    payments = Payment.objects.filter(
                        payment_schedule__activity=self
                    )
                else:
                    min_date = min_payment.date
                    payments = Payment.objects.filter(
                        payment_schedule__activity=self
                    ).exclude(date__gte=min_date)
        else:
            payments = Payment.objects.filter(payment_schedule__activity=self)

        return payments

    @property
    def total_cost_this_year(self):
        """Calculate total cost this year for this activity."""
        return self.applicable_payments.in_this_year().amount_sum()

    @property
    def total_granted_this_year(self):
        """Calculate total amount *granted* on this activity this year."""
        if self.status == STATUS_GRANTED:
            payments = Payment.objects.filter(payment_schedule__activity=self)
            return payments.in_this_year().amount_sum()
        else:
            return Decimal(0)

    @property
    def total_expected_this_year(self):
        """Calculate total amount *expected* this year.

        As may be noted, this is redundant and identical to "total cost
        this year". Maybe one of these functions should be removed, the
        redundancy is due to a desire for clarity as to what is returned
        in different contexts.
        """
        return self.total_cost_this_year

    @property
    def total_cost(self):
        """Calculate the total cost of this activity at all times."""
        return self.applicable_payments.amount_sum()

    @property
    def total_cost_full_year(self):
        """Retrieve total amount expected for this year.

        Extrapolate for the full year (January 1 - December 31).
        """
        if not hasattr(self, "payment_plan") or not self.payment_plan:
            return Decimal(0.0)

        vat_factor = self.vat_factor
        now = timezone.now()
        start_date = date(now.year, month=1, day=1)
        end_date = date(now.year, month=12, day=31)
        num_payments = len(
            list(self.payment_plan.create_rrule(start_date, until=end_date))
        )
        return (
            self.payment_plan.calculate_per_payment_amount(vat_factor)
            * num_payments
        )

    @property
    def triggers_payment_email(self):
        """Decide if this activity triggers an email when saved.

        If this activity is not granted or doesn't have a payment plan we don't
        send an email.
        """
        if not self.status == STATUS_GRANTED:
            return False

        if not hasattr(self, "payment_plan") or not self.payment_plan:
            return False
        return True

    @property
    def vat_factor(self):
        """Calculate the VAT factor for this activity."""
        vat_factor = Decimal("100")
        if self.service_provider:
            vat_factor = self.service_provider.vat_factor
        return vat_factor

    def get_all_modified_by_activities(self):
        """Retrieve all modified_by objects recursively."""
        r = []
        if self.modified_by.exists():
            r.append(
                self.modified_by.prefetch_related(
                    "payment_plan__payments"
                ).first()
            )
            return (
                r + self.modified_by.first().get_all_modified_by_activities()
            )
        return r

    def save(self, *args, **kwargs):
        """
        Save activity.

        Also updates "modified" field on appropriation and
        payment_plan payments.
        """
        super().save(*args, **kwargs)
        self.appropriation.save()
        if hasattr(self, "payment_plan") and self.payment_plan:
            self.payment_plan.save()


class RelatedPerson(AuditModelMixin, models.Model):
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
    from_serviceplatformen = models.BooleanField(
        blank=True, default=True, verbose_name=_("fra Serviceplatformen")
    )

    main_case = models.ForeignKey(
        Case,
        related_name="related_persons",
        on_delete=models.CASCADE,
        verbose_name=_("hovedsag"),
    )

    @staticmethod
    def serviceplatformen_to_related_person(data):
        """Convert data from Serviceplatformen to our RelatedPerson model."""
        converter_dict = {
            "cprnr": "cpr_number",
            "relation": "relation_type",
            "adresseringsnavn": "name",
        }
        converted_data = {
            converter_dict[k]: v
            for (k, v) in data.items()
            if k in converter_dict
        }
        extra_fields = {"from_serviceplatformen": True}
        converted_data.update(extra_fields)

        return converted_data

    def __str__(self):
        return f"{self.name} - {self.cpr_number} - {self.main_case}"


class Account(Classification):
    """Class containing account numbers.

    Should have a number for each
    (main activity, supplementary activity, section) pair.
    """

    main_account_number = models.CharField(
        max_length=128, verbose_name=_("hovedkontonummer")
    )
    activity_number = models.CharField(
        max_length=128, verbose_name=_("aktivitetsnummer"), blank=True
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

    @property
    def number(self):
        """Calculate the account number of this activity."""
        if not self.activity_number:
            if self.supplementary_activity:
                activity_number = self.supplementary_activity.activity_id
            else:
                activity_number = self.main_activity.activity_id
        else:
            activity_number = self.activity_number

        return f"{self.main_account_number}-{activity_number}"

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
