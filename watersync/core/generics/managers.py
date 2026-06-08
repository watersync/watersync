from django.db import models

from watersync.core.generics.querysets import (
    LocationScopedQuerySet,
    LocationWithCountsAndDetailQuerySet,
    LocationWithCountsQuerySet,
    LocationWithDetailQuerySet,
    ProjectScopedQuerySet,
    ProjectWithCountsQuerySet,
    ProjectWithDetailQuerySet,
    SoftDeleteMixin,
    TimeSeriesQuerySet,
    UserScopedQuerySet,
)


class UserScopedManager(models.Manager):
    """Manager providing for_user()."""

    def get_queryset(self):
        return UserScopedQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)


class ProjectScopedManager(UserScopedManager):
    """Manager providing for_project() and for_user()."""

    def get_queryset(self):
        return ProjectScopedQuerySet(self.model, using=self._db)

    def for_project(self, project_pk):
        return self.get_queryset().for_project(project_pk)


class LocationScopedManager(ProjectScopedManager):
    """Manager providing for_location(), for_project(), and for_user()."""

    def get_queryset(self):
        return LocationScopedQuerySet(self.model, using=self._db)

    def for_location(self, location_pk):
        return self.get_queryset().for_location(location_pk)


# ============================================================================
# COMPOSED MANAGERS - Match querysets with manager methods
# ============================================================================


class ProjectWithCountsManager(ProjectScopedManager):
    """Manager for project-scoped models with counts."""

    def get_queryset(self):
        return ProjectWithCountsQuerySet(self.model, using=self._db)

    def with_counts(self):
        return self.get_queryset().with_counts()


class ProjectWithDetailManager(ProjectScopedManager):
    """Manager for project-scoped models with detail loading."""

    def get_queryset(self):
        return ProjectWithDetailQuerySet(self.model, using=self._db)

    def with_details(self):
        return self.get_queryset().with_details()

    def with_detail_for_type(self, type_value):
        return self.get_queryset().with_detail_for_type(type_value)


class LocationWithCountsManager(LocationScopedManager):
    """Manager for location-scoped models with counts."""

    def get_queryset(self):
        return LocationWithCountsQuerySet(self.model, using=self._db)

    def with_counts(self):
        return self.get_queryset().with_counts()


class LocationWithDetailManager(LocationScopedManager):
    """Manager for location-scoped models with detail loading."""

    def get_queryset(self):
        return LocationWithDetailQuerySet(self.model, using=self._db)

    def with_details(self):
        return self.get_queryset().with_details()

    def with_detail_for_type(self, type_value):
        return self.get_queryset().with_detail_for_type(type_value)


class LocationWithCountsAndDetailManager(LocationScopedManager):
    """Manager for location-scoped models with both counts and detail loading."""

    def get_queryset(self):
        return LocationWithCountsAndDetailQuerySet(self.model, using=self._db)

    def with_counts(self):
        return self.get_queryset().with_counts()

    def with_details(self):
        return self.get_queryset().with_details()

    def with_detail_for_type(self, type_value):
        return self.get_queryset().with_detail_for_type(type_value)


class TimeSeriesManager(SoftDeleteMixin, LocationScopedManager):
    """Manager for time series models with soft delete."""

    def get_queryset(self):
        """Return queryset excluding soft-deleted records by default."""
        return TimeSeriesQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_counts(self):
        return self.get_queryset().with_counts()

    def date_range(self):
        return self.get_queryset().date_range()

    def statistics(self):
        return self.get_queryset().statistics()

    def for_plotting(self, include_location=False):
        return self.get_queryset().for_plotting(include_location)


class SoftDeleteLocationScopedManager(SoftDeleteMixin, LocationScopedManager):
    """Manager for location-scoped models with soft delete."""

    def get_queryset(self):
        """Return queryset excluding soft-deleted records by default."""
        return LocationScopedQuerySet(self.model, using=self._db).filter(is_deleted=False)