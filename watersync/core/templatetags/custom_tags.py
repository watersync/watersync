from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('shared/table.html')
def render_table(queryset, columns, url_name, url_params=None):
    """
    Renders a dynamic table.

    - queryset: Queryset of objects to display in the table.
    - columns: List of field names to display as columns.
    - url_name: The name of the URL for the detail view of each row item.
    - url_params: Additional parameters to include in the URL, if necessary.
    """
    return {
        'queryset': queryset,
        'columns': columns,
        'url_name': url_name,
        'url_params': url_params or [],
    }
    

@register.filter
def getattr(value, arg):
    """Gets an attribute of an object dynamically from a string name."""
    return getattr(value, arg, None)