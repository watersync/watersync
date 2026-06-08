from django.core.exceptions import ValidationError
from django.db import models

from simple_history.models import HistoricalRecords

from watersync.core.config import (
    get_all_sensor_unit_choices,
    get_variable_choices,
    get_variable_label,
    is_valid_unit_for_variable,
)
from watersync.core.generics.managers import (
    LocationWithCountsManager,
    UserScopedManager,
)
from watersync.core.generics.models import SetupSimpleHistory, TimeSeriesModel
from watersync.core.models import Location
from watersync.users.models import User


class Sensor(models.Model, SetupSimpleHistory):
    """Sensing devices.

    Sensors are devices that can be deployed in a location to measure
    various parameters. Often one sensor can measure multiple parameters.

    Attributes:
        identifier: The unique identifier of the sensor.
        user: The owner of the sensor.
        manufacturer: The manufacturer of the sensor.
        model: The model name/number of the sensor.
    """

    identifier = models.CharField(max_length=55, unique=True)
    user = models.ManyToManyField(User, blank=True, related_name="sensors")
    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Manufacturer",
        help_text="The manufacturer of the sensor",
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Model",
        help_text="The model name/number of the sensor",
    )
    date_purchased = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date Purchased",
        help_text="The date when the sensor was purchased",
    )

    objects = UserScopedManager()
    history = HistoricalRecords()

    _list_view_fields = {
        "Identifier": "identifier",
        "Manufacturer": "manufacturer",
        "Model": "model",
        "Date Purchased": "date_purchased",
    }

    _detail_view_fields = {
        "Identifier": "identifier",
        "Manufacturer": "manufacturer",
        "Model": "model",
        "Date Purchased": "date_purchased",
    }

    def __str__(self):
        return self.identifier


class Deployment(models.Model):
    """Metadata for sensor timeseries.

    Groups sensor records with common metadata like location, variable, and unit.
    Detail information specific to the deployment type is stored in related
    one-to-one models (e.g., PressureSensorDeploymentDetail).

    Attributes:
        location: Location where measurements are taken.
        sensor: The sensor taking measurements.
        type: The type of deployment (gauge_pressure, absolute_pressure, other).
        variable: The variable being measured (from SENSOR_VARIABLES config).
        unit: The unit of measurement (must be valid for the variable).
        started_at: When this timeseries started (optional).
        ended_at: When this timeseries ended (optional, null if ongoing).
    """

    class DeploymentTypes(models.TextChoices):
        GAUGE_PRESSURE = "gauge_pressure", "Gauge Pressure"
        ABSOLUTE_PRESSURE = "absolute_pressure", "Absolute Pressure"
        OTHER = "other", "Other"

    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="deployments")
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, related_name="deployments")
    type = models.CharField(
        max_length=20,
        choices=DeploymentTypes.choices,
        default=DeploymentTypes.OTHER,
        help_text="The type of sensor deployment"
    )
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
    started_at = models.DateTimeField(null=True, blank=True, help_text="When this timeseries started")
    ended_at = models.DateTimeField(null=True, blank=True, help_text="When this timeseries ended (null if ongoing)")

    objects = LocationWithCountsManager()
    history = HistoricalRecords()

    # Fields to count in with_counts() - used for overview pages
    _count_fields = ['records']

    _list_view_fields = {
            "Location": "location",
            "Sensor": "sensor",
            "Type": "get_type_display",
            "Variable": "get_variable_display",
            "Unit": "get_unit_display",
            "Start": "started_at",
            "End": "ended_at",
        }
    
    _detail_view_fields = {
            "Location": "location",
            "Sensor": "sensor",
            "Type": "get_type_display",
            "Variable": "get_variable_display",
            "Unit": "get_unit_display",
            "Start": "started_at",
            "End": "ended_at",
    }

    class Meta:
        unique_together = ("sensor", "location", "variable", "unit", "started_at")

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


class SensorRecord(TimeSeriesModel):
    """Measurements from sensors.

    This table stores the measurements taken by all sensors. Deployment model acts
    as metadata for the measurements, so we only need to store the deployment,
    the value and the timestamp.

    Records are immutable: update not allowed, use delete and recreate.
    Soft delete: records are marked deleted but preserved in database.

    Attributes:
        deployment: link to the particular logger deployment.
        value: Measured magnitude (inherited from TimeSeriesModel).
        timestamp: The date and time the measurement was taken.
        created_at, created_by: Record creation tracking (inherited from TimeSeriesModel)
        is_deleted, deleted_at, deleted_by: Soft delete fields (inherited from TimeSeriesModel)
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
