from django.contrib import admin

from .models import Deployment, Sensor, SensorRecord


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("identifier",)
    search_fields = ("identifier",)
    list_filter = ("user",)


@admin.register(SensorRecord)
class SensorRecordAdmin(admin.ModelAdmin):
    list_display = ("deployment", "value")
    search_fields = (
        "deployment__location",
        "deployment__sensor",
        "deployment__variable",
    )
    list_filter = (
        "deployment__location",
        "deployment__sensor",
        "deployment__variable",
        "timestamp",
    )


@admin.register(Deployment)
class DeploymentRecordAdmin(admin.ModelAdmin):
    list_display = ("location", "sensor", "deployed_at", "decommissioned_at")
    search_fields = (
        "location",
        "sensor",
    )
    list_filter = (
        "location",
        "location",
    )
