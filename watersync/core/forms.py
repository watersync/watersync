from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Row
from crispy_forms.layout import Submit
from django.contrib.gis.geos import Point
from django.forms import DateInput
from django.forms import FloatField
from django.forms import HiddenInput
from django.forms import ModelForm

from watersync.core.models import Location
from watersync.core.models import LocationStatus
from watersync.core.models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
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
