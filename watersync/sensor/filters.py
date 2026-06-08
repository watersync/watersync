"""Django-filter classes for sensor app."""

from django import forms

import django_filters

from watersync.core.generics.filters import ProjectScopedFilterSet, TimeseriesFilterSet
from watersync.sensor.models import Deployment, SensorRecord


class DeploymentFilter(ProjectScopedFilterSet):
    """Filter for sensor deployments.
    
    Supports filtering by location, sensor, and deployment date range.
    Uses custom date field (deployed_at) so defines filters explicitly.
    """
    
    started_at = django_filters.DateFilter(
        field_name='started_at',
        lookup_expr='gte',
        label='Deployed from',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    ended_at = django_filters.DateFilter(
        field_name='ended_at',
        lookup_expr='lte',
        label='Deployed to',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'})
    )
    
    class Meta:
        model = Deployment
        fields = ['location', 'sensor']


class SensorRecordFilter(TimeseriesFilterSet):
    """Filter for sensor records/timeseries data.
    
    Supports filtering by deployment and timestamp range.
    """
    
    date_field_name = 'timestamp'
    
    class Meta:
        model = SensorRecord
        fields = ['deployment']
