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

    def clean_data(self):
        data = self.cleaned_data["data"]
        if not isinstance(data, str):
            return data

        cleaned_data = []
        lines = data.splitlines()
        for line in lines:
            if not line.strip():
                continue

            fields = line.split("\t") if "\t" in line else line.split(",")
            if len(fields) != 2:
                msg = "Each line must contain exactly 2 fields."
                raise forms.ValidationError(msg)

            parameter, value = fields
            
            try:
                value = float(value)
            except ValueError:
                msg = f"Value '{value}' is not a valid number."
                raise forms.ValidationError(msg)

            cleaned_data.append(
                {
                    "sample": self.cleaned_data["sample"],
                    "unit": self.cleaned_data["unit"] or self.cleaned_data["unit"].strip(),
                    "parameter": parameter.strip(),
                    "value": value,
                }
            )

        return cleaned_data  # Return after processing all lines
