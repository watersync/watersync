from django.urls import include, path

from watersync.groundwater.views import gwl_create_view, gwl_list_view, gwl_update_view
from watersync.groundwater.views import (
    gwl_delete_view,
)

app_name = "groundwater"

gwl_urlpatterns = [
    path("", gwl_list_view, name="gwlmanualmeasurements"),
    path("add/", gwl_create_view, name="add-gwlmanualmeasurement"),
    path(
        "<str:gwlmanualmeasurement_pk>/update/", gwl_update_view, name="update-gwlmanualmeasurement"
    ),
    path(
        "<str:gwlmanualmeasurement_pk>/delete/", gwl_delete_view, name="delete-gwlmanualmeasurement"
    ),
]

urlpatterns = [
    path(
        "projects/<str:project_pk>/gwlmanualmeasurements/",
        include(gwl_urlpatterns),
    ),
]
