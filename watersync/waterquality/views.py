from watersync.waterquality.models import Protocol, Sample, Measurement
from watersync.core.models import Project
from watersync.waterquality.forms import ProtocolForm, SampleForm, MeasurementForm, MeasurementBulkForm
from watersync.core.generics.views import (
    WatersyncCreateView,
    WatersyncDeleteView,
    WatersyncDetailView,
    WatersyncListView,
    WatersyncUpdateView,
)
from django.views.generic import TemplateView
import json
from django.urls import reverse
from watersync.core.generics.decorators import filter_by_location, filter_by_conditions
from django.shortcuts import get_object_or_404
from watersync.core.generics.utils import get_resource_list_context


# ================ Protocols ========================
class ProtocolCreateView(WatersyncCreateView):
    model = Protocol
    form_class = ProtocolForm


class ProtocolUpdateView(WatersyncUpdateView):
    model = Protocol
    form_class = ProtocolForm


class ProtocolDeleteView(WatersyncDeleteView):
    model = Protocol


class ProtocolListView(WatersyncListView):
    model = Protocol
    detail_type = "modal"

    def get_queryset(self):
        return Protocol.objects.all()


class ProtocolDetailView(WatersyncDetailView):
    model = Protocol
    detail_type = "modal"


protocol_create_view = ProtocolCreateView.as_view()
protocol_update_view = ProtocolUpdateView.as_view()
protocol_delete_view = ProtocolDeleteView.as_view()
protocol_list_view = ProtocolListView.as_view()
protocol_detail_view = ProtocolDetailView.as_view()


# ================ Sample views ========================
class SampleCreateView(WatersyncCreateView):
    model = Sample
    form_class = SampleForm


class SampleUpdateView(WatersyncUpdateView):
    model = Sample
    form_class = SampleForm

class SampleDeleteView(WatersyncDeleteView):
    model = Sample

class SampleListView(WatersyncListView):
    model = Sample
    detail_type = "page"

    @filter_by_location
    def get_queryset(self):
        project = self.get_project()
        return Sample.objects.filter(
                location__in=project.locations.all()
            ).order_by("-created")


class SampleDetailView(WatersyncDetailView):
    model = Sample
    detail_type = "popover"


class SampleOverviewView(TemplateView):
    template_name = "waterquality/sample_overview.html"
    
    def get_resource_list_context(self):
        views = {
            "measurements": MeasurementListView,
        }

        return get_resource_list_context(self.request, self.kwargs, views)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        sample = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])
        context["project"] = project
        context["sample"] = sample
        context.update(self.get_resource_list_context())
        context["hx_vals"] = json.dumps({"sample_pk": str(sample.pk)})

        return context

sample_overview_view = SampleOverviewView.as_view()
sample_create_view = SampleCreateView.as_view()
sample_update_view = SampleUpdateView.as_view()
sample_delete_view = SampleDeleteView.as_view()
sample_list_view = SampleListView.as_view()
sample_detail_view = SampleDetailView.as_view()


# ================ Measurement views ========================

class MeasurementCreateView(WatersyncCreateView):
    model = Measurement
    form_class = MeasurementForm
    bulk_form_class = MeasurementBulkForm

    def get_form_class(self):
        """
        Return the form class to use based on the request parameters.
        If 'bulk' is in the request parameters, return the bulk form class.
        """
        if 'bulk' in self.request.GET or 'bulk' in self.request.POST:
            return self.bulk_form_class
        return self.form_class
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.get_form_class() == self.bulk_form_class:
            kwargs.pop('instance', None)
        return kwargs
    
    def form_valid(self, form):
        cleaned_data = form.clean_data()
        for data in cleaned_data:
            Measurement.objects.create(
                sample=data["sample"],
                parameter=data["parameter"],
                value=data["value"],
                unit=data["unit"],
            )
        return super().form_valid(form)

class MeasurementBulkCreateView(WatersyncCreateView):
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


class MeasurementUpdateView(WatersyncUpdateView):
    model = Measurement
    form_class = MeasurementForm


class MeasurementDeleteView(WatersyncDeleteView):
    model = Measurement


class MeasurementDetailView(WatersyncDetailView):
    model = Measurement


class MeasurementListView(WatersyncListView):
    model = Measurement
    detail_type = None

    def get_queryset(self):
        # for all locations in the project
        project = self.get_project()
        locations = project.locations.all()
        samples = Sample.objects.filter(location__in=locations)

        if self.request.GET.get("sample_pk"):
            samples = samples.filter(pk=self.request.GET.get("sample_pk"))

        return Measurement.objects.filter(
            sample__in=samples
        ).order_by("-created")


measurement_create_view = MeasurementCreateView.as_view()
measurement_bulk_create_view = MeasurementBulkCreateView.as_view()
measurement_update_view = MeasurementUpdateView.as_view()
measurement_delete_view = MeasurementDeleteView.as_view()
measurement_detail_view = MeasurementDetailView.as_view()
measurement_list_view = MeasurementListView.as_view()
