from django.urls import path
from watersync.sensor.views import (SensorCreateView, SensorListView,
                                    SensorDeleteView, SensorUpdateView,
                                    SensorDetailView)

app_name = "sensor"


urlpatterns = [
    # Sensor list view with user_id
    path('sensors/',
         SensorListView.as_view(), name='sensors'),

    # Add a new sensor for a specific user
    path('sensor/add/',
         SensorCreateView.as_view(), name='add-sensor'),

    # Sensor detail view with user_id
    path('sensor/<int:sensor_pk>/',
         SensorDetailView.as_view(), name='detail-sensor'),

    # Update sensor with user_id
    path('sensor/update/<int:sensor_pk>/',
         SensorUpdateView.as_view(), name='update-sensor'),

    # Delete sensor with user_id
    path('sensor/delete/<int:sensor_pk>/',
         SensorDeleteView.as_view(), name='delete-sensor'),
]
