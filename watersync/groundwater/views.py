from watersync.users.models import User
from watersync.core.models import Project, Location
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView)
from .models import GWLManualMeasurements
from .forms import GWLForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404


def get_project_location(request, kwargs):
    project = get_object_or_404(Project,
                                pk=kwargs['project_pk'],
                                user__id=request.user.id)
    location = get_object_or_404(Location,
                                 pk=kwargs['location_pk'],
                                 project=project)

    return project, location


class GWLCreateView(LoginRequiredMixin, CreateView):
    model = GWLManualMeasurements
    form_class = GWLForm
    template_name = 'groundwater/gwl_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request,
                                                 self.kwargs)
        context['project'] = project
        context['location'] = location
        return context

    def form_valid(self, form):
        project, location = get_project_location(self.request,
                                                 self.kwargs)
        form.instance.project = project
        form.instance.location = location

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('groundwater:gwlmeasurements', kwargs=self.kwargs)


class GWLDeleteView(LoginRequiredMixin, DeleteView):
    model = GWLManualMeasurements
    template_name = 'confirm_delete.html'

    def get_object(self):
        project, location = get_project_location(self.request,
                                                 self.kwargs)
        return get_object_or_404(GWLManualMeasurements,
                                 pk=self.kwargs['gwlmeasurement_pk'],
                                 location=location,
                                 location__project=project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request,
                                                 self.kwargs)
        context['project'] = project
        context['location'] = location
        return context

    def get_success_url(self):
        kwargs = self.kwargs.copy()
        kwargs.pop('gwlmeasurement_pk', None)
        return reverse('groundwater:gwlmeasurements', kwargs=kwargs)


class GWLUpdateView(LoginRequiredMixin, UpdateView):
    model = GWLManualMeasurements
    form_class = GWLForm
    template_name = 'groundwater/gwl_form.html'
    success_url = reverse_lazy('groundwater:gwlmeasurements')


class GWLListView(LoginRequiredMixin, ListView):
    model = GWLManualMeasurements
    template_name = 'groundwater/gwl_list.html'

    def get_queryset(self):
        project, location = get_project_location(self.request,
                                                 self.kwargs)

        measurements = GWLManualMeasurements.objects.\
            filter(location=location,
                   location__project=project)

        return measurements

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request,
                                                 self.kwargs)
        context['project'] = project
        context['location'] = location
        return context


class GWLDetailView(LoginRequiredMixin, DetailView):
    model = GWLManualMeasurements
    template_name = 'groundwater/gwl_detail.html'
    context_object_name = 'measurement'

    def get_object(self):
        project, location = get_project_location(self.request,
                                                 self.kwargs)
        return get_object_or_404(GWLManualMeasurements,
                                 pk=self.kwargs['gwlmeasurement_pk'],
                                 location=location,
                                 location__project=project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project, location = get_project_location(self.request,
                                                 self.kwargs)
        context['project'] = project
        context['location'] = location
        return context
