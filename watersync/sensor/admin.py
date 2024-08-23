from django.contrib import admin
from .models import Sensor


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('identifier', 'owner')
    search_fields = ('identifier',)  # Fields to search by
    list_filter = ('owner',)  # Add filters in the right sidebar
