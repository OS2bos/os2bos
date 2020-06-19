# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Proxy models for customizing the django-admin."""

from django.utils.translation import gettext

from core.models import Section, ActivityDetails, HistoricalRatePerDate


class SectionEffortStepProxy(Section.allowed_for_steps.through):
    """Proxy model for the allowed_for_steps (EffortStep) m2m field on Section.

    We use a proxy so we can override __str__ and m2m verbose_name for use in
    django admin without an explicit through model.
    """

    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.section.paragraph} {self.section.text}"


# Set the verbose_name of the 'section' foreign key for use in django admin.
SectionEffortStepProxy._meta.get_field("section").verbose_name = gettext(
    "paragraf"
)


class ActivityDetailsSectionProxy(
    ActivityDetails.supplementary_activity_for.through
):
    """
    Proxy model for supplementary_activity_for (Section) on ActivityDetails.

    We use a proxy model so we can override __str__ and m2m verbose_name for
    use in django admin without an explicit through model.
    """

    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.activitydetails} - {self.section}"


# Set the verbose_name of the 'section' foreign key for use in django admin.
ActivityDetailsSectionProxy._meta.get_field("section").verbose_name = gettext(
    "paragraf"
)

# Set the verbose_name of the 'activitydetails' foreign key for use in
# django admin.
ActivityDetailsSectionProxy._meta.get_field(
    "activitydetails"
).verbose_name = gettext("aktivitetsdetalje")


class HistoricalRatePerDateProxy(HistoricalRatePerDate):
    """
    Proxy model for HistoricalRatePerDate.

    We use a proxy model so we can override __str__ and the fields verbose_name
    for use in django admin.
    """

    class Meta:
        proxy = True

    def __str__(self):
        return f"{self.rate} - {self.start_date} - {self.end_date}"


# Set the verbose_name of the 'history_date' foreign key
# for use in django admin.
HistoricalRatePerDateProxy._meta.get_field(
    "history_date"
).verbose_name = gettext("historik dato")
# Set the verbose_name of the 'history_user' foreign key
# for use in django admin.
HistoricalRatePerDateProxy._meta.get_field(
    "history_user"
).verbose_name = gettext("historik bruger")
# Set the verbose_name of the 'history_type' foreign key
# for use in django admin.
HistoricalRatePerDateProxy._meta.get_field(
    "history_type"
).verbose_name = gettext("historik type")
