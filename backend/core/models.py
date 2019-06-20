from django.db import models
from django.contrib.postgres import fields
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django_audit_fields.models import AuditModelMixin
from simple_history.models import HistoricalRecords

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
    case_worker = models.ForeignKey(
        User,
        verbose_name=_("sagsbehandler"),
        related_name="cases",
        on_delete=models.PROTECT,
    )
    district = models.ForeignKey(
        SchoolDistrict,
        related_name="cases",
        verbose_name=_("skoledistrikt"),
        on_delete=models.PROTECT,
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


class Sections(models.Model):
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

    def __str__(self):
        return f"{self.paragraph} - {self.kle_number}"


class Appropriation(AuditModelMixin, models.Model):
    """An appropriation of funds in a Case - corresponds to a Sag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, max_length=128, verbose_name=_("SBSYS-ID")
    )
    section = models.ForeignKey(
        Sections,
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
    def payment_plan(self):
        """Return the payment plan for this appropriation."""

        # TODO: Implement this.


class ServiceProvider(models.Model):
    """
    Class containing information for a specific service provider.
    """

    cvr_number = models.CharField(max_length=8, blank=True)
    name = models.CharField(max_length=128, blank=False)
    vat_factor = models.DecimalField(max_digits=5, decimal_places=2)


class ActivityCatalog(models.Model):
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
        Sections, related_name="main_activities"
    )
    supplementary_activity_for = models.ManyToManyField(
        Sections, related_name="supplementary_activities"
    )
    service_providers = models.ManyToManyField(
        ServiceProvider, related_name="activity_catalogs"
    )

    def __str__(self):
        return f"{self.activity_id} - {self.name}"


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
    EXPECTED_CHANGE = "EXPECTED_CHANGE"
    type_choices = (
        (MAIN_ACTIVITY, _("hovedaktivitet")),
        (SUPPL_ACTIVITY, _("følgeaktivitet")),
        (EXPECTED_CHANGE, _("forventning")),
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

    # Supplementary activities will point to their main activity.
    # Root activities may be a main activity and followed by any
    # supplementary activity.
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

    service_provider = models.ForeignKey(
        ServiceProvider,
        null=True,
        blank=True,
        related_name="activities",
        on_delete=models.SET_NULL,
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

    Should have a different number for each (ActivityCatalog, Sections) pair.
    """

    number = models.CharField(max_length=128)
    activity_catalog = models.ForeignKey(
        ActivityCatalog, null=False, on_delete=models.CASCADE
    )
    section = models.ForeignKey(Sections, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number} - {self.activity_catalog} - {self.section}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["activity_catalog", "section"],
                name="unique_account_number",
            )
        ]
