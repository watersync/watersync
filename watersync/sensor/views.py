import csv
import json
from decimal import Decimal

import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
    TemplateView
)
from watersync.core.generics.views import WatersyncListView
from watersync.core.models import Location, Project
from watersync.sensor.models import Deployment, Sensor, SensorRecord, SensorVariable
from watersync.core.generics.views import WatersyncListView, WatersyncCreateView, WatersyncDetailView, WatersyncUpdateView, WatersyncDeleteView
from watersync.core.generics.decorators import filter_by_location
from .forms import DeploymentForm, SensorForm, SensorRecordForm, SensorVariableForm
from .plotting import create_sensor_graph

class SensorVariableCreateView(WatersyncCreateView):
    model = SensorVariable
    form_class = SensorForm


class SensorVariableUpdateView(WatersyncUpdateView):
    model = SensorVariable
    form_class = SensorVariableForm


class SensorVariableListView(WatersyncListView):
    model = SensorVariable
    detail_type = "modal"


class SensorVariableDeleteView(WatersyncDeleteView):
    model = SensorVariable

class SensorVariableDetailView(WatersyncDetailView):
    model = SensorVariable
    detail_type = "popover"

sensor_variable_create_view = SensorVariableCreateView.as_view()
sensor_variable_update_view = SensorVariableUpdateView.as_view()
sensor_variable_list_view = SensorVariableListView.as_view()
sensor_variable_delete_view = SensorVariableDeleteView.as_view()
sensor_variable_detail_view = SensorVariableDetailView.as_view()
# ================ Sensor views ========================


class SensorCreateView(WatersyncCreateView):
    model = Sensor
    form_class = SensorForm


class SensorUpdateView(WatersyncUpdateView):
    model = Sensor
    form_class = SensorForm


class SensorListView(WatersyncListView):
    model = Sensor
    detail_type = "modal"

    def get_queryset(self):
        return self.request.user.sensors.all()


class SensorDetailView(WatersyncDetailView):
    model = Sensor
    detail_type = "modal"


class SensorDeleteView(WatersyncDeleteView):
    model = Sensor


sensor_create_view = SensorCreateView.as_view()
sensor_delete_view = SensorDeleteView.as_view()
sensor_update_view = SensorUpdateView.as_view()
sensor_detail_view = SensorDetailView.as_view()
sensor_list_view = SensorListView.as_view()

# ================ Sensor Records views ========================
# Placing the sensor records above deployments because they will be reused there


class SensorRecordListView(LoginRequiredMixin, ListView):
    model = SensorRecord
    template_name = "sensor/partial/record_list.html"
    paginate_by = 100

    def get_queryset(self):
        deployment_pk = self.kwargs.get("deployment_pk")
        deployment = get_object_or_404(Deployment, pk=deployment_pk)
        queryset = deployment.records.all()

        # Filter by type
        sensor_type = self.request.GET.get("type")
        if sensor_type:
            queryset = queryset.filter(type=sensor_type)

        # Filter by date range
        date_start = self.request.GET.get("date_start")
        date_end = self.request.GET.get("date_end")
        if date_start:
            try:
                date_start = timezone.datetime.strptime(date_start, "%Y-%m-%d")
                queryset = queryset.filter(timestamp__gte=date_start)
            except ValueError:
                pass  # Handle invalid date format or raise a validation error

        if date_end:
            try:
                date_end = timezone.datetime.strptime(date_end, "%Y-%m-%d")
                date_end = timezone.make_aware(
                    timezone.datetime.combine(date_end, timezone.datetime.max.time())
                )
                queryset = queryset.filter(timestamp__lte=date_end)
            except ValueError:
                pass  # Handle invalid date format or raise a validation error

        return queryset.order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deployment = get_object_or_404(Deployment, pk=self.kwargs["deployment_pk"])
        records = self.get_queryset()
        sensor_types = deployment.records.all()
        data = [
            {
                "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "value": float(record.value)
                if isinstance(record.value, Decimal)
                else record.value,
                "type": record.type,
                "unit": record.unit,
            }
            for record in records
        ]

        # Create graph using the extracted function
        graph_json = create_sensor_graph(data, deployment)

        # Add data to context
        # context["sensor_types"] = sensor_types.values_list("type", flat=True)
        context["graph_json"] = graph_json
        context["sensor_record_list"] = json.dumps(data)  # JSON format for JavaScript
        context["deployment"] = deployment
        return context


class SensorRecordCreateView(LoginRequiredMixin, FormView):
    template_name = "sensor/record_form.html"
    form_class = SensorRecordForm

    def form_valid(self, form):
        # Get the cleaned CSV data as a DataFrame
        df = form.cleaned_data["csv_file"]

        # Convert the 'timestamp' column to datetime with the correct format
        df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True)

        # Resolve the deployment based on the first row's location and sensor
        deployment = get_object_or_404(
            Deployment,
            location__name=df.iloc[0]["location"],
            sensor__identifier=df.iloc[0]["sensor"],
        )

        # Prepare SensorRecord instances
        records = [
            SensorRecord(
                deployment=deployment,
                timestamp=row["timestamp"],
                value=row["value"],
                unit=row["unit"],
                type=row["type"],
            )
            for _, row in df.iterrows()
        ]

        # Bulk create SensorRecord instances
        SensorRecord.objects.bulk_create(records, ignore_conflicts=True)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "sensor:deployments",
            kwargs={
                "user_id": self.kwargs["user_id"],
                "project_pk": self.kwargs["project_pk"],
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        project_pk = self.kwargs.get("project_pk")

        # Optionally, you might want to fetch these objects to pass more details:
        context["project"] = get_object_or_404(Project, pk=project_pk)

        context["user_id"] = user_id
        context["project_pk"] = project_pk

        return context


class SensorRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = SensorRecord
    form_class = SensorRecordForm
    template_name = "sensor/sensorrecord_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "sensor:sensorrecord-list",
            kwargs={"deployment_pk": self.object.deployment.pk},
        )


class SensorRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = SensorRecord
    template_name = "sensor/sensorrecord_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "sensor:sensorrecord-list",
            kwargs={"deployment_pk": self.object.deployment.pk},
        )


class SensorRecordDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Get the deployment based on the provided deployment_pk
        deployment = get_object_or_404(Deployment, pk=kwargs["deployment_pk"])

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{deployment.sensor.identifier}_timeseries.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(["timestamp", "value", "type", "unit"])

        # Fetch the sensor records for the deployment
        records = SensorRecord.objects.filter(deployment=deployment).order_by(
            "timestamp"
        )

        for record in records:
            writer.writerow([record.timestamp, record.value, record.type, record.unit])

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get("project_pk")
        deployment_pk = self.kwargs.get("deployment_pk")

        # Optionally, you might want to fetch these objects to pass more details:
        context["project"] = get_object_or_404(Project, pk=project_pk)
        context["deployment"] = get_object_or_404(Deployment, pk=deployment_pk)
        return context


sensorrecord_create_view = SensorRecordCreateView.as_view()
sensorrecord_delete_view = SensorRecordDeleteView.as_view()
sensorrecord_update_view = SensorRecordUpdateView.as_view()
sensorrecord_download_view = SensorRecordDownloadView.as_view()
sensorrecord_list_view = SensorRecordListView.as_view()
# ================ Deployment views ========================


class DeploymentCreateView(WatersyncCreateView):
    model = Deployment
    form_class = DeploymentForm

class DeploymentUpdateView(WatersyncUpdateView):
    model = Deployment
    form_class = DeploymentForm

class DeploymentListView(WatersyncListView):
    model = Deployment
    detail_type = "page"

    @filter_by_location
    def get_queryset(self, **kwargs):
        project = self.get_project()
        locations = project.locations.all()
        return Deployment.objects.filter(
            location__in=locations
        ).order_by("-deployed_at")


class DeploymentDetailView(WatersyncDetailView):
    model = Deployment


class DeploymentDeleteView(WatersyncDeleteView):
    model = Deployment


class DeploymentOverviewView(TemplateView):
    template_name = "sensor/deployment_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deployment = get_object_or_404(Deployment, pk=self.kwargs["deployment_pk"])

        # Include additional context from SensorRecordListView
        record_view = SensorRecordListView.as_view()(
            self.request, deployment_pk=deployment.pk
        ).context_data
        context.update(record_view)

        # Additional context
        context["deployment"] = deployment
        context["project"] = deployment.location.project

        return context

deployment_create_view = DeploymentCreateView.as_view()
deployment_delete_view = DeploymentDeleteView.as_view()
deployment_detail_view = DeploymentDetailView.as_view()
deployment_list_view = DeploymentListView.as_view()
deployment_update_view = DeploymentUpdateView.as_view()
deployment_overview_view = DeploymentOverviewView.as_view()

# ================ Additionaly functional views ========================


class DeploymentDecommissionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        deployment = get_object_or_404(Deployment, pk=kwargs["deployment_pk"])
        deployment.decommission()
        return redirect(request.META.get("HTTP_REFERER", "sensor:deployments"))


deployment_decommission_view = DeploymentDecommissionView.as_view()
