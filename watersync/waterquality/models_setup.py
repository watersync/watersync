from django.utils.text import slugify
from watersync.core.generics.interfaces import InterfaceModelTemplate


from django.db import models


class ParameterGroup(models.Model, InterfaceModelTemplate):
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


class Parameter(models.Model, InterfaceModelTemplate):
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
    code = models.CharField(max_length=10, unique=True)
    group = models.ForeignKey(ParameterGroup, on_delete=models.CASCADE)

    _list_view_fields = {
        "Name": "name",
        "Group": "group",
    }

    def __str__(self):
        return self.name


class Protocol(models.Model, InterfaceModelTemplate):
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