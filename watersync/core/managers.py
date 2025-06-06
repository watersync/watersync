from django.db import models
from django.db.models import Count, Sum
from django.db.models import F

class LocationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class WatersyncManager(models.Manager):
    def with_user_data(self, user):
        """Filter objects by user and add common annotations"""
        return self.get_queryset().filter(created_by=user)
    
    def with_stats(self):
        """Add calculated fields to the queryset"""
        return self.get_queryset().annotate(
            locvisits=Count('visits'),
            locsamples=Count('visits__samples')
        )
    
    def with_filters(self, **filters):
        """Apply dynamic filters from request parameters"""
        valid_filters = {k: v for k, v in filters.items() if v}
        return self.get_queryset().filter(**valid_filters) if valid_filters else self.get_queryset()
    
    def get_full_queryset(self, user=None, filters=None, stats=None, for_export=False):
        """Combine multiple query customizations
        
        Args:
            user: Optional user to filter by
            filters: Dictionary of field:value pairs for direct filtering
            stats: Dictionary of annotation expressions to add
            for_export: Boolean flag to indicate if this is for export (returns dictionaries)
        """
        queryset = self.get_queryset()

        stats = stats or {}
        
        if user:
            queryset = queryset.filter(created_by=user)
            
        if filters:
            # Apply filters directly to the queryset
            valid_filters = {k: v for k, v in filters.items() if v}
            if valid_filters:
                queryset = queryset.filter(**valid_filters)
        
        # Apply annotations directly
        queryset = queryset.annotate(**stats)
        
        # Only transform to dictionaries if this is for export
        if for_export and hasattr(self.model, '_csv_columns'):
            # Convert field names to F expressions
            annotations = {label: F(field_name) for label, field_name in self.model._csv_columns.items()}
            queryset = queryset.annotate(**annotations)
            
            # Then select only those fields
            queryset = queryset.values(*self.model._csv_columns.keys())
            
        return queryset
