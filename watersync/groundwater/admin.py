from django.contrib import admin
from .models import GWLManualMeasurements


@admin.register(GWLManualMeasurements)
class GWLAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('location', 'depth', 'timestamp')
    search_fields = ('location',)  # Fields to search by
    list_filter = ('location',)  # Add filters in the right sidebar
