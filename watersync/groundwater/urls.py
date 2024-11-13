from django.urls import include
from django.urls import path

from .views import gwl_create_view
from .views import gwl_delete_view
from .views import gwl_detail_view
from .views import gwl_list_view
from .views import gwl_update_view

app_name = "groundwater"

gwl_urlpatterns = [
    path("", gwl_list_view, name="gwlmeasurements"),
    path("add/", gwl_create_view, name="add-gwlmeasurement"),
    path("<int:gwlmeasurement_pk>/", gwl_detail_view, name="detail-gwlmeasurement"),
    path(
        "<int:gwlmeasurement_pk>/update/", gwl_update_view, name="update-gwlmeasurement"
    ),
    path(
        "<int:gwlmeasurement_pk>/delete/", gwl_delete_view, name="delete-gwlmeasurement"
    ),
]

urlpatterns = [
    path(
        "projects/<int:project_pk>/locations/<int:location_pk>/gwlmeasurements",
        include(gwl_urlpatterns),
    ),
]
