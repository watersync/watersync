from watersync.waterquality.models_setup import Protocol


from django import forms

from watersync.waterquality.models_setup import Parameter, ParameterGroup


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


class ParameterForm(forms.ModelForm):
    title = "Add Parameter"

    class Meta:
        model = Parameter
        fields = ["name", "group"]


class TargetParameterGroupForm(forms.ModelForm):
    title = "Add Target Parameter Group"

    class Meta:
        model = ParameterGroup
        fields = ["name", "code", "description"]