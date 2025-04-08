from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    TimeInput,
    TimeField,
    DateInput,
    DateField,
    FloatField,
    IntegerField,
    HiddenInput,
    ModelForm,
    ModelMultipleChoiceField,
    Form,
    ChoiceField,
)

from watersync.core.generics.forms import FormWithDetailMixin
from watersync.core.generics.forms import HTMXChoiceField
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


class PiezometerDetailForm(Form):
    # Define fields based on your schema
    depth = FloatField(required=False, label="Depth (m)")
    diameter = FloatField(required=False, label="Diameter (mm)")
    material = ChoiceField(
        required=False, choices=[("pvc", "PVC"), ("steel", "Steel"), ("other", "Other")]
    )


class LakeDetailForm(Form):
    depth = FloatField(required=False, label="Depth (m)")
    area = FloatField(required=False, label="Area (m²)")
    volume = FloatField(required=False, label="Volume (m³)")
    water_quality = CharField(
        required=False,
        label="Water Quality",
        widget=CharField.widget(attrs={"placeholder": "e.g. Clear, Murky"}),
    )

class WastewaterDetailForm(Form):
    number_of_tanks = IntegerField(required=False, label="Number of tanks")
    treatment_level = IntegerField(required=False, label="Treatment level")

class RiverDetailForm(Form):
    width = FloatField(required=False, label="Width (m)")
    depth = FloatField(required=False, label="Depth (m)")
    flow_rate = FloatField(required=False, label="Flow rate (m³/s)")

class PrecipitationDetailForm(Form):
    intensity = FloatField(required=False, label="Intensity (mm/h)")
    duration = IntegerField(required=False, label="Duration (minutes)")

class LocationForm(FormWithDetailMixin):
    """Temporary solution to the geometry not being properly created is to make the gemo field a CharField
    and not required. The latitude and longitude fields are used to create the geometry field in update_form_instance method."""

    title = "Add or Edit Location"
    latitude = FloatField(required=False, label="Latitude", initial=0)
    longitude = FloatField(required=False, label="Longitude")
    # geom field is important because in the template latitude and longitude are used to
    # populate the geometry from coordinates
    geom = CharField(required=False, widget=HiddenInput())
    type = HTMXChoiceField(
        choices=Location.LOCATION_TYPES,
        required=True,
        label="Type",
    )

    detail_forms = {
        "well": PiezometerDetailForm,
        "lake": LakeDetailForm,
        "wastewater": WastewaterDetailForm,
        "river": RiverDetailForm,
        "precipitation": PrecipitationDetailForm,
    }

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
            "project": HiddenInput(),
            "detail": HiddenInput(),
        }
