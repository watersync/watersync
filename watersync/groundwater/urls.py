from django.urls import path
from .views import (GWLCreateView, GWLListView,
                    GWLDeleteView, GWLUpdateView, GWLDetailView)

app_name = "groundwater"


urlpatterns = [
    # GWL views
    path('project/<int:project_pk>/location/<int:location_pk>/gwlmeasurements',
         GWLListView.as_view(), name='gwlmeasurements'),

    path('project/<int:project_pk>/location/<int:location_pk>/gwlmeasurement/add/',
         GWLCreateView.as_view(), name='add-gwlmeasurement'),

    path('project/<int:project_pk>/location/<int:location_pk>/gwlmeasurement/<int:gwlmeasurement_pk>/',
         GWLDetailView.as_view(), name='detail-gwlmeasurement'),

    path('project/<int:project_pk>/location/<int:location_pk>/gwlmeasurement/<int:gwlmeasurement_pk>/update/',
         GWLUpdateView.as_view(), name='update-gwlmeasurement'),

    path('project/<int:project_pk>/location/<int:location_pk>/gwlmeasurement/<int:gwlmeasurement_pk>/delete/',
         GWLDeleteView.as_view(), name='delete-gwlmeasurement'),
]
