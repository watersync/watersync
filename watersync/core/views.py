from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.views.generic import ListView, TemplateView
from watersync.core.generics.decorators import filter_by_location
from watersync.core.generics.utils import update_location_geom, add_current_project
from watersync.groundwater.views import GWLListView
from watersync.core.forms import FieldworkForm, LocationForm, ProjectForm, UnitForm
from watersync.core.generics.htmx import RenderToResponseMixin
from watersync.core.models import Fieldwork, Location, Project, Unit
from watersync.core.generics.views import WatersyncCreateView, WatersyncDetailView, WatersyncDeleteView, WatersyncListView, WatersyncUpdateView
from watersync.sensor.views import DeploymentListView
from watersync.waterquality.views import SampleListView
from watersync.core.generics.utils import get_resource_list_context
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

    def get_resource_counts(self, fieldwork):
        """Keeping this for the pattern:
            "samplecount": fieldwork.visits.aggregate(
            total=Count('samples')
                )['total'],
        """

        fieldwork = Fieldwork.objects.annotate(
            gwlmeasurementcount=Count('gwlmeasurements'),
            samplecount=Count('samples')
        ).get(pk=fieldwork.pk)

        views = {
            "gwlmeasurementcount": fieldwork.gwlmeasurementcount,
            "samplecount": fieldwork.samplecount
        }

        return views
    
    def get_resource_list_context(self):
        views = {
            "gwlmeasurements": GWLListView,
            "samples": SampleListView,
        }

        return get_resource_list_context(self.request, self.kwargs, views)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fieldwork = get_object_or_404(Fieldwork, pk=self.kwargs["fieldwork_pk"])

        context.update(self.get_resource_counts(fieldwork))
        context.update(self.get_resource_list_context())
        context["hx_vals"] = json.dumps({"fieldwork_pk": str(fieldwork.pk)})

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
        add_current_project(self.kwargs, form)


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
        print("CUSTOM MANAGER: ", self.model.watersync.get_full_queryset(stats=stats, for_export=True))
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


class ProjectListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    """For now this view has its own template."""
    model = Project
    template_name = "core/partial/project_list.html"
    htmx_template = "core/partial/project_table.html"

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

    def get_resource_counts(self, location):
        """Keeping this for the pattern:
            "samplecount": location.visits.aggregate(
            total=Count('samples')
                )['total'],
        """

        location = Location.objects.annotate(
            gwlmeasurementcount=Count('gwlmeasurements'),
            deploymentcount=Count('deployments'),
            samplecount=Count('samples')
        ).get(pk=location.pk)

        views = {
            "gwlmeasurementcount": location.gwlmeasurementcount,
            "deploymentcount": location.deploymentcount,
            "samplecount": location.samplecount
        }

        return views
    
    def get_resource_list_context(self):
        views = {
            "gwlmeasurements": GWLListView,
            "deployments": DeploymentListView,
            "samples": SampleListView,
        }

        return get_resource_list_context(self.request, self.kwargs, views)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        context.update(self.get_resource_counts(location))
        context.update(self.get_resource_list_context())
        context["hx_vals"] = json.dumps({"location_pk": str(location.pk)})

        return context

location_overview_view = LocationOverviewView.as_view()

## ============================List views============================
class UnitCreateView(WatersyncCreateView):
    model = Unit
    form_class = UnitForm


class UnitUpdateView(WatersyncUpdateView):
    model = Unit
    form_class = UnitForm


class UnitDeleteView(WatersyncDeleteView):
    model = Unit


class UnitListView(WatersyncListView):
    model = Unit
    detail_type = "popover"

    def get_queryset(self):
        return Unit.objects.all().order_by("symbol")


class UnitDetailView(WatersyncDetailView):
    model = Unit
    detail_type = "popover"


unit_create_view = UnitCreateView.as_view()
unit_detail_view = UnitDetailView.as_view()
unit_list_view = UnitListView.as_view()
unit_delete_view = UnitDeleteView.as_view()
unit_update_view = UnitUpdateView.as_view()