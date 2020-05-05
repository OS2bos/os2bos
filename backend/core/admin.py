# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Customize django-admin interface."""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape, mark_safe
from django.urls import reverse
from django import forms

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
    SectionInfo,
    EffortStep,
    TargetGroup,
    Effort,
)

for klass in (
    PaymentMethodDetails,
    Case,
    Appropriation,
    Activity,
    RelatedPerson,
    Team,
    SectionInfo,
):
    admin.site.register(klass, admin.ModelAdmin)


User = get_user_model()


class ClassificationAdmin(admin.ModelAdmin):
    def is_workflow_engine_or_admin(self, request):
        try:
            profile = request.user.profile
        except AttributeError:
            return False

        if profile in [User.WORKFLOW_ENGINE, User.ADMIN]:
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return self.is_workflow_engine_or_admin(request)

    def has_add_permission(self, request):
        return self.is_workflow_engine_or_admin(request)

    def has_change_permission(self, request, obj=None):
        return self.is_workflow_engine_or_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self.is_workflow_engine_or_admin(request)

    def has_module_permission(self, request):
        return self.is_workflow_engine_or_admin(request)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Dislay read only fields on payment."""

    readonly_fields = ("payment_id", "account_string")
    search_fields = ("payment_schedule__payment_id",)

    list_display = (
        "id",
        "payment_id",
        "account_string",
        "date",
        "paid",
        "paid_date",
        "payment_schedule_str",
    )
    list_filter = (
        "paid",
        "payment_schedule__fictive",
        "date",
        "paid_date",
        "payment_method",
        "recipient_type",
    )

    def payment_schedule_str(self, obj):
        """Get related payment schedule link."""
        link = reverse(
            "admin:core_paymentschedule_change", args=[obj.payment_schedule.id]
        )
        return mark_safe(
            f'<a href="{link}">{escape(obj.payment_schedule.__str__())}</a>'
        )

    def payment_id(self, obj):
        """Get payment ID from payment plan."""
        return obj.payment_schedule.payment_id

    def account_string(self, obj):
        """Get account string."""
        return obj.account_string

    payment_id.short_description = _("betalings-ID")
    account_string.short_description = _("kontostreng")
    payment_schedule_str.short_description = _("betalingsplan")


class TargetGroupForm(forms.ModelForm):
    """Form for TargetGroup to set required_fields_for_case."""

    def __init__(self, *args, **kwargs):
        """__init__ for TargetGroupForm.

        Set initial value for required_fields_for_case.
        """
        super(TargetGroupForm, self).__init__(*args, **kwargs)
        # Set initial value as a list
        self.initial[
            "required_fields_for_case"
        ] = self.instance.required_fields_for_case

    def required_fields_for_case_choices():
        """Define the choices for the required_fields_for_case field."""
        excluded_fields = ["revision"]

        choices = [
            (field.name, field.verbose_name)
            for field in Case._meta.get_fields()
            if field.null
            and hasattr(field, "verbose_name")
            and field.name not in excluded_fields
        ]
        return choices

    required_fields_for_case = forms.MultipleChoiceField(
        choices=required_fields_for_case_choices(),
        label=_("Påkrævede felter på sag"),
        required=False,
    )


@admin.register(TargetGroup)
class TargetGroupAdmin(ClassificationAdmin):
    """ModelAdmin for TargetGroup with custom ModelForm."""

    fields = ("name", "required_fields_for_case")
    form = TargetGroupForm


@admin.register(Effort)
class EffortAdmin(ClassificationAdmin):
    """ModelAdmin for Effort."""

    filter_horizontal = ("allowed_for_target_groups",)


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """Display read only fields on payment schedule."""

    readonly_fields = ("payment_id", "account_string")
    search_fields = ("payment_id",)
    list_display = (
        "id",
        "payment_id",
        "recipient_type",
        "recipient_id",
        "recipient_name",
        "payment_frequency",
        "payment_method",
        "payment_type",
        "payment_amount",
        "account_string",
        "fictive",
    )
    list_filter = (
        "payment_method",
        "payment_type",
        "payment_frequency",
        "fictive",
    )

    def account_string(self, obj):
        """Get account string."""
        return obj.account_string

    account_string.short_description = _("kontostreng")


@admin.register(Account)
class AccountAdmin(ClassificationAdmin):
    """Display account number (konteringsnummer) as read only field."""

    readonly_fields = ("number",)

    def number(self, obj):
        """Get account number."""
        return obj.number

    number.short_description = _("konteringsnummer")


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Add team to user admin interface."""

    fieldsets = (
        ("Organisation", {"fields": ("team",)}),
    ) + BaseUserAdmin.fieldsets


@admin.register(ActivityDetails)
class ActivityDetailsAdmin(admin.ModelAdmin):
    """Widgets: Filter_horizontal for many to many links, add search field."""

    filter_horizontal = (
        "main_activity_for",
        "supplementary_activity_for",
        "service_providers",
        "main_activities",
    )
    search_fields = ("activity_id",)


@admin.register(Section)
class SectionAdmin(ClassificationAdmin):
    """Add search field."""

    search_fields = ("paragraph",)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(ClassificationAdmin):
    """Add search fields."""

    search_fields = ("name", "cvr_number")


@admin.register(Municipality)
class MunicipalityAdmin(ClassificationAdmin):
    pass


@admin.register(ApprovalLevel)
class ApprovalLevelAdmin(ClassificationAdmin):
    pass


@admin.register(EffortStep)
class EffortStepAdmin(ClassificationAdmin):
    pass


@admin.register(SchoolDistrict)
class SchoolDistrictAdmin(ClassificationAdmin):
    pass
