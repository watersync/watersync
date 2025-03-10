from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from watersync.core.mixins import DeleteHTMX, HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, Project
from watersync.groundwater.forms import GWLForm
from watersync.groundwater.models import GWLManualMeasurement


class GWLCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = GWLManualMeasurement
    form_class = GWLForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "gwlChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class GWLUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = GWLManualMeasurement
    form_class = GWLForm
    template_name = "groundwater/gwl_form.html"

    htmx_trigger_header = "gwlChanged"
    htmx_render_template = "core/location_status_form.html"

    def get_object(self):
        return get_object_or_404(
            GWLManualMeasurement, pk=self.kwargs["gwlmeasurement_pk"]
        )

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class GWLDeleteView(LoginRequiredMixin, DeleteHTMX, DeleteView):
    model = GWLManualMeasurement
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(
            GWLManualMeasurement, pk=self.kwargs["gwlmeasurement_pk"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])


class GWLListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = GWLManualMeasurement
    template_name = "groundwater/partial/gwl_list.html"
    htmx_template = "groundwater/partial/gwl_table.html"

    def get_queryset(self):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        return location.gwlmeasurements.order_by("-measured_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        return context


gwl_list_view = GWLListView.as_view()
gwl_create_view = GWLCreateView.as_view()
gwl_update_view = GWLUpdateView.as_view()
gwl_delete_view = GWLDeleteView.as_view()
