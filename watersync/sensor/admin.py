from django.contrib import admin
from .models import Sensor, SensorRecord


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('identifier',)
    search_fields = ('identifier',)  # Fields to search by
    list_filter = ('user',)  # Add filters in the right sidebar


@admin.register(SensorRecord)
class SensorRecordAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ('deployment', 'value', 'unit', 'type')
    # Fields to search by
    search_fields = ('deployment__location', 'deployment__sensor',)
    # Add filters in the right sidebar
    list_filter = ('deployment__location', 'deployment__sensor',)
