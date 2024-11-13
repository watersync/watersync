from django.shortcuts import get_object_or_404
from watersync.core.models import Location
from watersync.core.models import Project

def get_project_location(request, kwargs):
    project = get_object_or_404(
        Project, pk=kwargs["project_pk"], user__id=request.user.id
    )
    location = get_object_or_404(Location, pk=kwargs["location_pk"], project=project)

    return project, location