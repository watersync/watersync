"""The workflow of collecting data looks as follows:

A sample (Sample) of physicochemical parameters is registered as STN-YYYYMMDD-PARAMS
Other samples (Sample) are defined, e.g., for nutrients (NUT), metals (MET), etc.
Once the measurements (MEASUREMENT) are completed, they are created and linked to the previously created samples.
"""

from django.db import models
from django.utils.text import slugify
from django_extensions.db.models import TimeStampedModel

from watersync.core.models import LocationVisit, Unit
from watersync.core.generics.mixins import ModelTemplateInterface
from watersync.users.models import User

class ParameterGroup(models.Model, ModelTemplateInterface):
    """Group of target parameters for analysis.

    These are groups of parameters like nutrients, metals, etc. that are
    normally analyzed together. These values will be used in the
    sample form as select options.

    These items are available in the Settings panel in the app.
    
    Attributes:
        name: The name of the target parameter group.
        description: A brief description of the group.
    """

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)

    _list_view_fields = {
        "Name": "name",
        "Code": "code",
    }

    def __str__(self):
        return self.name

class Parameter(models.Model, ModelTemplateInterface):
    """Parameter for analysis.

    Each parameter is a specific measurement that can be taken from a sample.
    Parameters are grouped into target parameter groups. When adding measurements,
    the select options for the parameters will be restricted to the sample target group.

    These items are available in the Settings panel in the app.
    
    Attributes:
        name: The name of the parameter.
        group: The target parameter group to which the parameter belongs.
    """

    name = models.CharField(max_length=50)
    group = models.ForeignKey(ParameterGroup, on_delete=models.CASCADE)

    _list_view_fields = {
        "Name": "name",
        "Group": "group",
    }
    
    def __str__(self):
        return self.name

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
        LocationVisit, on_delete=models.CASCADE, related_name="samples",
        blank=True, null=True
    )
    measured_on = models.DateField(blank=True, null=True)
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    parameter_group = models.ForeignKey(ParameterGroup, on_delete=models.PROTECT)
    container_type = models.CharField(max_length=50, blank=True, null=True)
    volume_collected = models.FloatField(blank=True, null=True)
    replica_number = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    
    _list_view_fields = {
        "Location visit": "location_visit",
        "Target Parameters": "parameter_group",
        "Replica Number": "replica_number",
    }

    _detail_view_fields = {
        "Location Visit": "location_visit",
        "Measured At": "measured_on",
        "Target Parameters": "parameter_group",
        "Container Type": "container_type",
        "Volume Collected": "volume_collected",
        "Replica Number": "replica_number",
        "Created": "created",
        "Modified": "modified",
    }

    def __str__(self):
        return f"{self.location_visit.fieldwork.date:%Y%m%d}/{slugify(self.location_visit.location.name)}/{self.parameter_group}/{self.replica_number}"


class Measurement(TimeStampedModel, ModelTemplateInterface):
    """Individual measurements of parameters in a sample.

    It is possible to create a sample first, let's say in the field when it's taken, and
    then add the measurements later when the analysis is done.
    """
    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE, related_name="measurements"
    )
    parameter = models.ForeignKey(Parameter, on_delete=models.PROTECT)
    value = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)

    _list_view_fields = {
        "Sample": "sample",
        "Parameter": "parameter",
        "Value": "value",
        "Unit": "unit",
    }

    _detail_view_fields = {
        "Sample": "sample",
        "Parameter": "parameter",
        "Value": "value",
        "Unit": "unit",
        "Created": "created",
        "Modified": "modified",
    }

    create_bulk = True

    def __str__(self):
        return f"{self.sample} - {self.parameter}"