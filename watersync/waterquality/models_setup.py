"""
Water Quality Setup Models

This module contains setup/configuration models that are user-defined
and need database storage. Parameter groups and individual parameters
are now defined in YAML config files - see config/parameters/water_quality.yaml.

Use watersync.core.config for accessing parameter definitions.
"""

from django.db import models
from django.utils.text import slugify

from simple_history.models import HistoricalRecords


class Protocol(models.Model):
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

    history = HistoricalRecords()

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