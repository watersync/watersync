"""The workflow of collecting data looks as follows:

A sample (Sample) of physicochemical parameters is registered as STN-YYYYMMDD-PARAMS
Other samples (Sample) are defined, e.g., for nutrients (NUT), metals (MET), etc.
Once the measurements (MEASUREMENT) are completed, they are created and linked to the previously created samples.
"""

from django.db import models
from django.utils.text import slugify
from django_extensions.db.models import TimeStampedModel

from watersync.core.models import LocationVisit
from watersync.core.generics.mixins import ModelTemplateInterface
from watersync.users.models import User


class Protocol(models.Model, ModelTemplateInterface):
    """Protocols for sampling and analysis.

    Protocol describes the details of the sampling collection and analysis process,
    starting form sample collection, preservation, storage, analysis and data
    postprocessing.

    Attributes:
        slug: A unique identifier for the protocol, generated from the method name.
        method_name: The name of the analytical method.
        sample_collection: Details about sample collection.
        sample_preservation: Details about sample preservation.
        sample_storage: Details about sample storage.
        analytical_method: Details about the analytical method used.
        data_postprocessing: Details about data postprocessing.
        standard_reference: Reference to a standard or guideline followed.
        description: A brief description of the protocol.
        user: The user associated with the protocol.
    """

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
    """Samples taken for analysis.

    Each sample represents a volume of water collected for analysis of specific parameters.
    The sample is linked to a specific location visit and protocol.

    Attributes:
        location_visit: The location visit associated with the sample.
        protocol: The protocol used for the sample.
        target_parameters: The parameters targeted for analysis in the sample.
        container_type: The type of container used for the sample.
        volume_collected: The volume of water collected in the
            sample.
    """

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
        "Location Visit": "location_visit",
        "Target Parameters": "target_parameters",
        "Container Type": "container_type",
        "Volume Collected": "volume_collected",
        "Replica Number": "replica_number",
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
    """Individual measurements of parameters in a sample.
    
    It is possible to create a sample first, let's say in the field when it's taken, and
    then add the measurements later when the analysis is done.
    """
    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE, related_name="measurements"
    )
    parameter = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    measured_on = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    detail = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.sample}: "
