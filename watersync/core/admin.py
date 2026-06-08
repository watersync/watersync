from django.contrib import admin

from .models import Fieldwork, Location, Project
from .models_detail import (
    LakeDetail,
    PiezometerDetail,
    PrecipitationDetail,
    PumpingWellDetail,
    RiverDetail,
    WastewaterDetail,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("name",)
    search_fields = ("name",)  # Fields to search by
    list_filter = ("user",)  # Add filters in the right sidebar


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("name",)
    search_fields = ("name",)  # Fields to search by


@admin.register(Fieldwork)
class FieldworkAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = ("date",)
    search_fields = ("date",)  # Fields to search by


@admin.register(PiezometerDetail)
class PiezometerDetailAdmin(admin.ModelAdmin):
    list_display = ("location", "depth", "diameter", "material")
    search_fields = ("location__name",)


@admin.register(PumpingWellDetail)
class PumpingWellDetailAdmin(admin.ModelAdmin):
    list_display = ("location", "pumping_rate")
    search_fields = ("location__name",)


@admin.register(LakeDetail)
class LakeDetailAdmin(admin.ModelAdmin):
    list_display = ("location", "depth", "area", "volume")
    search_fields = ("location__name",)


@admin.register(WastewaterDetail)
class WastewaterDetailAdmin(admin.ModelAdmin):
    list_display = ("location", "number_of_tanks", "treatment_level")
    search_fields = ("location__name",)


@admin.register(RiverDetail)
class RiverDetailAdmin(admin.ModelAdmin):
    list_display = ("location", "width", "depth", "flow_rate")
    search_fields = ("location__name",)


@admin.register(PrecipitationDetail)
class PrecipitationDetailAdmin(admin.ModelAdmin):
    list_display = ("location", "intensity", "duration")
    search_fields = ("location__name",)