from watersync.core.models import Location
from django import forms
from django.forms import Textarea
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Field
from .models import Sensor, Deployment, SensorRecord
import pandas as pd


class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ('identifier', 'user', 'detail')


class DeploymentForm(forms.ModelForm):
    class Meta:
        model = Deployment
        fields = ['sensor', 'location', 'decommissioned_at', 'detail']
        widgets = {
            'decommissioned_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        # Get project_pk from kwargs
        project_pk = kwargs.pop('project_pk', None)
        super().__init__(*args, **kwargs)
        if project_pk:
            # Filter the location field to only show locations within the project
            self.fields['location'].queryset = Location.objects.filter(
                project__pk=project_pk)
            # Filter the sensor field to only show available sensors
            self.fields['sensor'].queryset = Sensor.objects.filter(
                available=True)


class SensorRecordForm(forms.Form):
    csv_file = forms.FileField(help_text="Upload a CSV file")

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        try:
            # Attempt to read the CSV file with pandas
            df = pd.read_csv(csv_file)
        except Exception as e:
            raise forms.ValidationError(f"Error parsing CSV file: {str(e)}")

        # Check if required columns are present
        required_columns = ['timestamp', 'value', 'unit', 'type']
        for col in required_columns:
            if col not in df.columns:
                raise forms.ValidationError(f"Missing required column: {col}")

        return df
