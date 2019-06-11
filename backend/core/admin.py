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
):
    admin.site.register(klass, admin.ModelAdmin)
