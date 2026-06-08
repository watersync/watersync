from watersync.core.generics.forms import WatersyncForm
from watersync.groundwater.models import GWLManualMeasurement


class GWLForm(WatersyncForm):
    title = "Groundwater Level Measurement"

    class Meta:
        model = GWLManualMeasurement
        fields = ("location", "fieldwork", "value", "description")
