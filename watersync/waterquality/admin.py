from django.contrib import admin
from .models import Sample, Measurement


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('timestamp', 'location')
    search_fields = ('location',)  # Fields to search by
    list_filter = ('location',)  # Add filters in the right sidebar


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('sample', 'property', 'value', 'unit')
    search_fields = ('sample',)  # Fields to search by
    list_filter = ('sample', 'property')  # Add filters in the right sidebar
