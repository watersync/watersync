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

from django.urls import path, include
from watersync.waterquality.views import (
    SampleCreateView,
    SampleListView,
    SampleDeleteView,
    SampleUpdateView,
    SampleDetailView,
)
from watersync.waterquality.views import (
    ProtocolCreateView,
    ProtocolListView,
    ProtocolDeleteView,
    ProtocolUpdateView,
    ProtocolDetailView,
)

from watersync.waterquality.views import (
    SamplingEventCreateView,
    SamplingEventListView,
    SamplingEventDeleteView,
    SamplingEventUpdateView,
    SamplingEventDetailView,
)
from watersync.waterquality.views import (
    MeasurementCreateView,
    MeasurementListView,
    MeasurementDeleteView,
    MeasurementUpdateView,
)

app_name = "waterquality"

protocol_patterns = [
    path("<int:protocol_pk>/", ProtocolDetailView.as_view(), name="detail-protocol"),
    path("add/", ProtocolCreateView.as_view(), name="add-protocol"),
    path("<int:protocol_pk>/update/", ProtocolUpdateView.as_view(), name="update-protocol"),
    path("<int:protocol_pk>/delete/", ProtocolDeleteView.as_view(), name="delete-protocol"),
]

samplingevent_patterns = [
    path("<int:samplingevent_pk>/", SamplingEventDetailView.as_view(), name="detail-samplingevent"),
    path("add/", SamplingEventCreateView.as_view(), name="add-samplingevent"),
    path("<int:samplingevent_pk>/update/", SamplingEventUpdateView.as_view(), name="update-samplingevent"),
    path("<int:samplingevent_pk>/delete/", SamplingEventDeleteView.as_view(), name="delete-samplingevent"),
]

sample_patterns = [
    path("add/", SampleCreateView.as_view(), name="add-sample"),
    path("", SampleListView.as_view(), name="samples"),
    path("<int:sample_pk>/", SampleDetailView.as_view(), name="detail-sample"),
    path("<int:sample_pk>/update/", SampleUpdateView.as_view(), name="update-sample"),
    path("<int:sample_pk>/delete/", SampleDeleteView.as_view(), name="delete-sample"),
]

measurement_patterns = [
    path("add/", MeasurementCreateView.as_view(), name="add-measurement"),
    path("", MeasurementListView.as_view(), name="measurements"),
    path("<int:measurement_pk>/update/", MeasurementUpdateView.as_view(), name="update-measurement"),
    path("<int:measurement_pk>/delete/", MeasurementDeleteView.as_view(), name="delete-measurement"),
]

urlpatterns = [
    path("projects/<int:project_pk>/locations/<int:location_pk>/samplingevents/", include(samplingevent_patterns)),
    path("settings/protocols/", include(protocol_patterns)),
    path("project/<int:project_pk>/location/<int:location_pk>/samplingevents/<int:samplingevent_pk>/samples/", include(sample_patterns)),
    path("project/<int:project_pk>/location/<int:location_pk>/samplingevents/<int:samplingevent_pk>/samples/<int:sample_pk>/measurements/", include(measurement_patterns)),
]
