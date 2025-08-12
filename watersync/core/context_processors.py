from watersync.core.models import Project, Location, Fieldwork

def current_project(request):
    """
    Add the current project to the context if 'project' is available in the URL.
    """

    project = request.resolver_match.kwargs.get('project_pk') if request.resolver_match else None

    if project:
        try:
            project = Project.objects.get(pk=project)
        except Project.DoesNotExist:
            project = None

    return {'project': project}

def current_location(request):
    """Add the current location to the context if 'location' is available in the URL.
    """

    location = request.resolver_match.kwargs.get('location_pk') if request.resolver_match else None

    if location:
        try:
            location = Location.objects.get(pk=location)
        except Location.DoesNotExist:
            location = None

    return {'location': location}

def current_fieldwork(request):
    """Add the current fieldwork to the context if 'fieldwork' is available in the URL.
    """

    fieldwork = request.resolver_match.kwargs.get('fieldwork_pk') if request.resolver_match else None

    if fieldwork:
        try:
            fieldwork = Fieldwork.objects.get(pk=fieldwork)
        except Fieldwork.DoesNotExist:
            fieldwork = None

    return {'fieldwork': fieldwork}

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
