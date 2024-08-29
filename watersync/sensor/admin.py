from django.contrib import admin
from .models import Sensor, SensorRecord, Deployment


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):

    list_display = ('identifier',)
    search_fields = ('identifier',)
    list_filter = ('user',)


@admin.register(SensorRecord)
class SensorRecordAdmin(admin.ModelAdmin):

    list_display = ('deployment', 'value', 'unit', 'type')
    search_fields = ('deployment__location', 'deployment__sensor',)
    list_filter = ('deployment__location',
                   'deployment__sensor', 'type', 'timestamp')


@admin.register(Deployment)
class DeploymentRecordAdmin(admin.ModelAdmin):

    list_display = ('location', 'sensor', 'deployed_at', 'decommissioned_at')
    search_fields = ('location', 'sensor',)
    list_filter = ('location', 'location',)
