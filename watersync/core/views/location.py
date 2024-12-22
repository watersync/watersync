from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from watersync.core.forms import LocationForm
from watersync.core.mixins import DeleteHTMX, HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, Project
from watersync.core.views.locationstatus import LocationStatusListView
from watersync.groundwater.views.groundwaterlevel import GWLListView
from watersync.sensor.views import DeploymentListView
from watersync.waterquality.views.samplingevent import SamplingEventListView


class LocationCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "locationChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        lat = form.cleaned_data.get("latitude")
        lon = form.cleaned_data.get("longitude")
        if lat and lon:
            form.instance.geom = Point(lon, lat, srid=4326)


class LocationDeleteView(LoginRequiredMixin, DeleteHTMX, DeleteView):
    """Deteleting location is only possible from the location detail view.
    User is redirected to the locations list view after deletion."""

    model = Location
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

    @property
    def htmx_redirect(self):
        return reverse(
            "core:locations",
            kwargs={
                "user_id": self.kwargs["user_id"],
                "project_pk": self.kwargs["project_pk"],
            },
        )

    def get_object(self):
        return get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])


class LocationUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "core/location_form.html"

    def get_object(self):
        return get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        lat = form.cleaned_data.get("latitude")
        lon = form.cleaned_data.get("longitude")
        if lat and lon:
            form.instance.geom = Point(lon, lat, srid=4326)


class LocationListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
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


class LocationDetailView(LoginRequiredMixin, DetailView):
    """Optimization needed: should actually change the way the counts are requested
    and use htmx instead of passing the counts in the context"""

    model = Location
    template_name = "core/location_detail.html"

    def get_object(self):
        return get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def render_to_response(self, context, **response_kwargs):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["project"] = project
        context["location"] = location

        if self.request.headers.get("HX-Request"):
            html = render_to_string(
                "core/partial/location_detail.html", context, request=self.request
            )
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = self.get_object()

        views = {
            "statuscount": LocationStatusListView,
            "gwlmeasurementcount": GWLListView,
            "deploymentcount": DeploymentListView,
            "samplingeventcount": SamplingEventListView,
        }

        counts = {}
        for key, view_class in views.items():
            view = view_class()
            view.request = self.request
            view.kwargs = self.kwargs
            counts[key] = view.get_queryset().count()

        context.update(counts)
        context["project"] = location.project

        return context


location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_list_view = LocationListView.as_view()
