from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView)
from watersync.core.models import Location, Project
from watersync.waterquality.models import Sample, Measurement
from watersync.waterquality.forms import SampleForm, MeasurementForm
from django.contrib.auth.mixins import LoginRequiredMixin


# ================ Sample views ========================

class SampleCreateView(LoginRequiredMixin, CreateView):
    model = Sample
    form_class = SampleForm
    template_name = 'waterquality/sample_form.html'

    def get_success_url(self):
        return reverse_lazy('waterquality:samples', kwargs={
            'location_pk': self.kwargs['location_pk'],
            'project_pk': self.kwargs['project_pk'],
            'user_id': self.request.user.id
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)
        return context

    def form_valid(self, form):
        sample = form.save(commit=False)
        location_id_from_url = self.kwargs.get('location_pk')

        if location_id_from_url:
            sample.location_id = location_id_from_url

        sample.save()
        return super().form_valid(form)


class SampleListView(LoginRequiredMixin, ListView):
    model = Sample
    template_name = 'waterquality/sample_list.html'

    def get_queryset(self):
        location_pk = self.kwargs.get('location_pk')

        samples = Sample.objects.filter(location=location_pk)

        return samples

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)

        return context


class SampleDetailView(LoginRequiredMixin, DetailView):
    model = Sample
    template_name = 'waterquality/sample_detail.html'

    def get_object(self):
        return get_object_or_404(Sample, pk=self.kwargs['sample_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample = self.get_object()

        measurements = sample.measurements.all()

        context['measurement_list'] = measurements
        context['project'] = sample.location.project
        context['sample'] = sample
        context['location'] = sample.location

        return context


class SampleDeleteView(LoginRequiredMixin, DeleteView):
    model = Sample
    template_name = 'confirm_delete.html'

    def get_object(self):
        return get_object_or_404(Sample, pk=self.kwargs['sample_pk'])

    def get_success_url(self):
        return reverse('waterquality:samples', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk'],
            'location_pk': self.kwargs['location_pk']
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)

        return context


class SampleUpdateView(LoginRequiredMixin, UpdateView):
    model = Sample
    form_class = SampleForm
    template_name = 'waterquality/sample_form.html'

    def get_object(self):
        return get_object_or_404(Sample, pk=self.kwargs['sample_pk'])

    def get_success_url(self):
        return reverse('waterquality:detail-sample', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk'],
            'location_pk': self.kwargs['location_pk'],
            'sample_pk': self.kwargs['sample_pk'],
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)

        return context


# ================ Measurement views ========================

class MeasurementCreateView(LoginRequiredMixin, CreateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'waterquality/measurement_form.html'

    def get_success_url(self):
        return reverse_lazy('waterquality:detail-sample', kwargs={
            'location_pk': self.kwargs['location_pk'],
            'project_pk': self.kwargs['project_pk'],
            'sample_pk': self.kwargs['sample_pk'],
            'user_id': self.request.user.id
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')
        sample_pk = self.kwargs.get('sample_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)
        context['sample'] = get_object_or_404(Sample, pk=sample_pk)
        return context

    def form_valid(self, form):

        measurement = form.save(commit=False)
        sample_id = self.kwargs.get('sample_pk')

        if sample_id:
            measurement.sample_id = sample_id

        measurement.save()
        return super().form_valid(form)


class MeasurementListView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = 'waterquality/measurement_list.html'

    def get_queryset(self):
        sample_pk = self.kwargs.get('sample_pk')
        samples = Measurement.objects.filter(sample=sample_pk)

        return samples

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')
        sample_pk = self.kwargs.get('sample_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)
        context['sample'] = get_object_or_404(Sample, pk=sample_pk)

        return context


class MeasurementDetailView(LoginRequiredMixin, DetailView):
    model = Measurement
    template_name = 'waterquality/measurement_detail.html'

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs['measurement_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        measurement = self.get_object()

        context['project'] = measurement.sample.location.project
        context['sample'] = measurement.sample
        context['location'] = measurement.sample.location

        return context


class MeasurementDeleteView(LoginRequiredMixin, DeleteView):
    model = Measurement
    template_name = 'confirm_delete.html'

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs['measurement_pk'])

    def get_success_url(self):
        return reverse('waterquality:detail-sample', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk'],
            'location_pk': self.kwargs['location_pk'],
            'sample_pk': self.kwargs['sample_pk'],
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        measurement = self.get_object()
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')
        sample_pk = self.kwargs.get('sample_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)
        context['sample'] = get_object_or_404(Sample, pk=sample_pk)
        context['measurement_pk'] = measurement

        return context


class MeasurementUpdateView(LoginRequiredMixin, UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'waterquality/measurement_form.html'

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs['measurement_pk'])

    def get_success_url(self):
        return reverse('waterquality:detail-measurement', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk'],
            'location_pk': self.kwargs['location_pk'],
            'sample_pk': self.kwargs['sample_pk'],
            'measurement_pk': self.kwargs['measurement_pk'],
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        measurement = self.get_object()
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')
        sample_pk = self.kwargs.get('sample_pk')

        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)
        context['sample'] = get_object_or_404(Sample, pk=sample_pk)
        context['measurement_pk'] = measurement
        return context
