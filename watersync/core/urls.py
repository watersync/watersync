from django.urls import path
from .views import (ProjectCreateView, ProjectListView,
                    ProjectDeleteView, ProjectUpdateView, ProjectDetailView)
from .views import (LocationCreateView, LocationListView,
                    LocationDeleteView, LocationUpdateView, LocationDetailView)

app_name = "core"


urlpatterns = [
    # Project list view with user_id
    path('projects/',
         ProjectListView.as_view(), name='projects'),

    # Add a new project for a specific user
    path('project/add/',
         ProjectCreateView.as_view(), name='add-project'),

    # Project detail view with user_id
    path('project/<int:project_pk>/',
         ProjectDetailView.as_view(), name='detail-project'),

    # Update project with user_id
    path('project/update/<int:project_pk>/',
         ProjectUpdateView.as_view(), name='update-project'),

    # Delete project with user_id
    path('project/delete/<int:project_pk>/',
         ProjectDeleteView.as_view(), name='delete-project'),

    # Location views
    path('project/<int:project_pk>/locations/',
         LocationListView.as_view(), name='locations'),
    path('project/<int:project_pk>/location/add/',
         LocationCreateView.as_view(), name='add-location'),
    path('project/<int:project_pk>/location/<int:location_pk>/',
         LocationDetailView.as_view(), name='detail-location'),
    path('project/<int:project_pk>/location/update/<int:location_pk>/',
         LocationUpdateView.as_view(), name='update-location'),
    path('project/<int:project_pk>/location/delete/<int:location_pk>/',
         LocationDeleteView.as_view(), name='delete-location'),
]
