import csv
import json
from decimal import Decimal

import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)
from watersync.core.views.base import WatersyncListView
from watersync.core.mixins import (
    HTMXFormMixin,
    RenderToResponseMixin,
    ListContext,
)
from watersync.core.models import Location, Project
from watersync.sensor.models import Deployment, Sensor, SensorRecord

from .forms import DeploymentForm, SensorForm, SensorRecordForm
from .plotting import create_sensor_graph


class SensorCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Sensor
    form_class = SensorForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "sensorChanged"
    htmx_render_template = "shared/simple_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user not in form.instance.user.all():
            form.instance.user.add(self.request.user)
        return response


class SensorListView(WatersyncListView):
    model = Sensor
    template_name = "list.html"
    htmx_template = "sensor/partial/sensor_table.html"

    def get_queryset(self):
        return self.request.user.sensors.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        list_context = ListContext(
            columns=["Identifier", "Available", "Action"],
            add_url=reverse(
                "sensor:add-sensor", kwargs={"user_id": self.request.user.id}
            ),
            list_url=reverse(
                "sensor:sensors", kwargs={"user_id": self.request.user.id}
            ),
            action="sensorChanged",
        )

        context["list_context"] = list_context

        return context


class SensorDetailView(LoginRequiredMixin, RenderToResponseMixin, DetailView):
    model = Sensor
    template_name = "sensor/sensor_detail.html"
    htmx_template = "sensor/sensor_detail.html"

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs["sensor_pk"])


class SensorUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Sensor
    form_class = SensorForm
    template_name = "sensor/sensor_form.html"

    htmx_trigger_header = "sensorChanged"
    htmx_render_template = "sensor/sensor_form.html"

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs["sensor_pk"])


class SensorDeleteView(LoginRequiredMixin, RenderToResponseMixin, DeleteView):
    model = Sensor
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(Sensor, pk=self.kwargs["sensor_pk"])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("HX-Request"):
            sensors_url = reverse(
                "sensor:sensors", kwargs={"user_id": self.kwargs["user_id"]}
            )
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "configRequest",
                    "HX-Redirect": sensors_url,
                },
            )
        return super().delete(request, *args, **kwargs)


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
        sensor_types = deployment.records.all().order_by("type").distinct("type")
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
        context["sensor_types"] = sensor_types.values_list("type", flat=True)
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


class DeploymentCreateView(LoginRequiredMixin, CreateView):
    model = Deployment
    form_class = DeploymentForm
    template_name = "sensor/deployment_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        deployment = form.save(commit=False)

        # This creates the deployment and
        # sets the sensor availability to False
        deployment.deploy()
        return response

    def get_success_url(self):
        return reverse_lazy(
            "sensor:deployments",
            kwargs={
                "project_pk": self.kwargs["project_pk"],
                "user_id": self.request.user.id,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["project"] = project
        return context


class DeploymentListView(WatersyncListView):
    model = Deployment
    template_name = "list.html"
    htmx_template = "sensor/partial/deployment_table.html"

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs.get("project_pk"))
        location_url = self.kwargs.get("location_pk", None)

        # if location_pk is present it means the request is made from the
        # location view and I want to get deployments from only one station
        # otherwise get all deployments from the project
        if not location_url:
            locations = get_list_or_404(Location, project=project)
            deployments = Deployment.objects.filter(location__in=locations)

        else:
            location = get_object_or_404(Location, pk=location_url)
            deployments = Deployment.objects.filter(location=location)

        return deployments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = get_object_or_404(Project, pk=self.kwargs.get("project_pk"))
        context["project"] = project

        list_context = ListContext(
            add_url=reverse(
                "sensor:add-deployment",
                kwargs={
                    "user_id": self.request.user.id,
                    "project_pk": project.pk,
                    "location_pk": self.kwargs.get("location_pk"),
                },
            ),
        )

        return context


class DeploymentDetailView(LoginRequiredMixin, DetailView):
    model = Deployment
    template_name = "sensor/deployment_detail.html"

    def get_object(self):
        return get_object_or_404(Deployment, pk=self.kwargs["deployment_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deployment = self.get_object()

        # Include additional context from SensorRecordListView
        record_view = SensorRecordListView.as_view()(
            self.request, deployment_pk=deployment.pk
        ).context_data
        context.update(record_view)

        # Additional context
        context["deployment"] = deployment
        context["project"] = deployment.location.project

        return context


class DeploymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Deployment
    form_class = DeploymentForm
    template_name = "sensor/deployment_form.html"

    def get_object(self):
        return get_object_or_404(Deployment, pk=self.kwargs["deployment_pk"])

    def get_success_url(self):
        return reverse(
            "sensor:detail-deployment",
            kwargs={
                "user_id": self.request.user.id,
                "project_pk": self.kwargs["project_pk"],
                "deployment_pk": [self.kwargs["deployment_pk"]],
            },
        )


class DeploymentDeleteView(LoginRequiredMixin, DeleteView):
    model = Deployment

    def get_object(self):
        return get_object_or_404(Deployment, pk=self.kwargs["deployment_pk"])

    def get_success_url(self):
        return reverse(
            "sensor:deployments",
            kwargs={
                "user_id": self.kwargs["user_id"],
                "project_pk": self.kwargs["project_pk"],
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs.get("project_pk")

        context["project"] = get_object_or_404(Project, pk=project_pk)

        return context


deployment_create_view = DeploymentCreateView.as_view()
deployment_delete_view = DeploymentDeleteView.as_view()
deployment_detail_view = DeploymentDetailView.as_view()
deployment_list_view = DeploymentListView.as_view()
deployment_update_view = DeploymentUpdateView.as_view()

# ================ Additionaly functional views ========================


class DeploymentDecommissionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        deployment = get_object_or_404(Deployment, pk=kwargs["deployment_pk"])
        deployment.decommission()
        return redirect(request.META.get("HTTP_REFERER", "sensor:deployments"))


deployment_decommission_view = DeploymentDecommissionView.as_view()
