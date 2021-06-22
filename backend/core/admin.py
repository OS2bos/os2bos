# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Customize django-admin interface."""

import datetime
import io

from django.contrib import admin
from django.contrib.messages import constants as messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape, mark_safe, format_html_join
from django.urls import reverse
from django.db.models import F
from django.db import transaction
from django import forms
from django.urls import path
from django.shortcuts import redirect

from simple_history.admin import SimpleHistoryAdmin

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
    Price,
    PaymentDateExclusion,
    AccountAliasMapping,
    InternalPaymentRecipient,
    ActivityCategory,
)
from core.proxies import (
    SectionEffortStepProxy,
    ActivityDetailsSectionProxy,
    HistoricalRatePerDateProxy,
)

from core.utils import parse_account_alias_mapping_data_from_csv_string

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

    readonly_fields = (
        "account_number",
        "account_alias",
    )

    def account_number(self, obj):
        """Get account number."""
        return obj.account_number

    def account_alias(self, obj):
        """Get account alias."""
        return obj.account_alias

    account_number.short_description = _("kontonummer")
    account_alias.short_description = _("kontoalias")


class RatePerDateInline(ClassificationInline):
    """RatePerDateInline for VariablerateAdmin."""

    model = RatePerDate

    readonly_fields = ["rate", "start_date", "end_date"]
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        """Override has_add_permission for RatePerDateInline."""
        return False


class HistoricalRatePerDateInline(ClassificationInline):
    """HistoricalRatePerDateInline for VariablerateAdmin."""

    model = HistoricalRatePerDateProxy
    verbose_name = _("Historisk takst for datoer")
    verbose_name_plural = _("Historiske takster for datoer")
    classes = ("collapse",)

    exclude = ("history_change_reason",)

    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        """Override has_add_permission for HistoricalRatePerDateInline."""
        return False

    def has_change_permission(self, request, obj=None):
        """Override has_change_permission for HistoricalRatePerDateInline."""
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

    def __init__(self, *args, **kwargs):
        """__init__ for VariableRateAdminForm.

        Set initial value for rate and start_date.
        """
        super().__init__(*args, **kwargs)
        # Find RatePerDate ordered by start_date.
        latest = self.instance.rates_per_date.order_by(
            F("start_date").asc(nulls_first=True)
        ).last()
        # If any object exists set the initial rate and start_date.
        if latest:
            self.initial["start_date"] = latest.start_date
            self.initial["rate"] = latest.rate


class VariableRateAdmin(ClassificationAdmin):
    """ModelAdmin for VariableRate subclasses."""

    inlines = [RatePerDateInline, HistoricalRatePerDateInline]
    form = VariableRateAdminForm

    def save_model(self, request, obj, form, change):
        """Override save_model to set rate after model save."""
        if form.is_valid() and form.has_changed():
            super().save_model(request, obj, form, change)
            obj.set_rate_amount(
                form.cleaned_data["rate"], form.cleaned_data["start_date"]
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
    exclude = ("needs_recalculation",)


class PriceForm(VariableRateAdminForm):
    """PriceForm for PriceAdmin."""

    class Meta:
        Model = Price
        fields = "__all__"


@admin.register(Price)
class PriceAdmin(VariableRateAdmin):
    """ModelAdmin for Price."""

    readonly_fields = ("payment_schedule",)
    list_display = ("payment_schedule",)
    form = PriceForm


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    """ModelAdmin for Payment."""

    readonly_fields = (
        "payment_id",
        "account_string",
        "account_alias",
    )
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

    def account_alias(self, obj):
        """Get account alias."""
        return obj.account_alias

    payment_id.short_description = _("betalings-ID")
    account_string.short_description = _("kontostreng")
    account_alias.short_description = _("kontoalias")
    payment_schedule_str.short_description = _("betalingsplan")


class TargetGroupForm(forms.ModelForm):
    """Form for TargetGroup to set required_fields_for_case."""

    def __init__(self, *args, **kwargs):
        """__init__ for TargetGroupForm.

        Set initial value for required_fields_for_case.
        """
        super().__init__(*args, **kwargs)
        # Set initial value as comma-separated string.
        self.initial[
            "required_fields_for_case"
        ] = self.instance.required_fields_for_case.split(",")

    def clean_required_fields_for_case(self):
        """Clean required_fields_for_case as comma-separated string."""
        cleaned = ",".join(self.cleaned_data["required_fields_for_case"])
        return cleaned

    def required_fields_for_case_choices():
        """Define the choices for the required_fields_for_case field."""
        excluded_fields = ["revision", "target_group", "created", "modified"]

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
    list_display = ("name", "active")
    form = TargetGroupForm


@admin.register(Effort)
class EffortAdmin(ClassificationAdmin):
    """ModelAdmin for Effort."""

    filter_horizontal = ("allowed_for_target_groups",)

    list_display = ("name", "active")


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    """Display read only fields on payment schedule."""

    readonly_fields = (
        "payment_id",
        "account_string",
        "account_alias",
        "price_per_unit",
    )
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

    def account_alias(self, obj):
        """Get account alias."""
        return obj.account_alias

    account_string.short_description = _("kontostreng")
    account_alias.short_description = _("kontoalias")


@admin.register(PaymentMethodDetails)
class PaymentMethodDetails(admin.ModelAdmin):
    """ModelAdmin for PaymentMethodDetails."""

    pass


@admin.register(Team)
class TeamAdmin(ClassificationAdmin):
    """ModelAdmin for Team."""

    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Add team to user admin interface."""

    fieldsets = (
        ("Organisation", {"fields": ("team",)}),
    ) + BaseUserAdmin.fieldsets

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
    list_display = ("name", "activity_id", "active")
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

    inlines = (MainActivityDetailsInline, SupplementaryActivityDetailsInline)

    def list_main_activity_for(self, obj):
        """HTML list of main activities for Django admin purposes."""
        return format_html_join(
            "\n",
            '<div><a href="{}">{}</a></div>',
            (
                (reverse("admin:core_activitydetails_change", args=[x.id]), x)
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

    list_display = ("name", "cvr_number", "active")


@admin.register(RelatedPerson)
class RelatedPersonAdmin(admin.ModelAdmin):
    """ModelAdmin for RelatedPerson."""

    pass


@admin.register(Municipality)
class MunicipalityAdmin(ClassificationAdmin):
    """ModelAdmin for Municipality."""

    search_fields = ("name",)
    list_display = ("name", "active")


@admin.register(ApprovalLevel)
class ApprovalLevelAdmin(ClassificationAdmin):
    """ModelAdmin for ApprovalLevel."""

    list_display = ("name", "active")


class SectionEffortStepProxyInline(ClassificationInline):
    """SectionEffortStepProxyInline for EffortStepAdmin."""

    model = SectionEffortStepProxy
    extra = 0
    verbose_name = _("Tilladt paragraf")
    verbose_name_plural = _("Tilladte paragraffer")


@admin.register(EffortStep)
class EffortStepAdmin(ClassificationAdmin):
    """ModelAdmin for EffortStep."""

    search_fields = ("name", "number")
    list_display = ("name", "list_sections", "active")

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


@admin.register(InternalPaymentRecipient)
class InternalPaymentRecipientAdmin(ClassificationAdmin):
    """ModelAdmin for InternalPaymentRecipient."""

    list_display = ("name",)


@admin.register(SchoolDistrict)
class SchoolDistrictAdmin(ClassificationAdmin):
    """ModelAdmin for SchoolDistrict."""

    list_display = ("name", "active")


@admin.register(PaymentDateExclusion)
class PaymentDateExclusionAdmin(ClassificationAdmin):
    """ModelAdmin for PaymentDateExclusion."""

    search_fields = ("date",)

    list_filter = (("date", admin.DateFieldListFilter),)

    list_display = ("date", "weekday")

    def weekday(self, obj):
        """Return translated weekday of date."""
        return _(obj.date.strftime("%A"))

    weekday.short_description = _("Ugedag")


@admin.register(SectionInfo)
class SectionInfoAdmin(ClassificationAdmin):
    """ModelAdmin for SectionInfo."""

    list_display = (
        "activity_details",
        "section",
        "kle_number",
        "activity_category",
    )


class AccountAliasMappingCSVFileUploadForm(forms.Form):
    """CSV Upload form for AccountAliasMappingAdmin."""

    csv_file = forms.FileField(required=True, label=_("vælg venligst en fil"))


@admin.register(AccountAliasMapping)
class AccountAliasMappingAdmin(ClassificationAdmin):
    """ModelAdmin for AccountAlias."""

    change_list_template = "core/admin/accountaliasmapping/change_list.html"

    list_display = ("main_account_number", "activity_number", "alias")

    def get_urls(self):
        """Override get_urls adding upload_url path."""
        urls = super().get_urls()
        my_urls = [path("upload_csv/", self.upload_csv, name="upload_csv")]
        return my_urls + urls

    urls = property(get_urls)

    def changelist_view(self, *args, **kwargs):
        """Override changelist_view adding form to context."""
        view = super().changelist_view(*args, **kwargs)
        view.context_data[
            "submit_csv_form"
        ] = AccountAliasMappingCSVFileUploadForm
        return view

    def upload_csv(self, request):
        """Handle the uploaded CSV file."""
        if not request.method == "POST":
            return redirect("..")

        form = AccountAliasMappingCSVFileUploadForm(
            request.POST, request.FILES
        )
        if not form.is_valid():
            self.message_user(
                request,
                _("Der var en fejl i formen: {}".format(form.errors)),
                level=messages.ERROR,
            )
            return redirect("..")

        if not request.FILES["csv_file"].name.endswith("csv"):
            self.message_user(
                request,
                _(
                    "Ukorrekt filtype: {}".format(
                        request.FILES["csv_file"].name.split(".")[1]
                    )
                ),
                level=messages.ERROR,
            )
            return redirect("..")

        try:
            decoded_file = request.FILES["csv_file"].read().decode("utf-8")
        except UnicodeDecodeError as e:
            self.message_user(
                request,
                _(
                    "Fejl ved afkodning af filen: {}".format(e),
                ),
                level=messages.ERROR,
            )
            return redirect("..")

        # We can delete the existing AccountAliasMapping
        # objects and create new ones.
        io_string = io.StringIO(decoded_file)
        with transaction.atomic():
            account_alias_data = (
                parse_account_alias_mapping_data_from_csv_string(io_string)
            )
            account_alias_objs = [
                AccountAliasMapping(
                    main_account_number=main_account_number,
                    activity_number=activity_number,
                    alias=alias,
                )
                for (
                    main_account_number,
                    activity_number,
                    alias,
                ) in account_alias_data
            ]
            if account_alias_objs:
                AccountAliasMapping.objects.all().delete()
                objects = AccountAliasMapping.objects.bulk_create(
                    account_alias_objs
                )
                self.message_user(
                    request,
                    _(
                        "{} kontoalias objekter blev oprettet.".format(
                            len(objects)
                        ),
                    ),
                    level=messages.INFO,
                )
            else:
                self.message_user(
                    request,
                    _("Ingen kontoalias objekter blev oprettet."),
                    level=messages.ERROR,
                )
        return redirect("..")


class SectionInfoActivityCategoryInline(ClassificationInline):
    """SectionInfoInline for ActivityDetailsAdmin."""

    model = SectionInfo
    extra = 0


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(ClassificationAdmin):
    """ModelAdmin for ActivityCategory."""

    list_display = ("category_id", "name")
    inlines = [SectionInfoActivityCategoryInline]
