from django.contrib.gis.db import models as geomodels
from django_extensions.db.models import TimeStampedModel
from django.db import models
from simple_history.models import HistoricalRecords

from watersync.core.managers import LocationManager, WatersyncManager
from watersync.core.generics.mixins import ModelTemplateInterface, SimpleHistorySetup
from watersync.users.models import User

class Unit(models.Model, ModelTemplateInterface):
    """Unit of measurement for parameters.

    Each parameter can have a specific unit of measurement. This model defines
    the units that can be used for parameters.

    Attributes:
        symbol (CharField): The name of the unit.
        description (CharField): The symbol of the unit.
    """

    symbol = models.CharField(max_length=10)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.symbol
    
    _list_view_fields = {
        "Symbol": "symbol",
    }

class Project(models.Model, ModelTemplateInterface, SimpleHistorySetup):
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
        is_active (BooleanField): The status of the project.
        created (DateTimeField): The date and time when the project was
            created. Handled by TimesStampedModel. This field will autoupdate
            when created.
        modified (DateTimeField): The date and time when the project was
            updated. Handled by TimesStampedModel. This field will update
            when created.
    """

    user = models.ManyToManyField(User, related_name="projects")
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(null=True, blank=True)
    geom = geomodels.PolygonField(srid=4326, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = ProjectManager()
    history = HistoricalRecords()

    _detail_view_fields = {
        "Started": "start_date",
        "Ended": "end_date",
        "Active": "is_active",
    }

    def natural_key(self):
        return (self.name,)
    
    def __str__(self):
        return self.name


class Location(TimeStampedModel, ModelTemplateInterface, SimpleHistorySetup):
    """List of locations.

    Locations are attached to projects and most of other types of data in projects like
    measurements or analyses are attached to locations. Location also tracks the
    history of the updates. The history is tracked by the simple_history package.
    It is useful in cases when the location parameters like height of the top of the
    casing change, but old measurement still refer to the old location height.

    Attributes:
        user (ForeignKey): The user that created the location.
        project (ForeignKey): The project to which the location is attached.
        name (CharField): The name of the location.
        geom (PointField): The geographic coordinates of the location.
        altitude (DecimalField): The altitude of the location.
        type (CharField): The type of the location. The type is one of the
            following: well, river, lake, wastewater, precipitation.
        description (TextField): The description of the location.
        detail (JSONField): JSON field with station detail to provide flexible
            schema and avoid related models.
        created (DateTimeField): The date and time when the location was
            created. This field is handled by TimesStampedModel and will be populated
            when created.
        updated (DateTimeField): The date and time when the location was
            updated. This field is handled by TimesStampedModel and will autoupdate
            when updated.

        Properties:
            latest_status (str): The latest status of the location.
    """

    LOCATION_TYPES = {
        "well": "Well",
        "river": "River",
        "lake": "Lake",
        "wastewater": "Wastewater",
        "precipitation": "Precipitation",
    }

    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="locations"
    )
    name = models.CharField(max_length=50)
    geom = geomodels.PointField(srid=4326)
    altitude = models.DecimalField(max_digits=8, decimal_places=2)
    type = models.CharField(choices=LOCATION_TYPES)
    description = models.TextField(blank=True, null=True)
    detail = models.JSONField(null=True, blank=True)

    objects = LocationManager()
    watersync = WatersyncManager()
    history = HistoricalRecords()

    _detail_view_fields = {
        "Type": "type",
        "Altitude": "altitude",
        "Created at": "created",
        "Modified at": "modified",
    }
    _list_view_fields = {
        "Name": "name",
    }

    _csv_columns = {"Name": "name", "Type": "type", "Created": "project__created", "Visits": "locvisits"}

    class Meta:
        unique_together = ("project", "name")

    def __str__(self):
        return f"{self.name}"

    @property
    def latest_status(self):
        return self.visits.latest("created").status


class LocationVisit(TimeStampedModel, ModelTemplateInterface):
    """Status of locations at the given time.

    Normally when you go to the field, you visit one or more locations of interst and 
    take measurements at them. First it is important to give an update on the status of
    the location. Then measurements are taken. In the database, those measurements are
    linked to location visits for easy retrieval.

    Attributes:
        location (ForeignKey): The location to which the status is attached.
        status (CharField): Short status of the location.
        description (Optional[CharField]): Descriptive comment about the status, if necessary.
        timestamp (DateTimeField): The date and time when the status was
            created.
    """

    STATUS_CHOICES = [
        ("operational", "Operational"),
        ("needs-maintenance", "Needs maintenance"),
        ("decommissioned", "Decommissioned"),
        ("unknown", "Unknown"),
    ]

    fieldwork = models.ForeignKey(
        "Fieldwork",
        related_name="visits",
        on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, related_name="visits", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unknown")
    description = models.TextField(blank=True, null=True)

    _list_view_fields = {
        "Fieldwork": "fieldwork",
        "Location": "location",
        "Status": "status",
    }

    def __str__(self) -> str:
        return f"{self.location} - {self.fieldwork.date:%Y-%m-%d}"


class Fieldwork(TimeStampedModel, ModelTemplateInterface):
    """Reports from days spent in the field.

    This model aggregates data from a fieldwork event. During one fieldwork event,
    user can take multiple measurements at different locations. The fieldwork is related to a
    project and users. Should also contain information on weather conditions and other
    relevant information about what happened during the fieldwork.
    """
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
    user = models.ManyToManyField(User, related_name="fieldworks")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    weather =  models.CharField(
        max_length=20,
        choices=WeatherConditions.choices,
        default=WeatherConditions.SUNNY
    )
    description = models.TextField(blank=True, null=True)

    _list_view_fields = {
        "Date": "date",
    }

    _detail_view_fields = {
        "Project": "project",
        "Date": "date",
        "Start time": "start_time",
        "End time": "end_time",
        "Created at": "created",
        "Modified at": "modified",
    }

    def __str__(self):
        return f"{self.project} - {self.date}"
