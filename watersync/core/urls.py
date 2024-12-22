from django.urls import include, path

from watersync.core.views.location import (
    location_create_view,
    location_delete_view,
    location_detail_view,
    location_list_view,
    location_update_view,
)
from watersync.core.views.locationstatus import (
    location_status_create_view,
    location_status_delete_view,
    location_status_list_view,
    location_status_update_view,
)
from watersync.core.views.project import (
    project_create_view,
    project_delete_view,
    project_detail_view,
    project_list_view,
    project_update_view,
)

app_name = "core"

project_urlpatterns = [
    path("", project_list_view, name="projects"),
    path("add/", project_create_view, name="add-project"),
    path("<int:project_pk>/", project_detail_view, name="detail-project"),
    path("<int:project_pk>/update/", project_update_view, name="update-project"),
    path("<int:project_pk>/delete/", project_delete_view, name="delete-project"),
]

location_urlpatterns = [
    path("", location_list_view, name="locations"),
    path("add/", location_create_view, name="add-location"),
    path("<int:location_pk>/", location_detail_view, name="detail-location"),
    path("<int:location_pk>/update/", location_update_view, name="update-location"),
    path("<int:location_pk>/delete/", location_delete_view, name="delete-location"),
]

location_status_urlpatterns = [
    path("", location_status_list_view, name="locationstatus"),
    path("add/", location_status_create_view, name="add-locationstatus"),
    path(
        "<int:locationstatus_pk>/update/",
        location_status_update_view,
        name="update-locationstatus",
    ),
    path(
        "<int:locationstatus_pk>/delete/",
        location_status_delete_view,
        name="delete-locationstatus",
    ),
]

urlpatterns = [
    path("projects/", include(project_urlpatterns)),
    path(
        "projects/<int:project_pk>/locations/",
        include(location_urlpatterns),
    ),
    path(
        "projects/<int:project_pk>/locations/<int:location_pk>/statuses/",
        include(location_status_urlpatterns),
    ),
]
