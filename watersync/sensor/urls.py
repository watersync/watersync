"""
Some basic assumption about sensors and sensor deployments:

     1. Sensors can be shared between users.
     2. Users can have access to specific sensors.
     3. Users that have access to a sensor not necessarily have access to the
          project in which the sensor is deployed.

The URLs below are therefore not linked to the project, but only to the user.

For now, the sensor deployments are only viewable from the level on a project
and location. They can be listed added, deleted and updated under the project
View for now.
"""

from django.urls import path

from watersync.sensor.views import (
    DeploymentCreateView,
    DeploymentDecommissionView,
    DeploymentDeleteView,
    DeploymentDetailView,
    DeploymentListView,
    DeploymentUpdateView,
    SensorCreateView,
    SensorDeleteView,
    SensorDetailView,
    SensorListView,
    SensorRecordCreateView,
    SensorRecordDeleteView,
    SensorRecordDownloadView,
    SensorRecordListView,
    SensorRecordUpdateView,
    SensorUpdateView,
)

app_name = "sensor"


urlpatterns = [
    # Sensor list view with user_id
    path("sensors/", SensorListView.as_view(), name="sensors"),
    # Add a new sensor for a specific user
    path("sensor/add/", SensorCreateView.as_view(), name="add-sensor"),
    # Sensor detail view with user_id
    path("sensor/<int:sensor_pk>/", SensorDetailView.as_view(), name="detail-sensor"),
    # Update sensor with user_id
    path(
        "sensor/<int:sensor_pk>/update/",
        SensorUpdateView.as_view(),
        name="update-sensor",
    ),
    # Delete sensor with user_id
    path(
        "sensor/<int:sensor_pk>/delete/",
        SensorDeleteView.as_view(),
        name="delete-sensor",
    ),
    # ============== Sensor deployments ====================
    # Deplying the sensor to a location linked to a project
    path(
        "project/<int:project_pk>/deployment/add/",
        DeploymentCreateView.as_view(),
        name="add-deployment",
    ),
    # Decommissioning of the sensor (releasing it back to the pool)
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/decommission/",
        DeploymentDecommissionView.as_view(),
        name="decommission-deployment",
    ),
    # List all sensor deployments linked to a project.
    path(
        "project/<int:project_pk>/deployments",
        DeploymentListView.as_view(),
        name="deployments",
    ),
    # Deployment detail view
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/",
        DeploymentDetailView.as_view(),
        name="detail-deployment",
    ),
    # Update deployment
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/update",
        DeploymentUpdateView.as_view(),
        name="update-deployment",
    ),
    # Delete deployment
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/delete",
        DeploymentDeleteView.as_view(),
        name="delete-deployment",
    ),
    # ============== Sensor record ====================
    # list records
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/records/",
        SensorRecordListView.as_view(),
        name="records",
    ),
    path(
        "project/<int:project_pk>/sensor/record/add/",
        SensorRecordCreateView.as_view(),
        name="add-record",
    ),
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/record/<int:pk>/update/",
        SensorRecordUpdateView.as_view(),
        name="update-record",
    ),
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/record/<int:pk>/delete/",
        SensorRecordDeleteView.as_view(),
        name="delete-record",
    ),
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/download-timeseries/",
        SensorRecordDownloadView.as_view(),
        name="download-timeseries",
    ),
]
