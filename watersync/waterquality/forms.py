from bootstrap_datepicker_plus.widgets import DatePickerInput
from django import forms
from django.conf import settings
from django.forms import Textarea

from watersync.core.config import (
    get_all_wq_unit_choices,
    get_parameter_choices,
    get_parameter_default_unit,
    get_parameter_group_choices,
    get_parameters_json,
    get_wq_unit_choices,
    is_valid_unit_for_parameter,
)
from watersync.waterquality.models import Measurement, Sample


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
    parameter_group = forms.ChoiceField(
        choices=lambda: get_parameter_group_choices(),
        label="Target Parameters",
        help_text="Select the parameter group targeted for analysis",
    )

    class Meta:
        model = Sample
        fields = (
            "location",
            "fieldwork",
            "measured_on",
            "protocol",
            "parameter_group",
            "field_sample",
            "container_type",
            "volume_collected",
            "replica_number",
            "description",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter field_sample to only show FIELD parameter samples
        field_sample_qs = Sample.objects.filter(parameter_group="FIELD")
        
        # Further filter by location if available (from initial data or instance)
        location = None
        if self.instance.pk and self.instance.location:
            location = self.instance.location
        elif self.initial.get("location"):
            location = self.initial["location"]
        
        if location:
            field_sample_qs = field_sample_qs.filter(location=location)
        
        # Further filter by fieldwork if available
        fieldwork = None
        if self.instance.pk and self.instance.fieldwork:
            fieldwork = self.instance.fieldwork
        elif self.initial.get("fieldwork"):
            fieldwork = self.initial["fieldwork"]
            
        if fieldwork:
            field_sample_qs = field_sample_qs.filter(fieldwork=fieldwork)
        
        self.fields["field_sample"].queryset = field_sample_qs.order_by("-fieldwork__date")
        self.fields["field_sample"].label = "Field Measurement Sample"
        self.fields["field_sample"].help_text = (
            "Link to the field measurements (PARAMS) sample taken at the same time"
        )


class MeasurementForm(forms.ModelForm):
    title = "Add Measurement"

    parameter = forms.ChoiceField(
        choices=lambda: get_parameter_choices(),
        label="Parameter",
        help_text="Select the parameter measured",
    )
    unit = forms.ChoiceField(
        choices=lambda: get_all_wq_unit_choices(),
        label="Unit",
        help_text="Select the unit of measurement",
    )

    class Meta:
        model = Measurement
        fields = ("sample", "parameter", "value", "unit", "detection_limit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing existing instance, set initial values
        if self.instance.pk:
            self.fields["parameter"].initial = self.instance.parameter
            self.fields["unit"].initial = self.instance.unit

        # Pass parameters config to template for JavaScript filtering
        self.parameters_config = get_parameters_json()

    def clean(self):
        cleaned_data = super().clean()

        parameter = cleaned_data.get("parameter")
        unit = cleaned_data.get("unit")
        value = cleaned_data.get("value")

        # Validate unit is valid for the selected parameter
        if parameter and unit:
            if not is_valid_unit_for_parameter(parameter, unit):
                raise forms.ValidationError({
                    "unit": f"'{unit}' is not a valid unit for this parameter"
                })

        # Validate unit with Pint
        if unit:
            try:
                settings.UREG.Quantity(1.0, unit)
            except Exception as exc:
                raise forms.ValidationError({"unit": f"Invalid unit '{unit}'."}) from exc

        # Optional detection limit validation
        detection_limit = cleaned_data.get("detection_limit")
        if detection_limit is not None and detection_limit < 0:
            raise forms.ValidationError({
                "detection_limit": "Detection limit must be a non-negative number."
            })

        return cleaned_data


class MeasurementBulkForm(forms.Form):
    """Form for bulk adding measurements from pasted data.

    Expected data format: parameter, value, unit (tab or comma separated)
    """

    bulk = forms.CharField(widget=forms.HiddenInput(), initial="true", required=False)
    sample = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        label="Sample",
        help_text="Select the sample to which these measurements belong.",
    )
    data = forms.CharField(
        label="Data",
        help_text="Paste tab-separated or comma-separated data with columns: "
        "parameter, value, unit",
        widget=Textarea(attrs={"rows": 5}),
    )

    def clean(self):
        cleaned_data = super().clean()

        # Only process if data field is present and valid
        if "data" in cleaned_data and isinstance(cleaned_data["data"], str):
            data_str = cleaned_data["data"]
            processed_data = []

            lines = data_str.splitlines()
            for i, line in enumerate(lines, 1):
                if not line.strip():
                    continue

                fields = line.split("\t") if "\t" in line else line.split(",")
                if len(fields) != 3:
                    raise forms.ValidationError(
                        f"Line {i}: Expected 3 fields (parameter, value, unit), got {len(fields)}."
                    )

                parameter, value, unit = [f.strip() for f in fields]

                # Validate parameter
                valid_params = [k for k, _ in get_parameter_choices()]
                if parameter not in valid_params:
                    raise forms.ValidationError(
                        f"Line {i}: Unknown parameter '{parameter}'."
                    )

                # Validate value
                try:
                    value = float(value)
                except ValueError:
                    raise forms.ValidationError(
                        f"Line {i}: Value '{value}' is not a valid number."
                    )

                # Validate unit for parameter
                if not is_valid_unit_for_parameter(parameter, unit):
                    raise forms.ValidationError(
                        f"Line {i}: Unit '{unit}' is not valid for parameter '{parameter}'."
                    )

                processed_data.append({
                    "sample": cleaned_data.get("sample"),
                    "parameter": parameter,
                    "value": value,
                    "unit": unit,
                })

            # Store the processed data back in cleaned_data
            cleaned_data["processed_data"] = processed_data

        return cleaned_data
