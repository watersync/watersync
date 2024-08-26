from django.urls import path, include
from .views import (project_create_view, project_delete_view,
                    project_update_view, project_detail_view,
                    project_list_view)
from .views import (location_create_view, location_delete_view,
                    location_update_view, location_detail_view,
                    location_list_view)


app_name = "core"


urlpatterns = [
    # Project list view
    path('projects/', project_list_view, name='projects'),

    # Add a new project
    path('project/add/', project_create_view, name='add-project'),

    # Project-specific views (detail, update, delete)
    path('project/<int:project_pk>/', include([
        path('', project_detail_view, name='detail-project'),
        path('update/', project_update_view, name='update-project'),
        path('delete/', project_delete_view, name='delete-project'),

        # Location-related views nested under the project
        path('locations/', location_list_view, name='locations'),
        path('location/add/', location_create_view, name='add-location'),
        path('location/<int:location_pk>/', location_detail_view,
             name='detail-location'),
        path('location/<int:location_pk>/update/', location_update_view,
             name='update-location'),
        path('location/<int:location_pk>/delete/', location_delete_view,
             name='delete-location'),
    ])),
]
