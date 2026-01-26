from decimal import Decimal
from django.db import models

from watersync.core.models import Location
from watersync.core.generics.models import TimeSeriesModel


class GWLManualMeasurement(TimeSeriesModel):
    """Manual measurements of groundwater levels.

    The value field stores depth to water measured from the top of the casing.
    Should always be corrected for the casing height before saving.

    Records are immutable: update not allowed, use delete and recreate.
    Soft delete: records are marked deleted but preserved in database.
    
    Attributes:
        value: Depth to water from top of casing (meters) - inherited from TimeSeriesModel
        groundwater_elevation: Computed elevation of groundwater surface
        created_at, created_by: Record creation tracking (inherited from TimeSeriesModel)
        is_deleted, deleted_at, deleted_by: Soft delete fields (inherited from TimeSeriesModel)
    """

    # TimeSeriesModel configuration
    timestamp_field = "fieldwork__date"
    location_field = "location"

    fieldwork = models.ForeignKey(
        "core.Fieldwork",
        on_delete=models.PROTECT,
        related_name="gwlmeasurements",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="gwlmeasurements",
        null=True,
        blank=True,
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-fieldwork__date"]

    _list_view_fields = {
        "Location": "location",
        "Depth": "value",
        "Elevation": "groundwater_elevation",
    }

    @property
    def groundwater_elevation(self):
        """Calculate groundwater elevation using historical TOC value at measurement time.
        
        Returns None if location is missing, history is unavailable, or TOC is not set.
        """
        try:
            if not self.location:
                return None
            
            if not self.fieldwork or not self.fieldwork.date:
                return None

            # Get historical location record from the time of measurement
            historical_location = self.location.history.as_of(self.fieldwork.date)

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
            return historical_toc - self.value
        except Exception:
            # Return None for any errors (missing history, invalid data, etc.)
            return None

