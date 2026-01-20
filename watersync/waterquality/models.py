"""The workflow of collecting data looks as follows:

A sample (Sample) of physicochemical parameters is registered as STN-YYYYMMDD-PARAMS
Other samples (Sample) are defined, e.g., for nutrients (NUT), metals (MET), etc.
Once the measurements (MEASUREMENT) are completed, they are created and linked to the previously created samples.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from watersync.core.config import (
    get_all_wq_unit_choices,
    get_parameter_choices,
    get_parameter_group_choices,
    get_parameter_label,
    get_wq_unit_label,
    is_valid_unit_for_parameter,
)
from watersync.core.generics.interfaces import InterfaceModelTemplate, ModelURLMixin
from watersync.waterquality.models_setup import Protocol


class Sample(models.Model, InterfaceModelTemplate, ModelURLMixin):
    """Samples taken for analysis.

    Each sample represents a volume of water collected for analysis of specific parameters.
    The sample is linked to a specific location, fieldwork and protocol.

    Attributes:
        fieldwork: The fieldwork associated with the sample.
        location: The location where the sample was taken.
        protocol: The protocol used for the sample.
        target_parameters: The parameters targeted for analysis in the sample.
        container_type: The type of container used for the sample.
        volume_collected: The volume of water collected in the
            sample.
    """

    # URL configuration for ModelURLMixin
    # Sample URLs are: /projects/<project_pk>/samples/<sample_pk>/
    # We need to traverse: sample.location.project to get project_pk
    _url_app_label = "waterquality"""
    # In case of internal samples, fieldwork is required
    fieldwork = models.ForeignKey(
        "core.Fieldwork", on_delete=models.CASCADE, related_name="samples",
        blank=True, null=True
    )
    location = models.ForeignKey(
        "core.Location", on_delete=models.CASCADE, related_name="samples",
        blank=True, null=True
    )
    measured_on = models.DateField(blank=True, null=True)
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    parameter_group = models.CharField(
        max_length=50,
        help_text="The group of parameters targeted for analysis",
    )
    container_type = models.CharField(max_length=50, blank=True, null=True)
    volume_collected = models.FloatField(blank=True, null=True)
    replica_number = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    # in case of external samples, provide the source, location and date
    is_external = models.BooleanField(default=False)
    source = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    
    _list_view_fields = {
        "Location": "location",
        "Fieldwork": "fieldwork",
        "Target Parameters": "parameter_group",
        "Replica Number": "replica_number",
    }

    _detail_view_fields = {
        "Location": "location",
        "Fieldwork": "fieldwork",
        "Measured At": "measured_on",
        "Target Parameters": "parameter_group",
        "Container Type": "container_type",
        "Volume Collected": "volume_collected",
        "Replica Number": "replica_number",
    }

    def _get_url_kwargs(self):
        """Build URL kwargs. Sample URLs need project_pk from location.project."""
        kwargs = {"sample_pk": self.pk}
        if self.location and self.location.project:
            kwargs["project_pk"] = self.location.project.pk
        return kwargs

    def __str__(self):
        return f"{self.fieldwork.date:%Y%m%d}/{slugify(self.location.name)}/{self.parameter_group}/{self.replica_number}"

class Measurement(models.Model, InterfaceModelTemplate, ModelURLMixin):
    """Individual measurements of parameters in a sample.

    It is possible to create a sample first, let's say in the field when it's taken, and
    then add the measurements later when the analysis is done.

    Uses config-based parameter and unit definitions with Pint integration
    for unit conversions.
    """

    # URL configuration for ModelURLMixin
    # Measurement URLs are: /projects/<project_pk>/measurements/<measurement_pk>/
    _url_app_label = "waterquality"

    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE, related_name="measurements"
    )
    parameter = models.CharField(
        max_length=50,
        help_text="The parameter measured",
    )
    value = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        help_text="The measured value",
    )
    unit = models.CharField(
        max_length=50,
        help_text="The unit of measurement",
    )
    detection_limit = models.DecimalField(
        max_digits=20,
        decimal_places=10,
        null=True,
        blank=True,
        help_text="The detection limit value (same unit as measurement)",
    )

    _list_view_fields = {
        "Sample": "sample",
        "Parameter": "parameter_display",
        "Value": "formatted_value",
        "Detection Limit": "formatted_detection_limit",
    }

    _detail_view_fields = {
        "Sample": "sample",
        "Parameter": "parameter_display",
        "Measurement": "formatted_value",
        "Unit": "unit_display",
        "Detection Limit": "formatted_detection_limit",
    }

    _has_bulk_create = True
    _detail_type = "modal"

    def _get_url_kwargs(self):
        """Build URL kwargs. Measurement URLs need project_pk from sample.location.project."""
        kwargs = {"measurement_pk": self.pk}
        if self.sample and self.sample.location and self.sample.location.project:
            kwargs["project_pk"] = self.sample.location.project.pk
        return kwargs

    def __str__(self):
        return f"{self.sample} - {self.parameter_display}: {self.formatted_value}"

    def clean(self):
        """Validate that the unit is valid for the selected parameter."""
        super().clean()
        if self.parameter and self.unit:
            if not is_valid_unit_for_parameter(self.parameter, self.unit):
                raise ValidationError({
                    "unit": f"'{self.unit}' is not a valid unit for parameter '{self.parameter_display}'"
                })

    @property
    def parameter_display(self):
        """Get human-readable parameter label."""
        return get_parameter_label(self.parameter)

    @property
    def unit_display(self):
        """Get human-readable unit label."""
        return get_wq_unit_label(self.unit)

    @property
    def formatted_value(self):
        """Get the measurement as a formatted string with unit."""
        if self.value is None:
            return None
        return f"{self.value} {self.unit}"

    @property
    def formatted_detection_limit(self):
        """Get the detection limit as a formatted string with unit."""
        if self.detection_limit is None:
            return None
        return f"< {self.detection_limit} {self.unit}"

    @property
    def measurement(self):
        """Get the measurement as a Pint Quantity object."""
        if self.value is None:
            return None
        try:
            return settings.UREG.Quantity(float(self.value), self.unit)
        except (ValueError, TypeError):
            return None

    @property
    def detection_limit_quantity(self):
        """Get the detection limit as a Pint Quantity object."""
        if self.detection_limit is None:
            return None
        try:
            return settings.UREG.Quantity(float(self.detection_limit), self.unit)
        except (ValueError, TypeError):
            return None

    def convert_to(self, target_unit):
        """Convert the measurement to a different unit."""
        measurement = self.measurement
        if measurement is None:
            return None

        try:
            return measurement.to(target_unit)
        except Exception as e:
            raise ValueError(f"Cannot convert to '{target_unit}': {e}")

    def is_compatible_with(self, other_unit):
        """Check if the measurement can be converted to another unit."""
        measurement = self.measurement
        if measurement is None:
            return False

        try:
            test_unit = settings.UREG(other_unit)
            return measurement.dimensionality == test_unit.dimensionality
        except Exception:
            return False

    def get_standard_unit_value(self):
        """Get the measurement value in a standard unit for its type."""
        measurement = self.measurement
        if measurement is None:
            return None

        # Define standard units based on dimensionality
        dimensionality_standards = {
            "[mass] / [length] ** 3": "milligram/liter",  # concentration
            "[temperature]": "celsius",  # temperature
            "[length]": "meter",  # length/depth
            "[current] / [length] ** 2": "microsiemens/centimeter",  # conductivity
            "[mass] * [length] ** 2 / [current] / [time] ** 3": "millivolt",  # voltage
            "[turbidity]": "NTU",  # turbidity (custom dimension)
            "[count]": "CFU",  # bacterial count (custom dimension)
            "[acidity]": "pH_unit",  # pH (custom dimension)
            "": "dimensionless",  # dimensionless quantities
        }

        dim_str = str(measurement.dimensionality)
        standard_unit = dimensionality_standards.get(dim_str)

        if standard_unit:
            try:
                return measurement.to(standard_unit)
            except Exception:
                pass

        return measurement  # Return as-is if no standard conversion available

    class Meta:
        # Ensure only one measurement per sample/parameter combination
        unique_together = ("sample", "parameter")