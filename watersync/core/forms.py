from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from crispy_forms.layout import Submit
from django.contrib.gis import forms
from django.contrib.gis.geos import Point
from django.forms import DateInput
from django.forms import FloatField
from django.forms import HiddenInput
from django.forms import ModelForm
from leaflet.forms.widgets import LeafletWidget

from watersync.core.models import Location
from watersync.core.models import LocationStatus
from watersync.core.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "location": LeafletWidget(),
            "start_date": DateInput(attrs={"type": "date"}),
            "end_date": DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group col-md-6 mb-0"),
                Column("is_active", css_class="form-group col-md-6 mb-0"),
                Field("description", css_class="form-group col-md-12"),
                css_class="card mb-3 p-2",
            ),
            Row(
                Column("start_date", css_class="col-md-6 mb-0"),
                Column("end_date", css_class="col-md-6 mb-0"),
                css_class="card mb-3 p-2",
            ),
            Field("user", css_class="card mb-3 p-2"),
            Field("location", css_class="card mb-3 p-2"),
        )
        self.helper.add_input(Submit("submit", "Save project"))


class LocationStatusForm(forms.ModelForm):
    class Meta:
        model = LocationStatus
        fields = ["status", "comment"]


class LocationForm(ModelForm):
    latitude = FloatField(required=False, label="Latitude")
    longitude = FloatField(required=False, label="Longitude")
    geom = forms.PointField(required=False)

    class Meta:
        model = Location
        fields = (
            "name",
            "type",
            "description",
            "altitude",
            "latitude",
            "longitude",
            "geom",
            "detail",
        )
        widgets = {
            "geom": HiddenInput(),  # Hide the geom field in the form
            "detail": HiddenInput(),
        }

    def save(self, commit=True):
        # Get the instance of the location but do not save it yet
        instance = super(LocationForm, self).save(commit=False)

        # If latitude and longitude are provided, create a Point and assign it to the geom field
        if (
            self.cleaned_data["latitude"] is not None
            and self.cleaned_data["longitude"] is not None
        ):
            instance.geom = Point(
                self.cleaned_data["longitude"], self.cleaned_data["latitude"], srid=4326
            )

        if commit:
            instance.save()

        return instance
