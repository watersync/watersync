from django.forms import ModelForm

from watersync.groundwater.models import GWLManualMeasurement


class GWLForm(ModelForm):
    title = "Groundwater Level Measurement"

    class Meta:
        model = GWLManualMeasurement
        fields = ("location_visit", "depth", "description")
