from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, TemplateView

from watersync.core.forms import (
    FieldworkBulkForm,
    FieldworkForm,
    LocationForm,
    ProjectForm,
)
from watersync.core.forms_detail import LOCATION_TYPE_DETAIL_FORMS
from watersync.core.generics.utils import update_location_geom
from watersync.core.generics.views import (
    WatersyncCreateView,
    WatersyncDeleteView,
    WatersyncDetailView,
    WatersyncHistoryListView,
    WatersyncListView,
    WatersyncUpdateView,
)
from watersync.core.models import (
    Fieldwork,
    HistoricalFieldwork,
    HistoricalLocation,
    HistoricalProject,
    Location,
    Project,
)

# ----- Fieldwork Views ----- #

class FieldworkBulkPreviewView(LoginRequiredMixin, View):
    """HTMX endpoint for live preview of bulk fieldwork data (paste or file)."""
    
    def post(self, request, *args, **kwargs):
        from watersync.core.parsers import (
            parse_bulk_fieldwork_data,
            parse_bulk_fieldwork_file,
            validate_bulk_fieldwork_for_project,
        )
        
        rows = []
        error_message = None
        
        # Check if it's a file upload or paste data
        if request.FILES.get("file"):
            rows, error_message = parse_bulk_fieldwork_file(request.FILES["file"])
        else:
            data_str = request.POST.get("data", "")
            rows = parse_bulk_fieldwork_data(data_str)
        
        # Get project for additional validation
        project_pk = request.POST.get("project_pk") or self.kwargs.get("project_pk")
        project = None
        
        if project_pk:
            try:
                project = Project.objects.get(pk=project_pk)
            except Project.DoesNotExist:
                pass
        
        # Add project-specific validation (duplicate dates)
        if project:
            rows = validate_bulk_fieldwork_for_project(project, rows)
        
        valid_count = sum(1 for r in rows if r["is_valid"])
        invalid_count = sum(1 for r in rows if not r["is_valid"])
        
        return TemplateResponse(
            request,
            "core/bulk_fieldwork_preview.html",
            {
                "rows": rows,
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "error_message": error_message,
            }
        )


fieldwork_bulk_preview_view = FieldworkBulkPreviewView.as_view()


class FieldworkCreateView(WatersyncCreateView):
    model = Fieldwork
    form_class = FieldworkForm
    bulk_form_class = FieldworkBulkForm

    def get_template_names(self):
        """Use custom template for bulk form."""
        if self.get_form_class() == self.bulk_form_class:
            return ["core/bulk_fieldwork_form.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add context for bulk form only
        if self.get_form_class() == self.bulk_form_class:
            context["preview_url"] = reverse(
                "core:preview-fieldwork",
                kwargs={"project_pk": self.kwargs.get("project_pk")}
            )
        return context

    def handle_bulk_create(self, form, instance):
        """Handle bulk fieldwork creation."""
        if not isinstance(form, FieldworkBulkForm):
            return
        
        processed_data = form.cleaned_data.get("processed_data", [])
        users = form.cleaned_data.get("user", [])
        
        for data in processed_data:
            fieldwork = Fieldwork.objects.create(
                project=data["project"],
                date=data["date"],
                start_time=data["start_time"],
                end_time=data["end_time"],
                weather=data["weather"],
                description=data["description"],
            )
            fieldwork.user.set(users)

class FieldworkUpdateView(WatersyncUpdateView):
    model = Fieldwork
    form_class = FieldworkForm

class FieldworkDeleteView(WatersyncDeleteView):
    model = Fieldwork

class FieldworkListView(WatersyncListView):
    model = Fieldwork
    detail_type = "page"


    def get_queryset(self):
        return (
            Fieldwork.objects
            .for_project(self.kwargs["project_pk"])
            .for_user(self.request.user)
            .order_by("-date")
        )

class FieldworkDetailView(WatersyncDetailView):
    model = Fieldwork

class FieldworkOverviewView(TemplateView):
    template_name = "core/fieldwork_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fieldwork"] = get_object_or_404(
            Fieldwork.objects.with_counts(),
            pk=self.kwargs["fieldwork_pk"]
        )
        return context
    
class FieldworkHistoryListView(WatersyncHistoryListView):
    model = HistoricalFieldwork

class FieldworkHistoryDeleteView(WatersyncDeleteView):
    model = HistoricalFieldwork

fieldwork_history_list_view = FieldworkHistoryListView.as_view()
fieldwork_history_delete_view = FieldworkHistoryDeleteView.as_view()
fieldwork_overview_view = FieldworkOverviewView.as_view()
fieldwork_create_view = FieldworkCreateView.as_view()
fieldwork_detail_view = FieldworkDetailView.as_view()
fieldwork_list_view = FieldworkListView.as_view()
fieldwork_delete_view = FieldworkDeleteView.as_view()
fieldwork_update_view = FieldworkUpdateView.as_view()

# ----- Location Views ----- #

class LocationCreateView(WatersyncCreateView):
    model = Location
    form_class = LocationForm
    detail_forms = LOCATION_TYPE_DETAIL_FORMS
    detail_related_names = Location.DETAIL_RELATED_NAMES

    def pre_save(self, form):
        """Set geometry from lat/lon/alt before saving."""
        update_location_geom(form)


class LocationUpdateView(WatersyncUpdateView):
    model = Location
    form_class = LocationForm
    detail_forms = LOCATION_TYPE_DETAIL_FORMS
    detail_related_names = Location.DETAIL_RELATED_NAMES

    def pre_save(self, form):
        """Update geometry from lat/lon/alt before saving."""
        update_location_geom(form)


class LocationDeleteView(WatersyncDeleteView):
    """Deteleting location is only possible from the location detail view.
    User is redirected to the locations list view after deletion."""

    model = Location

class LocationListView(WatersyncListView):
    """Location list has a special view which includes a table and a map, so for
    now it does inherit the WaterstncListView.
    
    Note:
        Consider letting this handle the location list view as table and add create
        a separate template view combining the table and map.
    """

    model = Location
    detail_type = "page"

    def get_queryset(self):
        return Location.objects.for_project(self.kwargs["project_pk"])


class LocationDetailView(WatersyncDetailView):
    model = Location
    detail_related_names = Location.DETAIL_RELATED_NAMES


class LocationHistoryListView(WatersyncHistoryListView):
    model = HistoricalLocation

class LocationHistoryDeleteView(WatersyncDeleteView):
    model = HistoricalLocation

class LocationOverviewView(TemplateView):
    template_name = "core/location_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = get_object_or_404(
            Location.objects.with_counts(),
            pk=self.kwargs["location_pk"]
        )
        return context

location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_list_view = LocationListView.as_view()
location_overview_view = LocationOverviewView.as_view()
location_history_list_view = LocationHistoryListView.as_view()
location_history_delete_view = LocationHistoryDeleteView.as_view()

# ----- Project Views ----- #

class ProjectCreateView(WatersyncCreateView):
    model = Project
    form_class = ProjectForm


class ProjectUpdateView(WatersyncUpdateView):
    model = Project
    form_class = ProjectForm


class ProjectDeleteView(WatersyncDeleteView):
    model = Project


class ProjectListView(LoginRequiredMixin, ListView):
    """Project list view using template-based HTMX handling.
    
    Template selection via base_template context variable:
    - HTMX without context: returns project_table.html (just cards)
    - Other requests: returns full page with card container
    """
    model = Project
    template_name = "core/partial/project_list.html"

    def get_queryset(self):
        return self.request.user.projects.all()


class ProjectDetailView(WatersyncDetailView):
    model = Project

class ProjectHistoryListView(WatersyncHistoryListView):
    model = HistoricalProject

class ProjectHistoryDeleteView(WatersyncDeleteView):
    model = HistoricalProject

project_create_view = ProjectCreateView.as_view()
project_delete_view = ProjectDeleteView.as_view()
project_update_view = ProjectUpdateView.as_view()
project_detail_view = ProjectDetailView.as_view()
project_list_view = ProjectListView.as_view()
project_history_list_view = ProjectHistoryListView.as_view()
project_history_delete_view = ProjectHistoryDeleteView.as_view()


