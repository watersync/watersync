from watersync.users.models import User
from watersync.core.models import Project, Location
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView)
from .models import GWLManualMeasurements
from .forms import GWLForm
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404


class GWLCreateView(CreateView):
    model = GWLManualMeasurements
    form_class = GWLForm
    template_name = 'groundwater/gwl_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(
            Project, pk=self.kwargs['project_pk'], user__id=self.kwargs['user_id'])
        context['location'] = get_object_or_404(
            Location, pk=self.kwargs['location_pk'], project__user__id=self.kwargs['user_id'])
        return context

    def form_valid(self, form):
        # Set the project and location based on the URL parameters
        form.instance.project = get_object_or_404(
            Project, pk=self.kwargs['project_pk'], user__id=self.kwargs['user_id'])
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs['location_pk'], project__user__id=self.kwargs['user_id'])
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('groundwater:gwlmeasurements', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk'],
            'location_pk': self.kwargs['location_pk'],
        })


class GWLDeleteView(LoginRequiredMixin, DeleteView):
    model = GWLManualMeasurements
    template_name = 'groundwater/gwl_confirm_delete.html'

    def get_object(self):
        # Retrieve the measurement object based on the correct primary key
        return get_object_or_404(GWLManualMeasurements,
                                 # Use gwlmeasurement_pk here
                                 pk=self.kwargs['gwlmeasurement_pk'],
                                 # Ensure it matches the correct location
                                 location__pk=self.kwargs['location_pk'],
                                 location__project__pk=self.kwargs['project_pk'])  # Ensure it matches the correct project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['project'] = get_object_or_404(
            Project, pk=self.kwargs['project_pk'])
        context['location'] = get_object_or_404(
            Location, pk=self.kwargs['location_pk'])
        return context

    def get_success_url(self):
        return reverse('groundwater:gwlmeasurements', kwargs={
            'user_id': self.request.user.id,
            'project_pk': self.kwargs['project_pk'],
            # Include location_pk to redirect correctly
            'location_pk': self.kwargs['location_pk'],
        })


class GWLUpdateView(UpdateView):
    model = GWLManualMeasurements
    form_class = GWLForm
    template_name = 'groundwater/gwl_update_form.html'
    success_url = reverse_lazy('core:list')


class GWLListView(ListView):
    model = GWLManualMeasurements
    template_name = 'groundwater/gwl_list.html'

    def get_queryset(self):
        location_id = self.kwargs.get('location_pk')
        user = self.request.user

        location = get_object_or_404(
            Location, id=location_id, project__user=user)

        measurements = GWLManualMeasurements.objects.filter(location=location)

        return measurements

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(
            Project, id=self.kwargs['project_pk'])
        context['location'] = get_object_or_404(
            Location, id=self.kwargs['location_pk'])
        return context


class GWLDetailView(LoginRequiredMixin, DetailView):
    model = GWLManualMeasurements
    template_name = 'groundwater/gwl_detail.html'
    context_object_name = 'measurement'

    def get_object(self):
        # Retrieve the measurement object based on the project, location, and measurement primary keys
        return get_object_or_404(GWLManualMeasurements,
                                 pk=self.kwargs['gwlmeasurement_pk'],
                                 location__pk=self.kwargs['location_pk'],
                                 location__project__pk=self.kwargs['project_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created_at'] = timezone.now()
        context['project'] = get_object_or_404(
            Project, pk=self.kwargs['project_pk'])
        context['location'] = get_object_or_404(
            Location, pk=self.kwargs['location_pk'])
        return context
