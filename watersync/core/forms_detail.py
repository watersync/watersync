from django.db import models
from django.forms import CharField, ChoiceField, FloatField, Form, IntegerField


class PiezometerDetailForm(Form):
    """Form for Piezometer details.

    Total length can be obtained by adding the top of piezometer and total depth.
    Screen length is the length of the perforated section of the piezometer.
    """
    class PiezometerMaterialTypes(models.TextChoices):
        PVC = "pvc", "PVC"
        STEEL = "steel", "Steel"
        OTHER = "other", "Other"

    class PiezometerDrillTypes(models.TextChoices):
        HAND_AUGER = "hand_auger", "Hand Auger"
        DIRECT_PUSH = "direct_push", "Direct Push"
        ROTARY_DRILLING = "rotary_drilling", "Rotary Drilling"
        SONIC_RIG = "sonic_rig", "Sonic Rig"
        OTHER = "other", "Other"

    depth = FloatField(required=True, label="Total depth below ground (m)")
    casing_top = FloatField(
        required=True, label="Top of Piezometer below (-)/above ground (+) (m)"
    )
    screen_top = FloatField(
        required=True, label="Top of Screen below ground (+) (m)"
    )
    screen_bottom = FloatField(
        required=True, label="Bottom of Screen below ground (+) (m)"
    )
    drill_type = ChoiceField(
        required=True, choices=PiezometerDrillTypes.choices, label="Drill Type"
    )
    profile_description = CharField(
        required=False,
        label="Profile Description",
        widget=CharField.widget(attrs={"placeholder": "e.g. Sandy, Clayey"}),
    )
    diameter = FloatField(required=True, label="Diameter (mm)")
    material = ChoiceField(
        required=True, choices=PiezometerMaterialTypes.choices, label="Material"
    )


class PumpingWellDetailForm(Form):
    """Form for Pumping Well details."""
    pumping_rate = FloatField(
        required=False, label="Pumping Rate (m³/h)",
        widget=CharField.widget(attrs={"placeholder": "e.g. 10 m³/h"})
    )


class LakeDetailForm(Form):
    depth = FloatField(required=False, label="Depth (m)")
    area = FloatField(required=False, label="Area (m²)")
    volume = FloatField(required=False, label="Volume (m³)")
    water_quality = CharField(
        required=False,
        label="Water Quality",
        widget=CharField.widget(attrs={"placeholder": "e.g. Clear, Murky"}),
    )


class WastewaterDetailForm(Form):
    number_of_tanks = IntegerField(required=False, label="Number of tanks")
    treatment_level = IntegerField(required=False, label="Treatment level")


class RiverDetailForm(Form):
    width = FloatField(required=False, label="Width (m)")
    depth = FloatField(required=False, label="Depth (m)")
    flow_rate = FloatField(required=False, label="Flow rate (m³/s)")


class PrecipitationDetailForm(Form):
    intensity = FloatField(required=False, label="Intensity (mm/h)")
    duration = IntegerField(required=False, label="Duration (minutes)")