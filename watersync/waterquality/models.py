from django.db import models
from watersync.core.models import Location


class Sample(models.Model):
    """Represents the entire volume of water taken from a particular location 
    for analysis.

    !!! note:

        This model represents the total volume of water taken at a specific time
        from a well (or other location) for analysis. It does not differentiate 
        between multiple containers filled at the same time.

    Attributes:
        location: where the sample was taken
        timestamp: when the sample was taken
        detail: space for any additional information in key-value pair format.
    """

    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    timestamp = models.DateTimeField()
    detail = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('location', 'timestamp')
        verbose_name = "Water Sample"
        verbose_name_plural = "Water Samples"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Sample from {self.location} at {self.timestamp:%Y-%m-%d %H:%M}"


class Measurement(models.Model):
    """Represents a specific measurement taken on a water sample.

    I merged initially separated physicochemical parameters and analytical 
    measurements results into Measurements class. This is to simplify storing
    and retrieving of the data. I kept groupping by sample, to make it easier to
    compute statistics per sample (like ionic balance or other QC params).

    Attributes:
        sample (ForeignKey): The water sample on which the measurement was 
            performed.
        property (CharField): The parameter that was measured
            (e.g., pH, temperature, Cl, ).
        value (FloatField): The value of the measurement.
        unit (CharField): The unit of the measurement (e.g., °C, mg/L).
        detail (JSONField): Additional details about the measurement.
    """

    sample = models.ForeignKey(Sample, on_delete=models.PROTECT)
    property = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    detail = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Water Measurement"
        verbose_name_plural = "Water Measurements"
        ordering = ['sample', 'property']

    def __str__(self):
        return f"{self.property} at {self.sample.location} on \
        {self.sample.timestamp: % Y-%m-%d % H: % M} - {self.value} {self.unit}"
