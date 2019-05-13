from django.db import models


class Case(models.Model):
    """A case, covering one child - corresponding to a Hovedsag in SBSYS."""
    pass


class Appropriation(models.Model):
    """An appropriation of funds in a Case - corresponds to a Sag in SBSYS."""
    pass


class Activity(models.Model):
    """An activity is a specific service provided within an appropriation."""
    pass


class RelatedPerson(models.Model):
    """A person related to a Case, e.g. as a parent or sibling."""
    pass


class PaymentSchedule(models.Model):
    """Schedule a payment for an Activity."""
    pass


class Payment(models.Model):
    """Represents an amount paid to a supplier - amount, recpient, date.

    These may be entered manually, but ideally they should be imported
    from an accounts payable system."""
    pass


class Municipalities(models.Model):
    """Represents a Danish municipality."""
    pass


class Articles(models.Model):
    """Law articles and the corresponding KLE codes."""
    pass


class ActivityCatalog(models.Model):
    """Class containing all services offered by this municipality.

    Each service is associated with the legal articles for which it is
    allowed as well as a price range."""
    pass


class ServiceRange(models.Model):
    """Class containing all the service providers for each service.

    Also contains price information etc."""
    pass
