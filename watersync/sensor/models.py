from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from watersync.core.models import Location
from watersync.core.generics.interfaces import InterfaceModelTemplate, TimeSeriesModel
from watersync.users.models import User
from watersync.core.config import (
    get_variable_choices,
    get_all_sensor_unit_choices,
    is_valid_unit_for_variable,
    get_variable_label,
    get_sensor_unit_label,
)


class Sensor(models.Model, InterfaceModelTemplate):
    """Sensing devices.

    Sensors are devices that can be deployed in a location to measure
    various parameters. Often one sensor can measure multiple parameters.

    Attributes:
        identifier: The unique identifier of the sensor.
        user: The owner of the sensor.
        available: whether the sensor is currently deployed or not.
        detail: Additional information about the sensor
            in a JSON format.
    """

    identifier = models.CharField(max_length=55, unique=True)
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


class Deployment(models.Model, InterfaceModelTemplate):
    """Timeseries from sensors.

    A sensor deployment happens when a sensor is placed in a particular location. Deployment
    marks the beginning and the end of a timeseries obtained from a particular location from
    a particular sensor. The details are a JSONField because sensors can have different
    needs for details.

    Attributes:
        location: Location of deployment.
        sensor: The sensor deployed.
        variable: The variable being measured (from SENSOR_VARIABLES config).
        unit: The unit of measurement (must be valid for the variable).
        deployed_at: The date and time the sensor was deployed.
        decommissioned_at: The date and time the sensor was decommissioned.
        detail: Additional information relevant to the sensor deployment.

    Methods:
        decommission: Decommissions the sensor.
        find_deployment: retrieve a deployment by station, sensor and timesetamp.
    """

    # URL configuration fo
    # Deployment URLs are: /projects/<project_pk>/deployments/<deployment_pk>/
    _url_app_label = "sensor"

    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="deployments")
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, related_name="deployments")
    variable = models.CharField(
        max_length=50,
        choices=get_variable_choices(),
        help_text="The variable being measured by this deployment"
    )
    unit = models.CharField(
        max_length=50,
        choices=get_all_sensor_unit_choices(),
        help_text="Unit of measurement (must be valid for the selected variable)"
    )
    deployed_at = models.DateTimeField(auto_now_add=True)
    decommissioned_at = models.DateTimeField(null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)

    _list_view_fields = {
            "Location": "location",
            "Sensor": "sensor",
            "Variable": "get_variable_display",
            "Unit": "get_unit_display",
            "Start": "deployed_at",
            "End": "decommissioned_at",
        }
    
    _detail_view_fields = {
            "Location": "location",
            "Sensor": "sensor",
            "Variable": "get_variable_display",
            "Unit": "get_unit_display",
            "Start": "deployed_at",
            "End": "decommissioned_at",
    }

    class Meta:
        """Extra attribute in the Meta is the table_view_fields. It's used in the view to
        automate the creation of tables and lists."""

        unique_together = ("sensor", "location", "variable", "unit", "deployed_at")

    def __str__(self) -> str:
        return f"{self.sensor.identifier} at {self.location.name} ({self.get_variable_display()})"

    def clean(self):
        """Validate that the unit is valid for the selected variable."""
        super().clean()
        errors = {}
        
        # Validate variable-unit combination
        if self.variable and self.unit:
            if not is_valid_unit_for_variable(self.variable, self.unit):
                errors['unit'] = (
                    f"Unit '{self.unit}' is not valid for variable '{get_variable_label(self.variable)}'. "
                    f"Please select a compatible unit."
                )
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full_clean before saving to ensure validation."""
        self.full_clean()
        super().save(*args, **kwargs)

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


class SensorRecord(TimeSeriesModel):
    """Measurements from sensors.

    This table stores the measurements taken by all sensors. Deployment model acts
    as metadata for the measurements, so we only need to store the deployment,
    the value and the timestamp.

    Attributes:
        deployment: link to the particular logger deployment.
        value: Measured magnitude (inherited from TimeSeriesModel).
        timestamp: The date and time the measurement was taken.
    """

    # TimeSeriesModel configuration
    timestamp_field = "timestamp"
    location_field = "deployment__location"

    deployment = models.ForeignKey(
        Deployment, on_delete=models.CASCADE, related_name="records", db_index=True
    )
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        unique_together = ("deployment", "timestamp")
        ordering = ["-timestamp"]
