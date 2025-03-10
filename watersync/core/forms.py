from django.contrib.gis.geos import Point
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    DateInput,
    FloatField,
    HiddenInput,
    ModelForm,
    ModelMultipleChoiceField,
)

from watersync.core.models import Location, LocationVisit, Project, Fieldwork
from watersync.users.models import User


class ProjectForm(ModelForm):
    title = "Add Project"
    latitude = FloatField(required=False, label="Latitude")
    longitude = FloatField(required=False, label="Longitude")
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
            "latitude",
            "longitude",
            "geom",
        ]
        widgets = {
            "start_date": DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "end_date": DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "geom": HiddenInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        latitude = self.cleaned_data.get("latitude")
        longitude = self.cleaned_data.get("longitude")
        if latitude is not None and longitude is not None:
            instance.geom = Point(longitude, latitude, srid=4326)

        if commit:
            instance.save()
            self.save_m2m()
        return instance


class LocationVisitForm(ModelForm):
    title = "Add Location Status"

    class Meta:
        model = LocationVisit
        fields = ["status", "comment"]


class FieldworkForm(ModelForm):
    title = "Fieldwork"

    class Meta:
        model = Fieldwork
        exclude = ["project"]


class LocationForm(ModelForm):
    """Temporary solution to the geometry not being properly created is to make the gemo field a CharField
    and not required. The latitude and longitude fields are used to create the geometry field in update_form_instance method."""

    title = "Add Location"
    detail_schema = "piezometer_detail_schema.json"
    latitude = FloatField(required=False, label="Latitude")
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
            "detail",
            "geom",
        )
        widgets = {
            "detail": HiddenInput(),
            "geom": HiddenInput(),
        }
