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

from django.urls import include, path

from watersync.sensor.views import (
    sensor_create_view,
    sensor_delete_view,
    sensor_update_view,
    sensor_detail_view,
    sensor_list_view,
    deployment_create_view,
    deployment_decommission_view,
    deployment_delete_view,
    deployment_detail_view,
    deployment_list_view,
    deployment_overview_view,
    deployment_update_view,
    sensorrecord_create_view,
    sensorrecord_delete_view,
    sensorrecord_update_view,
    sensorrecord_download_view,
    sensorrecord_list_view,
    sensor_variable_create_view,
    sensor_variable_delete_view,
    sensor_variable_update_view,
    sensor_variable_list_view,
    sensor_variable_detail_view,
)

app_name = "sensor"

sensor_urlpatterns = [
    path("", sensor_list_view, name="sensors"),
    path("add/", sensor_create_view, name="add-sensor"),
    path("<str:sensor_pk>/", sensor_detail_view, name="detail-sensor"),
    path("<str:sensor_pk>/update/", sensor_update_view, name="update-sensor"),
    path("<str:sensor_pk>/delete/", sensor_delete_view, name="delete-sensor"),
]

sensor_variable_urlpatterns = [
    path("", sensor_variable_list_view, name="sensorvariables"),
    path("add/", sensor_variable_create_view, name="add-sensorvariable"),
    path(
        "<str:sensorvariable_pk>/update/",
        sensor_variable_update_view,
        name="update-sensorvariable",
    ),
    path(
        "<str:sensorvariable_pk>/delete/",
        sensor_variable_delete_view,
        name="delete-sensorvariable",
    ),
    path(
        "<str:sensorvariable_pk>/",
        sensor_variable_detail_view,
        name="detail-sensorvariable",
    ),
]

deployment_urlpatterns = [
    path("", deployment_list_view, name="deployments"),
    path("add/", deployment_create_view, name="add-deployment"),
    path("<str:deployment_pk>/", deployment_detail_view, name="detail-deployment"),
    path("<str:deployment_pk>/overview", deployment_overview_view, name="overview-deployment"),
    path(
        "<str:deployment_pk>/update/", deployment_update_view, name="update-deployment"
    ),
    path(
        "<str:deployment_pk>/delete/", deployment_delete_view, name="delete-deployment"
    ),
    # Additional view to decommission the sensor from the deployment
    path(
        "<str:deployment_pk>/decommission/",
        deployment_decommission_view,
        name="decommission-deployment",
    ),
]

sensorrecord_urlpatterns = [
    path("", sensorrecord_list_view, name="sensorrecords"),
    path("add/", sensorrecord_create_view, name="add-sensorrecord"),
    # I am not sure the user should be able to update the sensor records. it's the whole
    # point of automatically recorded data. Also the delete method should probably be a
    # bulk delete method. Or maybe instead I should just let the user to delete the
    # deployment and all the records will be deleted (CASCADE). Then the default would
    # be to just reupload corrected data.
    path(
        "<int:sensorrecords_pk>/update/",
        sensorrecord_update_view,
        name="update-sensorrecord",
    ),
    path(
        "<int:sensorrecords_pk>/delete/",
        sensorrecord_delete_view,
        name="delete-sensorrecord",
    ),
    path(
        "<int:sensorrecords_pk>/download/",
        sensorrecord_download_view,
        name="download-sensorrecord",
    ),
]


urlpatterns = [
    path("sensors/", include(sensor_urlpatterns)),
    path(
        "projects/<str:project_pk>/deployments/",
        include(deployment_urlpatterns),
    ),
    path(
        "sensorvariables/",
        include(sensor_variable_urlpatterns)
    ),
    # This one should probably be just a downloadable or viewable as a graph only.
    # There is no sense in displaying the records as a list.
    path(
        "project/<str:project_pk>/deployments/<str:deployment_pk>/records/",
        include(sensorrecord_urlpatterns),
    ),
]
