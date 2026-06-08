
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from watersync.core.config import get_parameter_choices, get_parameters_json
from watersync.core.generics.mixins import FilterMixin
from watersync.core.generics.views import (
    WatersyncCreateView,
    WatersyncDeleteView,
    WatersyncDetailView,
    WatersyncHistoryListView,
    WatersyncListView,
    WatersyncUpdateView,
)
from watersync.core.models import Project
from watersync.waterquality.filters import SampleFilter
from watersync.waterquality.forms import (
    MeasurementBulkForm,
    MeasurementForm,
    MeasurementRowFormSet,
    SampleForm,
)
from watersync.waterquality.forms_setup import ProtocolForm
from watersync.waterquality.models import HistoricalSample, Measurement, Sample
from watersync.waterquality.models_setup import Protocol


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


class SampleListView(FilterMixin, WatersyncListView):
    model = Sample
    detail_type = "page"
    filterset_class = SampleFilter

    def get_base_queryset(self):
        return Sample.objects.for_project(
            self.kwargs["project_pk"]
        ).order_by("-fieldwork__date")


class SampleDetailView(WatersyncDetailView):
    model = Sample
    detail_type = "popover"


class SampleOverviewView(TemplateView):
    template_name = "waterquality/sample_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["sample"] = get_object_or_404(
            Sample.objects.with_counts(),
            pk=self.kwargs["sample_pk"]
        )
        return context
    
class SampleHistoryListView(WatersyncHistoryListView):
    model = HistoricalSample

class SampleHistoryDeleteView(WatersyncDeleteView):
    model = HistoricalSample

sample_history_list_view = SampleHistoryListView.as_view()
sample_history_delete_view = SampleHistoryDeleteView.as_view()

sample_overview_view = SampleOverviewView.as_view()
sample_create_view = SampleCreateView.as_view()
sample_update_view = SampleUpdateView.as_view()
sample_delete_view = SampleDeleteView.as_view()
sample_list_view = SampleListView.as_view()
sample_detail_view = SampleDetailView.as_view()


# ================ Measurement views ========================

class MeasurementBulkPreviewView(LoginRequiredMixin, View):
    """HTMX endpoint for live preview of bulk measurement data."""
    
    def post(self, request, *args, **kwargs):
        from watersync.waterquality.utils import (
            parse_bulk_file,
            parse_bulk_measurement_data,
            validate_bulk_data_for_sample,
        )
        
        rows = []
        error_message = None
        
        # Check if it's a file upload or paste data
        if request.FILES.get("file"):
            rows, error_message = parse_bulk_file(request.FILES["file"])
        else:
            data_str = request.POST.get("data", "")
            rows = parse_bulk_measurement_data(data_str)
        
        # Get sample for validation
        sample_pk = request.POST.get("sample_pk") or request.POST.get("sample")
        sample = None
        
        if sample_pk:
            try:
                sample = Sample.objects.get(pk=sample_pk)
                rows = validate_bulk_data_for_sample(sample, rows)
            except Sample.DoesNotExist:
                pass
        
        valid_count = sum(1 for r in rows if r["is_valid"])
        invalid_count = sum(1 for r in rows if not r["is_valid"])
        
        return TemplateResponse(
            request,
            "waterquality/bulk_preview.html",
            {
                "rows": rows,
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "error_message": error_message,
            }
        )


measurement_bulk_preview_view = MeasurementBulkPreviewView.as_view()


class MeasurementCreateView(WatersyncCreateView):
    model = Measurement
    form_class = MeasurementForm
    bulk_form_class = MeasurementBulkForm

    def get_template_names(self):
        """Use custom template for bulk form."""
        if self.get_form_class() == self.bulk_form_class:
            return ["waterquality/bulk_measurement_form.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add context for bulk form only
        if self.get_form_class() == self.bulk_form_class:
            # Preview URL for paste mode
            context["preview_url"] = reverse(
                "waterquality:bulk-preview-measurement",
                kwargs={"project_pk": self.kwargs.get("project_pk")}
            )
            
            # Get sample's parameter group for filtering
            sample_pk = self.request.GET.get("sample_pk") or self.request.POST.get("sample_pk")
            parameter_group = None
            
            if sample_pk:
                try:
                    sample = Sample.objects.get(pk=sample_pk)
                    parameter_group = sample.parameter_group
                    context["sample_parameter_group"] = parameter_group
                except Sample.DoesNotExist:
                    pass
            
            # Formset for manual entry mode
            if self.request.method == "POST":
                formset = MeasurementRowFormSet(self.request.POST, prefix="form")
            else:
                formset = MeasurementRowFormSet(prefix="form")
            
            # Filter parameter choices if we have a parameter group
            if parameter_group:
                filtered_choices = [("", "---------")] + list(get_parameter_choices(group=parameter_group))
                for form in formset:
                    form.fields["parameter"].choices = filtered_choices
            
            context["formset"] = formset
            context["parameters_json"] = get_parameters_json()
        
        return context

    def handle_bulk_create(self, form, instance):
        """Handle bulk creation based on input mode."""
        if not isinstance(form, self.bulk_form_class):
            return
        
        input_mode = form.cleaned_data.get("input_mode", "paste")
        
        if input_mode == "formset":
            # Handle formset data
            formset = MeasurementRowFormSet(self.request.POST, prefix="form")
            
            if formset.is_valid():
                sample = form.cleaned_data.get("sample")
                measurements = []
                
                for row_form in formset:
                    if row_form.cleaned_data and row_form.cleaned_data.get("parameter"):
                        measurements.append(
                            Measurement(
                                sample=sample,
                                parameter=row_form.cleaned_data["parameter"],
                                value=row_form.cleaned_data["value"],
                                unit=row_form.cleaned_data["unit"],
                            )
                        )
                
                if measurements:
                    Measurement.objects.bulk_create(measurements)
        else:
            # Handle paste or file mode
            processed_data = form.cleaned_data.get("processed_data", [])
            measurements = [
                Measurement(
                    sample=data["sample"],
                    parameter=data["parameter"],
                    value=data["value"],
                    unit=data["unit"],
                )
                for data in processed_data
            ]
            
            if measurements:
                Measurement.objects.bulk_create(measurements)


class MeasurementDeleteView(WatersyncDeleteView):
    model = Measurement


class MeasurementDetailView(WatersyncDetailView):
    model = Measurement


class MeasurementListView(WatersyncListView):
    model = Measurement
    detail_type = None

    def get_base_queryset(self):
        qs = Measurement.objects.for_project(
            self.kwargs["project_pk"]
        ).order_by("-sample__fieldwork__date")

        if self.request.GET.get("sample_pk"):
            qs = qs.filter(sample_id=self.request.GET.get("sample_pk"))

        return qs


measurement_create_view = MeasurementCreateView.as_view()
measurement_delete_view = MeasurementDeleteView.as_view()
measurement_detail_view = MeasurementDetailView.as_view()
measurement_list_view = MeasurementListView.as_view()
