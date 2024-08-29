from watersync.waterquality.models import Sample, Measurement
from django import forms
from django.forms import HiddenInput, DateTimeInput
from django.utils import timezone


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ('timestamp', 'detail', )
        widgets = {
            'timestamp': DateTimeInput(attrs={'type': 'datetime-local'}),
            'detail': HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super(SampleForm, self).__init__(*args, **kwargs)
        if 'initial' not in kwargs:
            self.fields['timestamp'].initial = timezone.now()


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ('property', 'value', 'unit', 'detail')
        widgets = {
            'detail': HiddenInput()
        }
