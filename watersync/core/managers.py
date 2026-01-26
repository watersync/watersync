from django.db import models
from django.db.models import Avg, Count, Max, Min


class UserScopedQuerySet(models.QuerySet):
    """QuerySet that can filter objects by user access.
    
    Handles three cases:
    1. Models with direct 'user' M2M (e.g., Project, Sensor) - filters directly
    2. Models linked to project - filters via project's user M2M
    3. Models not linked to either - raises error
    
    Example:
        # Direct user M2M
        Project.objects.for_user(request.user)
        Sensor.objects.for_user(request.user)
        
        # Via project (auto-detects path)
        Sample.objects.for_user(request.user)
    """
    
    def _get_user_filter_path(self):
        """Determine how to filter by user.
        
        Returns:
            str or None: The filter path to user, or None if direct 'user' field exists
        """
        meta = self.model._meta
        field_names = [f.name for f in meta.get_fields()]
        
        # Check if model has direct user M2M
        if 'user' in field_names:
            return None  # Direct user field
        
        # Otherwise, find path to project
        if 'project' in field_names:
            return 'project__user'
        elif 'location' in field_names:
            return 'location__project__user'
        elif 'fieldwork' in field_names:
            return 'fieldwork__project__user'
        elif 'sample' in field_names:
            return 'sample__location__project__user'
        elif 'deployment' in field_names:
            return 'deployment__location__project__user'
        else:
            raise ValueError(
                f"Cannot determine user access path for {self.model.__name__}. "
                "Model must have 'user' field or be linked to project."
            )
    
    def _get_project_path(self):
        """Determine the path to project based on model fields."""
        meta = self.model._meta
        field_names = [f.name for f in meta.get_fields()]
        
        # Check if this IS the Project model
        if self.model.__name__ == 'Project':
            return None
        
        if 'project' in field_names:
            return 'project'
        elif 'location' in field_names:
            return 'location__project'
        elif 'fieldwork' in field_names:
            return 'fieldwork__project'
        elif 'sample' in field_names:
            return 'sample__location__project'
        elif 'deployment' in field_names:
            return 'deployment__location__project'
        else:
            return None  # Model not linked to project (e.g., Sensor)
    
    def for_user(self, user):
        """Filter queryset to objects the user has access to."""
        user_path = self._get_user_filter_path()
        
        if user_path is None:
            # Direct user M2M field
            return self.filter(user=user)
        else:
            # Filter via path to user
            return self.filter(**{user_path: user})


class UserScopedManager(models.Manager):
    """Manager providing for_user() from UserScopedQuerySet."""
    
    def get_queryset(self):
        return UserScopedQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)


class ProjectScopedQuerySet(UserScopedQuerySet):
    """QuerySet that can filter objects by project.
    
    Inherits from UserScopedQuerySet to provide for_user().
    
    Example:
        Sample.objects.for_project(project_pk)
        Sample.objects.for_user(user).for_project(project_pk)
    """
    
    def for_project(self, project_pk):
        """Filter queryset to objects belonging to a project."""
        project_path = self._get_project_path()
        if project_path is None:
            # This is the Project model
            return self.filter(pk=project_pk)
        return self.filter(**{project_path: project_pk})


class ProjectScopedManager(UserScopedManager):
    """Manager providing for_project() and for_user()."""
    
    def get_queryset(self):
        return ProjectScopedQuerySet(self.model, using=self._db)
    
    def for_project(self, project_pk):
        return self.get_queryset().for_project(project_pk)


class LocationScopedQuerySet(ProjectScopedQuerySet):
    """QuerySet that can filter objects by location.
    
    Inherits from ProjectScopedQuerySet to provide both for_project() and for_location().
    
    Automatically determines the filter path to location by checking model fields:
    - If model has 'location' FK → filter by location=pk
    - If model has 'sample' FK → filter by sample__location=pk
    
    Example:
        class Measurement(models.Model):
            sample = models.ForeignKey(Sample, ...)
            objects = LocationScopedManager()
            
        # Automatically uses sample__location
        Measurement.objects.for_location(location_pk)
    """
    
    def _get_location_path(self):
        """Determine the path to location FK based on model fields."""
        meta = self.model._meta
        field_names = [f.name for f in meta.get_fields()]
        
        if 'location' in field_names:
            return 'location'
        elif 'sample' in field_names:
            return 'sample__location'
        else:
            raise ValueError(
                f"Cannot determine location path for {self.model.__name__}. "
                "Model must have 'location' or 'sample' field."
            )
    
    def for_location(self, location_pk):
        """Filter queryset to objects belonging to a location."""
        location_path = self._get_location_path()
        return self.filter(**{location_path: location_pk})


class LocationScopedManager(ProjectScopedManager):
    """Manager providing for_location() and for_project()."""
    
    def get_queryset(self):
        return LocationScopedQuerySet(self.model, using=self._db)
    
    def for_location(self, location_pk):
        return self.get_queryset().for_location(location_pk)


class SoftDeleteLocationScopedManager(LocationScopedManager):
    """Manager for models with soft delete that are scoped to location.
    
    Default queryset excludes soft-deleted records.
    Use all_with_deleted() to include deleted records.
    """
    
    def get_queryset(self):
        """Return queryset excluding soft-deleted records by default."""
        return LocationScopedQuerySet(self.model, using=self._db).filter(is_deleted=False)
    
    def all_with_deleted(self):
        """Return queryset including soft-deleted records."""
        return LocationScopedQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """Return queryset with only soft-deleted records."""
        return LocationScopedQuerySet(self.model, using=self._db).filter(is_deleted=True)


class WithCountsQuerySet(LocationScopedQuerySet):
    """QuerySet providing related object counting.
    
    Models should define `_count_fields`: list of related field names to count.
    
    Example:
        class Location(models.Model):
            _count_fields = ['gwlmeasurements', 'deployments', 'samples']
            objects = WithCountsManager()
            
        # Usage - chainable
        Location.objects.for_project(pk).with_counts()
        
        # Accessing in template
        {{ location.gwlmeasurements_count }}
    """
    
    def with_counts(self):
        """Annotate queryset with counts of related objects.
        
        Uses model's `_count_fields` to determine which relations to count.
        Each field gets a `{field}_count` annotation.
        """
        count_fields = getattr(self.model, '_count_fields', [])
        annotations = {
            f"{field}_count": Count(field, distinct=True)
            for field in count_fields
        }
        return self.annotate(**annotations)


class WithCountsManager(LocationScopedManager):
    """Manager providing with_counts(), for_location(), and for_project()."""
    
    def get_queryset(self):
        return WithCountsQuerySet(self.model, using=self._db)
    
    def with_counts(self):
        return self.get_queryset().with_counts()


class TimeSeriesQuerySet(WithCountsQuerySet):
    """QuerySet with time series analysis methods and soft delete support.
    
    Inherits from WithCountsQuerySet to provide:
    - for_user() - filter by user access
    - for_project() - filter by project
    - for_location() - filter by location
    - with_counts() - annotate with related counts
    
    Soft delete support:
    - Default queryset excludes soft-deleted records
    - Use all_with_deleted() to include deleted records
    - Use deleted_only() to get only deleted records
    
    Example:
        GWLManualMeasurement.objects.for_location(pk).statistics()
        SensorRecord.objects.filter(deployment=dep).for_plotting()
        SensorRecord.objects.all_with_deleted()  # includes deleted
    """
    
    def date_range(self):
        """Get the min and max timestamps from this queryset.

        Returns:
            tuple: (min_timestamp, max_timestamp) or (None, None) if empty
        """
        timestamp_field = getattr(self.model, 'timestamp_field', 'timestamp')
        aggregation = self.aggregate(
            min_ts=Min(timestamp_field),
            max_ts=Max(timestamp_field),
        )
        return aggregation["min_ts"], aggregation["max_ts"]

    def statistics(self):
        """Get basic statistics for the value field.

        Returns:
            dict with min_value, max_value, avg_value, count
        """
        return self.aggregate(
            min_value=Min("value"),
            max_value=Max("value"),
            avg_value=Avg("value"),
            count=Count("id"),
        )

    def for_plotting(self, include_location=False):
        """Convert queryset to a values list for plotting.

        Args:
            include_location: If True, includes location in output

        Returns:
            ValuesListQuerySet of (timestamp, value) or (timestamp, value, location) tuples
        """
        timestamp_field = getattr(self.model, 'timestamp_field', 'timestamp')
        location_field = getattr(self.model, 'location_field', 'location')
        
        fields = [timestamp_field, "value"]
        if include_location:
            fields.append(location_field)

        return self.values_list(*fields)


class TimeSeriesManager(WithCountsManager):
    """Manager for time series models with analysis methods and soft delete.
    
    Default queryset excludes soft-deleted records.
    Use all_with_deleted() to include deleted records.
    """
    
    def get_queryset(self):
        """Return queryset excluding soft-deleted records by default."""
        return TimeSeriesQuerySet(self.model, using=self._db).filter(is_deleted=False)
    
    def all_with_deleted(self):
        """Return queryset including soft-deleted records."""
        return TimeSeriesQuerySet(self.model, using=self._db)
    
    def deleted_only(self):
        """Return queryset with only soft-deleted records."""
        return TimeSeriesQuerySet(self.model, using=self._db).filter(is_deleted=True)
    
    def date_range(self):
        return self.get_queryset().date_range()
    
    def statistics(self):
        return self.get_queryset().statistics()
    
    def for_plotting(self, include_location=False):
        return self.get_queryset().for_plotting(include_location)


class LocationManager(WithCountsManager):
    """Manager for Location with natural key support and related counts."""
    
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ProjectManager(WithCountsManager):
    """Manager for Project model with natural key support and related counts."""

    def get_by_natural_key(self, name):
        return self.get(name=name)
