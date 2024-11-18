from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from django.http import HttpResponse
from django.template.loader import render_to_string
from watersync.groundwater.views import GWLListView
from watersync.sensor.views import DeploymentListView
from watersync.waterquality.views import SampleListView, SamplingEventListView
from django.http import JsonResponse, HttpResponse
from .forms import LocationForm, LocationStatusForm, ProjectForm
from .models import Location, LocationStatus, Project

from watersync.waterquality.forms import SamplingEventForm
from watersync.groundwater.forms import GWLForm
from .mixins import RenderToResponseMixin, RenderToResponseMixin, HTMXFormMixin
from watersync.users.models import User


class ProjectCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "core/project_form.html"

    htmx_trigger_header = "locationChanged"
    htmx_render_template = "core/location_form.html"

    def update_form_instance(self, form):
        instance = form.instance

        selected_users = form.cleaned_data.get("user", [])

        requesting_user = self.request.user
        if requesting_user not in selected_users:
            selected_users.append(requesting_user)

        instance.user.set(selected_users)

        return instance


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


class ProjectUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "core/project_form.html"

    htmx_trigger_header = "locationChanged"
    htmx_render_template = "core/location_form.html"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])

    def update_form_instance(self, form):
        instance = form.instance

        selected_users = form.cleaned_data.get("users", [])

        requesting_user = self.request.user
        if requesting_user not in selected_users:
            selected_users.append(requesting_user)

        instance.user.set(selected_users)

        return instance


class ProjectDeleteView(LoginRequiredMixin, RenderToResponseMixin, DeleteView):
    model = Project
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(
            Project, pk=self.kwargs["project_pk"], user=self.request.user
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("HX-Request"):
            projects_url = reverse(
                "core:projects", kwargs={"user_id": self.kwargs["user_id"]}
            )
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "configRequest",
                    "HX-Redirect": projects_url,
                },
            )
        return super().delete(request, *args, **kwargs)


# Exporting just the .as_view() elements
project_create_view = ProjectCreateView.as_view()
project_delete_view = ProjectDeleteView.as_view()
project_update_view = ProjectUpdateView.as_view()
project_detail_view = ProjectDetailView.as_view()
project_list_view = ProjectListView.as_view()


# ========================= Location status views ============================ #
class LocationStatusCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = LocationStatus
    form_class = LocationStatusForm
    template_name = "core/location_status_form.html"

    htmx_trigger_header = "locationStatusChanged"
    htmx_render_template = "core/location_status_form.html"

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class LocationStatusListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = LocationStatus
    template_name = "core/location_status_list.html"
    htmx_template = "core/partial/locationstatus_table.html"

    def get_queryset(self):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        return location.statuses.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        return context


class LocationStatusDeleteView(LoginRequiredMixin, RenderToResponseMixin, DeleteView):
    model = LocationStatus
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(LocationStatus, pk=self.kwargs["locationstatus_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("HX-Request"):
            return HttpResponse(status=204, headers={"HX-Trigger": "configRequest"})
        return super().delete(request, *args, **kwargs)


class LocationStatusUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = LocationStatus
    form_class = LocationStatusForm
    template_name = "core/location_status_form.html"

    htmx_trigger_header = "locationStatusChanged"
    htmx_render_template = "core/location_status_form.html"

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )

    def get_object(self):
        return get_object_or_404(LocationStatus, pk=self.kwargs["locationstatus_pk"])


location_status_create_view = LocationStatusCreateView.as_view()
location_status_list_view = LocationStatusListView.as_view()
location_status_delete_view = LocationStatusDeleteView.as_view()
location_status_update_view = LocationStatusUpdateView.as_view()


# ========================= Location views ============================ #


class LocationCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Location
    form_class = LocationForm

    htmx_trigger_header = "locationChanged"
    htmx_render_template = "core/location_form.html"

    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])


class LocationDeleteView(LoginRequiredMixin, DeleteView, RenderToResponseMixin):
    model = Location
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("HX-Request"):
            locations_url = reverse(
                "core:locations",
                kwargs={
                    "user_id": self.kwargs["user_id"],
                    "project_pk": self.kwargs["project_pk"],
                },
            )
            return HttpResponse(
                status=204,
                headers={"HX-Redirect": locations_url},
            )
        return super().delete(request, *args, **kwargs)

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

        location_status_view = LocationStatusListView()
        gwl_list_view = GWLListView()
        deployment_view = DeploymentListView()
        sample_view = SampleListView()
        samplingevent_list_view = SamplingEventListView()
        samplingevent_list_view.request = self.request
        samplingevent_list_view.kwargs = self.kwargs
        location_status_view.request = self.request
        location_status_view.kwargs = self.kwargs
        gwl_list_view.request = self.request
        gwl_list_view.kwargs = self.kwargs
        deployment_view.request = self.request
        deployment_view.kwargs = self.kwargs
        sample_view.request = self.request
        sample_view.kwargs = self.kwargs

        context["project"] = location.project
        context["deployment_list"] = deployment_view.get_queryset()
        context["statuscount"] = location_status_view.get_queryset().count()
        context["locationstatus_list"] = location_status_view.get_queryset()
        context["locationstatus_form"] = LocationStatusForm()

        context["gwlmanualmeasurements_list"] = gwl_list_view.get_queryset()
        context["gwlmeasurement_form"] = GWLForm()

        context["samplingevent_list"] = samplingevent_list_view.get_queryset()
        context["samplingevent_form"] = SamplingEventForm()

        context["sample_list"] = sample_view.get_queryset()

        return context


# Exporting just the .as_view() elements
location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_list_view = LocationListView.as_view()
