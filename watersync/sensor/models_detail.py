"""Detail models for Deployment types.

Each Deployment type can have specific detail information stored
in a related one-to-one model.
"""

from django.db import models

from simple_history.models import HistoricalRecords

from watersync.core.generics.models import SetupSimpleHistory


class PressureSensorDeploymentDetail(models.Model, SetupSimpleHistory):
    """Detail information for pressure sensor deployments.

    Used for both gauge pressure and absolute pressure sensor deployments.
    Stores the installation elevation which is needed for water level calculations.
    """

    deployment = models.OneToOneField(
        "sensor.Deployment",
        on_delete=models.CASCADE,
        related_name="pressure_sensor_detail",
        primary_key=True,
    )
    installation_elevation = models.FloatField(
        verbose_name="Installation Elevation (m)",
        help_text="Elevation of the sensor installation point in meters (above sea level or reference datum)",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Pressure Sensor Deployment Detail"
        verbose_name_plural = "Pressure Sensor Deployment Details"

    def __str__(self):
        return f"Pressure sensor detail for {self.deployment}"


# Mapping from deployment type to detail model classes
DEPLOYMENT_TYPE_DETAIL_MODELS = {
    "gauge_pressure": PressureSensorDeploymentDetail,
    "absolute_pressure": PressureSensorDeploymentDetail,
    # "other" has no detail model
}

# Mapping from deployment type to related detail attribute name
DEPLOYMENT_TYPE_DETAIL_RELATED_NAMES = {
    "gauge_pressure": "pressure_sensor_detail",
    "absolute_pressure": "pressure_sensor_detail",
}
