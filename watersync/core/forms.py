from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    TimeField,
    DateField,
    FloatField,
    HiddenInput,
    ModelForm,
    ModelMultipleChoiceField,
)

from bootstrap_datepicker_plus.widgets import TimePickerInput, DatePickerInput

from watersync.core.forms_detail import LakeDetailForm, PiezometerDetailForm, PrecipitationDetailForm, PumpingWellDetailForm, RiverDetailForm, WastewaterDetailForm
from watersync.core.generics.forms import FormWithDetailMixin, FormWithHistory
from watersync.core.generics.forms import HTMXChoiceField
from watersync.core.models import Location, Project, Fieldwork, Unit
from watersync.users.models import User



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
            "user",
        ]

class LocationForm(FormWithDetailMixin, FormWithHistory):
    """Temporary solution to the geometry not being properly created is to make the gemo field a CharField
    and not required. The latitude and longitude fields are used to create the geometry field in update_form_instance method."""

    title = "Add or Edit Location"
    latitude = FloatField(required=False, label="Latitude")
    longitude = FloatField(required=False, label="Longitude")
    altitude = FloatField(required=False, label="Altitude")
    # geom field is important because in the template latitude and longitude are used to
    # populate the geometry from coordinates
    geom = CharField(required=False, widget=HiddenInput())
    type = HTMXChoiceField(
        choices=Location.LocationTypes.choices,
        required=True,
        label="Type",
    )

    detail_forms = {
        "piezometer": PiezometerDetailForm,
        "pumping_well": PumpingWellDetailForm,
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
            "detail",
            "geom",
        )
        widgets = {
            "detail": HiddenInput(),
        }
