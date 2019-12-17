# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Customize django-admin interface."""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

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
)

for klass in (
    Municipality,
    PaymentMethodDetails,
    Case,
    Appropriation,
    Activity,
    RelatedPerson,
    SchoolDistrict,
    Team,
    ApprovalLevel,
    SectionInfo,
    EffortStep,
):
    admin.site.register(klass, admin.ModelAdmin)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Dislay read only fields on payment."""

    readonly_fields = ("payment_id", "account_string")

    def payment_id(self, obj):
        """Get payment ID from payment plan."""
        return obj.payment_schedule.payment_id

    def account_string(self, obj):
        """Get account string."""
        return obj.account_string

    payment_id.short_description = _("betalings-ID")
    account_string.short_description = _("kontostreng")


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """Display read only fields on payment schedule."""

    readonly_fields = ("payment_id", "account_string")

    def account_string(self, obj):
        """Get account string."""
        return obj.account_string

    account_string.short_description = _("kontostreng")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
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
class SectionAdmin(admin.ModelAdmin):
    """Add search field."""

    search_fields = ("paragraph",)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    """Add search fields."""

    search_fields = ("name", "cvr_number")
