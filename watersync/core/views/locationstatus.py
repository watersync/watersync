# ========================= Location status views ============================ #
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from watersync.core.forms import LocationStatusForm
from watersync.core.mixins import HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, LocationStatus, Project


class LocationStatusCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = LocationStatus
    form_class = LocationStatusForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "locationStatusChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class LocationStatusUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = LocationStatus
    form_class = LocationStatusForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "locationStatusChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )

    def get_object(self):
        return get_object_or_404(LocationStatus, pk=self.kwargs["locationstatus_pk"])


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


location_status_create_view = LocationStatusCreateView.as_view()
location_status_list_view = LocationStatusListView.as_view()
location_status_delete_view = LocationStatusDeleteView.as_view()
location_status_update_view = LocationStatusUpdateView.as_view()
