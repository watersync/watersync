from django.contrib import admin

from watersync.waterquality.models import Measurement, Sample


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("parameter_group", )
