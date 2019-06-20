from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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
    ApprovalLevel,
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
    ApprovalLevel,
):
    admin.site.register(klass, admin.ModelAdmin)


class CustomUserAdmin(BaseUserAdmin):
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("team", "is_team_leader")}),
    )


admin.site.register(User, CustomUserAdmin)
