from decimal import Decimal
from django.db import models
from django_extensions.db.models import TimeStampedModel

from watersync.core.models import Location, LocationVisit
from watersync.core.generics.mixins import ModelTemplateInterface



class GWLManualMeasurement(TimeStampedModel, ModelTemplateInterface):
    """Manual measurements of groundwater levels.

    The depth is measured from the top of the casing to the water level.
    Should always be cprrected for the casing height before saving."""

    location_visit = models.ForeignKey(
        LocationVisit,
        on_delete=models.PROTECT,
        related_name="gwlmeasurements",
        null=True,
        blank=True,
    )
    depth = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    _list_view_fields = {
        "Location visit": "location_visit",
        "Depth": "depth",
        "Elevation": "groundwater_elevation",
    }

    @property
    def groundwater_elevation(self):
        """Calculate groundwater elevation using historical TOC value at measurement time.
        
        TODO: still need to implement handling of the timezone
        """
        if not self.measured_at:
            return None

        # Get historical location record from the time of measurement
        historical_location = self.location_vist.location.history.as_of(self.location_visit.date)

        # Get TOC from historical detail field
        historical_detail = historical_location.detail or []

        # Find the object with property='toc_height'
        historical_toc = next(
            (Decimal(item['value']) for item in historical_detail
            if isinstance(item, dict) and item.get('property') == 'toc_height'),
            None
        )

        if historical_toc is None:
            return None

        # Calculate groundwater elevation
        return historical_toc - self.depth

