from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404

from watersync.core.models import Project


def update_location_geom(form):
    lat = form.cleaned_data.get("latitude")
    lon = form.cleaned_data.get("longitude")
    alt = form.cleaned_data.get("altitude")

    if None not in (lat, lon, alt):
        form.instance.geom = Point(lon, lat, alt, srid=4326)

def add_current_project(kwargs, form):
    form.instance.project = get_object_or_404(Project, pk=kwargs.get("project_pk"))
