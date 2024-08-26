from django.forms import ModelForm, DateInput, HiddenInput
from watersync.core.models import Project, Location
from leaflet.forms.widgets import LeafletWidget

"""Some things to do here:

    1. Validate that the start date is not after the end date.
    2. Include a nicer date picker.
"""


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'location': LeafletWidget(),
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ('altitude', 'type', 'name', 'description',
                  'geom', 'detail')
        widgets = {
            'geom': LeafletWidget(),
            'detail': HiddenInput()
        }
