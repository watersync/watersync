from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.views.generic import ListView, TemplateView
from watersync.core.generics.decorators import filter_by_location
from watersync.core.generics.utils import update_location_geom, add_current_project
from watersync.core.forms import FieldworkForm, LocationForm, ProjectForm
from watersync.core.models import Fieldwork, Location, Project, HistoricalLocation, HistoricalProject
from watersync.core.generics.views import WatersyncCreateView, WatersyncDetailView, WatersyncDeleteView, WatersyncListView, WatersyncUpdateView
from django.db.models import Count
import json
from django.shortcuts import get_object_or_404


class FieldworkCreateView(WatersyncCreateView):
    model = Fieldwork
    form_class = FieldworkForm

    def update_form_instance(self, form):
        """Always set the current project for the fieldwork instance."""
        add_current_project(self.kwargs, form)

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
    detail_type = "modal"

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
