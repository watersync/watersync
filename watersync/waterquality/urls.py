"""
Some basic assumption about sensors and sensor Samples:

     1. Sensors can be shared between users.
     2. Users can have access to specific sensors.
     3. Users that have access to a sensor not necessarily have access to the
          project in which the sensor is deployed.

The URLs below are therefore not linked to the project, but only to the user. 

For now, the sensor Samples are only viewable from the level on a project 
and location. They can be listed added, deleted and updated under the project
View for now.
"""

from django.urls import path
from watersync.waterquality.views import (SampleCreateView, SampleListView,
                                          SampleDeleteView, SampleUpdateView,
                                          SampleDetailView)
from watersync.waterquality.views import (MeasurementCreateView, MeasurementListView,
                                          MeasurementDeleteView, MeasurementUpdateView,
                                          MeasurementDetailView)

app_name = "waterquality"


urlpatterns = [
    # ============== Sample ====================
    # Deplying the sensor to a location linked to a project
    path('project/<int:project_pk>/location/<int:location_pk>/sample/add/',
         SampleCreateView.as_view(), name='add-sample'),

    # List all sensor deployments linked to a project.
    path('project/<int:project_pk>/location/<int:location_pk>/samples',
         SampleListView.as_view(), name='samples'),

    # Sample detail view
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/',
         SampleDetailView.as_view(), name='detail-sample'),

    # Update sample
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/update/',
         SampleUpdateView.as_view(), name='update-sample'),

    # Delete sample
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/delete/',
         SampleDeleteView.as_view(), name='delete-sample'),
    # ============== Measurement ====================
    # Deplying the sensor to a location linked to a project
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/measurement/add/',
         MeasurementCreateView.as_view(), name='add-measurement'),

    # List all sensor deployments linked to a project.
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/measurements',
         MeasurementListView.as_view(), name='measurements'),

    # Sample detail view
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/measurement/<int:measurement_pk>/',
         MeasurementDetailView.as_view(), name='detail-measurement'),

    # Update sample
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/measurement/<int:measurement_pk>/update/',
         MeasurementUpdateView.as_view(), name='update-measurement'),

    # Delete sample
    path('project/<int:project_pk>/location/<int:location_pk>/sample/<int:sample_pk>/measurement/<int:measurement_pk>/delete/',
         MeasurementDeleteView.as_view(), name='delete-measurement'),
]
