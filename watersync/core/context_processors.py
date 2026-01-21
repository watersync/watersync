from watersync.core.models import Project, Location, Fieldwork


def url_context(request):
    """
    Unified context processor that extracts objects from URL kwargs and sets
    template context for HTMX-aware rendering.
    
    Location: watersync/core/context_processors.py
    Registered in: config/settings/base.py → TEMPLATES → OPTIONS → context_processors
    
    Provides:
        - project: The current Project object (if project_pk in URL)
        - location: The current Location object (if location_pk in URL)
        - fieldwork: The current Fieldwork object (if fieldwork_pk in URL)
        - base_template: The appropriate base template for the request
        - base_url_kwargs: Dict with project_pk for URL building
        - htmx_context: The HX-Context header value for conditional rendering
        - is_htmx: Boolean indicating if this is an HTMX request
    
    base_template Selection Logic:
        ┌─────────────────────────────────────────────────────────────────┐
        │ Request Type          │ base_template                          │
        ├─────────────────────────────────────────────────────────────────┤
        │ HTMX request          │ 'layouts/partial.html'                 │
        │ Full page + project   │ 'layouts/project_dashboard.html'       │
        │ Full page (no proj)   │ 'layouts/base_dashboard.html'          │
        │ No resolver match     │ 'layouts/base_dashboard.html'          │
        └─────────────────────────────────────────────────────────────────┘
    
    HTMX Template Pattern:
        Templates use {% extends base_template %} to automatically get the
        correct wrapper. For HTMX requests, 'layouts/partial.html' outputs
        just the content block with no HTML structure.
        
        View template selection is simple:
            {% if is_htmx %}
                {% include "table.html" %}    {# Just table rows #}
            {% else %}
                {% include "list.html" %}     {# Full list component #}
            {% endif %}
        
        htmx_context is used for UI decisions within templates:
            - htmx_context="block" → list is embedded in another page
              (hide title, show "See all" link)
            - htmx_context=None → standalone list page
    """
    context = {
        'project': None,
        'location': None,
        'fieldwork': None,
        'base_url_kwargs': {},
        'htmx_context': None,
        'htmx_rows_only': False,
        'is_htmx': False,
    }
    
    # Check if HTMX request (django-htmx middleware sets this)
    is_htmx = getattr(request, 'htmx', False)
    context['is_htmx'] = bool(is_htmx)
    
    # Check if this is a rows-only request (tbody refresh)
    context['htmx_rows_only'] = bool(request.headers.get("HX-Rows-Only"))
    
    # Get HX-Context header, filtering out "None" string that can come from template
    hx_context = request.headers.get("HX-Context")
    if hx_context and hx_context.lower() != "none":
        context['htmx_context'] = hx_context
    else:
        context['htmx_context'] = None
    
    if not request.resolver_match:
        context['base_template'] = 'layouts/base_dashboard.html'
        return context
    
    kwargs = request.resolver_match.kwargs
    
    # Extract project
    if project_pk := kwargs.get('project_pk'):
        try:
            context['project'] = Project.objects.get(pk=project_pk)
            context['base_url_kwargs']['project_pk'] = project_pk
        except Project.DoesNotExist:
            pass
    
    # Extract location
    if location_pk := kwargs.get('location_pk'):
        try:
            context['location'] = Location.objects.get(pk=location_pk)
        except Location.DoesNotExist:
            pass
    
    # Extract fieldwork
    if fieldwork_pk := kwargs.get('fieldwork_pk'):
        try:
            context['fieldwork'] = Fieldwork.objects.get(pk=fieldwork_pk)
        except Fieldwork.DoesNotExist:
            pass
    
    # Determine base template
    # HTMX requests get partial template (no base HTML structure)
    if is_htmx:
        context['base_template'] = 'layouts/partial.html'
    elif context['project']:
        context['base_template'] = 'layouts/project_dashboard.html'
    else:
        context['base_template'] = 'layouts/base_dashboard.html'
    
    return context
