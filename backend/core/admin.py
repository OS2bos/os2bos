# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Customize django-admin interface."""

import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape, mark_safe, format_html_join
from django.urls import reverse
from django.db.models import F
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
    ApprovalLevel,
    SectionInfo,
    EffortStep,
    TargetGroup,
    Effort,
    RatePerDate,
    VariableRate,
    Rate,
    SectionEffortStepProxy,
    ActivityDetailsSectionProxy,
)

for klass in (
    PaymentMethodDetails,
    Team,
    SectionInfo,
):
    admin.site.register(klass, admin.ModelAdmin)


User = get_user_model()


class ClassificationInline(admin.TabularInline):
    """TabularInline for Classification inlines."""

    def has_view_permission(self, request, obj=None):
        """Override has_view_permission for InlineModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()

    def has_add_permission(self, request):
        """Override has_add_permission for InlineModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()

    def has_change_permission(self, request, obj=None):
        """Override has_change_permission for InlineModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()

    def has_delete_permission(self, request, obj=None):
        """Override has_delete_permission for InlineModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()


class ClassificationAdmin(admin.ModelAdmin):
    """ModelAdmin for Classification models."""

    def has_view_permission(self, request, obj=None):
        """Override has_view_permission for ModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()

    def has_add_permission(self, request):
        """Override has_add_permission for ModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()

    def has_change_permission(self, request, obj=None):
        """Override has_change_permission for ModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()

    def has_delete_permission(self, request, obj=None):
        """Override has_delete_permission for ModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()

    def has_module_permission(self, request):
        """Override has_model_permission for ModelAdmin."""
        user = request.user
        return user.is_authenticated and user.is_workflow_engine_or_admin()


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """ModelAdmin for Case."""

    pass


@admin.register(Appropriation)
class AppropriationAdmin(admin.ModelAdmin):
    """ModelAdmin for Appropriation."""

    pass


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """ModelAdmin for Activity."""

    readonly_fields = ("account_number",)

    def account_number(self, obj):
        """Get account number."""
        return obj.account_number

    account_number.short_description = _("kontonummer")


class RatePerDateInline(ClassificationInline):
    """RatePerDateInline for VariablerateAdmin."""

    model = RatePerDate

    readonly_fields = ["rate", "start_date", "end_date"]
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        """Override has_add_permission for RatePerDateInline."""
        return False


class VariableRateAdminForm(forms.ModelForm):
    """Form for handling the specifics of date dependency."""

    class Meta:
        model = VariableRate
        fields = []

    rate = forms.DecimalField(label=_("Takst"))
    start_date = forms.DateField(
        label=_("Startdato"),
        initial=datetime.date.today(),
        required=False,
        widget=forms.SelectDateWidget(),
    )
    end_date = forms.DateField(
        label=_("Slutdato"), required=False, widget=forms.SelectDateWidget()
    )

    def __init__(self, *args, **kwargs):
        """__init__ for VariableRateAdminForm.

        Set initial value for rate and start_date.
        """
        super().__init__(*args, **kwargs)
        # Find RatePerDate ordered by start_date.
        latest = self.instance.rates_per_date.order_by(
            F("start_date").asc(nulls_first=True)
        ).last()
        # If any object exists set the initial rate, start_date and end_date.
        if latest:
            self.initial["start_date"] = latest.start_date
            self.initial["end_date"] = latest.end_date
            self.initial["rate"] = latest.rate

    def clean(self):
        """Override ModelForm clean."""
        cleaned_data = super().clean()
        rate_start_date = cleaned_data.get("start_date")
        rate_end_date = cleaned_data.get("end_date")

        if (
            rate_start_date
            and rate_end_date
            and not rate_start_date < rate_end_date
        ):
            raise forms.ValidationError(
                _("Slutdato skal være mindre end startdato")
            )
        return cleaned_data


class VariableRateAdmin(ClassificationAdmin):
    """ModelAdmin for VariableRate subclasses."""

    inlines = [
        RatePerDateInline,
    ]
    form = VariableRateAdminForm

    def save_model(self, request, obj, form, change):
        """Override save_model to set rate after model save."""
        if form.is_valid():
            super().save_model(request, obj, form, change)
            obj.set_rate_amount(
                form.cleaned_data["rate"],
                form.cleaned_data["start_date"],
                form.cleaned_data["end_date"],
            )


class RateForm(VariableRateAdminForm):
    """RateForm for RateAdmin."""

    class Meta:
        model = Rate
        fields = "__all__"


@admin.register(Rate)
class RateAdmin(VariableRateAdmin):
    """ModelAdmin for Rate."""

    list_display = ("name", "description")
    form = RateForm


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Dislay read only fields on payment."""

    readonly_fields = ("payment_id", "account_string", "account_string_new")
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

    def account_string_new(self, obj):
        """Get new account string."""
        return obj.account_string_new

    payment_id.short_description = _("betalings-ID")
    account_string.short_description = _("kontostreng")
    account_string_new.short_description = _("ny kontostreng")
    payment_schedule_str.short_description = _("betalingsplan")


class TargetGroupForm(forms.ModelForm):
    """Form for TargetGroup to set required_fields_for_case."""

    def __init__(self, *args, **kwargs):
        """__init__ for TargetGroupForm.

        Set initial value for required_fields_for_case.
        """
        super().__init__(*args, **kwargs)
        # Set initial value as a list
        self.initial[
            "required_fields_for_case"
        ] = self.instance.required_fields_for_case

    def required_fields_for_case_choices():
        """Define the choices for the required_fields_for_case field."""
        excluded_fields = ["revision", "target_group"]

        choices = [
            (field.name, field.verbose_name)
            for field in Case._meta.get_fields()
            if field.null
            and hasattr(field, "verbose_name")
            and field.name not in excluded_fields
        ]
        return choices

    required_fields_for_case = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=required_fields_for_case_choices(),
        label=_("Påkrævede felter på sag"),
        required=False,
    )


@admin.register(TargetGroup)
class TargetGroupAdmin(ClassificationAdmin):
    """ModelAdmin for TargetGroup with custom ModelForm."""

    fields = ("name", "required_fields_for_case", "active")
    list_display = (
        "name",
        "active",
    )
    form = TargetGroupForm


@admin.register(Effort)
class EffortAdmin(ClassificationAdmin):
    """ModelAdmin for Effort."""

    filter_horizontal = ("allowed_for_target_groups",)

    list_display = (
        "name",
        "active",
    )


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """Display read only fields on payment schedule."""

    readonly_fields = ("payment_id", "account_string", "account_string_new")
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

    def account_string_new(self, obj):
        """Get new account string."""
        return obj.account_string_new

    account_string.short_description = _("kontostreng")
    account_string_new.short_description = _("ny kontostreng")


@admin.register(Account)
class AccountAdmin(ClassificationAdmin):
    """Display account number (konteringsnummer) as read only field."""

    readonly_fields = ("number",)
    list_display = (
        "main_account_number",
        "active",
    )

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


class SectionInfoInline(ClassificationInline):
    """SectionInfoInline for ActivityDetailsAdmin."""

    model = ActivityDetails.main_activity_for.through
    extra = 0
    verbose_name = _("Tilladt paragraf (for hovedydelse)")
    verbose_name_plural = _("Tilladte paragraffer (for hovedydelse)")


class SupplementaryActivityInline(ClassificationInline):
    """SupplementaryActivityInline for ActivityDetailsAdmin."""

    model = ActivityDetailsSectionProxy
    extra = 0
    verbose_name = _("Tilladt paragraf (for følgeudgift)")
    verbose_name_plural = _("Tilladte paragraffer (for følgeudgift)")


@admin.register(ActivityDetails)
class ActivityDetailsAdmin(ClassificationAdmin):
    """Widgets: Filter_horizontal for many to many links, add search field."""

    filter_horizontal = ("main_activities",)
    search_fields = ("activity_id", "name")
    list_display = (
        "name",
        "activity_id",
        "active",
    )
    exclude = (
        "supplementary_activity_for",
        "main_activity_for",
        "service_providers",
    )
    inlines = (SectionInfoInline, SupplementaryActivityInline)


class MainActivityDetailsInline(ClassificationInline):
    """MainActivityDetailsInline for SectionAdmin."""

    model = ActivityDetails.main_activity_for.through
    extra = 0
    verbose_name = _("Tilladt hovedydelse")
    verbose_name_plural = _("Tilladte hovedydelser")
    ordering = ("activity_details__name",)


class SupplementaryActivityDetailsInline(ClassificationInline):
    """SupplementaryActivityDetailsInline for SectionAdmin."""

    model = ActivityDetailsSectionProxy
    extra = 0
    verbose_name = _("Tilladt følgeudgift")
    verbose_name_plural = _("Tilladte følgeudgifter")
    ordering = ("activitydetails__name",)


@admin.register(Section)
class SectionAdmin(ClassificationAdmin):
    """Add search field."""

    search_fields = ("paragraph", "text")

    list_display = (
        "paragraph",
        "text",
        "list_main_activity_for",
        "list_supplementary_activity_for",
        "active",
    )
    filter_horizontal = ("allowed_for_target_groups", "allowed_for_steps")

    inlines = (
        MainActivityDetailsInline,
        SupplementaryActivityDetailsInline,
    )

    def list_main_activity_for(self, obj):
        """HTML list of main activities for Django admin purposes."""
        return format_html_join(
            "\n",
            '<div><a href="{}">{}</a></div>',
            (
                (reverse("admin:core_activitydetails_change", args=[x.id]), x,)
                for x in obj.main_activities.all()
            ),
        )

    def list_supplementary_activity_for(self, obj):
        """HTML list of supplementary activities for Django admin purposes."""
        return format_html_join(
            "\n",
            '<div><a href="{}">{}</a></div>',
            (
                [
                    (
                        reverse(
                            "admin:core_activitydetails_change", args=[x.id]
                        ),
                        x,
                    )
                    for x in obj.supplementary_activities.all()
                ]
            ),
        )

    list_main_activity_for.short_description = _("Tilladte hovedydelser")
    list_supplementary_activity_for.short_description = _(
        "Tilladte følgeudgifter"
    )


@admin.register(ServiceProvider)
class ServiceProviderAdmin(ClassificationAdmin):
    """Add search fields."""

    search_fields = ("name", "cvr_number")

    list_display = (
        "name",
        "cvr_number",
        "active",
    )


@admin.register(RelatedPerson)
class RelatedPersonAdmin(admin.ModelAdmin):
    """ModelAdmin for RelatedPerson."""

    pass


@admin.register(Municipality)
class MunicipalityAdmin(ClassificationAdmin):
    """ModelAdmin for Municipality."""

    search_fields = ("name",)
    list_display = (
        "name",
        "active",
    )


@admin.register(ApprovalLevel)
class ApprovalLevelAdmin(ClassificationAdmin):
    """ModelAdmin for ApprovalLevel."""

    list_display = (
        "name",
        "active",
    )


class SectionEffortStepProxyInline(ClassificationInline):
    """SectionEffortStepProxyInline for EffortStepAdmin."""

    model = SectionEffortStepProxy
    extra = 0
    verbose_name = _("Tilladt paragraf")
    verbose_name_plural = _("Tilladte paragraffer")


@admin.register(EffortStep)
class EffortStepAdmin(ClassificationAdmin):
    """ModelAdmin for EffortStep."""

    search_fields = (
        "name",
        "number",
    )
    list_display = (
        "name",
        "list_sections",
        "active",
    )

    inlines = (SectionEffortStepProxyInline,)

    def list_sections(self, obj):
        """HTML list of sections for Django admin purposes."""
        return format_html_join(
            "\n",
            '<div><a href="{}">{} - {}</a></div>',
            (
                (
                    reverse("admin:core_section_change", args=[x.id]),
                    x.paragraph,
                    x.text,
                )
                for x in obj.sections.all()
            ),
        )

    list_sections.short_description = _("Tilladte paragraffer")


@admin.register(SchoolDistrict)
class SchoolDistrictAdmin(ClassificationAdmin):
    """ModelAdmin for SchoolDistrict."""

    list_display = (
        "name",
        "active",
    )
