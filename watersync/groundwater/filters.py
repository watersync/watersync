"""Django-filter classes for groundwater app."""

from watersync.core.generics.filters import TimeseriesFilterSet
from watersync.groundwater.models import GWLManualMeasurement


class GWLMeasurementFilter(TimeseriesFilterSet):
    """Filter for groundwater level measurements.
    
    Supports filtering by location, fieldwork, and date range.
    """
    
    date_field_name = 'fieldwork__date'
    
    class Meta:
        model = GWLManualMeasurement
        fields = ['location', 'fieldwork']
