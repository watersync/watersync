# ========================= Location status views ============================ #
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.forms import ModelForm
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from watersync.core.forms import LocationVisitForm
from watersync.core.mixins import HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, LocationVisit, Project


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


class LocationVisitListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = LocationVisit
    template_name = "core/location_visit_list.html"
    htmx_template = "core/partial/locationvisit_table.html"

    def get_queryset(self):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        return location.visits.order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        return context


location_visit_create_view = LocationVisitCreateView.as_view()
location_visit_list_view = LocationVisitListView.as_view()
location_visit_delete_view = LocationVisitDeleteView.as_view()
location_visit_update_view = LocationVisitUpdateView.as_view()
