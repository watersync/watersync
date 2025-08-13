"""The workflow of collecting data looks as follows:

A sample (Sample) of physicochemical parameters is registered as STN-YYYYMMDD-PARAMS
Other samples (Sample) are defined, e.g., for nutrients (NUT), metals (MET), etc.
Once the measurements (MEASUREMENT) are completed, they are created and linked to the previously created samples.
"""

from django.db import models
from django.utils.text import slugify
from django.conf import settings

from watersync.core.generics.interfaces import InterfaceModelTemplate
from watersync.waterquality.models_setup import Parameter, ParameterGroup, Protocol

class Sample(models.Model, InterfaceModelTemplate):
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
    parameter_group = models.ForeignKey(ParameterGroup, on_delete=models.PROTECT)
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

    def __str__(self):
        return f"{self.fieldwork.date:%Y%m%d}/{slugify(self.location.name)}/{self.parameter_group.code}/{self.replica_number}"

class Measurement(models.Model, InterfaceModelTemplate):
    """Individual measurements of parameters in a sample.

    It is possible to create a sample first, let's say in the field when it's taken, and
    then add the measurements later when the analysis is done.
    
    This model uses a hybrid approach with JSONField to store Pint quantities,
    providing flexibility while maintaining unit conversion capabilities.
    """
    sample = models.ForeignKey(
        Sample, on_delete=models.CASCADE, related_name="measurements"
    )
    parameter = models.ForeignKey(Parameter, on_delete=models.PROTECT)
    measurement_data = models.JSONField(
        help_text="JSON field storing measurement value and unit information"
    )
    detection_limit_data = models.JSONField(
        null=True, blank=True,
        help_text="JSON field storing detection limit value and unit information"
    )

    _list_view_fields = {
        "Sample": "sample",
        "Parameter": "parameter",
        "Value1": "measurement",
        "Detection Limit": "detection_limit",
    }

    _detail_view_fields = {
        "Sample": "sample",
        "Parameter": "parameter",
        "Measurement": "measurement",
        "Detection Limit": "detection_limit",
    }

    create_bulk = True

    def __str__(self):
        return f"{self.sample} - {self.parameter}: {self.measurement}"
    
    @property
    def measurement(self):
        """Get the measurement as a Pint Quantity object."""
        if not self.measurement_data:
            return None
        
        try:
            magnitude = self.measurement_data.get("magnitude")
            unit = self.measurement_data.get("unit")
            
            if magnitude is not None and unit:
                return settings.UREG.Quantity(magnitude, unit)
        except (ValueError, TypeError, KeyError):
            pass
        
        return None
    
    @measurement.setter
    def measurement(self, quantity):
        """Set the measurement from a Pint Quantity object."""
        print(f"Setting measurement: {quantity}")
        if quantity is None:
            self.measurement_data = None
        else:
            print(f"Setting measurement data: {quantity}")
            self.measurement_data = {
                "magnitude": float(quantity.magnitude),
                "unit": str(quantity.units),
                "dimensionality": str(quantity.dimensionality)
            }
            print(f"Measurement data set: {self.measurement_data}")
    
    @property
    def detection_limit(self):
        """Get the detection limit as a Pint Quantity object."""
        if not self.detection_limit_data:
            return None

        try:
            magnitude = self.detection_limit_data.get("magnitude")
            unit_str = self.detection_limit_data.get("unit")

            if magnitude is not None and unit_str:
                return settings.UREG.Quantity(magnitude, unit_str)
        except (ValueError, TypeError, KeyError):
            pass
            
        return None
    
    @detection_limit.setter
    def detection_limit(self, quantity):
        """Set the detection limit from a Pint Quantity object."""
        if quantity is None:
            self.detection_limit_data = None
        else:
            self.detection_limit_data = {
                "magnitude": float(quantity.magnitude),
                "unit": str(quantity.units),
                "dimensionality": str(quantity.dimensionality)
            }

    def convert_to(self, target_unit):
        """Convert the measurement to a different unit."""
        measurement = self.measurement
        if not measurement:
            return None
            
        try:
            return measurement.to(target_unit)
        except Exception as e:
            raise ValueError(f"Cannot convert to '{target_unit}': {e}")
    
    def is_compatible_with(self, other_unit):
        """Check if the measurement can be converted to another unit."""
        measurement = self.measurement
        if not measurement:
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
            "": "dimensionless"  # dimensionless quantities
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