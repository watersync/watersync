import json

from django import template
from django.db.models.query import QuerySet

register = template.Library()


@register.filter(is_safe=True)
def get_coordinates(obj):
    if isinstance(obj, QuerySet):
        coordinates = [
            {"name": obj.name, "lat": obj.geom.y, "lng": obj.geom.x} for obj in obj
        ]
    else:
        coordinates = [{"name": obj.name, "lat": obj.geom.y, "lng": obj.geom.x}]
    return json.dumps(coordinates)


@register.filter
def field_title(value):
    return value.replace("_"," ").capitalize()