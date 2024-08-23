from watersync.users.models import User
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView)
from watersync.sensor.models import Sensor
from .forms import SensorForm
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

# Project views


class SensorCreateView(LoginRequiredMixin, CreateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'sensor/sensor_form.html'

    def form_valid(self, form):
        # Set the current user as the owner of the sensor
        form.instance.owner = self.request.user

        # Proceed with the standard form validation and save
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('sensor:sensors', kwargs={'user_id': self.kwargs['user_id']})


class SensorDeleteView(DeleteView):
    model = Sensor

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs['sensor_pk'])

    def get_success_url(self):
        return reverse('sensor:sensors', kwargs={'user_id': self.kwargs['user_id']})


class SensorUpdateView(UpdateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'core/project_update_form.html'

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs['sensor_pk'])

    def get_success_url(self):
        return reverse('sensor:projects', kwargs={'user_id': self.kwargs['user_id']})


class SensorListView(ListView):
    model = Sensor
    paginate_by = 6
    template_name = 'sensor/sensor_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = User.objects.get(pk=self.kwargs['user_id'])
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Sensor.objects.filter(owner__id=user_id)


class SensorDetailView(DetailView):
    model = Sensor
    template_name = 'sensor/sensor_detail.html'

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs['sensor_pk'])
