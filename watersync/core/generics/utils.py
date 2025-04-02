from django.contrib.gis.geos import Point


def update_location_geom(form):
    lat = form.cleaned_data.get("latitude")
    lon = form.cleaned_data.get("longitude")
    if lat and lon:
        form.instance.geom = Point(lon, lat, srid=4326)


def get_resource_list_context(request, kwargs, resource_dict):
    
    return {
        key: view(request=request, kwargs=kwargs).get_context_data(object_list=0)
        for key, view in resource_dict.items()
    }