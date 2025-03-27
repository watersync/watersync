from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.forms import ModelForm
from django.views.generic import ListView, TemplateView
from watersync.groundwater.views import GWLListView
from watersync.core.forms import FieldworkForm, LocationForm, LocationVisitForm, ProjectForm
from watersync.core.mixins import RenderToResponseMixin
from watersync.core.models import Fieldwork, Location, LocationVisit, Project
from watersync.core.generics.base import WatersyncCreateView, WatersyncDetailView, WatersyncDeleteView, WatersyncListView, WatersyncUpdateView
from watersync.sensor.views import DeploymentListView
from django.utils.safestring import mark_safe
import json

from django.shortcuts import get_object_or_404


class FieldworkCreateView(WatersyncCreateView):
    model = Fieldwork
    form_class = FieldworkForm

    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])


class FieldworkUpdateView(WatersyncUpdateView):
    model = Fieldwork
    form_class = FieldworkForm

    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])


class FieldworkDeleteView(WatersyncDeleteView):
    model = Fieldwork


class FieldworkListView(WatersyncListView):
    model = Fieldwork
    detail_type = "modal"

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return project.fieldworks.order_by("-created")


class FieldworkDetailView(WatersyncDetailView):
    model = Fieldwork
    detail_type = "modal"


fieldwork_create_view = FieldworkCreateView.as_view()
fieldwork_detail_view = FieldworkDetailView.as_view()
fieldwork_list_view = FieldworkListView.as_view()
fieldwork_delete_view = FieldworkDeleteView.as_view()
fieldwork_update_view = FieldworkUpdateView.as_view()

# ================================LOCATION VIEWS================================

def update_location_geom(form):
    lat = form.cleaned_data.get("latitude")
    lon = form.cleaned_data.get("longitude")
    if lat and lon:
        form.instance.geom = Point(lon, lat, srid=4326)

class LocationCreateView(WatersyncCreateView):
    model = Location
    form_class = LocationForm

    def update_form_instance(self, form: ModelForm):
        form.instance.project = self.get_project()
        update_location_geom(form)


class LocationUpdateView(WatersyncUpdateView):
    model = Location
    form_class = LocationForm

    def update_form_instance(self, form: ModelForm):
        form.instance.project = self.get_project()
        update_location_geom(form)


class LocationDeleteView(WatersyncDeleteView):
    """Deteleting location is only possible from the location detail view.
    User is redirected to the locations list view after deletion."""

    model = Location

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.get_project()


class LocationListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    """Location list has a special view which includes a table and a map, so for
    now it does inherit the WaterstncListView.
    
    Note:
        Consider letting this handle the location list view as table and add create
        a separate template view combining the table and map.
    """

    model = Location
    template_name = "core/partial/location_list.html"
    htmx_template = "core/partial/location_table.html"

    def get_queryset(self):
        project_id = self.kwargs.get("project_pk")
        user = self.request.user

        project = get_object_or_404(Project, id=project_id, user=user)

        return Location.objects.filter(project=project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, id=self.kwargs["project_pk"])
        return context


class LocationDetailView(WatersyncDetailView):
    model = Location


location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_list_view = LocationListView.as_view()


def add_requesting_user_to_form(form, requesting_user):
    """Prototype function adding the requesting user to the form instance."""

    # in case no users are selected, add at least the requesting user to an empty list
    # I also meant to include it in the generic form_valid method so I am checking if
    # the form has a user field
    if hasattr(form.instance, 'user') and requesting_user not in form.cleaned_data.get("user", []):
        form.cleaned_data["user"].append(requesting_user)

        form.instance.user.set(form.cleaned_data["user"])
        return form.instance

    return form.instance

class ProjectCreateView(WatersyncCreateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        response = super().form_valid(form)
        add_requesting_user_to_form(form, self.request.user)
        return response


class ProjectUpdateView(WatersyncUpdateView):
    model = Project
    form_class = ProjectForm

    def update_form_instance(self, form):
        return add_requesting_user_to_form(form, self.request.user)


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

class LocationVisitListView(WatersyncListView):
    model = LocationVisit
    detail_type = "popover"

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        locations = project.locations.all()

        queryset = LocationVisit.objects.filter(location__in=locations).order_by("-created")

        if "location_pk" in self.request.GET:
            queryset = queryset.filter(location__pk=self.request.GET.get("location_pk"))

        return queryset


class LocationVisitCreateView(WatersyncCreateView):
    model = LocationVisit
    form_class = LocationVisitForm

    def update_form_instance(self, form):
        if "location_pk" in self.kwargs and not form.instance.location:
            form.instance.location = get_object_or_404(
                Location, pk=self.kwargs["location_pk"]
            )


class LocationVisitUpdateView(WatersyncUpdateView):
    model = LocationVisit
    form_class = LocationVisitForm

    def update_form_instance(self, form: ModelForm):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class LocationVisitDeleteView(WatersyncDeleteView):
    model = LocationVisit


location_visit_create_view = LocationVisitCreateView.as_view()
location_visit_list_view = LocationVisitListView.as_view()
location_visit_delete_view = LocationVisitDeleteView.as_view()
location_visit_update_view = LocationVisitUpdateView.as_view()


class LocationOverviewView(TemplateView):
    template_name = "core/location_overview.html"

    def get_resource_counts(self, location):
        views = {
            "statuscount": location.visits,
            "gwlmeasurementcount": location.gwlmeasurements,
            "deploymentcount": location.deployments,
            "samplingeventcount": location.samplingevents,
        }

        return {key: view.count() for key, view in views.items()}
    
    def get_resource_list_context(self):
        views = {
            "locationvisits": LocationVisitListView,
            "gwlmeasurements": GWLListView,
            "deployments": DeploymentListView,
            # "samplingevents": SamplingEventListView,
        }

        return {
            key: view(request=self.request, kwargs=self.kwargs).get_context_data(object_list=0)
            for key, view in views.items()
        }
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["location"] = location
        context["project"] = project
        context.update(self.get_resource_counts(location))
        context.update(self.get_resource_list_context())
        context["hx_vals"] = mark_safe(json.dumps({"location_pk": location.pk}))

        return context

location_overview_view = LocationOverviewView.as_view()