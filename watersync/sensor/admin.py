from django.contrib import admin

from .models import Deployment, Sensor, SensorRecord
from .models_detail import PressureSensorDeploymentDetail


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("identifier", "manufacturer", "model")
    search_fields = ("identifier", "manufacturer", "model")
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
    list_display = ("location", "sensor", "type")
    search_fields = (
        "location",
        "sensor",
    )
    list_filter = (
        "location",
        "type",
    )


@admin.register(PressureSensorDeploymentDetail)
class PressureSensorDeploymentDetailAdmin(admin.ModelAdmin):
    list_display = ("deployment", "installation_elevation")
    search_fields = ("deployment__sensor__identifier",)
