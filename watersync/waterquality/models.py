"""The workflow of collecting data looks as follows:

1. A sampling event is registered (SamplingEvent).
2. A sample (Sample) of physicochemical parameters is registered as STN-YYYYMMDD-PARAMS
3. Other samples (Sample) are defined, e.g., for nutrients (NUT), metals (MET), etc.
4. Once the measurements (MEASUREMENT) are completed, they are created and linked to the previously created samples.
"""

from django.db import models
from watersync.core.models import Location
from django.utils.text import slugify
from ..core.models import Location
from ..users.models import User
from django_extensions.db.models import TimeStampedModel


class Protocol(models.Model):
    """Protocol describes the details of the sampling collection and analysis process,
    starting form sample collection, preservation, storage, analysis and data postprocessing."""

    method_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, editable=False)
    sample_collection = models.TextField(blank=True, null=True)
    sample_preservation = models.TextField(blank=True, null=True)
    sample_storage = models.TextField(blank=True, null=True)
    analytical_method = models.TextField(blank=True, null=True)
    data_postprocessing = models.TextField(blank=True, null=True)
    standard_reference = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(max_length=256, blank=True, null=True)
    users = models.ManyToManyField(User, related_name="protocols")

    def __str__(self):
        return self.method_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.method_name)
        super().save(*args, **kwargs)


class SamplingEvent(TimeStampedModel):
    """Sampling event is linked to a particular location and date."""

    slug = models.SlugField(max_length=100, unique=True, editable=False)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="sampling_events"
    )
    executed_at = models.DateTimeField()
    executed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sampling_events"
    )
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Sampling at {self.location.name} on {self.executed_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.location.name}-{self.executed_at.strftime('%Y-%m-%d')}"
            )
        super().save(*args, **kwargs)


class Sample(models.Model):
    sampling_event = models.ForeignKey(
        SamplingEvent, on_delete=models.CASCADE, related_name="samples"
    )
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    target_parameters = models.CharField(max_length=50, blank=True, null=True)
    container_type = models.CharField(max_length=50, blank=True, null=True)
    volume_collected = models.FloatField(blank=True, null=True)
    replica_number = models.IntegerField(blank=True, null=True, default=0)
    details = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (("sampling_event", "target_parameters", "replica_number"),)

    def __str__(self):
        return f"{self.sampling_event.slug}-{self.target_parameters}-R{self.replica_number}"


class Measurement(TimeStampedModel):
    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE, related_name="measurements"
    )
    parameter_name = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    measured_on = models.DateTimeField(null=True, blank=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.parameter_name}: {self.value} {self.unit} ({self.sample})"
