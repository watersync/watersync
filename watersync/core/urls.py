from django.urls import include, path

from watersync.core.views.location import (
    location_create_view,
    location_delete_view,
    location_detail_view,
    location_list_view,
    location_update_view,
)
from watersync.core.views.locationvisit import (
    location_visit_create_view,
    location_visit_delete_view,
    location_visit_list_view,
    location_visit_update_view,
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

location_visit_urlpatterns = [
    path("", location_visit_list_view, name="locationvisit"),
    path("add/", location_visit_create_view, name="add-locationvisit"),
    path(
        "<int:locationvisit_pk>/update/",
        location_visit_update_view,
        name="update-locationvisit",
    ),
    path(
        "<int:locationstatus_pk>/delete/",
        location_visit_delete_view,
        name="delete-locationvisit",
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
        include(location_visit_urlpatterns),
    ),
]
