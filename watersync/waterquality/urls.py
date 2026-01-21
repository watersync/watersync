"""
Water Quality URL Configuration

URLs for water quality sample and measurement management.
"""

from django.urls import include, path

from watersync.waterquality.views import (
    measurement_create_view,
    measurement_delete_view,
    measurement_detail_view,
    measurement_list_view,
    measurement_update_view,
    protocol_create_view,
    protocol_delete_view,
    protocol_detail_view,
    protocol_list_view,
    protocol_update_view,
    sample_create_view,
    sample_delete_view,
    sample_detail_view,
    sample_list_view,
    sample_overview_view,
    sample_update_view,
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
