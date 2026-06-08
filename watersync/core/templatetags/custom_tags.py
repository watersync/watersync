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


@register.filter
def detail_fields(obj):
    """Get fields from a detail model instance for template display.
    
    Returns a list of (label, value) tuples for all non-pk fields on the model.
    Labels are derived from the field's verbose_name.
    
    Usage:
        {% for label, value in detail_obj|detail_fields %}
            <li>{{ label }}: {{ value }}</li>
        {% endfor %}
    """
    if obj is None:
        return []
    
    result = []
    for field in obj._meta.get_fields():
        # Skip the primary key field (which is the OneToOne to parent)
        if field.primary_key:
            continue
        # Skip reverse relations
        if not hasattr(field, 'attname'):
            continue
        
        field_name = field.name
        label = field.verbose_name.replace("_", " ").title()
        value = getattr(obj, field_name, None)
        
        # Format value for display
        if value is None:
            value = "-"
        
        result.append((label, value))
    
    return result


@register.filter
def query_to_json(query_dict):
    """Convert QueryDict to JSON string for hx-vals."""
    return json.dumps(dict(query_dict))