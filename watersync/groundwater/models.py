from decimal import Decimal
from django.db import models
from django_extensions.db.models import TimeStampedModel

from watersync.core.models import Location
from watersync.core.generics.interfaces import InterfaceModelTemplate, ModelURLMixin, TimeSeriesModel



class GWLManualMeasurement(TimeSeriesModel, TimeStampedModel, InterfaceModelTemplate, ModelURLMixin):
    """Manual measurements of groundwater levels.

    The value field stores depth to water measured from the top of the casing.
    Should always be corrected for the casing height before saving.
    
    Attributes:
        value: Depth to water from top of casing (meters) - inherited from TimeSeriesModel
        groundwater_elevation: Computed elevation of groundwater surface
    """

    # URL configuration for ModelURLMixin
    # GWLManualMeasurement URLs are: /projects/<project_pk>/gwlmanualmeasurements/<gwlmanualmeasurement_pk>/
    _url_app_label = "groundwater"

    # TimeSeriesModel configuration
    timestamp_field = "fieldwork__date"
    location_field = "location"

    fieldwork = models.ForeignKey(
        "core.Fieldwork",
        on_delete=models.CASCADE,
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

    def _get_url_kwargs(self):
        """Build URL kwargs. GWLManualMeasurement URLs need project_pk from location.project."""
        kwargs = {"gwlmanualmeasurement_pk": self.pk}
        if self.location and self.location.project:
            kwargs["project_pk"] = self.location.project.pk
        return kwargs

    @property
    def groundwater_elevation(self):
        """Calculate groundwater elevation using historical TOC value at measurement time.
        
        TODO: still need to implement handling of the timezone
        """

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

