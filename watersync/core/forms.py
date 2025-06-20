from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    TimeField,
    DateField,
    FloatField,
    IntegerField,
    HiddenInput,
    ModelForm,
    ModelMultipleChoiceField,
    Form,
    ChoiceField,
)

from bootstrap_datepicker_plus.widgets import TimePickerInput, DatePickerInput

from watersync.core.generics.forms import FormWithDetailMixin
from watersync.core.generics.forms import HTMXChoiceField
from watersync.core.models import Location, LocationVisit, Project, Fieldwork, Unit
from watersync.users.models import User
from django.db import models



class ProjectForm(ModelForm):
    """Temporarily there will be no geometry field in the form."""

    title = "Project Form"

    start_date = DateField(
        required=True,
        label="Start Date",
        widget=DatePickerInput(
            attrs={"placeholder": "Select start date", "autocomplete": "off"}
        ),
    )
    end_date = DateField(
        required=False,
        label="End Date",
        widget=DatePickerInput(
            attrs={"placeholder": "Select end date", "autocomplete": "off"},
            range_from="start_date",
        ),
    )

    user = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=CheckboxSelectMultiple,
        required=True,
        label="Project Members"
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
    title = "Location Status"

    class Meta:
        model = LocationVisit
        fields = ["fieldwork", "location", "status", "description"]

class UnitForm(ModelForm):
    title = "Unit Form"

    class Meta:
        model = Unit
        fields = ["symbol", "description"]


class FieldworkForm(ModelForm):
    title = "Fieldwork Form"

    date = DateField(
        required=True,
        label="Date",
        widget=DatePickerInput(
            attrs={"placeholder": "Select date", "autocomplete": "off"}
        ),
    )

    start_time = TimeField(
        required=True,
        label="Start Time",
        widget=TimePickerInput(
            attrs={"placeholder": "Select start time", "autocomplete": "off"}
        ),
    )

    end_time = TimeField(
        required=True,
        label="End Time",
        widget=TimePickerInput(
            attrs={"placeholder": "Select end time", "autocomplete": "off"}
        ),
    )

    user = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=CheckboxSelectMultiple,
        required=True,
        label="Fieldwork Members",
    )

    class Meta:
        model = Fieldwork
        fields = [
            "date",
            "start_time",
            "end_time",
            "weather",
            "description",
            "user"
        ]


class PiezometerDetailForm(Form):
    """Form for Piezometer details.
    
    Total length can be obtained by adding the top of piezometer and total depth.
    Screen length is the length of the perforated section of the piezometer.
    """
    class PiezometerMaterialTypes(models.TextChoices):
        PVC = "pvc", "PVC"
        STEEL = "steel", "Steel"
        OTHER = "other", "Other"

    class PiezometerDrillTypes(models.TextChoices):
        HAND_DRILL = "hand_drill", "Hand Drill"
        GEOPROBE = "geoprobe", "Geoprobe"
        SONIC_RIG = "sonic_rig", "Sonic Rig"
        OTHER = "other", "Other"

    depth = FloatField(required=True, label="Total depth below ground (m)")
    top_of_piezometer = FloatField(
        required=True, label="Top of Piezometer below (-)/above ground (+) (m)"
    )
    top_of_screen = FloatField(
        required=True, label="Top of Screen below ground (+) (m)"
    )
    bottom_of_screen = FloatField(
        required=True, label="Bottom of Screen below ground (+) (m)"
    )
    drill_type = ChoiceField(
        required=True, choices=PiezometerDrillTypes.choices, label="Drill Type"
    )
    diameter = FloatField(required=True, label="Diameter (mm)")
    material = ChoiceField(
        required=True, choices=PiezometerMaterialTypes.choices, label="Material"
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
