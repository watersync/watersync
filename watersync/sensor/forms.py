import json

from django import forms

import pandas as pd

from watersync.core.config import (
    get_sensor_unit_choices,
    get_variable_choices,
    get_variable_label,
    get_variables_json,
    is_valid_unit_for_variable,
)
from watersync.core.generics.forms import WatersyncForm
from watersync.sensor.models import Deployment, Sensor


class SensorForm(WatersyncForm):
    """Form for creating/editing Sensor objects."""

    title = "Add Sensor"

    class Meta:
        model = Sensor
        fields = ("identifier", "manufacturer", "model", "user")
        widgets = {"user": forms.CheckboxSelectMultiple()}


class DeploymentForm(WatersyncForm):
    """Form for creating/editing sensor deployments.

    Detail forms for specific deployment types (pressure sensor details)
    are handled separately via HTMX and saved in the view's post_save hook.
    """

    title = "Deployment Form"

    type = forms.ChoiceField(
        choices=Deployment.DeploymentTypes.choices,
        label="Type",
        required=True,
        help_text="The type of sensor deployment",
    )

    sensor = forms.ModelChoiceField(
        queryset=Sensor.objects.all(),
        label="Sensor",
        required=True,
    )

    variable = forms.ChoiceField(
        choices=get_variable_choices(),
        label="Variable",
        required=True,
        help_text="The variable being measured",
        widget=forms.Select(attrs={
            "id": "id_variable",
            "onchange": "updateUnitChoices(this.value)",
        })
    )

    unit = forms.ChoiceField(
        choices=[],  # Will be populated by JavaScript based on variable
        label="Unit",
        required=True,
        help_text="Unit of measurement (filtered by selected variable)",
        widget=forms.Select(attrs={"id": "id_unit"})
    )

    class Meta:
        model = Deployment
        fields = ["sensor", "location", "type", "variable", "unit", "started_at", "ended_at"]
        widgets = {
            "started_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ended_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial unit choices based on selected variable (for edit forms)
        if self.instance and self.instance.pk:
            variable = self.instance.variable
            self.fields['unit'].choices = get_sensor_unit_choices(variable)
        elif 'variable' in self.data:
            variable = self.data.get('variable')
            self.fields['unit'].choices = get_sensor_unit_choices(variable)
        else:
            # Default: show all units (JS will filter on client side)
            self.fields['unit'].choices = get_sensor_unit_choices()

    def get_units_json(self):
        """Return JSON mapping of variables to their valid units for JavaScript."""
        return json.dumps(get_variables_json())

    def clean(self):
        """Validate that the unit is valid for the selected variable."""
        cleaned_data = super().clean()
        variable = cleaned_data.get('variable')
        unit = cleaned_data.get('unit')

        if variable and unit:
            if not is_valid_unit_for_variable(variable, unit):
                self.add_error('unit', f"Unit '{unit}' is not valid for '{get_variable_label(variable)}'.")

        return cleaned_data



class SensorRecordForm(forms.Form):
    """Form for uploading sensor data with a time zone selection."""

    csv_file = forms.FileField(help_text="Upload a CSV file")
    # time_zone = forms.TypedChoiceField(
    #     choices=[(tz, tz) for tz in sorted(zoneinfo.available_timezones())],
    #     coerce=str,
    #     initial="Europe/Belgium"
    # )

    def clean_csv_file(self):
        # Get the cleaned data from the form fields
        csv_file = self.cleaned_data["csv_file"]
        # time_zone_str = self.cleaned_data['time_zone']

        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            raise forms.ValidationError(f"Error parsing CSV file: {e!s}")

        required_columns = ["timestamp", "value", "unit", "type"]
        for col in required_columns:
            if col not in df.columns:
                raise forms.ValidationError(f"Missing required column: {col}")

        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
        except Exception as e:
            raise forms.ValidationError(f"Error processing timestamps: {e!s}")

        return df
