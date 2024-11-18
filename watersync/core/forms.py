from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from crispy_forms.layout import Submit
from django.contrib.gis.geos import Point
from django.forms import (
    DateInput,
    ModelMultipleChoiceField,
    FloatField,
    HiddenInput,
    ModelForm,
    CheckboxSelectMultiple,
)


from watersync.core.models import Location
from watersync.core.models import LocationStatus
from watersync.core.models import Project
from watersync.users.models import User


class ProjectForm(ModelForm):
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


class LocationStatusForm(ModelForm):
    class Meta:
        model = LocationStatus
        fields = ["status", "comment"]


class LocationForm(ModelForm):
    latitude = FloatField(required=False, label="Latitude")
    longitude = FloatField(required=False, label="Longitude")

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
        )
        widgets = {
            "detail": HiddenInput(),
            "geom": HiddenInput(),
        }

    def save(self, commit=True):
        instance = super(LocationForm, self).save(commit=False)

        latitude = self.cleaned_data.get("latitude")
        longitude = self.cleaned_data.get("longitude")
        if latitude is not None and longitude is not None:
            instance.geom = Point(longitude, latitude, srid=4326)

        if commit:
            instance.save()
        return instance
