from django import forms
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    DateField,
    FileField,
    FloatField,
    HiddenInput,
    ModelChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    Textarea,
    TimeField,
)

from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput

from watersync.core.generics.forms import FormWithHistory, WatersyncBulkForm, WatersyncForm
from watersync.core.models import Fieldwork, Location, Project
from watersync.core.parsers import (
    check_duplicate_fieldwork_dates,
    parse_bulk_fieldwork_data,
    parse_bulk_fieldwork_file,
)
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


class FieldworkForm(WatersyncForm):
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
            "project",
            "date",
            "start_time",
            "end_time",
            "weather",
            "description",
            "user",
        ]


class FieldworkBulkForm(WatersyncBulkForm):
    """Form for bulk adding fieldwork entries from pasted data or file.

    Supports two input modes:
    - paste: Tab or comma separated text
    - file: CSV/Excel file upload
    
    Expected columns: date, start_time, end_time, weather, description (optional)
    """

    title = "Bulk Add Fieldwork"
    
    # Override INPUT_MODE_CHOICES for fieldwork-specific modes
    INPUT_MODE_CHOICES = [
        ("paste", "Paste Data"),
        ("file", "Upload File"),
    ]
    
    # 'bulk' and 'input_mode' inherited from WatersyncBulkForm
    
    project = ModelChoiceField(
        queryset=Project.objects.all(),
        label="Project",
        required=False,
        help_text="Select the project for these fieldwork entries.",
    )
    # Paste mode field
    data = CharField(
        label="Paste Data",
        help_text="Paste tab-separated or comma-separated data with columns: "
        "date, start_time, end_time, weather, description (optional).",
        required=False,
        widget=Textarea(attrs={"rows": 8}),
    )
    # File upload field
    file = FileField(
        label="Upload File",
        help_text="Upload a CSV or Excel file with columns: date, start_time, end_time, weather, description",
        required=False,
    )
    # Users to assign to all fieldwork entries
    user = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=CheckboxSelectMultiple,
        required=True,
        label="Assign Users",
        help_text="Select users to assign to all uploaded fieldwork entries.",
    )

    def clean(self):
        cleaned_data = super().clean()
        input_mode = cleaned_data.get("input_mode", "paste")
        
        # Handle project from either 'project' field or 'project_pk' hidden input
        project = cleaned_data.get("project")
        if not project and self.data.get("project_pk"):
            try:
                project = Project.objects.get(pk=self.data.get("project_pk"))
                cleaned_data["project"] = project
            except Project.DoesNotExist:
                raise forms.ValidationError("Invalid project selected.")
        
        if not project:
            raise forms.ValidationError("Please select a project.")
        
        processed_data = []
        
        if input_mode == "paste":
            data_str = cleaned_data.get("data", "")
            if data_str:
                rows = parse_bulk_fieldwork_data(data_str)
                invalid_rows = [r for r in rows if not r["is_valid"]]
                if invalid_rows:
                    errors = [f"Line {r['line_num']}: {r['error']}" for r in invalid_rows]
                    raise forms.ValidationError(errors)
                
                for row in rows:
                    processed_data.append({
                        "project": project,
                        "date": row["date"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "weather": row["weather"],
                        "description": row["description"],
                    })
        
        elif input_mode == "file":
            uploaded_file = cleaned_data.get("file")
            if uploaded_file:
                rows, error = parse_bulk_fieldwork_file(uploaded_file)
                if error:
                    raise forms.ValidationError(error)
                
                invalid_rows = [r for r in rows if not r["is_valid"]]
                if invalid_rows:
                    errors = [f"Line {r['line_num']}: {r['error']}" for r in invalid_rows]
                    raise forms.ValidationError(errors)
                
                for row in rows:
                    processed_data.append({
                        "project": project,
                        "date": row["date"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "weather": row["weather"],
                        "description": row["description"],
                    })
        
        if not processed_data:
            raise forms.ValidationError("No valid fieldwork data provided.")
        
        # Check for duplicate dates
        if processed_data and project:
            dates = [d["date"] for d in processed_data]
            
            # Check for duplicates in uploaded data
            seen_dates = set()
            internal_duplicates = []
            for d in dates:
                if d in seen_dates:
                    internal_duplicates.append(str(d))
                seen_dates.add(d)
            
            if internal_duplicates:
                raise forms.ValidationError(
                    f"Duplicate dates in uploaded data: {', '.join(internal_duplicates)}"
                )
            
            # Check for existing fieldwork on these dates
            existing_duplicates = check_duplicate_fieldwork_dates(project, dates)
            if existing_duplicates:
                raise forms.ValidationError(
                    f"Fieldwork already exists for these dates: {', '.join(str(d) for d in existing_duplicates)}"
                )
            
        cleaned_data["processed_data"] = processed_data
        return cleaned_data


class LocationForm(FormWithHistory, WatersyncForm):
    """Form for creating/editing Location objects.
    
    Note: The geometry is created from latitude/longitude/altitude fields
    in the view's pre_save hook using update_location_geom().

    Detail forms for each location type are handled separately via HTMX
    and saved in the view's post_save hook.
    """

    title = "Add or Edit Location"
    latitude = FloatField(required=False, label="Latitude")
    longitude = FloatField(required=False, label="Longitude")
    altitude = FloatField(required=False, label="Altitude")
    # geom field is important because in the template latitude and longitude are used to
    # populate the geometry from coordinates
    geom = CharField(required=False, widget=HiddenInput())
    type = ChoiceField(
        choices=Location.LocationTypes.choices,
        required=True,
        label="Type",
    )

    class Meta:
        model = Location
        fields = (
            "project",
            "name",
            "type",
            "status",
            "description",
            "altitude",
            "latitude",
            "longitude",
            "geom",
            "history_date",
        )