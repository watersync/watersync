from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView)
from watersync.core.models import Location, Project
from watersync.waterquality.models import Sample, Measurement
from watersync.waterquality.forms import SampleForm, MeasurementForm


# ================ Sample views ========================

class SampleCreateView(CreateView):
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
        context['user_id'] = self.request.user.id
        return context

    def form_valid(self, form):
        # Here you can add any additional processing before saving
        sample = form.save(commit=False)

        # Assuming 'sample_id' is the field in your model where you want to store the ID from the URL
        location_id_from_url = self.kwargs.get('location_pk')

        if location_id_from_url:
            sample.location_id = location_id_from_url

        # Now save the instance
        sample.save()

        # Proceed with the default form_valid behavior
        return super().form_valid(form)


class SampleListView(ListView):
    model = Sample
    template_name = 'waterquality/sample_list.html'

    def get_queryset(self):
        location_pk = self.kwargs.get('location_pk')

        samples = Sample.objects.filter(location=location_pk)

        return samples

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id  # Get the user ID from the request
        # Get the project_pk from the URL
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)

        # Pass user_id, project_pk, and location_pk to the template
        context['user_id'] = user_id
        context['project_pk'] = project_pk

        return context


class SampleDetailView(DetailView):
    model = Sample
    template_name = 'waterquality/sample_detail.html'

    def get_object(self):
        return get_object_or_404(Sample, pk=self.kwargs['sample_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sample = self.get_object()

        # Fetch the sensor records for this deployment
        measurements = Measurement.objects.filter(
            sample=sample)

        context['measuremet_list'] = measurements

        # Additional context
        context['project'] = sample.location.project
        context['sample'] = sample
        context['location'] = sample.location
        context['user_id'] = self.request.user.id
        context['project_pk'] = sample.location.project.pk
        context['sample_pk'] = sample.pk

        return context


class SampleDeleteView(DeleteView):
    model = Sample

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
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk
        context['location_pk'] = location_pk

        return context


class SampleUpdateView(UpdateView):
    model = Sample
    form_class = SampleForm
    template_name = 'waterquality/sample_form.html'

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
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk
        context['location_pk'] = location_pk

        return context


# ================ Measurement views ========================

class MeasurementCreateView(CreateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'waterquality/measurement_form.html'

    def get_success_url(self):
        return reverse_lazy('waterquality:measurements', kwargs={
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
        context['user_id'] = self.request.user.id
        return context

    def form_valid(self, form):
        # Here you can add any additional processing before saving
        measurement = form.save(commit=False)

        # Assuming 'sample_id' is the field in your model where you want to store the ID from the URL
        sample_id = self.kwargs.get('sample_pk')

        if sample_id:
            measurement.sample_id = sample_id

        # Now save the instance
        measurement.save()

        # Proceed with the default form_valid behavior
        return super().form_valid(form)


class MeasurementListView(ListView):
    model = Measurement
    template_name = 'waterquality/measurement_list.html'

    def get_queryset(self):
        sample_pk = self.kwargs.get('sample_pk')
        samples = Measurement.objects.filter(sample=sample_pk)

        return samples

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id  # Get the user ID from the request
        # Get the project_pk from the URL
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')
        sample_pk = self.kwargs.get('sample_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['location'] = get_object_or_404(Location, pk=location_pk)
        context['sample'] = get_object_or_404(Sample, pk=sample_pk)

        # Pass user_id, project_pk, and location_pk to the template
        context['user_id'] = user_id
        context['project_pk'] = project_pk

        return context


class MeasurementDetailView(DetailView):
    model = Measurement
    template_name = 'waterquality/measurement_detail.html'

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs['measurement_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        measurement = self.get_object()

        # Additional context
        context['project'] = measurement.sample.location.project
        context['sample'] = measurement.sample
        context['location'] = measurement.sample.location
        context['user_id'] = self.request.user.id
        context['project_pk'] = measurement.sample.location.project.pk
        context['sample_pk'] = measurement.sample.pk

        return context


class MeasurementDeleteView(DeleteView):
    model = Measurement

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs['measurement_pk'])

    def get_success_url(self):
        return reverse('waterquality:samples', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk'],
            'location_pk': self.kwargs['location_pk'],
            'sample_pk': self.kwargs['sample_pk']
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')
        sample_pk = self.kwargs.get('sample_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk
        context['location_pk'] = location_pk
        context['sample_pk'] = sample_pk

        return context


class MeasurementUpdateView(UpdateView):
    model = Measurement
    form_class = MeasurementForm
    template_name = 'waterquality/measurement_form.html'

    def get_object(self):
        return get_object_or_404(Measurement, pk=self.kwargs['measurement_pk'])

    def get_success_url(self):
        return reverse('waterquality:samples', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk'],
            'location_pk': self.kwargs['location_pk'],
            'sample_pk': self.kwargs['sample_pk'],
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')
        sample_pk = self.kwargs.get('sample_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk
        context['location_pk'] = location_pk
        context['sample_pk'] = sample_pk

        return context
