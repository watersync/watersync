from django.contrib.gis.db import models as geomodels
from django_extensions.db.models import TimeStampedModel
from django.db import models
from simple_history.models import HistoricalRecords

from watersync.core.managers import LocationManager
from watersync.core.generics.mixins import ModelTemplateInterface, SimpleHistorySetup
from watersync.users.models import User


class Project(TimeStampedModel, ModelTemplateInterface):
    """List of projects.

    Project is the main object of the database. All other objects are
    connected to the project. Depending on whether the user is attached
    to the project, the user can see the data related to the project.

    Attributes:
        user (ManyToManyField): The users attached to the project.
        name (CharField): The name of the project.
        description (TextField): The description of the project.
        location (PointField): The geographic coordinates of the project.
        start_date (DateField): The date when the project started.
        created_at (DateTimeField): The date and time when the project was
            created. This field will autoupdate when created.
        updated_at (DateTimeField): The date and time when the project was
            updated. This field will update when created.
        end_date (DateField): The date when the project ended.
        is_active (BooleanField): The status of the project.
    """

    user = models.ManyToManyField(User, related_name="projects")
    name = models.CharField(unique=True, max_length=50)
    description = models.TextField(null=True, blank=True)
    geom = geomodels.PolygonField(srid=4326, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    _detail_view_fields = {
        "Started": "start_date",
        "Ended": "end_date",
        "Created at": "created",
        "Modified at": "modified",
        "Active": "is_active",
    }

    def __str__(self):
        return self.name


class Location(TimeStampedModel, ModelTemplateInterface, SimpleHistorySetup):
    """List of locations.

    Locations are attached to projects and each measurement or analysis
    is attached to the location. On this basis the user can see the data
    related to the location.

    Attributes:
        project (ForeignKey): The project to which the location is attached.
        name (CharField): The name of the location.
        geom (PointField): The geographic coordinates of the location.
        altitude (DecimalField): The altitude of the location.
        description (TextField): The description of the location.
        added_by (ForeignKey): The user that added the location.
        created_at (DateTimeField): The date and time when the location was
            created.
        updated_at (DateTimeField): The date and time when the location was
            updated.
        detail (JSONField): JSON field with station detail to provide flexible
        schema and avoid related models.


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

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="locations"
    )
    name = models.CharField(max_length=50)
    geom = geomodels.PointField(srid=4326)
    altitude = models.DecimalField(max_digits=8, decimal_places=2)
    type = models.CharField(choices=LOCATION_TYPES)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    detail = models.JSONField(null=True, blank=True)

    objects = LocationManager()
    history = HistoricalRecords()

    _detail_view_fields = {
        "Type": "type",
        "Altitude": "altitude",
        "Created at": "created",
        "Modified at": "modified",
    }

    class Meta:
        unique_together = ("project", "name")

    def __str__(self):
        return f"{self.name}"

    @property
    def latest_status(self):
        return self.visits.latest("created").status


class LocationVisit(TimeStampedModel, ModelTemplateInterface):
    """Status of the location at the given time.

    Attributes:
        location (ForeignKey): The location to which the status is attached.
        status (CharField): Short status of the location.
        comment (Optional[CharField]): Descriptive comment about the status, if necessary.
        timestamp (DateTimeField): The date and time when the status was
            created.
    """

    STATUS_CHOICES = [
        ("operational", "Operational"),
        ("needs-maintenance", "Needs maintenance"),
        ("decommissioned", "Decommissioned"),
        ("unknown", "Unknown"),
    ]

    location = models.ForeignKey(
        Location, related_name="visits", on_delete=models.CASCADE
    )
    fieldwork = models.ForeignKey(
        "Fieldwork",
        related_name="visits",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unknown")
    comment = models.CharField(max_length=255, blank=True, null=True)

    _list_view_fields = {
        "Location": "location",
        "Status": "status",
        "Date": "created",
    }

    def __str__(self) -> str:
        return f"{self.location} - {self.created:%Y-%m-%d} - {self.status}"


class Fieldwork(TimeStampedModel, ModelTemplateInterface):
    """Register fieldwork day done in a project.

    This model aggregates data from a fieldwork event. During one fieldwork event,
    user can take multiple measurements at different locations. The fieldwork is related to a
    project and users. Should also contain information on weather conditions and other
    relevant information about what happened during the fieldwork.
    """

    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name="fieldworks"
    )
    user = models.ManyToManyField(User, related_name="fieldworks")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    weather = models.JSONField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

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
