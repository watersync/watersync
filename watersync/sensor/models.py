from django.db import models
from watersync.users.models import User
from watersync.core.models import Location
from django.utils import timezone


class Sensor(models.Model):
    """Stores sensing devices details.

    Attributes:
        identifier: The unique identifier of the sensor.
        owner: The owner of the sensor.
        detail: Additional information about the sensor 
            in a JSON format.
    """

    identifier = models.CharField(max_length=55, unique=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    available = models.BooleanField(default=True)
    detail = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Sensors'

    def __str__(self):
        return self.identifier


class Deployment(models.Model):
    """Deployments of sensors aka a sensor timeseries.

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
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)
    deployed_at = models.DateTimeField(auto_now_add=True)
    decommissioned_at = models.DateTimeField(null=True, blank=True)
    detail = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Sensor deployments'
        unique_together = ('sensor', 'location', 'deployed_at')

    def deploy(self):
        """
        Creates a new deployment and sets the sensor's availability to False.
        """
        if not self.sensor.available:
            raise ValueError(
                "This sensor is already deployed and not available.")
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
    def find_deployment(cls, station, sensor, timestamp=None):
        """
        Finds the deployment based on the station, sensor, and the time between 
        deployed_at and decommissioned_at.

        Args:
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
                station=station,
                sensor=sensor,
                deployed_at__lte=timestamp,
                decommissioned_at__gte=timestamp if timestamp else None
            )
            return deployment
        except cls.DoesNotExist:
            return None


class SensorRecord(models.Model):
    """All measurements linked to deployment.

    there can be records taken at the same time from the same deployment, but
    representing different property, so the unique is set to (deployment, timestamp, 
    type)

    Attributes:
        deployment: link to the particular logger deployment.
        value: Measured magnitude.
        unit: The unit of the measurement.
        measurement_type: The type of measurement.
        timestamp: The date and time the measurement was taken.
    """

    SENSOR_MEASUREMENT_TYPES = {
        "flowrate": "Flow rate",
        "pressure": "Pressure",
        "temperature": "Temperature",
        "volume": "Volume"
    }

    deployment = models.ForeignKey(Deployment, on_delete=models.PROTECT)
    value = models.DecimalField(max_digits=8, decimal_places=3)
    unit = models.CharField(max_length=10)
    type = models.CharField(max_length=20, choices=SENSOR_MEASUREMENT_TYPES)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('deployment', 'timestamp', 'type')
        ordering = ['-timestamp']
