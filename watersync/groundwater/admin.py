from django.contrib import admin

from .models import GWLManualMeasurement


@admin.register(GWLManualMeasurement)
class GWLAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("location_visit", "depth")

