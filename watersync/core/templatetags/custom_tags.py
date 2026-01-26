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

@register.filter
def display_fields(obj, field_type="list"):
    """Get display fields for a model instance.
    
    Usage:
        {% for label, value in object|display_fields:"list" %}
        {% for label, value in object|display_fields:"detail" %}
    
    Reads from model's _list_view_fields or _detail_view_fields dict.
    """
    if field_type == "detail":
        fields = getattr(obj, '_detail_view_fields', None)
    else:
        fields = getattr(obj, '_list_view_fields', None)
    
    if not fields:
        return []
    # Returns a list of tuples with field names and their corresponding verbose names.
    return [
        (label, getattr(obj, field_name, None))
        for label, field_name in fields.items()
    ]