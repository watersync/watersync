"""
Some basic assumption about sensors and sensor Samples:

     1. Sensors can be shared between users.
     2. Users can have access to specific sensors.
     3. Users that have access to a sensor not necessarily have access to the
          project in which the sensor is deployed.

The URLs below are therefore not linked to the project, but only to the user.

For now, the sensor Samples are only viewable from the level on a project
and location. They can be listed added, deleted and updated under the project
View for now.
"""

from django.urls import include, path

from watersync.waterquality.views import protocol_create_view, protocol_delete_view, protocol_list_view, protocol_update_view, sample_create_view, sample_delete_view, sample_list_view, sample_update_view
from watersync.waterquality.views import (
    # measurement_bulk_create_view,
    measurement_create_view,
    measurement_delete_view,
    measurement_detail_view,
    measurement_list_view,
    measurement_update_view,
)
from watersync.waterquality.views import (
protocol_create_view,
protocol_update_view,
protocol_delete_view,
protocol_list_view,
protocol_detail_view
)
from watersync.waterquality.views import (
sample_create_view,
sample_update_view,
sample_delete_view,
sample_list_view,
sample_detail_view,
sample_overview_view
)


app_name = "waterquality"

protocol_patterns = [
    path("", protocol_list_view, name="protocols"),
    path("add/", protocol_create_view, name="add-protocol"),
    path("<str:protocol_pk>/", protocol_detail_view, name="detail-protocol"),
    path(
        "<str:protocol_pk>/update/",
        protocol_update_view,
        name="update-protocol",
    ),
    path(
        "<str:protocol_pk>/delete/",
        protocol_delete_view,
        name="delete-protocol",
    ),
]

sample_patterns = [
    path("", sample_list_view, name="samples"),
    path("add/", sample_create_view, name="add-sample"),
    path("<str:sample_pk>/", sample_detail_view, name="detail-sample"),
    path("<str:sample_pk>/overview/", sample_overview_view, name="overview-sample"),
    path("<str:sample_pk>/update/", sample_update_view, name="update-sample"),
    path("<str:sample_pk>/delete/", sample_delete_view, name="delete-sample"),
]

measurement_patterns = [
    path("", measurement_list_view, name="measurements"),
    path("add/", measurement_create_view, name="add-measurement"),
    # path("add_bulk/", measurement_bulk_create_view, name="add_bulk-measurement"),
    path(
        "<str:measurement_pk>/update/",
        measurement_update_view,
        name="update-measurement",
    ),
    path(
        "<str:measurement_pk>/",
        measurement_detail_view,
        name="detail-measurement",
    ),
    path(
        "<str:measurement_pk>/delete/",
        measurement_delete_view,
        name="delete-measurement",
    ),
]

urlpatterns = [
    path("settings/protocols/", include(protocol_patterns)),
    path(
        "projects/<str:project_pk>/samples/",
        include(sample_patterns),
    ),
    path(
        "projects/<str:project_pk>/measurements/",
        include(measurement_patterns),
    ),
]
