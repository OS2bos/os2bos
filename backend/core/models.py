from django.db import models
from django.utils.translation import gettext_lazy as _
from django_audit_fields.models import AuditModelMixin


class Municipality(models.Model):
    """Represents a Danish municipality."""

    name = models.CharField(max_length=128, verbose_name=_("navn"))

    def __str__(self):
        return f"{self.name}"


class ActivityCatalog(models.Model):
    """Class containing all services offered by this municipality.

    Each service is associated with the legal articles for which it is
    allowed as well as a price range."""


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
    recipient_id = models.CharField(max_length=128, verbose_name=_("ID"))
    recipient_name = models.CharField(max_length=128, verbose_name=_("Navn"))
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
    payment_method = models.CharField(
        max_length=128,
        verbose_name=_("betalingsmåde"),
        choices=payment_method_choices,
    )

    # TODO: Add actual scheduling information.


class Payment(models.Model):
    """Represents an amount paid to a supplier - amount, recpient, date.

    These may be entered manually, but ideally they should be imported
    from an accounts payable system."""

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
        choices=PaymentSchedule.payment_method_choices,
    )

    payment_schedule = models.ForeignKey(
        PaymentSchedule, on_delete=models.CASCADE, related_name="payments"
    )


class Case(AuditModelMixin, models.Model):
    """A case, covering one child - corresponding to a Hovedsag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, max_length=128, verbose_name=_("SBSYS-ID")
    )
    cpr_number = models.CharField(max_length=12, verbose_name=_("cpr-nummer"))
    name = models.CharField(max_length=128, verbose_name=_("Navn"))
    case_worker = models.CharField(
        max_length=128, verbose_name=_("sagsbehandler")
    )
    district = models.CharField(
        blank=True, max_length=128, verbose_name=_("skoledistrikt")
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
    # Target group - definitions and choice list.
    FAMILY_DEPT = "FAMILY_DEPT"
    DISABILITY_DEPT = "DISABILITY_DEPT"
    target_group_choices = (
        (FAMILY_DEPT, _("familieafdelingen")),
        (DISABILITY_DEPT, _("handicapafdelingen")),
    )
    target_group = models.CharField(
        max_length=128,
        verbose_name=_("målgruppe"),
        choices=target_group_choices,
    )
    refugee_integration = models.BooleanField(
        verbose_name=_("integrationsindsatsen"), default=False
    )
    cross_department_measure = models.BooleanField(
        verbose_name=_("tværgående ungeindsats"), default=False
    )


class Appropriation(AuditModelMixin, models.Model):
    """An appropriation of funds in a Case - corresponds to a Sag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, max_length=128, verbose_name=_("SBSYS-ID")
    )
    section = models.CharField(verbose_name=_("paragraf"), max_length=128)

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

    # Approval level - definitions and choice list.
    CASE_WORKER = "CASE_WORKER"
    TEAM_LEADER = "TEAM_LEADER"
    SECTION_HEAD = "SECTION_HEAD"
    TEAM_MEETING = "TEAM_MEETING"
    SPECIALIST = "SPECIALIST"

    approval_level_choices = (
        (CASE_WORKER, _("egenkompetence")),
        (TEAM_LEADER, _("teamleder")),
        (SECTION_HEAD, _("afsnitsleder")),
        (TEAM_MEETING, _("teammøde")),
        (SECTION_HEAD, _("fagspecialist")),
    )
    approval_level = models.CharField(
        verbose_name=_("bevilling foretaget på niveau"),
        max_length=16,
        choices=approval_level_choices,
    )
    approval_note = models.TextField(verbose_name=_("evt. bemærkning"))

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, related_name="appropriations"
    )

    @property
    def payment_plan(self):
        """Return the payment plan for this appropriation."""

        # TODO: Implement this.


class Activity(AuditModelMixin, models.Model):
    """An activity is a specific service provided within an appropriation."""

    # The service contains the name, tolerance, etc.
    service = models.ForeignKey(ActivityCatalog, on_delete=models.PROTECT)

    # Status - definitions and choice list.
    STATUS_EXPECTED = "EXPECTED"
    STATUS_GRANTED = "GRANTED"
    status_choices = (
        (STATUS_EXPECTED, _("forventet")),
        (STATUS_GRANTED, _("bevilget")),
    )
    status = models.CharField(
        verbose_name=_("status"), max_length=128, choices=status_choices
    )

    start_date = models.DateField(verbose_name=_("startdato"))
    end_date = models.DateField(verbose_name=_("slutdato"))

    # Activity types and choice list.
    MAIN_ACTIVITY = "MAIN_ACTIVITY"
    SUPPL_ACTIVITY = "SUPPL_ACTIVITY"
    ONETIME_EXPENSE = "ONETIME_EXPENSE"
    EXPECTED_CHANGE = "EXPECTED_CHANGE"
    type_choices = (
        (MAIN_ACTIVITY, _("hovedaktivitet")),
        (SUPPL_ACTIVITY, _("følgeaktivitet")),
        (ONETIME_EXPENSE, _("engangsudgift")),
        (EXPECTED_CHANGE, _("forventning")),
    )

    activity_type = models.CharField(max_length=128, verbose_name=_("type"))

    payment_plan = models.OneToOneField(
        PaymentSchedule,
        on_delete=models.CASCADE,
        verbose_name=_("betalingsplan"),
    )

    # Supplementary activities will point to their main activity.
    # Root activities may be a main activity and followed by any
    # supplementary activity - one time payments must be followed by one
    # time payments only.
    main_activity = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="supplementary_activities",
        on_delete=models.CASCADE,
        verbose_name=_("hovedaktivitet"),
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
    # The appropriation that own this activity.
    # The appropriation will and must be set on the *main* activity
    # only.
    appropriation = models.ForeignKey(
        Appropriation,
        null=True,
        blank=True,
        related_name="activities",
        on_delete=models.CASCADE,
    )


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


class Sections(models.Model):
    """Law sections and the corresponding KLE codes."""

    paragraph = models.CharField(max_length=128, verbose_name=_("paragraf"))
    kle_number = models.CharField(max_length=128, verbose_name=_("KLE-nummer"))
    text = models.TextField(verbose_name=_("forklarende tekst"))

    def __str__(self):
        return f"{self.paragraph} - {self.kle_number}"


class ServiceRange(models.Model):
    """Class containing all the service providers for each service.

    Also contains price information etc."""
