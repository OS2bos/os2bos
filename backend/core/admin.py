# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


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
    readonly_fields = ("payment_id", "account_string")

    def payment_id(self, obj):
        return obj.payment_schedule.payment_id

    def account_string(self, obj):
        return obj.account_string

    payment_id.short_description = _("betalings-ID")
    account_string.short_description = _("kontostreng")


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    readonly_fields = ("payment_id", "account_string")

    def account_string(self, obj):
        return obj.account_string

    account_string.short_description = _("kontostreng")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    readonly_fields = "number"

    def number(self, obj):
        return obj.number

    number.short_description = _("kontonummer")


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
    search_fields = ("paragraph",)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    search_fields = ("name", "cvr_number")
