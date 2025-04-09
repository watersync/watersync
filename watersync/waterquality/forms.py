from django import forms
from django.forms import DateInput, DateTimeInput, HiddenInput, Textarea

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
            "date",
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
        fields = ("sample", "parameter", "value", "unit", "measured_on", "description")
        widgets = {
            "measured_on": DateInput(attrs={"type": "date"}),
        }


class MeasurementBulkForm(forms.Form):
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
            if len(fields) != 4:
                msg = "Each line must contain exactly 4 fields."
                raise forms.ValidationError(msg)

            parameter, value, unit, measured_on = fields
            try:
                value = float(value)
            except ValueError:
                msg = f"Value '{value}' is not a valid number."
                raise forms.ValidationError(msg)

            cleaned_data.append(
                {
                    "parameter": parameter.strip(),
                    "value": value,
                    "unit": unit.strip(),
                    "measured_on": measured_on.strip(),
                }
            )

        return cleaned_data  # Return after processing all lines
