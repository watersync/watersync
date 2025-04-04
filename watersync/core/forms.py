from django.contrib.gis.geos import Point
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    TimeInput,
    TimeField,
    DateInput,
    DateField,
    FloatField,
    HiddenInput,
    ModelForm,
    ModelMultipleChoiceField,
)

from watersync.core.models import Location, LocationVisit, Project, Fieldwork
from watersync.users.models import User

class ProjectForm(ModelForm):
    """Temporarily there will be no geometry field in the form."""
    title = "Add Project"
    user = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=CheckboxSelectMultiple,
        required=True,
    )

    class Meta:
        model = Project
        fields = [
            "name",
            "is_active",
            "description",
            "start_date",
            "end_date",
            "user",
        ]


    def save(self, commit=True):
        instance = super().save(commit=False)

        # Here comes the logic to create geometry in non-standard way

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class LocationVisitForm(ModelForm):
    title = "Add Location Status"

    class Meta:
        model = LocationVisit
        fields = ["location", "status", "description"]


class FieldworkForm(ModelForm):
    title = "Fieldwork"
    user = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=CheckboxSelectMultiple,
        required=True,
    )
    date = DateField(
        widget=DateInput(attrs={"type": "date"}),
        required=True,
    )
    start_time = TimeField(
        widget=TimeInput(attrs={"type": "time"}),
        required=False,
    )
    end_time = TimeField(
        widget=TimeInput(attrs={"type": "time"}),
        required=False,
    )

    class Meta:
        model = Fieldwork
        exclude = ["project"]


class LocationForm(ModelForm):
    """Temporary solution to the geometry not being properly created is to make the gemo field a CharField
    and not required. The latitude and longitude fields are used to create the geometry field in update_form_instance method."""

    title = "Add Location"
    detail_schema = "piezometer_detail_schema.json"
    latitude = FloatField(required=False, label="Latitude", initial=0)
    longitude = FloatField(required=False, label="Longitude")
    geom = CharField(required=False)

    class Meta:
        model = Location
        fields = (
            "name",
            "type",
            "description",
            "altitude",
            "latitude",
            "longitude",
            "project",
            "detail",
            "geom",
        )
        widgets = {
            # "project": HiddenInput(),
            "detail": HiddenInput(),
            "geom": HiddenInput(),
        }
