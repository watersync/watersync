import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic import TemplateView

from watersync.core.generics.decorators import filter_by_conditions, filter_by_location, filter_by_fieldwork
from watersync.core.generics.views import (
    WatersyncCreateView,
    WatersyncDeleteView,
    WatersyncDetailView,
    WatersyncListView,
    WatersyncUpdateView,
)
from watersync.core.models import Fieldwork, Location, Project
from watersync.waterquality.forms import (
    MeasurementBulkForm,
    MeasurementForm,
    SampleForm,
)
from watersync.waterquality.forms_setup import ProtocolForm
from watersync.waterquality.models import Measurement, Sample
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
    prefill_from_parent = {
        'location': ('location_pk', Location),
        'fieldwork': ('fieldwork_pk', Fieldwork),
    }


class SampleUpdateView(WatersyncUpdateView):
    model = Sample
    form_class = SampleForm


class SampleDeleteView(WatersyncDeleteView):
    model = Sample


class SampleListView(WatersyncListView):
    model = Sample
    detail_type = "page"

    @filter_by_fieldwork
    @filter_by_location
    def get_queryset(self):
        project = self.get_project()
        return Sample.objects.filter(
            location__in=project.locations.all()
        ).order_by("-fieldwork__date")


class SampleDetailView(WatersyncDetailView):
    model = Sample
    detail_type = "popover"


class SampleOverviewView(TemplateView):
    template_name = "waterquality/sample_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["sample"] = get_object_or_404(Sample, pk=self.kwargs["sample_pk"])
        return context

sample_overview_view = SampleOverviewView.as_view()
sample_create_view = SampleCreateView.as_view()
sample_update_view = SampleUpdateView.as_view()
sample_delete_view = SampleDeleteView.as_view()
sample_list_view = SampleListView.as_view()
sample_detail_view = SampleDetailView.as_view()


# ================ Measurement views ========================

class MeasurementBulkPreviewView(LoginRequiredMixin, View):
    """HTMX endpoint for live preview of bulk measurement data (paste or file)."""
    
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
        
        # Get sample for additional validation
        sample_pk = request.POST.get("sample_pk") or request.POST.get("sample")
        sample = None
        
        if sample_pk:
            try:
                sample = Sample.objects.get(pk=sample_pk)
            except Sample.DoesNotExist:
                pass
        
        # Add sample-specific validation (parameter group, duplicates)
        if sample:
            rows = validate_bulk_data_for_sample(sample, rows)
        
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
    prefill_from_parent = {
        'sample': ('sample_pk', Sample),
    }

    def get_template_names(self):
        """Use custom template for bulk form."""
        if self.get_form_class() == self.bulk_form_class:
            return ["waterquality/bulk_measurement_form.html"]
        return super().get_template_names()

    def dispatch(self, request, *args, **kwargs):
        """Set htmx_render_template dynamically based on form type."""
        response = super().dispatch(request, *args, **kwargs)
        return response

    def get_htmx_template(self):
        """Get the correct template for HTMX responses."""
        if self.get_form_class() == self.bulk_form_class:
            return "waterquality/bulk_measurement_form.html"
        return self.htmx_render_template

    def form_invalid(self, form):
        """Override to use correct template for bulk form errors."""
        if self.request.htmx:
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            
            self.update_form_instance(form)
            context = self.get_context_data(form=form)
            template = self.get_htmx_template()
            html = render_to_string(template, context, request=self.request)
            return HttpResponse(
                html, status=self.htmx_invalid_status, content_type="text/html"
            )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add context for bulk form
        if self.get_form_class() == self.bulk_form_class:
            from django.urls import reverse
            from watersync.core.config import get_parameters_json, get_parameter_choices
            from watersync.waterquality.forms import MeasurementRowFormSet
            
            # Preview URL for paste mode
            context["preview_url"] = reverse(
                "waterquality:bulk-preview-measurement",
                kwargs={"project_pk": self.kwargs.get("project_pk")}
            )
            
            # Get sample's parameter group to filter formset choices
            sample_pk = self.request.GET.get("sample_pk") or self.request.POST.get("sample_pk")
            parameter_group = None
            if sample_pk:
                try:
                    sample = Sample.objects.get(pk=sample_pk)
                    parameter_group = sample.parameter_group
                    context["sample_parameter_group"] = parameter_group
                except Sample.DoesNotExist:
                    pass
            
            # Formset for manual entry mode with filtered parameters
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
            
            # Parameters JSON for JavaScript unit filtering
            context["parameters_json"] = get_parameters_json()
            
        return context

    def handle_bulk_create(self, form):
        if isinstance(form, self.bulk_form_class):
            input_mode = form.cleaned_data.get("input_mode", "paste")
            
            if input_mode == "formset":
                # Handle formset data
                from watersync.waterquality.forms import MeasurementRowFormSet
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
        ).order_by("-sample__fieldwork__date")


measurement_create_view = MeasurementCreateView.as_view()
measurement_update_view = MeasurementUpdateView.as_view()
measurement_delete_view = MeasurementDeleteView.as_view()
measurement_detail_view = MeasurementDetailView.as_view()
measurement_list_view = MeasurementListView.as_view()
