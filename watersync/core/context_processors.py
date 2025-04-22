from watersync.core.models import Project, Location
import re

def current_project(request):
    """
    A context processor to add the current project to the context
    if 'project' is available in the URL kwargs.
    """

    project = request.resolver_match.kwargs.get('project_pk') if request.resolver_match else None

    if project:
        try:
            project = Project.objects.get(pk=project)
        except Project.DoesNotExist:
            project = None

    return {'project': project}

def current_location(request):
    """
    A context processor to add the current location to the context
    if 'location' is available in the URL kwargs.
    """

    location = request.resolver_match.kwargs.get('location_pk') if request.resolver_match else None

    if location:
        try:
            location = Location.objects.get(pk=location)
        except Location.DoesNotExist:
            location = None

    return {'location': location}

def base_template(request):
    """
    A context processor to add the base template to the context.
    This is useful for rendering the base template in HTMX requests.
    """
    
    if request.headers.get("HX-Context") == "block":
        return {"base_template": "layouts/blank.html"}
    if "projects" in request.path:
        return {"base_template": "layouts/project_dashboard.html"}

    return {"base_template": "layouts/base_dashboard.html"}

def model_documentation(request):
    """
    Context processor that provides model documentation for templates.
    
    This extracts the docstring from a model and splits it into explanation and explanation_detail.
    The model is determined from the current view's model attribute if available.
    
    This will be used once I move from using include tags to render the partial templates to
    actually making the htmx requests to the views once the user clicks on the
    tab or the button.
    """
    context = {}
    
    # Get the current view from the request
    view = request.resolver_match.func.view_class if hasattr(request.resolver_match, 'func') and hasattr(request.resolver_match.func, 'view_class') else None
    
    if view and hasattr(view, 'model') and view.model:
        model = view.model
        if model.__doc__:
            docstring_parts = re.split(r'\n\n|\r\n\r\n', model.__doc__)
            context['explanation'] = docstring_parts[0] if docstring_parts else None
            context['explanation_detail'] = docstring_parts[1] if len(docstring_parts) > 1 else None

    return context
