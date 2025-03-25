from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.forms import ModelForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView
from watersync.core.forms import FieldworkForm, LocationForm, LocationVisitForm, ProjectForm
from watersync.core.mixins import DeleteHTMX, HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Fieldwork, Location, LocationVisit, Project
from watersync.core.generics.base import WatersyncCreateView, WatersyncDetailView, WatersyncDeleteView, WatersyncListView, WatersyncUpdateView
from django.utils.safestring import mark_safe
import json

from django.shortcuts import get_object_or_404

from watersync.groundwater.views.groundwaterlevel import GWLListView
from watersync.sensor.views import DeploymentListView
from watersync.waterquality.views.samplingevent import SamplingEventListView


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
    detail_type = "offcanvas"

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return project.fieldworks.order_by("-created")


class FieldworkDetailView(LoginRequiredMixin, RenderToResponseMixin, DetailView):
    model = Fieldwork
    template_name = "core/fieldwork_detail.html"
    htmx_template = "core/fieldwork_detail.html"

    def get_object(self):
        return get_object_or_404(Fieldwork, pk=self.kwargs["fieldwork_pk"])



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


class LocationVisitListView(WatersyncListView):
    model = LocationVisit
    detail_type = "popover"

    def get_queryset(self):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        return location.visits.order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        return context

class LocationDetailView(WatersyncDetailView):
    model = Location

class LocationOverviewView(TemplateView):
    template_name = "core/location_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["location"] = location
        context["project"] = project
        return context

# class LocationDetailView(LoginRequiredMixin, DetailView):
#     """Optimization needed: should actually change the way the counts are requested
#     and use htmx instead of passing the counts in the context"""

#     model = Location
#     template_name = "core/location_detail.html"

#     def get_object(self):
#         return get_object_or_404(Location, pk=self.kwargs["location_pk"])

#     def render_to_response(self, context, **response_kwargs):
#         location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
#         project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
#         context["project"] = project
#         context["location"] = location

#         if self.request.headers.get("HX-Request"):
#             html = render_to_string(
#                 "core/partial/location_detail.html", context, request=self.request
#             )
#             return HttpResponse(html)
#         return super().render_to_response(context, **response_kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         location = self.get_object()

#         views = {
#             "statuscount": LocationVisitListView,
#             "gwlmeasurementcount": GWLListView,
#             "deploymentcount": DeploymentListView,
#             "samplingeventcount": SamplingEventListView,
#         }

#         counts = {}
#         for key, view_class in views.items():
#             view = view_class()
#             view.request = self.request
#             view.kwargs = self.kwargs
#             counts[key] = view.get_queryset().count()

#         context.update(counts)
#         context["project"] = location.project
#         context["hx_vals"] = mark_safe(json.dumps({"location_pk": location.pk}))

#         # Update for DeploymentListView
#         deployments_view = DeploymentListView(
#             request=self.request,
#             kwargs=self.kwargs
#             )
        
#         locationvisits_view = LocationVisitListView(
#             request=self.request,
#             kwargs=self.kwargs
#         )


#         context["deployments"] = deployments_view.get_context_data(
#             object_list=0
#         )
#         context["locationvisits"] = locationvisits_view.get_context_data(
#             object_list=0
#         )

#         return context


location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_overview_view = LocationOverviewView.as_view()
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
    model = Project
    template_name = "core/partial/project_list.html"
    htmx_template = "core/partial/project_table.html"

    def get_queryset(self):
        return self.request.user.projects.all()


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "core/project_detail.html"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])


project_create_view = ProjectCreateView.as_view()
project_delete_view = ProjectDeleteView.as_view()
project_update_view = ProjectUpdateView.as_view()
project_detail_view = ProjectDetailView.as_view()
project_list_view = ProjectListView.as_view()


class LocationVisitCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = LocationVisit
    form_class = LocationVisitForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "LocationVisitChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class LocationVisitUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = LocationVisit
    form_class = LocationVisitForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "LocationVisitChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form: ModelForm):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )

    def get_object(self):
        return get_object_or_404(LocationVisit, pk=self.kwargs["locationvisit_pk"])


class LocationVisitDeleteView(LoginRequiredMixin, RenderToResponseMixin, DeleteView):
    model = LocationVisit
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(LocationVisit, pk=self.kwargs["locationvisit_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("HX-Request"):
            return HttpResponse(status=204, headers={"HX-Trigger": "configRequest"})
        return super().delete(request, *args, **kwargs)


location_visit_create_view = LocationVisitCreateView.as_view()
location_visit_list_view = LocationVisitListView.as_view()
location_visit_delete_view = LocationVisitDeleteView.as_view()
location_visit_update_view = LocationVisitUpdateView.as_view()