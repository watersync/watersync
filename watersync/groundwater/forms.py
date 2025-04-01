from django.forms import DateTimeInput, ModelForm

from watersync.groundwater.models import GWLManualMeasurement


class GWLForm(ModelForm):
    title = "Add Groundwater Level Measurement"

    class Meta:
        model = GWLManualMeasurement
        fields = ("location", "depth", "measured_at", "description")

        widgets = {
            "measured_at": DateTimeInput(attrs={"type": "datetime-local"}),
        }
