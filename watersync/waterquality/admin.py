from django.contrib import admin

from watersync.waterquality.models import Measurement, Sample


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("parameter_group", )


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("sample", "parameter", "value", "unit")
    search_fields = ("sample",)  # Fields to search by
    list_filter = ("sample", "parameter")  # Add filters in the right sidebar
