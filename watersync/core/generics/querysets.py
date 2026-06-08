from django.db import models
from django.db.models import Avg, Count, Max, Min


class UserScopedQuerySet(models.QuerySet):
    """QuerySet that can filter objects by user access."""

    def _get_user_filter_path(self):
        """Determine how to filter by user."""
        meta = self.model._meta
        field_names = [f.name for f in meta.get_fields()]

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
            return None

    def for_user(self, user):
        """Filter queryset to objects the user has access to."""
        user_path = self._get_user_filter_path()

        if user_path is None:
            return self.filter(user=user)
        else:
            return self.filter(**{user_path: user})


class ProjectScopedQuerySet(UserScopedQuerySet):
    """QuerySet that can filter objects by project."""

    def for_project(self, project_pk):
        """Filter queryset to objects belonging to a project."""
        project_path = self._get_project_path()
        if project_path is None:
            return self.filter(pk=project_pk)
        return self.filter(**{project_path: project_pk})


class LocationScopedQuerySet(ProjectScopedQuerySet):
    """QuerySet that can filter objects by location."""

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


# ============================================================================
# FEATURE MIXINS - These add specific capabilities
# ============================================================================

class WithCountsMixin:
    """Mixin that adds with_counts() capability to QuerySet."""

    def with_counts(self):
        """Annotate queryset with counts of related objects."""
        count_fields = getattr(self.model, '_count_fields', [])
        annotations = {
            f"{field}_count": Count(field, distinct=True)
            for field in count_fields
        }
        return self.annotate(**annotations)


# ============================================================================
# COMPOSED QUERYSETS - Mix base scoping with feature mixins
# ============================================================================


class ProjectWithCountsQuerySet(WithCountsMixin, ProjectScopedQuerySet):
    """Project-scoped queryset with counts."""
    pass


class WithDetailMixin:
    """Mixin that adds detail prefetching capability to QuerySet."""

    def with_details(self):
        """Prefetch all possible detail relationships."""
        detail_map = getattr(self.model, 'DETAIL_RELATED_NAMES', {})
        if not detail_map:
            raise ValueError(
                f"{self.model.__name__} must define DETAIL_RELATED_NAMES "
                "to use with_details()"
            )
        return self.select_related(*detail_map.values())

    def with_detail_for_type(self, type_value):
        """Prefetch detail for a specific type."""
        detail_map = getattr(self.model, 'DETAIL_RELATED_NAMES', {})
        related_name = detail_map.get(type_value)
        if related_name:
            return self.select_related(related_name)
        return self


class ProjectWithDetailQuerySet(WithDetailMixin, ProjectScopedQuerySet):
    """Project-scoped queryset with detail loading."""
    pass


class LocationWithCountsQuerySet(WithCountsMixin, LocationScopedQuerySet):
    """Location-scoped queryset with counts."""
    pass


class LocationWithDetailQuerySet(WithDetailMixin, LocationScopedQuerySet):
    """Location-scoped queryset with detail loading."""
    pass


class LocationWithCountsAndDetailQuerySet(WithCountsMixin, WithDetailMixin, LocationScopedQuerySet):
    """Location-scoped queryset with both counts and detail loading."""
    pass


class TimeSeriesMixin:
    """Mixin that adds time series analysis methods to QuerySet."""

    def date_range(self):
        """Get the min and max timestamps from this queryset."""
        timestamp_field = getattr(self.model, 'timestamp_field', 'timestamp')
        aggregation = self.aggregate(
            min_ts=Min(timestamp_field),
            max_ts=Max(timestamp_field),
        )
        return aggregation["min_ts"], aggregation["max_ts"]

    def statistics(self):
        """Get basic statistics for the value field."""
        return self.aggregate(
            min_value=Min("value"),
            max_value=Max("value"),
            avg_value=Avg("value"),
            count=Count("id"),
        )

    def for_plotting(self, include_location=False):
        """Convert queryset to a values list for plotting."""
        timestamp_field = getattr(self.model, 'timestamp_field', 'timestamp')
        location_field = getattr(self.model, 'location_field', 'location')

        fields = [timestamp_field, "value"]
        if include_location:
            fields.append(location_field)

        return self.values_list(*fields)


class TimeSeriesQuerySet(TimeSeriesMixin, WithCountsMixin, LocationScopedQuerySet):
    """Location-scoped queryset with time series methods and counts."""
    pass


class SoftDeleteMixin:
    """Mixin that adds soft delete filtering to Manager."""

    def get_queryset(self):
        """Return queryset excluding soft-deleted records by default."""
        qs = super().get_queryset()
        return qs.filter(is_deleted=False)

    def all_with_deleted(self):
        """Return queryset including soft-deleted records."""
        # Get base queryset class from get_queryset's return type
        return super().get_queryset()

    def deleted_only(self):
        """Return queryset with only soft-deleted records."""
        return super().get_queryset().filter(is_deleted=True)