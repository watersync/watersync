import pandas as pd
from django import forms
from django.forms import HiddenInput

from watersync.core.generics.forms import FormWithDetailMixin
from watersync.sensor.models import Deployment, Sensor, SensorVariable


class SensorVariableForm(forms.ModelForm):
    title = "Add Sensor Variable"

    class Meta:
        model = SensorVariable
        fields = ["name", "code", "description"]


class SensorDetailForm(forms.Form):
    """Form for additional details about the sensor."""

    # Add any additional fields you need for the sensor detail
    # For example, if you want to add a field for the sensor's model:
    model = forms.CharField(
        label="Sensor Model",
        max_length=100,
        required=False,
        help_text="Optional: Enter the model of the sensor.",
    )
    manufacturer = forms.CharField(
        label="Manufacturer",
        max_length=100,
        required=False,
        help_text="Optional: Enter the manufacturer of the sensor.",
    )

class SensorForm(FormWithDetailMixin):
    title = "Add Sensor"
    type = forms.ChoiceField(
        choices=Sensor.SENSOR_TYPE_CHOICES,
        required=True,
        label="Type",
        widget=forms.ChoiceField.widget(
            attrs={
                "hx-trigger": "change, revealed",
                "hx-target": "#detail_form",
                "hx-swap": "innerHTML",
            }
        ),
    )
    detail_forms = {
        "vented": SensorDetailForm,
        "unvented": SensorDetailForm,
        "other": SensorDetailForm,
    }

    class Meta:
        model = Sensor
        fields = ("identifier", "type", "user", "detail", "available")
        widgets = {"detail": HiddenInput(), "user": forms.CheckboxSelectMultiple()}


class DeploymentVentedDetailForm(forms.Form):
    """Information necessary for further processing of data from deployments of
    vented sensors."""

    rope_length = forms.FloatField(
        label="Rope length (m)",
        help_text="Length of the rope in meters.",
        required=True,
    )

class DeploymentForm(FormWithDetailMixin):
    # I should make this auto-populate based on the sensor type. Can be done with htmx,
    # but for now, I will just use a simple form.
    sensor = forms.ModelChoiceField(
        queryset=Sensor.objects.filter(available=True),
        label="Sensor",
        required=True,
        widget=forms.Select(
            attrs={
                "hx-trigger": "change, revealed, click",
                "hx-target": "#id_type",
            }
        ),

    )
    type = forms.ChoiceField(
        choices=Sensor.SENSOR_TYPE_CHOICES,
        label="Sensor type",
        required=True,
        widget=forms.ChoiceField.widget(
            attrs={
                "hx-trigger": "change, revealed",
                "hx-target": "#detail_form",
                "hx-swap": "innerHTML",
            }
        ),
    )

    detail_forms = {
        "vented": DeploymentVentedDetailForm,
        "unvented": forms.Form,
        "other": forms.Form,
    }

    class Meta:
        model = Deployment
        fields = ["sensor", "location", "detail"]
        widgets = {
            "decommissioned_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "detail": forms.HiddenInput(),
        }



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
