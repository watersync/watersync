from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
    DeleteView,
    DetailView,
)
from watersync.core.models import Location, Project
from watersync.waterquality.models import Sample, Measurement
from watersync.waterquality.forms import SampleForm, MeasurementForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Protocol, SamplingEvent, Sample, Measurement
from .forms import ProtocolForm, SampleForm, SamplingEventForm, MeasurementForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from watersync.utils.get_objects import get_project_location

# ================ Protocols ========================
class ProtocolListView(LoginRequiredMixin, ListView):
    model = Protocol

    def get_queryset(self):
        return Protocol.objects.all()


class ProtocolDetailView(LoginRequiredMixin, DetailView):
    model = Protocol
    template_name = "waterquality/protocol_detail.html"

    def get_object(self):
        return get_object_or_404(
            Protocol,
            pk=self.kwargs["protocol_pk"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['protocol'] = self.get_object()
        return context


class ProtocolCreateView(LoginRequiredMixin, CreateView):
    model = Protocol
    form_class = ProtocolForm
    template_name = "waterquality/protocol_form.html"

    def get_success_url(self):
        return reverse("users:settings", kwargs=self.kwargs)


class ProtocolUpdateView(LoginRequiredMixin, UpdateView):
    model = Protocol
    form_class = ProtocolForm
    template_name = "waterquality/protocol_form.html"

    def get_object(self):
        return get_object_or_404(
            Protocol,
            pk=self.kwargs["protocol_pk"]
        )

    def get_success_url(self):
        return reverse("waterquality:detail-protocol", kwargs=self.kwargs)


class ProtocolDeleteView(LoginRequiredMixin, DeleteView):
    model = Protocol
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(
            Protocol,
            pk=self.kwargs["protocol_pk"]
        )

    def get_success_url(self):
        # Use "user_id" to match the URL pattern
        return reverse("users:settings", kwargs={"user_id": self.request.user.id})
    


# ================ Sample Events ========================
class SamplingEventListView(LoginRequiredMixin, ListView):
    model = SamplingEvent

    def get_queryset(self):
        return SamplingEvent.objects.all()

class SamplingEventDetailView(LoginRequiredMixin, DetailView):
    model = SamplingEvent
    template_name = "waterquality/samplingevent_detail.html"

    def get_object(self):
        return get_object_or_404(SamplingEvent, pk=self.kwargs["samplingevent_pk"])

    def get_success_url(self):
        return reverse("core:detail-location", kwargs=self.kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request, self.kwargs)
        context["project"] = project
        context["location"] = location
        context["sample_list"] = self.get_object().samples.all()
        context["sample_form"] = SampleForm()
        return context


class SamplingEventCreateView(LoginRequiredMixin, CreateView):
    model = SamplingEvent
    form_class = SamplingEventForm
    template_name = "samplingevent_form.html"

    def form_valid(self, form):
        form.instance.executed_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:detail-location", kwargs=self.kwargs)


class SamplingEventUpdateView(LoginRequiredMixin, UpdateView):
    model = SamplingEvent
    form_class = SamplingEventForm
    template_name = "waterquality/samplingevent_form.html"

    def get_object(self):
        return get_object_or_404(SamplingEvent, pk=self.kwargs["samplingevent_pk"])

    def get_success_url(self):
        return reverse("waterquality:detail-samplingevent", kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request, self.kwargs)
        context["project"] = project
        context["location"] = location
        return context

class SamplingEventDeleteView(LoginRequiredMixin, DeleteView):
    model = SamplingEvent
    template_name = "confirm_delete.html"

    def get_success_url(self):
        return reverse("core:detail-location", kwargs=self.kwargs)


# ================ Sample views ========================
class SampleListView(LoginRequiredMixin, ListView):
    model = Sample
    template_name = "sample_list.html"


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
        sampling_event = get_object_or_404(SamplingEvent, pk=self.kwargs["samplingevent_pk"])
        
        context["project"] = project
        context["location"] = location
        context["samplingevent"] = sampling_event
        context["measurement_list"] = self.get_object().measurements.all()
        context["measurement_form"] = MeasurementForm()
        return context


class SampleCreateView(LoginRequiredMixin, CreateView):
    model = Sample
    form_class = SampleForm
    template_name = "sample_form.html"

    def get_success_url(self):
        return reverse("waterquality:detail-samplingevent", kwargs=self.kwargs)


class SampleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sample
    form_class = SampleForm
    template_name = "sample_form.html"

    def get_success_url(self):
        return reverse("waterquality:detail-sample", kwargs=self.kwargs)


class SampleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sample
    template_name = "confirm_delete.html"

    def get_success_url(self):
        return reverse("waterquality:detail-samplingevent", kwargs=self.kwargs)


# Measurement Views
class MeasurementListView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = "measurement_list.html"


class MeasurementCreateView(LoginRequiredMixin, CreateView):
    model = Measurement
    form_class = MeasurementForm

    def get_success_url(self):
        return reverse("waterquality:detail-sample", kwargs=self.kwargs)


class MeasurementUpdateView(LoginRequiredMixin, UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = "measurement_form.html"

    def get_success_url(self):
        return reverse("detail-measurement", kwargs=self.kwargs)


class MeasurementDeleteView(LoginRequiredMixin, DeleteView):
    model = Measurement
    template_name = "confirm_delete.html"

    def get_success_url(self):
        return reverse("waterquality:detail-sample", kwargs=self.kwargs)