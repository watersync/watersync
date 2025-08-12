from django.urls import include, path

from watersync.core.views import fieldwork_create_view, fieldwork_update_view, fieldwork_delete_view, fieldwork_detail_view, fieldwork_list_view, fieldwork_overview_view, location_create_view, location_delete_view, location_detail_view, location_overview_view, location_update_view, project_create_view, project_delete_view, project_detail_view, project_update_view
from watersync.core.views import (
    location_list_view,
)
from watersync.core.views import (
    project_list_view,
)
from watersync.core.views import (
    unit_create_view,
    unit_delete_view,
    unit_detail_view,
    unit_update_view,
    unit_list_view
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
    path("<str:fieldwork_pk>/overview/", fieldwork_overview_view, name="overview-fieldwork"),
]

location_urlpatterns = [
    path("", location_list_view, name="locations"),
    path("add/", location_create_view, name="add-location"),
    path("<str:location_pk>/", location_detail_view, name="detail-location"),
    path("<str:location_pk>/overview/", location_overview_view, name="overview-location"),
    path("<str:location_pk>/update/", location_update_view, name="update-location"),
    path("<str:location_pk>/delete/", location_delete_view, name="delete-location"),
]


unit_urlpatterns = [
    path("", unit_list_view, name="units"),
    path("add/", unit_create_view, name="add-unit"),
    path("<str:unit_pk>/", unit_detail_view, name="detail-unit"),
    path("<str:unit_pk>/update/", unit_update_view, name="update-unit"),
    path("<str:unit_pk>/delete/", unit_delete_view, name="delete-unit"),
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
    path("units/", include(unit_urlpatterns)),
]
