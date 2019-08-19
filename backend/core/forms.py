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
