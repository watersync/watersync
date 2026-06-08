from django.forms import ModelForm

from watersync.core.models_detail import (
    LakeDetail,
    PiezometerDetail,
    PrecipitationDetail,
    PumpingWellDetail,
    RiverDetail,
    WastewaterDetail,
)


class PiezometerDetailForm(ModelForm):
    """Form for Piezometer details.

    Total length can be obtained by adding the top of piezometer and total depth.
    Screen length is the length of the perforated section of the piezometer.
    """

    class Meta:
        model = PiezometerDetail
        fields = [
            "depth",
            "casing_top",
            "screen_top",
            "screen_bottom",
            "drill_type",
            "profile_description",
            "diameter",
            "material",
        ]


class PumpingWellDetailForm(ModelForm):
    """Form for Pumping Well details."""

    class Meta:
        model = PumpingWellDetail
        fields = ["pumping_rate"]


class LakeDetailForm(ModelForm):
    """Form for Lake details."""

    class Meta:
        model = LakeDetail
        fields = ["depth", "area", "volume", "water_quality"]


class WastewaterDetailForm(ModelForm):
    """Form for Wastewater details."""

    class Meta:
        model = WastewaterDetail
        fields = ["number_of_tanks", "treatment_level"]


class RiverDetailForm(ModelForm):
    """Form for River details."""

    class Meta:
        model = RiverDetail
        fields = ["width", "depth", "flow_rate"]


class PrecipitationDetailForm(ModelForm):
    """Form for Precipitation details."""

    class Meta:
        model = PrecipitationDetail
        fields = ["intensity", "duration"]


# Mapping from location type to detail form class
LOCATION_TYPE_DETAIL_FORMS = {
    "piezometer": PiezometerDetailForm,
    "pumping_well": PumpingWellDetailForm,
    "lake": LakeDetailForm,
    "wastewater": WastewaterDetailForm,
    "river": RiverDetailForm,
    "precipitation": PrecipitationDetailForm,
}