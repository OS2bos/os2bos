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
    PaymentMethodDetails,
    ApprovalLevel,
)

for klass in (
    Municipality,
    PaymentSchedule,
    PaymentMethodDetails,
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
    ApprovalLevel,
):
    admin.site.register(klass, admin.ModelAdmin)
