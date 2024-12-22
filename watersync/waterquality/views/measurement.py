from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from watersync.core.mixins import DeleteHTMX, HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, Project
from watersync.waterquality.forms import (
    MeasurementBulkForm,
    MeasurementForm,
)
from watersync.waterquality.models import Measurement, Sample, SamplingEvent


class MeasurementCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "measurementChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.sample = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])


class MeasurementBulkCreateView(LoginRequiredMixin, HTMXFormMixin, FormView):
    form_class = MeasurementBulkForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "measurementChanged"
    htmx_render_template = "shared/simple_form.html"

    def form_valid(self, form):
        sample = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])
        cleaned_data = form.clean_data()
        for data in cleaned_data:
            Measurement.objects.create(
                sample=sample,
                parameter=data["parameter"],
                value=data["value"],
                unit=data["unit"],
                measured_on=data["measured_on"],
                details=form.cleaned_data.get("details", ""),
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("sample_detail", kwargs={"pk": self.kwargs["sample_pk"]})


class MeasurementUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "measurementChanged"
    htmx_render_template = "shared/simple_form.html"

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs["measurement_pk"])

    def update_form_instance(self, form):
        form.instance.sample = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])


class MeasurementDeleteView(LoginRequiredMixin, DeleteHTMX, DeleteView):
    model = Measurement
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs["measurement_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["samplingevent"] = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )
        context["sample"] = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])

        return context


class MeasurementDetailView(LoginRequiredMixin, RenderToResponseMixin, DetailView):
    model = Measurement
    template_name = "waterquality/partial/measurement_detail.html"
    htmx_template = "waterquality/partial/measurement_detail.html"

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs["measurement_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["samplingevent"] = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )
        context["sample"] = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])

        return context


class MeasurementListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = Measurement
    template_name = "waterquality/partial/measurement_list.html"
    htmx_template = "waterquality/partial/measurement_table.html"

    def get_queryset(self):
        sample = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])
        return sample.measurements.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["samplingevent"] = get_object_or_404(
            SamplingEvent, pk=self.kwargs["samplingevent_pk"]
        )
        context["sample"] = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])

        return context


measurement_create_view = MeasurementCreateView.as_view()
measurement_bulk_create_view = MeasurementBulkCreateView.as_view()
measurement_update_view = MeasurementUpdateView.as_view()
measurement_delete_view = MeasurementDeleteView.as_view()
measurement_detail_view = MeasurementDetailView.as_view()
measurement_list_view = MeasurementListView.as_view()
