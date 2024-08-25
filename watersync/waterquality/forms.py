from watersync.waterquality.models import Sample, Measurement
from django import forms
from django.forms import Textarea
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Field
import pandas as pd


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ('detail', )
        widgets = {
            'detail': Textarea(attrs={'rows': 5, 'cols': 40, 'placeholder': 'Enter JSON data here'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save sensor'))

        # Custom layout with Crispy Forms to structure the form
        self.helper.layout = Layout(
            Fieldset(
                'Details about the sample',
                Field('detail', css_class='json-field'),
            )
        )


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ('property', 'value', 'unit', 'detail')
        widgets = {
            'detail': Textarea(attrs={'rows': 5, 'cols': 40, 'placeholder': 'Enter JSON data here'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save sensor'))

        # Custom layout with Crispy Forms to structure the form
        self.helper.layout = Layout(
            Fieldset(
                'Details about the sample',
                Field('detail', css_class='json-field'),
            )
        )
