"""The workflow of collecting data looks as follows:

A sample (Sample) of physicochemical parameters is registered as STN-YYYYMMDD-PARAMS
Other samples (Sample) are defined, e.g., for nutrients (NUT), metals (MET), etc.
Once the measurements (MEASUREMENT) are completed, they are created and linked to the previously created samples.
"""


from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from simple_history.models import HistoricalRecords

from watersync.core.config import (
    get_parameter_label,
    get_wq_unit_label,
    is_valid_unit_for_parameter,
)
from watersync.core.generics.managers import (
    LocationWithCountsManager,
    SoftDeleteLocationScopedManager,
)
from watersync.core.generics.models import SetupSimpleHistory, SoftDeleteMixin
from watersync.waterquality.models_setup import Protocol


class Sample(models.Model, SetupSimpleHistory):
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

    # Link lab samples to their associated field measurement sample
    field_sample = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_samples',
        help_text="Link to the field measurement sample (PARAMS) taken at the same time/location"
    )

    # in case of external samples, provide the source, location and date
    is_external = models.BooleanField(default=False)
    source = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    objects = LocationWithCountsManager()
    history = HistoricalRecords()

    # Fields to count in with_counts() - used for overview pages
    _count_fields = ['measurements']

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

    def __str__(self):
        date_str = self.fieldwork.date.strftime("%Y%m%d") if self.fieldwork else "no-date"
        location_str = slugify(self.location.name) if self.location else "no-location"
        return f"{date_str}/{location_str}/{self.parameter_group}/{self.replica_number}"

    def clean(self):
        """Validate field_sample only points to FIELD parameter samples."""
        super().clean()
        if self.field_sample:
            if self.field_sample.parameter_group != 'FIELD':
                raise ValidationError({
                    'field_sample': "Can only link to a Field Parameters sample"
                })
            if self.field_sample_id == self.pk:
                raise ValidationError({
                    'field_sample': "A sample cannot link to itself"
                })

    def get_field_measurements(self):
        """Get associated field measurements.
        
        For FIELD samples, returns own measurements.
        For lab samples with a linked field_sample, returns field_sample's measurements.
        """
        if self.parameter_group == 'FIELD':
            return self.measurements.all()
        elif self.field_sample:
            return self.field_sample.measurements.all()
        return Measurement.objects.none()

    def get_all_measurements(self):
        """Get both field and lab measurements together.
        
        For lab samples, combines the linked field measurements with own lab measurements.
        """
        field = self.get_field_measurements()
        lab = self.measurements.all() if self.parameter_group != 'FIELD' else Measurement.objects.none()
        return field | lab


class Measurement(SoftDeleteMixin, models.Model):
    """Individual measurements of parameters in a sample.

    It is possible to create a sample first, let's say in the field when it's taken, and
    then add the measurements later when the analysis is done.

    Records are immutable: update not allowed, use delete and recreate.
    Soft delete: records are marked deleted but preserved in database.

    Uses config-based parameter and unit definitions with Pint integration
    for unit conversions.
    """

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

    # Record creation tracking
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="measurements_created",
    )

    objects = SoftDeleteLocationScopedManager()

    # Records are immutable - no update allowed
    _has_update = False
    _has_bulk_create = True

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