# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import effort_steps_choices


class SectionForm(forms.ModelForm):
    allowed_for_steps = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=effort_steps_choices,
        required=False,
        label=_("Tilladt for trin i indsatstrappen"),
    )
