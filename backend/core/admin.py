from django.contrib import admin

from core.models import (
    Municipality,
    PaymentSchedule,
    Payment,
    Case,
    Appropriation,
    Activity,
    RelatedPerson,
    SchoolDistrict,
    Sections,
    ActivityCatalog,
    Account,
    ServiceProvider,
)

for klass in (
    Municipality,
    PaymentSchedule,
    Payment,
    Case,
    Appropriation,
    Activity,
    RelatedPerson,
    SchoolDistrict,
    Sections,
    ActivityCatalog,
    Account,
    ServiceProvider,
):
    admin.site.register(klass, admin.ModelAdmin)
