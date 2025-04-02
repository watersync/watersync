"""The workflow of collecting data looks as follows:

1. A sampling event is registered (SamplingEvent).
2. A sample (Sample) of physicochemical parameters is registered as STN-YYYYMMDD-PARAMS
3. Other samples (Sample) are defined, e.g., for nutrients (NUT), metals (MET), etc.
4. Once the measurements (MEASUREMENT) are completed, they are created and linked to the previously created samples.
"""

from django.db import models
from django.utils.text import slugify
from django_extensions.db.models import TimeStampedModel

from watersync.core.models import LocationVisit
from watersync.core.generics.mixins import ModelTemplateInterface
from watersync.users.models import User


class Protocol(models.Model, ModelTemplateInterface):
    """Protocol describes the details of the sampling collection and analysis process,
    starting form sample collection, preservation, storage, analysis and data postprocessing."""

    slug = models.SlugField(max_length=100, unique=True, editable=False)
    method_name = models.CharField(max_length=100)
    sample_collection = models.TextField(blank=True, null=True)
    sample_preservation = models.TextField(blank=True, null=True)
    sample_storage = models.TextField(blank=True, null=True)
    analytical_method = models.TextField(blank=True, null=True)
    data_postprocessing = models.TextField(blank=True, null=True)
    standard_reference = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(max_length=256, blank=True, null=True)
    user = models.ManyToManyField(User, related_name="protocols")

    _list_view_fields = {
        "Method Name": "method_name",
    }

    _detail_view_fields = {
        "Method Name": "method_name",
        "Sample Collection": "sample_collection",
        "Sample Preservation": "sample_preservation",
        "Sample Storage": "sample_storage",
        "Analytical Method": "analytical_method",
        "Data Postprocessing": "data_postprocessing",
        "Standard Reference": "standard_reference",
        "Description": "description",
    }

    def __str__(self):
        return self.method_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.method_name)
        super().save(*args, **kwargs)


class Sample(TimeStampedModel, ModelTemplateInterface):
    location_visit = models.ForeignKey(
        LocationVisit, on_delete=models.CASCADE, related_name="samples"
    )
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    target_parameters = models.CharField(max_length=50)
    container_type = models.CharField(max_length=50, blank=True, null=True)
    volume_collected = models.FloatField(blank=True, null=True)
    replica_number = models.IntegerField(default=0)
    detail = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    _list_view_fields = {
        "Target Parameters": "target_parameters",
        "Container Type": "container_type",
        "Volume Collected": "volume_collected",
        "Replica Number": "replica_number",
        "Created": "created",
        "Modified": "modified",
    }

    _detail_view_fields = {
        "Target Parameters": "target_parameters",
        "Container Type": "container_type",
        "Volume Collected": "volume_collected",
        "Replica Number": "replica_number",
        "Created": "created",
        "Modified": "modified",
    }

    def __str__(self):
        return f"{self.target_parameters} - {self.container_type} - {self.volume_collected} - {self.replica_number}"



class Measurement(TimeStampedModel):
    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE, related_name="measurements"
    )
    parameter = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    measured_on = models.DateField(null=True, blank=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.parameter}: {self.value} {self.unit} ({self.sample})"
