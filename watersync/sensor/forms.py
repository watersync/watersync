import pandas as pd
from django import forms
from django.forms import HiddenInput

from watersync.core.models import Location

from .models import Deployment, Sensor


class SensorForm(forms.ModelForm):
    title = "Add Sensor"
    detail_schema = "sensor_detail_schema.json"

    class Meta:
        model = Sensor
        fields = ("identifier", "user", "detail")
        widgets = {"detail": HiddenInput(), "user": forms.CheckboxSelectMultiple()}


class DeploymentForm(forms.ModelForm):
    class Meta:
        model = Deployment
        fields = ["sensor", "location", "detail"]
        widgets = {
            "decommissioned_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "detail": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        # Get project_pk from kwargs
        project_pk = kwargs.pop("project_pk", None)
        super().__init__(*args, **kwargs)
        if project_pk:
            self.fields["location"].queryset = Location.objects.filter(
                project__pk=project_pk
            )

        self.fields["sensor"].queryset = Sensor.objects.filter(available=True)


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
