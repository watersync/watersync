import json

from django import template
from django.db.models.query import QuerySet

register = template.Library()


@register.inclusion_tag("shared/table.html")
def render_table(queryset, columns, url_name, url_params=None):
    """
    Renders a dynamic table.

    - queryset: Queryset of objects to display in the table.
    - columns: List of field names to display as columns.
    - url_name: The name of the URL for the detail view of each row item.
    - url_params: Additional parameters to include in the URL, if necessary.
    """
    return {
        "queryset": queryset,
        "columns": columns,
        "url_name": url_name,
        "url_params": url_params or [],
    }


@register.filter
def getattr(value, arg):
    """Gets an attribute of an object dynamically from a string name."""
    return getattr(value, arg, None)


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
def replace_placeholder(url, pk):
    """Replaces a placeholder in the URL with the actual primary key."""
    return url.replace("__placeholder__", str(pk))
