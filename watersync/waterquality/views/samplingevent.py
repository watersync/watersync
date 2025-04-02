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

from watersync.core.generics.htmx import HTMXFormMixin, RenderToResponseMixin
from watersync.core.generics.htmx import DeleteHTMX
from watersync.core.models import Location, Project
from watersync.waterquality.forms import (
    SamplingEventForm,
)
from watersync.waterquality.models import SamplingEvent


class SamplingEventCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = SamplingEvent
    form_class = SamplingEventForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "samplingeventChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class SamplingEventUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = SamplingEvent
    form_class = SamplingEventForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "samplingeventChanged"
    htmx_render_template = "shared/simple_form.html"

    def get_object(self):
        return get_object_or_404(SamplingEvent, pk=self.kwargs["samplingevent_pk"])

    def update_form_instance(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )


class SamplingEventDeleteView(LoginRequiredMixin, DeleteHTMX, DeleteView):
    model = SamplingEvent
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(SamplingEvent, pk=self.kwargs["samplingevent_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])


class SamplingEventListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = SamplingEvent
    template_name = "waterquality/partial/samplingevent_list.html"
    htmx_template = "waterquality/partial/samplingevent_table.html"

    def get_queryset(self):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        return location.samplingevents.order_by("-executed_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        return context


class SamplingEventDetailView(LoginRequiredMixin, DetailView):
    model = SamplingEvent
    template_name = "waterquality/samplingevent_detail.html"

    def get_object(self):
        return get_object_or_404(SamplingEvent, pk=self.kwargs["samplingevent_pk"])

    def get_success_url(self):
        return reverse("core:detail-location", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        return context


samplingevent_create_view = SamplingEventCreateView.as_view()
samplingevent_update_view = SamplingEventUpdateView.as_view()
samplingevent_delete_view = SamplingEventDeleteView.as_view()
samplingevent_list_view = SamplingEventListView.as_view()
samplingevent_detail_view = SamplingEventDetailView.as_view()
