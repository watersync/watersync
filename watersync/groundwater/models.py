from django.db import models
from django_extensions.db.models import TimeStampedModel

from watersync.core.models import Location
from watersync.core.generics.mixins import ModelTemplateInterface



class GWLManualMeasurement(TimeStampedModel, ModelTemplateInterface):
    """Manual measurements of groundwater levels.

    The depth is measured from the top of the casing to the water level.
    Should always be cprrected for the casing height before saving."""

    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="gwlmeasurements"
    )
    depth = models.DecimalField(max_digits=5, decimal_places=2)
    measured_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    _list_view_fields = {
        "Location": "location",
        "Depth": "depth",
        "Measured at": "measured_at",
    }
