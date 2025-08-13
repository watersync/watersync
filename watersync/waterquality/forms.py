from django import forms
from django.forms import Textarea

from watersync.waterquality.models import Measurement, Sample

from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.conf import settings


class SampleForm(forms.ModelForm):
    title = "Add Sample"
    measured_on = forms.DateField(
        label="Measured On",
        widget=DatePickerInput(
            attrs={"placeholder": "Select date", "autocomplete": "off"},
            format="%Y-%m-%d",
        ),
        help_text="The date when the sample was analysed.",
    )
    
    class Meta:
        model = Sample
        fields = (
            "location",
            "fieldwork",
            "measured_on",
            "protocol",
            "parameter_group",
            "container_type",
            "volume_collected",
            "replica_number",
            "description",
        )


class MeasurementForm(forms.ModelForm):
    title = "Add Measurement"

    # Simple, clean fields for measurement input
    value = forms.DecimalField(
        max_digits=10,
        decimal_places=4,
        label="Measurement Value",
        help_text="Enter the numeric measurement value",
        required=True
    )
    unit = forms.CharField(
        max_length=50,
        label="Unit",
        help_text="Enter the unit (e.g., mg/L, NTU, pH_unit, CFU/100mL, °C)",
        required=True
    )
    detection_limit = forms.DecimalField(
        max_digits=10,
        decimal_places=4,
        required=False,
        label="Detection Limit (optional)",
        help_text="Optional detection limit in the same unit as the measurement"
    )

    class Meta:
        model = Measurement
        fields = ("sample", "parameter")

    def clean(self):
        cleaned_data = super().clean()

        value = cleaned_data.get("value")
        unit = cleaned_data.get("unit")

        # Require both value and unit
        if value is None or not unit:
            raise forms.ValidationError("Both value and unit are required.")

        # Validate unit with Pint
        try:
            settings.UREG.Quantity(1.0, unit)
        except Exception as exc:
            raise forms.ValidationError(f"Invalid unit '{unit}'.") from exc

        # Optional detection limit validation
        detection_limit = cleaned_data.get("detection_limit")
        if detection_limit is not None and detection_limit < 0:
            raise forms.ValidationError("Detection limit must be a non-negative number.")

        # Populate instance JSON-backed fields BEFORE model validation runs
        self.instance.measurement = settings.UREG.Quantity(float(value), unit)
        if detection_limit is not None:
            self.instance.detection_limit = settings.UREG.Quantity(float(detection_limit), unit)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        value = self.cleaned_data.get("value")
        unit = self.cleaned_data.get("unit")
        detection_limit = self.cleaned_data.get("detection_limit")

        # Redundant safety: ensure measurement/detection limit still set
        if value is not None and unit:
            instance.measurement = settings.UREG.Quantity(float(value), unit)
        if detection_limit is not None and unit:
            instance.detection_limit = settings.UREG.Quantity(float(detection_limit), unit)

        if commit:
            instance.save()
        
        return instance


class MeasurementBulkForm(forms.Form):

    bulk = forms.CharField(widget=forms.HiddenInput(), initial="true", required=False)
    sample = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        label="Sample",
        help_text="Select the sample to which these measurements belong.",
    )
    # unit = forms.ModelChoiceField(
    #     queryset=Unit.objects.all(),
    #     label="Unit",
    #     help_text="Select the unit of measurement",
    #     required=False,
    # )
    data = forms.CharField(
        label="Data",
        help_text="Paste tab-separated or comma-separated data with the following columns: "
        "parameter, value",
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
