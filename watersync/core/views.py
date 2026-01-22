from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic import ListView, TemplateView
from watersync.core.generics.decorators import filter_by_location
from watersync.core.generics.utils import update_location_geom, add_current_project
from watersync.core.forms import FieldworkForm, FieldworkBulkForm, LocationForm, ProjectForm
from watersync.core.models import Fieldwork, Location, Project, HistoricalLocation, HistoricalProject
from watersync.core.generics.views import WatersyncCreateView, WatersyncDetailView, WatersyncDeleteView, WatersyncListView, WatersyncUpdateView
from django.db.models import Count
import json
from django.shortcuts import get_object_or_404


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

    def get_form_class(self):
        """Return bulk form if bulk=true in request."""
        if self.request.GET.get("bulk") == "true" or self.request.POST.get("bulk"):
            return self.bulk_form_class
        return super().get_form_class()

    def get_template_names(self):
        """Use custom template for bulk form."""
        if self.get_form_class() == self.bulk_form_class:
            return ["core/bulk_fieldwork_form.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add context for bulk form
        if self.get_form_class() == self.bulk_form_class:
            from django.urls import reverse
            project_pk = self.kwargs.get("project_pk")
            context["project_pk"] = project_pk
            context["preview_url"] = reverse(
                "core:preview-fieldwork",
                kwargs={"project_pk": project_pk}
            )
        return context

    def update_form_instance(self, form):
        """Always set the current project for the fieldwork instance."""
        add_current_project(self.kwargs, form)

    def form_valid(self, form):
        """Handle bulk form submission."""
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"form_valid called with form type: {type(form)}")
        logger.error(f"isinstance check: {isinstance(form, FieldworkBulkForm)}")
        logger.error(f"form.cleaned_data: {form.cleaned_data}")
        
        if isinstance(form, FieldworkBulkForm):
            processed_data = form.cleaned_data.get("processed_data", [])
            users = form.cleaned_data.get("user", [])
            
            logger.error(f"processed_data: {processed_data}")
            logger.error(f"users: {users}")
            
            created_fieldworks = []
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
                created_fieldworks.append(fieldwork)
            
            logger.error(f"Created {len(created_fieldworks)} fieldworks")
            
            # Build success URL manually since we don't have self.object
            from django.urls import reverse
            success_url = reverse(
                "core:fieldworks",
                kwargs={"project_pk": self.kwargs.get("project_pk")}
            )
            
            # Return success response
            from django.http import HttpResponse
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "fieldworkCreated",
                    "HX-Redirect": success_url,
                }
            )
        
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle bulk form errors."""
        if isinstance(form, FieldworkBulkForm):
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_invalid(form)

class FieldworkUpdateView(WatersyncUpdateView):
    model = Fieldwork
    form_class = FieldworkForm


class FieldworkDeleteView(WatersyncDeleteView):
    model = Fieldwork


class FieldworkListView(WatersyncListView):
    model = Fieldwork
    detail_type = "page"


    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return project.fieldworks.order_by("-created")


class FieldworkDetailView(WatersyncDetailView):
    model = Fieldwork

class FieldworkOverviewView(TemplateView):
    template_name = "core/fieldwork_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fieldwork = get_object_or_404(
            Fieldwork.objects.annotate(
                gwlmeasurementcount=Count('gwlmeasurements'),
                samplecount=Count('samples')
            ),
            pk=self.kwargs["fieldwork_pk"]
        )
        context["fieldwork"] = fieldwork
        context["gwlmeasurementcount"] = fieldwork.gwlmeasurementcount
        context["samplecount"] = fieldwork.samplecount
        return context

fieldwork_overview_view = FieldworkOverviewView.as_view()
fieldwork_create_view = FieldworkCreateView.as_view()
fieldwork_detail_view = FieldworkDetailView.as_view()
fieldwork_list_view = FieldworkListView.as_view()
fieldwork_delete_view = FieldworkDeleteView.as_view()
fieldwork_update_view = FieldworkUpdateView.as_view()

class LocationCreateView(WatersyncCreateView):
    model = Location
    form_class = LocationForm


    def update_form_instance(self, form: ModelForm):
        update_location_geom(form)
        add_current_project(self.kwargs, form)


class LocationUpdateView(WatersyncUpdateView):
    model = Location
    form_class = LocationForm

    def update_form_instance(self, form: ModelForm):
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
        stats = {
            "locsamples": Count("samples"),
        }

        project = self.get_project()
        return project.locations.all()


class LocationDetailView(WatersyncDetailView):
    model = Location


location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_list_view = LocationListView.as_view()


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


project_create_view = ProjectCreateView.as_view()
project_delete_view = ProjectDeleteView.as_view()
project_update_view = ProjectUpdateView.as_view()
project_detail_view = ProjectDetailView.as_view()
project_list_view = ProjectListView.as_view()

class LocationOverviewView(TemplateView):
    template_name = "core/location_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = get_object_or_404(
            Location.objects.annotate(
                gwlmeasurementcount=Count('gwlmeasurements'),
                deploymentcount=Count('deployments'),
                samplecount=Count('samples')
            ),
            pk=self.kwargs["location_pk"]
        )
        context["location"] = location
        context["gwlmeasurementcount"] = location.gwlmeasurementcount
        context["deploymentcount"] = location.deploymentcount
        context["samplecount"] = location.samplecount
        return context

location_overview_view = LocationOverviewView.as_view()

class LocationHistoryDeleteView(WatersyncDeleteView):
    model = HistoricalLocation


class LocationHistoryListView(WatersyncListView):
    model = HistoricalLocation
    template_name = "shared/list_history.html"
    htmx_template = "shared/list_history.html"
    detail_type = "popover"

    def get_queryset(self):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        history = list(location.history.all().order_by("-history_date"))
        history_with_diffs = []

        for i, record in enumerate(history):
            prev_record = history[i + 1] if i + 1 < len(history) else None
            changes = None

            if prev_record:
                changes = record.diff_against(prev_record).changes
            history_with_diffs.append({
                'record': record,
                'prev_record': prev_record,
                'changes': changes,
            })

        return history_with_diffs

    def get_context_data(self, **kwargs):
        return ListView.get_context_data(self, **kwargs)


location_history_list_view = LocationHistoryListView.as_view()
location_history_delete_view = LocationHistoryDeleteView.as_view()

class ProjectHistoryDeleteView(WatersyncDeleteView):
    model = HistoricalProject

project_history_delete_view = ProjectHistoryDeleteView.as_view()
