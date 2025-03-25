from django.urls import include, path

from watersync.core.views import fieldwork_create_view, fieldwork_update_view, fieldwork_delete_view, fieldwork_detail_view, fieldwork_list_view, location_create_view, location_delete_view, location_detail_view, location_overview_view, location_update_view, location_visit_create_view, location_visit_delete_view, location_visit_list_view, project_create_view, project_delete_view, project_detail_view, project_update_view
from watersync.core.views import (
    location_list_view,
)
from watersync.core.views import (
    location_visit_update_view,
)
from watersync.core.views import (
    project_list_view,
)


app_name = "core"

project_urlpatterns = [
    path("", project_list_view, name="projects"),
    path("add/", project_create_view, name="add-project"),
    path("<str:project_pk>/", project_detail_view, name="detail-project"),
    path("<str:project_pk>/update/", project_update_view, name="update-project"),
    path("<str:project_pk>/delete/", project_delete_view, name="delete-project"),
]

fieldwork_urlpatterns = [
    path("", fieldwork_list_view, name="fieldworks"),
    path("add/", fieldwork_create_view, name="add-fieldwork"),
    path("<str:fieldwork_pk>/", fieldwork_detail_view, name="detail-fieldwork"),
    path("<str:fieldwork_pk>/update/", fieldwork_update_view, name="update-fieldwork"),
    path("<str:fieldwork_pk>/delete/", fieldwork_delete_view, name="delete-fieldwork"),
]

location_urlpatterns = [
    path("", location_list_view, name="locations"),
    path("add/", location_create_view, name="add-location"),
    path("<str:location_pk>/", location_detail_view, name="detail-location"),
    path("<str:location_pk>/overview/", location_overview_view, name="overview-location"),
    path("<str:location_pk>/update/", location_update_view, name="update-location"),
    path("<str:location_pk>/delete/", location_delete_view, name="delete-location"),
]

location_visit_urlpatterns = [
    path("", location_visit_list_view, name="locationvisits"),
    path("add/", location_visit_create_view, name="add-locationvisit"),
    path(
        "<str:locationvisit_pk>/update/",
        location_visit_update_view,
        name="update-locationvisit",
    ),
    path(
        "<str:locationvisit_pk>/delete/",
        location_visit_delete_view,
        name="delete-locationvisit",
    ),
]

urlpatterns = [
    path("projects/", include(project_urlpatterns)),
    path(
        "projects/<str:project_pk>/fieldworks/",
        include(fieldwork_urlpatterns),
    ),
    path(
        "projects/<str:project_pk>/locations/",
        include(location_urlpatterns),
    ),
    path(
        "projects/<str:project_pk>/locationvisits/",
        include(location_visit_urlpatterns),
    ),
]
