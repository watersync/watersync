from django.db import models
from watersync.core.models import Location


class GWLManualMeasurements(models.Model):
    """Manual measurements of groundwater levels.

    The depth is measured from the top of the casing to the water level. 
    Should always be cprrected for the casing height before saving."""

    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    depth = models.DecimalField(max_digits=5, decimal_places=2)
    comment = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'Groundwater level - manual measurements'
        unique_together = ('location', 'timestamp')
