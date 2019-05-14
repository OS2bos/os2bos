from django.db import models
from django.utils.translation import gettext_lazy as _
from django_audit_fields.models import AuditModelMixin


class Municipality(models.Model):
    """Represents a Danish municipality."""


class ActivityCatalog(models.Model):
    """Class containing all services offered by this municipality.

    Each service is associated with the legal articles for which it is
    allowed as well as a price range."""


class Case(AuditModelMixin, models.Model):
    """A case, covering one child - corresponding to a Hovedsag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, null=False, max_length=128, verbose_name=_("SBSYS-ID")
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
        null=False, verbose_name=_("Tværgående ungeindsats")
    )


class Appropriation(AuditModelMixin, models.Model):
    """An appropriation of funds in a Case - corresponds to a Sag in SBSYS."""

    sbsys_id = models.CharField(
        unique=True, null=False, max_length=128, verbose_name=_("SBSYS-ID")
    )
    section = models.CharField(
        null=False, verbose_name=_("paragraf"), max_length=128
    )
    status = models.CharField(verbose_name=_("status"), max_length=128)
    approval_level = models.CharField(
        verbose_name=_("bevilling foretaget på niveau"), max_length=128
    )
    approval_note = models.TextField(verbose_name=_("evt. bemærkning"))

    case = models.ForeignKey(Case, null=False, on_delete=models.CASCADE)

    @property
    def payment_plan(self):
        """Return the payment plan for this appropriation."""

        # TODO: Implement this.


class Activity(AuditModelMixin, models.Model):
    """An activity is a specific service provided within an appropriation."""

    activity_type = models.ForeignKey(
        ActivityCatalog, null=False, on_delete=models.PROTECT
    )
    status = models.CharField(verbose_name=_("status"), max_length=128)
    start_date = models.DateField(verbose_name=_("start"))
    end_date = models.DateField(verbose_name=_("end"))


class RelatedPerson(models.Model):
    """A person related to a Case, e.g. as a parent or sibling."""


class PaymentSchedule(models.Model):
    """Schedule a payment for an Activity."""


class Payment(models.Model):
    """Represents an amount paid to a supplier - amount, recpient, date.

    These may be entered manually, but ideally they should be imported
    from an accounts payable system."""


class Sections(models.Model):
    """Law sections and the corresponding KLE codes."""


class ServiceRange(models.Model):
    """Class containing all the service providers for each service.

    Also contains price information etc."""
