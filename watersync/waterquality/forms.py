from watersync.waterquality.models import Protocol, SamplingEvent, Sample, Measurement
from django import forms
from django.forms import HiddenInput, DateTimeInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div


class ProtocolForm(forms.ModelForm):
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
            "details",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Protocol Details",
                "method_name",
                Div("sample_collection", css_class="form-group"),
                Div("sample_preservation", css_class="form-group"),
                Div("sample_storage", css_class="form-group"),
                Div("analytical_method", css_class="form-group"),
                Div("data_postprocessing", css_class="form-group"),
                Div("standard_reference", css_class="form-group"),
                Div("details", css_class="form-group"),
            ),
            Submit("submit", "Save Protocol", css_class="btn btn-primary"),
        )


class SamplingEventForm(forms.ModelForm):
    class Meta:
        model = SamplingEvent
        fields = ("location", "executed_at", "executed_by")
        widgets = {
            "executed_at": DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Sampling Event Details",
                "location",
                "executed_at",
                "executed_by",
            ),
            Submit("submit", "Save Sampling Event", css_class="btn btn-primary"),
        )


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = (
            "sampling_event",
            "protocol",
            "target_parameters",
            "container_type",
            "volume_collected",
            "details",
            "replica_number",
        )
        widgets = {
            "details": HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Sample Details",
                "sampling_event",
                "protocol",
                "target_parameters",
                "container_type",
                "volume_collected",
                "replica_number",
                Div("details", css_class="form-group"),
            ),
            Submit("submit", "Save Sample", css_class="btn btn-primary"),
        )


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ("sample", "parameter_name", "value", "unit", "measured_on", "details")
        widgets = {
            "details": HiddenInput(),
            "measured_on": DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Measurement Details",
                "sample",
                "parameter_name",
                "value",
                "unit",
                "measured_on",
                Div("details", css_class="form-group"),
            ),
            Submit("submit", "Save Measurement", css_class="btn btn-primary"),
        )
