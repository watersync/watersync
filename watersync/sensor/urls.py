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
    deployment_update_view,
    sensorrecord_create_view,
    sensorrecord_delete_view,
    sensorrecord_update_view,
    sensorrecord_download_view,
    sensorrecord_list_view,
)

app_name = "sensor"

sensor_urlpatterns = [
    path("", sensor_list_view, name="sensors"),
    path("add/", sensor_create_view, name="add-sensor"),
    path("<int:sensor_pk>/", sensor_detail_view, name="detail-sensor"),
    path("<int:sensor_pk>/update/", sensor_update_view, name="update-sensor"),
    path("<int:sensor_pk>/delete/", sensor_delete_view, name="delete-sensor"),
]

deployment_urlpatterns = [
    path("", deployment_list_view, name="deployments"),
    path("add/", deployment_create_view, name="add-deployment"),
    path("<int:deployment_pk>/", deployment_detail_view, name="detail-deployment"),
    path(
        "<int:deployment_pk>/update/", deployment_update_view, name="update-deployment"
    ),
    path(
        "<int:deployment_pk>/delete/", deployment_delete_view, name="delete-deployment"
    ),
    # Additional view to decommission the sensor from the deployment
    path(
        "<int:deployment_pk>/decommission/",
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
        "projects/<int:project_pk>/locations/<int:location_pk>/deployments/",
        include(deployment_urlpatterns),
    ),
    # This one should probably be just a downloadable or viewable as a graph only.
    # There is no sense in displaying the records as a list.
    path(
        "project/<int:project_pk>/deployment/<int:deployment_pk>/records/",
        include(sensorrecord_urlpatterns),
    ),
]
