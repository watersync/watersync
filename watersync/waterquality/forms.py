from django import forms
from django.forms import Textarea
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div

from watersync.waterquality.models import Measurement, Protocol, Sample


class ProtocolForm(forms.ModelForm):
    title = "Add Protocol"
    class Meta:
        model = Protocol
        fields = [
            "method_name",
            "sample_collection",
            "sample_preservation",
            "sample_storage",
            "analytical_method",
            "data_postprocessing",
            "standard_reference",
            "description",
        ]


class SampleForm(forms.ModelForm):
    title = "Add Sample"
    class Meta:
        model = Sample
        fields = (
            "location",
            "collected_at",
            "measured_at",
            "location_visit",
            "protocol",
            "target_parameters",
            "container_type",
            "volume_collected",
            "replica_number",
            "description",
        )


class MeasurementForm(forms.ModelForm):
    title = "Add Measurement"

    class Meta:
        model = Measurement
        fields = ("sample", "parameter", "value", "unit")


class MeasurementBulkForm(forms.Form):

    bulk = forms.CharField(widget=forms.HiddenInput(), initial="true", required=False)
    sample = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        label="Sample",
        help_text="Select the sample to which these measurements belong.",
    )
    unit = forms.CharField(
        label="Unit",
        help_text="Enter the unit of measurement (e.g., mg/L, µg/L).",
        max_length=10,
        required=False,
    )
    data = forms.CharField(
        label="Data",
        help_text="Paste tab-separated or comma-separated data with the following columns: "
        "parameter, value, unit, measured_on",
        widget=Textarea(attrs={"rows": 5}),
    )

    def clean(self):
        cleaned_data = super().clean()
        
        # Only process if data field is present and valid
        if 'data' in cleaned_data and isinstance(cleaned_data['data'], str):
            data_str = cleaned_data['data']
            processed_data = []
            
            lines = data_str.splitlines()
            for line in lines:
                if not line.strip():
                    continue

                fields = line.split("\t") if "\t" in line else line.split(",")
                if len(fields) != 2:
                    raise forms.ValidationError("Each line must contain exactly 2 fields: parameter and value.")

                parameter, value = fields
                
                try:
                    value = float(value)
                except ValueError:
                    raise forms.ValidationError(f"Value '{value}' is not a valid number.")

                processed_data.append({
                    "sample": cleaned_data.get('sample'),
                    "unit": cleaned_data.get('unit', ''),
                    "parameter": parameter.strip(),
                    "value": value,
                })
            
            # Store the processed data back in cleaned_data
            cleaned_data['processed_data'] = processed_data
            
        return cleaned_data
