from django.db import models
from django_extensions.db.models import TimeStampedModel

from watersync.core.models import Location


class GWLManualMeasurement(TimeStampedModel):
    """Manual measurements of groundwater levels.

    The depth is measured from the top of the casing to the water level.
    Should always be cprrected for the casing height before saving."""

    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name="gwlmeasurements"
    )
    depth = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.TextField(null=True, blank=True)
    measured_at = models.DateTimeField(null=True, blank=True)
    