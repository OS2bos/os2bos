# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape, mark_safe
from django.urls import reverse

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
        link = reverse(
            "admin:core_paymentschedule_change", args=[obj.payment_schedule.id]
        )
        return mark_safe(
            f'<a href="{link}">{escape(obj.payment_schedule.__str__())}</a>'
        )

    def payment_id(self, obj):
        return obj.payment_schedule.payment_id

    def account_string(self, obj):
        return obj.account_string

    payment_id.short_description = _("betalings-ID")
    account_string.short_description = _("kontostreng")
    payment_schedule_str.short_description = _("betalingsplan")


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
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
        return obj.account_string

    account_string.short_description = _("kontostreng")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ("number",)

    def number(self, obj):
        return obj.number

    number.short_description = _("konteringsnummer")


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
