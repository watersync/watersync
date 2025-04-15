from django.forms import DateTimeInput, ModelForm

from watersync.groundwater.models import GWLManualMeasurement


class GWLForm(ModelForm):
    title = "Add Groundwater Level Measurement"

    class Meta:
        model = GWLManualMeasurement
        fields = ("location_visit", "depth", "description")
