from django.contrib.gis.geos import Point


def update_location_geom(form):
    lat = form.cleaned_data.get("latitude")
    lon = form.cleaned_data.get("longitude")
    if lat and lon:
        form.instance.geom = Point(lon, lat, srid=4326)