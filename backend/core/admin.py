from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.forms import SectionForm

from core.models import (
    Municipality,
    PaymentSchedule,
    Payment,
    Case,
    Appropriation,
    Activity,
    RelatedPerson,
    SchoolDistrict,
    Section,
    ActivityDetails,
    Account,
    ServiceProvider,
    PaymentMethodDetails,
    Team,
    User,
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
    Account,
    Team,
    ApprovalLevel,
):
    admin.site.register(klass, admin.ModelAdmin)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        ("Organisation", {"fields": ("team",)}),
    ) + BaseUserAdmin.fieldsets


@admin.register(ActivityDetails)
class ActivityDetailsAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "main_activity_for",
        "supplementary_activity_for",
        "service_providers",
        "main_activities",
    )
    search_fields = ("activity_id",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    form = SectionForm
    search_fields = ("paragraph", "kle_number")


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    search_fields = ("name", "cvr_number")
