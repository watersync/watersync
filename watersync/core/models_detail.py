"""Detail models for Location types.

Each Location type can have specific detail information stored in a related
one-to-one model. This provides a structured schema while maintaining flexibility
for different location types.
"""

from django.db import models

from simple_history.models import HistoricalRecords

from watersync.core.generics.models import SetupSimpleHistory


class PiezometerDetail(models.Model, SetupSimpleHistory):
    """Detail information for Piezometer locations.

    Total length can be obtained by adding the casing_top and depth.
    Screen length is the length of the perforated section of the piezometer.
    """

    class MaterialTypes(models.TextChoices):
        PVC = "pvc", "PVC"
        STEEL = "steel", "Steel"
        OTHER = "other", "Other"

    class DrillTypes(models.TextChoices):
        HAND_AUGER = "hand_auger", "Hand Auger"
        DIRECT_PUSH = "direct_push", "Direct Push"
        ROTARY_DRILLING = "rotary_drilling", "Rotary Drilling"
        SONIC_RIG = "sonic_rig", "Sonic Rig"
        OTHER = "other", "Other"

    location = models.OneToOneField(
        "core.Location",
        on_delete=models.CASCADE,
        related_name="piezometer_detail",
        primary_key=True,
    )
    depth = models.FloatField(
        verbose_name="Total depth below ground (m)",
        help_text="Total depth of the piezometer below ground level in meters",
    )
    casing_top = models.FloatField(
        verbose_name="Top of Piezometer below (-)/above ground (+) (m)",
        help_text="Height of the casing top relative to ground level",
    )
    screen_top = models.FloatField(
        verbose_name="Top of Screen below ground (+) (m)",
        help_text="Depth to the top of the screen section below ground",
    )
    screen_bottom = models.FloatField(
        verbose_name="Bottom of Screen below ground (+) (m)",
        help_text="Depth to the bottom of the screen section below ground",
    )
    drill_type = models.CharField(
        max_length=20,
        choices=DrillTypes.choices,
        verbose_name="Drill Type",
    )
    profile_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Profile Description",
        help_text="e.g. Sandy, Clayey",
    )
    diameter = models.FloatField(
        verbose_name="Diameter (mm)",
        help_text="Internal diameter of the piezometer in millimeters",
    )
    material = models.CharField(
        max_length=20,
        choices=MaterialTypes.choices,
        verbose_name="Material",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Piezometer Detail"
        verbose_name_plural = "Piezometer Details"

    def __str__(self):
        return f"Piezometer detail for {self.location}"

    @property
    def total_length(self):
        """Calculate total length of the piezometer."""
        return self.casing_top + self.depth

    @property
    def screen_length(self):
        """Calculate the screen length."""
        return self.screen_bottom - self.screen_top


class PumpingWellDetail(models.Model, SetupSimpleHistory):
    """Detail information for Pumping Well locations."""

    location = models.OneToOneField(
        "core.Location",
        on_delete=models.CASCADE,
        related_name="pumping_well_detail",
        primary_key=True,
    )
    pumping_rate = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Pumping Rate (m³/h)",
        help_text="Pumping rate in cubic meters per hour",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Pumping Well Detail"
        verbose_name_plural = "Pumping Well Details"

    def __str__(self):
        return f"Pumping well detail for {self.location}"


class LakeDetail(models.Model, SetupSimpleHistory):
    """Detail information for Lake locations."""

    location = models.OneToOneField(
        "core.Location",
        on_delete=models.CASCADE,
        related_name="lake_detail",
        primary_key=True,
    )
    depth = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Depth (m)",
        help_text="Maximum depth of the lake in meters",
    )
    area = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Area (m²)",
        help_text="Surface area of the lake in square meters",
    )
    volume = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Volume (m³)",
        help_text="Total volume of the lake in cubic meters",
    )
    water_quality = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Water Quality",
        help_text="e.g. Clear, Murky",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Lake Detail"
        verbose_name_plural = "Lake Details"

    def __str__(self):
        return f"Lake detail for {self.location}"


class WastewaterDetail(models.Model, SetupSimpleHistory):
    """Detail information for Wastewater locations."""

    location = models.OneToOneField(
        "core.Location",
        on_delete=models.CASCADE,
        related_name="wastewater_detail",
        primary_key=True,
    )
    number_of_tanks = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Number of tanks",
    )
    treatment_level = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Treatment level",
        help_text="Treatment level indicator",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Wastewater Detail"
        verbose_name_plural = "Wastewater Details"

    def __str__(self):
        return f"Wastewater detail for {self.location}"


class RiverDetail(models.Model, SetupSimpleHistory):
    """Detail information for River locations."""

    location = models.OneToOneField(
        "core.Location",
        on_delete=models.CASCADE,
        related_name="river_detail",
        primary_key=True,
    )
    width = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Width (m)",
        help_text="Width of the river at the measurement point in meters",
    )
    depth = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Depth (m)",
        help_text="Depth of the river at the measurement point in meters",
    )
    flow_rate = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Flow rate (m³/s)",
        help_text="Flow rate of the river in cubic meters per second",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "River Detail"
        verbose_name_plural = "River Details"

    def __str__(self):
        return f"River detail for {self.location}"


class PrecipitationDetail(models.Model, SetupSimpleHistory):
    """Detail information for Precipitation measurement locations."""

    location = models.OneToOneField(
        "core.Location",
        on_delete=models.CASCADE,
        related_name="precipitation_detail",
        primary_key=True,
    )
    intensity = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Intensity (mm/h)",
        help_text="Rainfall intensity in millimeters per hour",
    )
    duration = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Duration (minutes)",
        help_text="Duration of precipitation event in minutes",
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Precipitation Detail"
        verbose_name_plural = "Precipitation Details"

    def __str__(self):
        return f"Precipitation detail for {self.location}"


# Mapping from Location.LocationTypes to detail model classes
LOCATION_TYPE_DETAIL_MODELS = {
    "piezometer": PiezometerDetail,
    "pumping_well": PumpingWellDetail,
    "lake": LakeDetail,
    "wastewater": WastewaterDetail,
    "river": RiverDetail,
    "precipitation": PrecipitationDetail,
}
