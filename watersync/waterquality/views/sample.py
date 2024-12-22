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

from watersync.core.mixins import DeleteHTMX, HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, Project
from watersync.utils.get_objects import get_project_location
from watersync.waterquality.forms import (
    MeasurementForm,
    SampleForm,
)
from watersync.waterquality.models import Sample, SamplingEvent


class SampleCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Sample
    form_class = SampleForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "sampleChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.sampling_event = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )


class SampleUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Sample
    form_class = SampleForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "sampleChanged"
    htmx_render_template = "shared/simple_form.html"

    def get_object(self):
        return get_object_or_404(Sample, pk=self.kwargs["sample_pk"])

    def update_form_instance(self, form):
        form.instance.samplingevent = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )


class SampleDeleteView(LoginRequiredMixin, DeleteHTMX, DeleteView):
    model = Sample
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(Sample, pk=self.kwargs["sample_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["samplingevent"] = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )

        return context


class SampleListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = Sample
    template_name = "waterquality/partial/sample_list.html"

    htmx_template = "waterquality/partial/sample_table.html"

    def get_queryset(self):
        samplingevent = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )
        return samplingevent.samples.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["samplingevent"] = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )

        return context


class SampleDetailView(LoginRequiredMixin, DetailView):
    model = Sample
    template_name = "waterquality/sample_detail.html"

    def get_object(self):
        return get_object_or_404(Sample, pk=self.kwargs["sample_pk"])

    def get_success_url(self):
        return reverse("waterquality:detail-samplingevent", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request, self.kwargs)
        sampling_event = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )

        context["project"] = project
        context["location"] = location
        context["samplingevent"] = sampling_event
        context["measurement_list"] = self.get_object().measurements.all()
        context["measurement_form"] = MeasurementForm()
        return context


sample_create_view = SampleCreateView.as_view()
sample_update_view = SampleUpdateView.as_view()
sample_delete_view = SampleDeleteView.as_view()
sample_list_view = SampleListView.as_view()
sample_detail_view = SampleDetailView.as_view()
