from django.forms import ModelForm
from watersync.groundwater.models import GWLManualMeasurements
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class GWLForm(ModelForm):
    class Meta:
        model = GWLManualMeasurements
        fields = ('depth', 'timestamp', 'comment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save project'))
