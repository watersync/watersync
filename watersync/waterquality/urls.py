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

from watersync.waterquality.views.measurement import (
    measurement_bulk_create_view,
    measurement_create_view,
    measurement_delete_view,
    measurement_detail_view,
    measurement_list_view,
    measurement_update_view,
)
from watersync.waterquality.views.protocol import (
    protocol_create_view,
    protocol_delete_view,
    protocol_detail_view,
    protocol_list_view,
    protocol_update_view,
)
from watersync.waterquality.views.sample import (
    sample_create_view,
    sample_delete_view,
    sample_detail_view,
    sample_list_view,
    sample_update_view,
)
from watersync.waterquality.views.samplingevent import (
    samplingevent_create_view,
    samplingevent_delete_view,
    samplingevent_detail_view,
    samplingevent_list_view,
    samplingevent_update_view,
)

app_name = "waterquality"

protocol_patterns = [
    path("", protocol_list_view, name="protocols"),
    path("add/", protocol_create_view, name="add-protocol"),
    path("<int:protocol_pk>/", protocol_detail_view, name="detail-protocol"),
    path(
        "<int:protocol_pk>/update/",
        protocol_update_view,
        name="update-protocol",
    ),
    path(
        "<int:protocol_pk>/delete/",
        protocol_delete_view,
        name="delete-protocol",
    ),
]

samplingevent_patterns = [
    path("", samplingevent_list_view, name="samplingevents"),
    path("add/", samplingevent_create_view, name="add-samplingevent"),
    path(
        "<int:samplingevent_pk>/",
        samplingevent_detail_view,
        name="detail-samplingevent",
    ),
    path(
        "<int:samplingevent_pk>/update/",
        samplingevent_update_view,
        name="update-samplingevent",
    ),
    path(
        "<int:samplingevent_pk>/delete/",
        samplingevent_delete_view,
        name="delete-samplingevent",
    ),
]

sample_patterns = [
    path("", sample_list_view, name="samples"),
    path("add/", sample_create_view, name="add-sample"),
    path("<int:sample_pk>/", sample_detail_view, name="detail-sample"),
    path("<int:sample_pk>/update/", sample_update_view, name="update-sample"),
    path("<int:sample_pk>/delete/", sample_delete_view, name="delete-sample"),
]

measurement_patterns = [
    path("", measurement_list_view, name="measurements"),
    path("add/", measurement_create_view, name="add-measurement"),
    path("add_bulk/", measurement_bulk_create_view, name="add_bulk-measurement"),
    path(
        "<int:measurement_pk>/update/",
        measurement_update_view,
        name="update-measurement",
    ),
    path(
        "<int:measurement_pk>/",
        measurement_detail_view,
        name="detail-measurement",
    ),
    path(
        "<int:measurement_pk>/delete/",
        measurement_delete_view,
        name="delete-measurement",
    ),
]

urlpatterns = [
    path(
        "projects/<int:project_pk>/locations/<int:location_pk>/samplingevents/",
        include(samplingevent_patterns),
    ),
    path("settings/protocols/", include(protocol_patterns)),
    path(
        "projects/<int:project_pk>/locations/<int:location_pk>/samplingevents/<int:samplingevent_pk>/samples/",
        include(sample_patterns),
    ),
    path(
        "projects/<int:project_pk>/locations/<int:location_pk>/samplingevents/<int:samplingevent_pk>/samples/<int:sample_pk>/measurements/",
        include(measurement_patterns),
    ),
]
