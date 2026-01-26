"""Reusable django-filter classes for WaterSync views.

This module provides base filter classes that can be used across apps
for consistent queryset filtering with HTMX support.

Usage:
    from watersync.core.generics.filters import ProjectScopedFilterSet
    
    class SampleFilter(ProjectScopedFilterSet):
        class Meta:
            model = Sample
            fields = ['location', 'fieldwork']

In views:
    class SampleListView(FilterMixin, WatersyncListView):
        model = Sample
        filterset_class = SampleFilter
"""

import django_filters


class ProjectScopedFilterSet(django_filters.FilterSet):
    """Base FilterSet for models scoped to a project.
    
    Provides common filters for location, fieldwork, and other 
    project-related relationships. Subclass and specify Meta.model
    and Meta.fields.
    
    The filterset automatically limits choice fields to items within
    the current project when a `project` is passed to the constructor.
    
    Accepts both `location` and `location_pk` style parameters for 
    compatibility with HTMX hx-vals which use the `_pk` suffix.
    """
    
    # Filters that accept _pk suffix parameters (used by hx-vals in templates)
    location_pk = django_filters.NumberFilter(field_name='location__pk')
    fieldwork_pk = django_filters.NumberFilter(field_name='fieldwork__pk')
    sample_pk = django_filters.NumberFilter(field_name='sample__pk')
    
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        
        # Limit filter choices to project scope
        if project:
            self._limit_choices_to_project(project)
    
    def _limit_choices_to_project(self, project):
        """Limit filter field querysets to items within the project."""
        if 'location' in self.filters:
            self.filters['location'].queryset = project.locations.all()
        
        if 'fieldwork' in self.filters:
            from watersync.core.models import Fieldwork
            self.filters['fieldwork'].queryset = Fieldwork.objects.filter(
                project=project
            ).order_by('-date')


class TimeseriesFilterSet(ProjectScopedFilterSet):
    """FilterSet for timeseries data with date range support.
    
    Provides date_from and date_to filters in addition to 
    project-scoped relationship filters. Override `date_field_name`
    to specify which field to filter on.
    
    Usage:
        class SampleFilter(TimeseriesFilterSet):
            date_field_name = 'fieldwork__date'
            
            class Meta:
                model = Sample
                fields = ['location', 'fieldwork']
                
        class SensorRecordFilter(TimeseriesFilterSet):
            date_field_name = 'timestamp'
            
            class Meta:
                model = SensorRecord
                fields = ['deployment']
    """
    
    date_field_name = 'fieldwork__date'  # Override in subclass
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.filters['date_from'] = django_filters.DateFilter(
            field_name=self.date_field_name,
            lookup_expr='gte',
            label='From',
        )
        self.filters['date_to'] = django_filters.DateFilter(
            field_name=self.date_field_name,
            lookup_expr='lte',
            label='To',
        )
