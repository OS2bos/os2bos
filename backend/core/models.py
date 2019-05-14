from django.db import models
from django.utils.translation import gettext_lazy as _
from django_audit_fields.models import AuditModelMixin


class Municipality(models.Model):
    """Represents a Danish municipality."""

    name = models.CharField(null=False, max_length=128, verbose_name=_("navn"))


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
        null=False,
        max_length=128,
        verbose_name=_("betalingsmodtager"),
        choices=recipient_choices,
    )
    recipient_id = models.CharField(
        null=False, max_length=128, verbose_name=_("ID")
    )
    # Payment methods and choice list.
    payment_method = models.CharField(
        null=False, max_length=128, verbose_name=_("betalingsmåde")
    )

    # TODO: Add actual scheduling information.


class Payment(models.Model):
    """Represents an amount paid to a supplier - amount, recpient, date.

    These may be entered manually, but ideally they should be imported
    from an accounts payable system."""

    date = models.DateField(null=False, verbose_name=_("betalingsdato"))
    payment_method = models.CharField(
        null=False, max_length=128, verbose_name=_("betalingsmåde")
    )
    recipient_type = models.CharField(
        null=False,
        max_length=128,
        verbose_name=_("betalingsmodtager"),
        choices=PaymentSchedule.recipient_choices,
    )
    recipient_id = models.CharField(
        null=False, max_length=128, verbose_name=_("ID")
    )

    payment_schedule = models.ForeignKey(
        PaymentSchedule,
        on_delete=models.CASCADE,
        null=False,
        related_name="payments",
    )


class Case(AuditModelMixin, models.Model):
    """A case, covering one child - corresponding to a Hovedsag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, null=False, max_length=128, verbose_name=_("SBSYS-ID")
    )
    cpr_number = models.CharField(
        null=False, max_length=12, verbose_name=_("cpr-nummer")
    )
    case_worker = models.CharField(
        null=False, max_length=128, verbose_name=_("sagsbehandler")
    )
    district = models.CharField(
        max_length=128, verbose_name=_("skoledistrikt")
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
        max_length=128, verbose_name=_("målgruppe")
    )
    refugee_integration = models.BooleanField(
        null=False, verbose_name=_("integrationsindsatsen")
    )
    cross_department_measure = models.BooleanField(
        null=False, verbose_name=_("tværgående ungeindsats")
    )


class Appropriation(AuditModelMixin, models.Model):
    """An appropriation of funds in a Case - corresponds to a Sag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, null=False, max_length=128, verbose_name=_("SBSYS-ID")
    )
    section = models.CharField(
        null=False, verbose_name=_("paragraf"), max_length=128
    )

    # Status - definitions and choice list.
    STATUS_DRAFT = "DRAFT"
    STATUS_BUDGETED = "BUDGETED"
    STATUS_GRANTED = "GRANTED"
    STATUS_DISCONTINUED = "DISCONTINUED"
    status_choices = (
        (STATUS_DRAFT, _("Kladde")),
        (STATUS_BUDGETED, _("Disponeret")),
        (STATUS_GRANTED, _("Bevilget")),
        (STATUS_DISCONTINUED, _("Udgået")),
    )
    status = models.CharField(
        verbose_name=_("status"), max_length=16, choices=status_choices
    )

    # Approval level - definitions and choice list.
    CASE_WORKER = "CASE_WORKER"
    TEAM_LEADER = "TEAM_LEADER"
    SECTION_HEAD = "SECTION_HEAD"
    approval_level_choices = (
        (CASE_WORKER, _("Egenkompetence")),
        (TEAM_LEADER, _("Teamleder")),
        (SECTION_HEAD, _("Afsnitsleder")),
    )
    approval_level = models.CharField(
        verbose_name=_("bevilling foretaget på niveau"),
        max_length=16,
        choices=approval_level_choices,
    )
    approval_note = models.TextField(verbose_name=_("evt. bemærkning"))

    case = models.ForeignKey(
        Case,
        null=False,
        on_delete=models.CASCADE,
        related_name="appropriations",
    )

    @property
    def payment_plan(self):
        """Return the payment plan for this appropriation."""

        # TODO: Implement this.


class Activity(AuditModelMixin, models.Model):
    """An activity is a specific service provided within an appropriation."""

    # The activity type will contain the name, tolerance, etc.
    activity_type = models.ForeignKey(
        ActivityCatalog, null=False, on_delete=models.PROTECT
    )

    # Status - definitions and choice list.
    STATUS_EXPECTED = "EXPECTED"
    STATUS_GRANTED = "GRANTED"
    status_choices = (
        (STATUS_EXPECTED, _("forventet")),
        (STATUS_GRANTED, _("bevilget")),
    )
    status = models.CharField(verbose_name=_("status"), max_length=128)

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

    activity_type = models.CharField(
        null=False, max_length=128, verbose_name=_("type")
    )

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
        related_name="supplementary_activities",
        on_delete=models.CASCADE,
        verbose_name=_("hovedaktivitet"),
    )
    # An expected change modifies another actitvity and will eventually
    # be merged with it.
    modifies = models.ForeignKey(
        "self", null=True, related_name="modified_by", on_delete=models.CASCADE
    )
    # The appropriation that own this activity.
    # The appropriation will and must be set on the *main* activity
    # only.
    appropriation = models.ForeignKey(
        Appropriation,
        null=True,
        related_name="activities",
        on_delete=models.CASCADE,
    )


class RelatedPerson(models.Model):
    """A person related to a Case, e.g. as a parent or sibling."""

    relation_type = models.CharField(
        null=False, max_length=128, verbose_name=_("relation")
    )
    cpr_number = models.CharField(max_length=12, verbose_name=_("cpr-nummer"))
    name = models.CharField(null=False, max_length=128, verbose_name=_("navn"))
    related_case = models.CharField(
        max_length=128, verbose_name=_("SBSYS-sag")
    )

    main_case = models.ForeignKey(
        Case, related_name="related_persons", on_delete=models.CASCADE
    )


class Sections(models.Model):
    """Law sections and the corresponding KLE codes."""


class ServiceRange(models.Model):
    """Class containing all the service providers for each service.

    Also contains price information etc."""
