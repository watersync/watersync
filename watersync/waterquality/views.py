from watersync.waterquality.models import Protocol, Sample, Measurement
from watersync.core.models import LocationVisit, Location
from watersync.waterquality.forms import ProtocolForm, SampleForm, MeasurementForm
from watersync.core.generics.views import (
    WatersyncCreateView,
    WatersyncDeleteView,
    WatersyncDetailView,
    WatersyncListView,
    WatersyncUpdateView,
)
from watersync.core.generics.decorators import filter_by_location
from django.shortcuts import get_object_or_404


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
    detail_type = "modal"

    @filter_by_location
    def get_queryset(self):
        project = self.get_project()
        return Sample.objects.filter(
                location__in=project.locations.all()
            ).order_by("-created")


class SampleDetailView(WatersyncDetailView):
    model = Sample
    detail_type = "popover"


sample_create_view = SampleCreateView.as_view()
sample_update_view = SampleUpdateView.as_view()
sample_delete_view = SampleDeleteView.as_view()
sample_list_view = SampleListView.as_view()
sample_detail_view = SampleDetailView.as_view()

    # template_name = "waterquality/sample_detail.html"

    # def get_object(self):
    #     return get_object_or_404(Sample, pk=self.kwargs["sample_pk"])

    # def get_success_url(self):
    #     return reverse("waterquality:detail-samplingevent", kwargs=self.kwargs)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     project, location = get_project_location(self.request, self.kwargs)
    #     sampling_event = get_object_or_404(
    #         SamplingEvent, pk=self.kwargs["samplingevent_pk"]
    #     )

    #     context["project"] = project
    #     context["location"] = location
    #     context["samplingevent"] = sampling_event
    #     context["measurement_list"] = self.get_object().measurements.all()
    #     context["measurement_form"] = MeasurementForm()
    #     return context

# ================ Measurement views ========================

class MeasurementCreateView(WatersyncCreateView):
    model = Measurement
    form_class = MeasurementForm


# class MeasurementBulkCreateView(LoginRequiredMixin, HTMXFormMixin, FormView):
#     form_class = MeasurementBulkForm
#     template_name = "shared/simple_form.html"

#     htmx_trigger_header = "measurementChanged"
#     htmx_render_template = "shared/simple_form.html"

#     def form_valid(self, form):
#         sample = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])
#         cleaned_data = form.clean_data()
#         for data in cleaned_data:
#             Measurement.objects.create(
#                 sample=sample,
#                 parameter=data["parameter"],
#                 value=data["value"],
#                 unit=data["unit"],
#                 measured_on=data["measured_on"],
#                 details=form.cleaned_data.get("details", ""),
#             )
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse("sample_detail", kwargs={"pk": self.kwargs["sample_pk"]})


class MeasurementUpdateView(WatersyncUpdateView):
    model = Measurement
    form_class = MeasurementForm


class MeasurementDeleteView(WatersyncDeleteView):
    model = Measurement


class MeasurementDetailView(WatersyncDetailView):
    model = Measurement
    detail_type = "popover"

class MeasurementListView(WatersyncListView):
    model = Measurement
    detail_type = "popover"

    def get_queryset(self):
        project = self.get_project()
        locations = project.locations.all()
        samples = Sample.objects.filter(location__in=locations)

        return Measurement.objects.filter(
            sample__in=samples
        ).order_by("-created")


measurement_create_view = MeasurementCreateView.as_view()
# measurement_bulk_create_view = MeasurementBulkCreateView.as_view()
measurement_update_view = MeasurementUpdateView.as_view()
measurement_delete_view = MeasurementDeleteView.as_view()
measurement_detail_view = MeasurementDetailView.as_view()
measurement_list_view = MeasurementListView.as_view()
