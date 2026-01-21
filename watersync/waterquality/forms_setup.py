"""
Water Quality Setup Forms

Forms for user-defined setup models. Parameter and ParameterGroup forms
have been removed as those are now config-based (see config/parameters/water_quality.yaml).
"""

from django import forms

from watersync.waterquality.models_setup import Protocol


class ProtocolForm(forms.ModelForm):
    title = "Add Protocol"

    class Meta:
        model = Protocol
        fields = [
            "method_name",
            "sample_collection",
            "sample_preservation",
            "sample_storage",
            "analytical_method",
            "data_postprocessing",
            "standard_reference",
            "description",
        ]