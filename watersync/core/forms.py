from django.forms import ModelForm
from watersync.core.models import Project, Location
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from leaflet.forms.widgets import LeafletWidget


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'location')
        widgets = {
            'location': LeafletWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save project'))


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ('altitude', 'type', 'name', 'description',
                  'geom', 'detail')
        widgets = {
            'geom': LeafletWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save project'))
