from django.views.generic import TemplateView
import plotly.io as pio
import plotly.express as px
from watersync.users.models import User
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView, View, FormView)
from watersync.sensor.models import Sensor, Deployment, SensorRecord
from watersync.core.models import Location, Project
from .forms import SensorForm, DeploymentForm, SensorRecordForm
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
import pandas as pd
import csv
from django.http import HttpResponse

# Sensor views


class SensorCreateView(LoginRequiredMixin, CreateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'sensor/sensor_form.html'

    def form_valid(self, form):
        # Set the current user as the owner of the sensor
        form.instance.user = self.request.user

        # Proceed with the standard form validation and save
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('sensor:sensors',
                       kwargs={'user_id': self.request.user.id})


class SensorListView(ListView):
    model = Sensor
    template_name = 'sensor/sensor_list.html'

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.request.user.id)
        return Sensor.objects.filter(user=user)


class SensorDetailView(DetailView):
    model = Sensor
    template_name = 'sensor/sensor_detail.html'

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs['sensor_pk'])


class SensorUpdateView(UpdateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'sensor/sensor_form.html'

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs['sensor_pk'])

    def get_success_url(self):
        return reverse('sensor:sensors',
                       kwargs={'user_id': self.request.user.id})


class SensorDeleteView(DeleteView):
    model = Sensor
    template_name = 'confirm_delete.html'

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs['sensor_pk'])

    def get_success_url(self):
        return reverse('sensor:sensors',
                       kwargs={'user_id': self.request.user.id})


# ================ Deployment views ========================

class DeploymentCreateView(CreateView):
    model = Deployment
    form_class = DeploymentForm
    template_name = 'sensor/deployment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the project_pk to the form
        kwargs['project_pk'] = self.kwargs['project_pk']
        return kwargs

    def form_valid(self, form):
        # Create the deployment object, but don't save it to the database yet
        deployment = form.save(commit=False)

        # Use the deploy method to set the sensor availability to False
        deployment.deploy()  # This also saves the deployment and sets sensor availability

        # Redirect to the success URL
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('sensor:deployments', kwargs={
            'project_pk': self.kwargs['project_pk'],
            'user_id': self.request.user.id
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get('project_pk')
        context['project'] = get_object_or_404(Project, pk=project_pk)
        context['user_id'] = self.request.user.id
        return context


class DeploymentListView(ListView):
    model = Deployment
    template_name = 'sensor/deployment_list.html'

    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        location_pk = self.kwargs.get('location_pk')

        # if location_pk is present it means the request is made from the
        # location view and I want to get deployments from only one station
        if not location_pk:
            location = Location.objects.filter(project__pk=project_pk)
            # Filter deployments based on the stations linked to this project
            deployments = Deployment.objects.filter(location__in=location)

        else:
            deployments = Deployment.objects.filter(location=location_pk)

        return deployments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id  # Get the user ID from the request
        # Get the project_pk from the URL
        project_pk = self.kwargs.get('project_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        # Pass user_id, project_pk, and location_pk to the template
        context['user_id'] = user_id
        context['project_pk'] = project_pk

        return context


class DeploymentDecommissionView(View):
    def post(self, request, *args, **kwargs):
        deployment = get_object_or_404(Deployment, pk=kwargs['deployment_pk'])
        deployment.decommission()
        return redirect(request.META.get('HTTP_REFERER', 'sensor:deployments'))


class DeploymentDetailView(DetailView):
    model = Deployment
    template_name = 'sensor/deployment_detail.html'

    def get_object(self):
        return get_object_or_404(Deployment, pk=self.kwargs['deployment_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deployment = self.get_object()

        # Fetch the sensor records for this deployment
        records = SensorRecord.objects.filter(
            deployment=deployment).order_by('timestamp')

        # Prepare data for the Plotly graph
        data = {
            'Timestamp': [record.timestamp for record in records],
            'Value': [record.value for record in records],
            'Type': [record.type for record in records],
            'Unit': [record.unit for record in records],
        }

        # Create a Plotly line chart (or any other type of chart)
        fig = px.line(
            data_frame=data,
            x='Timestamp',
            y='Value',
            color='Type',
            title=f'Sensor Data for {deployment.sensor.identifier}',
            labels={'Value': 'Measurement Value', 'Timestamp': 'Timestamp'}
        )

        # Convert Plotly graph to JSON for rendering in the template
        graph_json = pio.to_json(fig)

        # Pass data to the template
        context['graph_json'] = graph_json
        context['deployment'] = deployment
        context['sensorrecord_list'] = records

        # Additional context
        context['project'] = deployment.location.project
        context['user_id'] = self.request.user.id
        context['project_pk'] = deployment.location.project.pk
        context['deployment_pk'] = deployment.pk

        return context


class DeploymentDeleteView(DeleteView):
    model = Deployment

    def get_object(self):
        return get_object_or_404(Deployment, pk=self.kwargs['deployment_pk'])

    def get_success_url(self):
        return reverse('sensor:deployments', kwargs={
            'user_id': self.kwargs['user_id'],
            'project_pk': self.kwargs['project_pk']
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk

        return context


class DeploymentUpdateView(UpdateView):
    model = Deployment
    form_class = DeploymentForm
    template_name = 'core/project_update_form.html'

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs['sensor_pk'])

    def get_success_url(self):
        return reverse('sensor:projects', kwargs={'user_id': self.kwargs['user_id']})


# Sensor records
class SensorRecordListView(ListView):
    model = SensorRecord
    template_name = 'sensor/record_list.html'
    paginate_by = 100

    def get_queryset(self):
        deployment_id = self.kwargs.get('deployment_pk')
        deployment = get_object_or_404(Deployment, pk=deployment_id)
        return SensorRecord.objects.filter(deployment=deployment)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')
        deployment_pk = self.kwargs.get('deployment_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk
        context['deployment_pk'] = deployment_pk
        return context


class SensorRecordCreateView(FormView):
    template_name = 'sensor/record_form.html'
    form_class = SensorRecordForm

    def form_valid(self, form):
        # Get the cleaned CSV data as a DataFrame
        df = form.cleaned_data['csv_file']

        # Convert the 'timestamp' column to datetime with the correct format
        df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)

        # Resolve the deployment based on the first row's location and sensor
        deployment = get_object_or_404(
            Deployment,
            location__name=df.iloc[0]['location'],
            sensor__identifier=df.iloc[0]['sensor']
        )

        # Prepare SensorRecord instances
        records = [
            SensorRecord(
                deployment=deployment,
                timestamp=row['timestamp'],
                value=row['value'],
                unit=row['unit'],
                type=row['type']
            )
            for _, row in df.iterrows()
        ]

        # Bulk create SensorRecord instances
        SensorRecord.objects.bulk_create(records, ignore_conflicts=True)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('sensor:deployments', kwargs={'user_id': self.kwargs['user_id'],
                                                          'project_pk': self.kwargs['project_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk

        return context
# Update View


class SensorRecordUpdateView(UpdateView):
    model = SensorRecord
    form_class = SensorRecordForm
    template_name = 'sensor/sensorrecord_form.html'

    def get_success_url(self):
        return reverse_lazy('sensor:sensorrecord-list', kwargs={'deployment_pk': self.object.deployment.pk})

# Delete View


class SensorRecordDeleteView(DeleteView):
    model = SensorRecord
    template_name = 'sensor/sensorrecord_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('sensor:sensorrecord-list', kwargs={'deployment_pk': self.object.deployment.pk})


class SensorRecordDownloadView(View):
    def get(self, request, *args, **kwargs):
        # Get the deployment based on the provided deployment_pk
        deployment = get_object_or_404(Deployment, pk=kwargs['deployment_pk'])

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{deployment.sensor.identifier}_timeseries.csv"'

        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Value', 'Type', 'Unit'])

        # Fetch the sensor records for the deployment
        records = SensorRecord.objects.filter(
            deployment=deployment).order_by('timestamp')

        for record in records:
            writer.writerow([record.timestamp, record.value,
                            record.type, record.unit])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        project_pk = self.kwargs.get('project_pk')
        deployment_pk = self.kwargs.get('deployment_pk')

        # Optionally, you might want to fetch these objects to pass more details:
        context['project'] = get_object_or_404(Project, pk=project_pk)

        context['user_id'] = user_id
        context['project_pk'] = project_pk
        context['deployment_pk'] = deployment_pk
        return context


class SensorRecordGraphView(TemplateView):
    template_name = 'sensor/partial/record_list_graph.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deployment_id = self.kwargs.get('deployment_pk')
        deployment = get_object_or_404(Deployment, pk=deployment_id)

        # Fetch the sensor records for this deployment
        records = SensorRecord.objects.filter(
            deployment=deployment).order_by('timestamp')

        # Prepare data for the Plotly graph
        data = {
            'Timestamp': [record.timestamp for record in records],
            'Value': [record.value for record in records],
            'Type': [record.type for record in records],
            'Unit': [record.unit for record in records],
        }

        # Create a Plotly line chart (or any other type of chart)
        fig = px.line(
            data_frame=data,
            x='Timestamp',
            y='Value',
            color='Type',
            title=f'Sensor Data for {deployment.sensor.identifier}',
            labels={'Value': 'Measurement Value', 'Timestamp': 'Timestamp'}
        )

        # Convert Plotly graph to JSON for rendering in the template
        graph_json = pio.to_json(fig)

        context['graph_json'] = graph_json
        context['deployment'] = deployment
        return context
