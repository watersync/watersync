from django import forms
from django.conf import settings
from django.forms import Textarea

from bootstrap_datepicker_plus.widgets import DatePickerInput

from watersync.core.config import (
    get_all_wq_unit_choices,
    get_parameter_choices,
    get_parameter_group_choices,
    get_parameters_json,
    is_valid_unit_for_parameter,
)
from watersync.core.generics.forms import WatersyncBulkForm, WatersyncForm
from watersync.waterquality.models import Measurement, Sample
from watersync.waterquality.utils import parse_bulk_file, parse_bulk_measurement_data
from watersync.waterquality.validators import (
    check_duplicate_measurements,
    get_allowed_parameters_for_sample,
)


class SampleForm(WatersyncForm):
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


class MeasurementForm(WatersyncForm):
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


class MeasurementRowForm(forms.Form):
    """Single row form for the formset approach."""
    
    parameter = forms.ChoiceField(
        choices=lambda: get_parameter_choices(),
        required=False,
    )
    value = forms.DecimalField(
        max_digits=20,
        decimal_places=10,
        required=False,
    )
    unit = forms.ChoiceField(
        choices=lambda: get_all_wq_unit_choices(),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        parameter = cleaned_data.get("parameter")
        value = cleaned_data.get("value")
        unit = cleaned_data.get("unit")
        
        # If any field is filled, all must be filled
        has_data = any([parameter, value is not None, unit])
        if has_data:
            if not parameter:
                raise forms.ValidationError("Parameter is required")
            if value is None:
                raise forms.ValidationError("Value is required")
            if not unit:
                raise forms.ValidationError("Unit is required")
            # Validate unit for parameter
            if not is_valid_unit_for_parameter(parameter, unit):
                raise forms.ValidationError(
                    f"Unit '{unit}' is not valid for parameter '{parameter}'"
                )
        return cleaned_data


# Create formset for multiple measurement rows
from django.forms import formset_factory

MeasurementRowFormSet = formset_factory(MeasurementRowForm, extra=5, can_delete=False)


class MeasurementBulkForm(WatersyncBulkForm):
    """Form for bulk adding measurements (paste/file/formset)."""

    title = "Bulk Add Measurements"
    
    # Override input mode choices if needed
    INPUT_MODE_CHOICES = [
        ("paste", "Paste Data"),
        ("formset", "Manual Entry"),  # Custom label
        ("file", "Upload File"),
    ]
    
    input_mode = forms.ChoiceField(
        choices=INPUT_MODE_CHOICES,
        initial="paste",
        widget=forms.HiddenInput(),
        required=False,
    )
    
    sample = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        label="Sample",
        help_text="Select the sample to which these measurements belong.",
    )
    
    data = forms.CharField(
        label="Paste Data",
        help_text="Paste tab-separated or comma-separated data with columns: parameter, value, unit.",
        required=False,
        widget=Textarea(attrs={"rows": 8}),
    )
    
    file = forms.FileField(
        label="Upload File",
        help_text="Upload a CSV or Excel file with columns: parameter, value, unit",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        input_mode = cleaned_data.get("input_mode", "paste")
        sample = cleaned_data.get("sample")
        
        if not sample:
            raise forms.ValidationError("Please select a sample.")
        
        processed_data = []
        
        if input_mode == "paste":
            data_str = cleaned_data.get("data", "")
            if data_str:
                rows = parse_bulk_measurement_data(data_str)
                invalid_rows = [r for r in rows if not r["is_valid"]]
                if invalid_rows:
                    errors = [f"Line {r['line_num']}: {r['error']}" for r in invalid_rows]
                    raise forms.ValidationError(errors)
                
                for row in rows:
                    processed_data.append({
                        "sample": sample,
                        "parameter": row["parameter"],
                        "value": float(row["value"]),
                        "unit": row["unit"],
                    })
        
        elif input_mode == "file":
            uploaded_file = cleaned_data.get("file")
            if uploaded_file:
                rows, error = parse_bulk_file(uploaded_file)
                if error:
                    raise forms.ValidationError(error)
                
                invalid_rows = [r for r in rows if not r["is_valid"]]
                if invalid_rows:
                    errors = [f"Line {r['line_num']}: {r['error']}" for r in invalid_rows]
                    raise forms.ValidationError(errors)
                
                for row in rows:
                    processed_data.append({
                        "sample": sample,
                        "parameter": row["parameter"],
                        "value": float(row["value"]),
                        "unit": row["unit"],
                    })
        
        if not processed_data and input_mode != "formset":
            raise forms.ValidationError("No valid measurement data provided.")
        
        # Validate parameters and check for duplicates
        if processed_data:
            allowed_params = get_allowed_parameters_for_sample(sample)
            invalid_params = [
                d["parameter"] for d in processed_data 
                if d["parameter"] not in allowed_params
            ]
            if invalid_params:
                raise forms.ValidationError(
                    f"These parameters are not in the sample's group ({sample.parameter_group}): {', '.join(invalid_params)}"
                )
            
            duplicates = check_duplicate_measurements(
                sample, 
                [d["parameter"] for d in processed_data]
            )
            if duplicates:
                raise forms.ValidationError(
                    f"Measurements for these parameters already exist: {', '.join(duplicates)}"
                )
            
        cleaned_data["processed_data"] = processed_data
        return cleaned_data