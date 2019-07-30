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


class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        ("Organisation", {"fields": ("team",)}),
    ) + BaseUserAdmin.fieldsets


class ActivityDetailsAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "main_activity_for",
        "supplementary_activity_for",
        "service_providers",
        "main_activities",
    )
    search_fields = ("activity_id",)


class SectionAdmin(admin.ModelAdmin):
    form = SectionForm
    search_fields = ("paragraph", "kle_number")


class ServiceProviderAdmin(admin.ModelAdmin):
    search_fields = ("name", "cvr_number")


admin.site.register(User, CustomUserAdmin)
admin.site.register(ActivityDetails, ActivityDetailsAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(ServiceProvider, ServiceProviderAdmin)
