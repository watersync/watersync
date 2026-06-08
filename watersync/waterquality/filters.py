"""Django-filter classes for water quality app."""

from watersync.core.generics.filters import ProjectScopedFilterSet, TimeseriesFilterSet
from watersync.waterquality.models import Measurement, Sample


class SampleFilter(TimeseriesFilterSet):
    """Filter for water quality samples.
    
    Supports filtering by location, fieldwork, and date range.
    """
    
    date_field_name = 'fieldwork__date'
    
    class Meta:
        model = Sample
        fields = ['location', 'fieldwork']


class MeasurementFilter(ProjectScopedFilterSet):
    """Filter for water quality measurements.
    
    Supports filtering by sample and parameter.
    """
    
    class Meta:
        model = Measurement
        fields = ['sample', 'parameter']
