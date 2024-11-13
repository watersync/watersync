from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from watersync.core.models import Location
from watersync.core.models import Project
from watersync.users.models import User

from watersync.utils.get_objects import get_project_location
from .forms import GWLForm
from .models import GWLManualMeasurements





class GWLCreateView(LoginRequiredMixin, CreateView):
    model = GWLManualMeasurements
    form_class = GWLForm
    template_name = "groundwater/gwl_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request, self.kwargs)
        context["project"] = project
        context["location"] = location
        return context

    def form_valid(self, form):
        project, location = get_project_location(self.request, self.kwargs)
        form.instance.project = project
        form.instance.location = location

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("groundwater:gwlmeasurements", kwargs=self.kwargs)


class GWLDeleteView(LoginRequiredMixin, DeleteView):
    model = GWLManualMeasurements
    template_name = "confirm_delete.html"

    def get_object(self):
        project, location = get_project_location(self.request, self.kwargs)
        return get_object_or_404(
            GWLManualMeasurements,
            pk=self.kwargs["gwlmeasurement_pk"],
            location=location,
            location__project=project,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request, self.kwargs)
        context["project"] = project
        context["location"] = location
        return context

    def get_success_url(self):
        kwargs = self.kwargs.copy()
        kwargs.pop("gwlmeasurement_pk", None)
        return reverse("groundwater:gwlmeasurements", kwargs=kwargs)


class GWLUpdateView(LoginRequiredMixin, UpdateView):
    model = GWLManualMeasurements
    form_class = GWLForm
    template_name = "groundwater/gwl_form.html"
    success_url = reverse_lazy("groundwater:gwlmeasurements")


class GWLListView(LoginRequiredMixin, ListView):
    model = GWLManualMeasurements
    template_name = "groundwater/gwl_list.html"

    def get_queryset(self):
        project, location = get_project_location(self.request, self.kwargs)

        measurements = GWLManualMeasurements.objects.filter(
            location=location, location__project=project
        )

        return measurements

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request, self.kwargs)
        context["project"] = project
        context["location"] = location
        return context


class GWLDetailView(LoginRequiredMixin, DetailView):
    model = GWLManualMeasurements
    template_name = "groundwater/gwl_detail.html"
    context_object_name = "measurement"

    def get_object(self):
        project, location = get_project_location(self.request, self.kwargs)
        return get_object_or_404(
            GWLManualMeasurements,
            pk=self.kwargs["gwlmeasurement_pk"],
            location=location,
            location__project=project,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request, self.kwargs)
        context["project"] = project
        context["location"] = location
        return context


gwl_list_view = GWLListView.as_view()
gwl_create_view = GWLCreateView.as_view()
gwl_detail_view = GWLDetailView.as_view()
gwl_update_view = GWLUpdateView.as_view()
gwl_delete_view = GWLDeleteView.as_view()
