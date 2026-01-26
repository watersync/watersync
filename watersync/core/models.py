from django.contrib.gis.db import models as geomodels
from django.db import models
from simple_history.models import HistoricalRecords

from watersync.core.generics.models import SetupSimpleHistory
from watersync.core.managers import LocationManager, ProjectManager, WithCountsManager
from watersync.users.models import User


class Project(models.Model, SetupSimpleHistory):
    """List of projects.

    Project is the main object of the database. All other objects are
    connected to the project. Only users that are attached to the project have access
    to the resources in it.

    Attributes:
        user (ManyToManyField): The users attached to the project.
        name (CharField): The name of the project.
        description (TextField): The description of the project.
        geom (PolygonField): The location of the project.
        start_date (DateField): The date when the project started.
        end_date (DateField): The date when the project ended.
    """

    user = models.ManyToManyField(User, related_name="projects")
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(null=True, blank=True)
    geom = geomodels.PolygonField(srid=4326, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    objects = ProjectManager()
    history = HistoricalRecords()

    # Fields to count in with_counts() - used for dashboard
    _count_fields = ['locations', 'fieldworks']

    _detail_view_fields = {
        "Started": "start_date",
        "Ended": "end_date",
        "Active": "active",
    }

    def active(self):
        """Check if the project is currently active."""
        return self.end_date is None or self.end_date >= models.functions.Now()

    def natural_key(self):
        return (self.name,)
    
    def __str__(self):
        return self.name

class Location(models.Model, SetupSimpleHistory):
    """List of locations.

    Locations are attached to projects and most of other types of data in projects like
    measurements or analyses are attached to locations. Location also tracks the
    history of the updates. The history is tracked by the simple_history package.
    It is useful in cases when the location parameters like height of the top of the
    casing change, but old measurement still refer to the old location height.

    Attributes:
        project (ForeignKey): The project to which the location is attached.
        name (CharField): The name of the location.
        geom (PointField): The geographic coordinates of the location.
        altitude (DecimalField): The altitude of the location.
        type (CharField): The type of the location. The type is one of the
            following: well, river, lake, wastewater, precipitation.
        description (TextField): The description of the location.
        detail (JSONField): JSON field with station detail to provide flexible
            schema and avoid related models.
    """

    class LocationTypes(models.TextChoices):
        WELL = "pumping_well", "Pumping well"
        PIEZOMETER = "piezometer", "Piezometer"
        RIVER = "river", "River"
        LAKE = "lake", "Lake"
        WASTEWATER = "wastewater", "Wastewater"
        PRECIPITATION = "precipitation", "Precipitation"

    class StatusChoices(models.TextChoices):
        OPERATIONAL = "operational", "Operational"
        NEEDS_MAINTENANCE = "needs-maintenance", "Needs Maintenance"
        DECOMMISSIONED = "decommissioned", "Decommissioned"
        UNKNOWN = "unknown", "Unknown"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="locations"
    )
    name = models.CharField(max_length=50)
    geom = geomodels.PointField(dim=3,srid=4326)
    type = models.CharField(choices=LocationTypes.choices, max_length=20)
    installation_date = models.DateField(null=True, blank=True)
    decommision_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices,
        default=StatusChoices.OPERATIONAL
    )
    detail = models.JSONField(null=True, blank=True)

    objects = LocationManager()
    history = HistoricalRecords()

    # Fields to count in with_counts() - used for overview pages
    _count_fields = ['gwlmeasurements', 'deployments', 'samples']

    _detail_view_fields = {
        "Type": "type",
    }
    _list_view_fields = {
        "Name": "name",
    }

    _csv_columns = {"Name": "name", "Type": "type", "Depth": "detail__depth"}

    class Meta:
        unique_together = ("project", "name")

    def __str__(self):
        return f"{self.name}"

class Fieldwork(models.Model, SetupSimpleHistory):
    """Reports from days spent in the field.

    This model aggregates data from a fieldwork event. During one fieldwork event,
    user can take multiple measurements at different locations. The fieldwork is related to a
    project and users. Should also contain information on weather conditions and other
    relevant information about what happened during the fieldwork. There can be only one
    fieldwork per day.
    """
    
    _has_bulk_create = True
    
    class WeatherConditions(models.TextChoices):
        SUNNY = "sunny", "Sunny"
        CLOUDY = "cloudy", "Cloudy"
        RAINY = "rainy", "Rainy"
        SNOWY = "snowy", "Snowy"
        WINDY = "windy", "Windy"
        STORMY = "stormy", "Stormy"

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="fieldworks"
    )
    user = models.ManyToManyField(User, null=True, blank=True, related_name="fieldworks")
    date = models.DateField(unique=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    weather =  models.CharField(
        max_length=20,
        choices=WeatherConditions.choices,
        default=WeatherConditions.SUNNY
    )
    description = models.TextField(blank=True, null=True)

    objects = WithCountsManager()
    history = HistoricalRecords()

    # Fields to count in with_counts() - used for overview pages
    _count_fields = ['gwlmeasurements', 'samples']

    _list_view_fields = {
        "Date": "date",
    }

    _detail_view_fields = {
        "Project": "project",
        "Date": "date",
        "Start time": "start_time",
        "End time": "end_time",
        "Weather": "weather"
    }

    def __str__(self):
        # Use project_id to avoid triggering a lazy DB query in async contexts
        return f"Fieldwork {self.project_id} - {self.date}"
