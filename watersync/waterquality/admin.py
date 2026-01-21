from django.contrib import admin

from watersync.waterquality.models import Measurement, Sample
from watersync.waterquality.models_setup import Protocol


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("parameter_group", "location", "fieldwork")
    list_filter = ("parameter_group",)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("sample", "parameter", "value", "unit")
    list_filter = ("parameter",)


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ("method_name", "slug")
    prepopulated_fields = {"slug": ("method_name",)}
