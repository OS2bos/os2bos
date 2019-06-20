from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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
    Team,
    User,
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
    Team,
):
    admin.site.register(klass, admin.ModelAdmin)

admin.site.register(User, UserAdmin)
