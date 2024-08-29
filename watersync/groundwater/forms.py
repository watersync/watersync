from django.forms import ModelForm, DateTimeInput
from watersync.groundwater.models import GWLManualMeasurements
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column


class GWLForm(ModelForm):
    class Meta:
        model = GWLManualMeasurements
        fields = ('depth', 'timestamp', 'comment')
        widgets = {
            'timestamp': DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('depth', css_class='form-group col-md-6 mb-0'),
                Column('timestamp', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('comment', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            )
        )
        self.helper.add_input(Submit('submit', 'Save measurement'))
