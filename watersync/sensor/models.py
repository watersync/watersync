from django.db import models
from django.utils import timezone

from watersync.core.models import Location
from watersync.core.generics.mixins import ModelTemplateInterface
from watersync.users.models import User


class Sensor(models.Model, ModelTemplateInterface):
    """Sensing devices.

    Attributes:
        identifier: The unique identifier of the sensor.
        user: The owner of the sensor.
        available: whether the sensor is currently deployed or not.
        detail: Additional information about the sensor
            in a JSON format.
    """

    SENSOR_TYPE_CHOICES = [
        ("vented", "Vented"),
        ("unvented", "Unvented"),
        ("other", "Other"),
    ]

    identifier = models.CharField(max_length=55, unique=True)
    type = models.CharField(
        max_length=20,
        choices=SENSOR_TYPE_CHOICES,
        default="other",
    )
    user = models.ManyToManyField(User, blank=True, related_name="sensors")
    available = models.BooleanField(default=True)
    detail = models.JSONField(null=True, blank=True)

    _list_view_fields = {
        "Identifier": "identifier",
        "Available": "available"
    }

    _detail_view_fields = {
        "Identifier": "identifier",
        "Available": "available"
    }

    def __str__(self):
        return self.identifier


class Deployment(models.Model, ModelTemplateInterface):
    """Timeseries from sensors.

    A sensor deployment happens when a sensor is placed in a particular location. Deployment
    marks the beginning and the end of a timeseries obtained from a particular location from
    a particular sensor. The details are a JSONField because sensors can have different
    needs for details.

    Attributes:
        location: Location of deployment.
        sensor: The sensor deployed.
        deployed_at: The date and time the sensor was deployed.
        decommissioned_at: The date and time the sensor was decommissioned.
        detail: Additional information about the deployment.

    Methods:
        decommission: Decommissions the sensor.
        find_deployment: retrieve a deployment by station, sensor and timesetamp.
    """

    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="deployments")
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, related_name="deployments")
    variable = models.CharField(max_length=20)
    unit = models.CharField(max_length=10)
    deployed_at = models.DateTimeField(auto_now_add=True)
    decommissioned_at = models.DateTimeField(null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)

    _list_view_fields = {
            "Location": "location",
            "Sensor": "sensor",
            "Start": "deployed_at",
            "End": "decommissioned_at",
        }
    
    _detail_view_fields = {
            "Location": "location",
            "Sensor": "sensor",
            "Start": "deployed_at",
            "End": "decommissioned_at",
    }

    class Meta:
        """Extra attribute in the Meta is the table_view_fields. It's used in the view to
        automate the creation of tables and lists."""

        unique_together = ("sensor", "location", "variable", "unit", "deployed_at")

    def __str__(self) -> str:
        return f"{self.sensor.identifier} at {self.location.name}"

    def deploy(self):
        """
        Creates a new deployment and sets the sensor's availability to False.
        """
        if not self.sensor.available:
            message = "This sensor is already deployed and not available."
            raise ValueError(message)

        self.sensor.available = False
        self.sensor.save()
        self.save()

    def decommission(self):
        """
        Decommissions the deployment and sets the sensor's availability to True.
        """
        if self.decommissioned_at is None:
            self.decommissioned_at = timezone.now()
            self.sensor.available = True
            self.sensor.save()
            self.save()

    @classmethod
    def find_deployment(cls, location, sensor, timestamp=None):
        """
        Finds the deployment based on the station, sensor, and the time between
        deployed_at and decommissioned_at.

        Parameters:
            station (Station): The station where the sensor is deployed.
            sensor (Sensor): The sensor deployed.
            timestamp (datetime, optional): The time to check the deployment against.
                                             Defaults to the current time.

        Returns:
            Deployment: The deployment instance that matches the criteria or None if not found.
        """
        timestamp = timestamp or timezone.now()

        try:
            deployment = cls.objects.get(
                location=location,
                sensor=sensor,
                deployed_at__lte=timestamp,
                decommissioned_at__gte=timestamp if timestamp else None,
            )
            return deployment

        except cls.DoesNotExist:
            return None


class SensorRecord(models.Model):
    """Measurements from sensors.

    This table stores the measurements taken by all sensors. Deployment model acts
    as metadata for the measurements, so we only need to store the deployment,
    the value and the timestamp.

    Attributes:
        deployment: link to the particular logger deployment.
        value: Measured magnitude.
        timestamp: The date and time the measurement was taken.
    """

    deployment = models.ForeignKey(
        Deployment, on_delete=models.CASCADE, related_name="records", db_index=True
    )
    value = models.DecimalField(max_digits=8, decimal_places=3)
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        unique_together = ("deployment", "timestamp")
        ordering = ["-timestamp"]
