from django.db import models


class ModelViewConfigMixin:
    """Configuration for how models appear in list and detail views.

    This mixin centralizes view configuration at the model level, reducing
    the need for context objects and view-level configuration.

    Class Attributes:
        _list_view_fields: dict mapping verbose names to field names for list display.
        _detail_view_fields: dict mapping verbose names to field names for detail display.
    """

    _list_view_fields: dict = None
    _detail_view_fields: dict = None
    _has_bulk_create: bool = False
    _url_model_name: str = None

    @classmethod
    def _get_url_model_name(cls):
        """Get the model name for URL construction."""
        if cls._url_model_name:
            return cls._url_model_name
        return cls._meta.model_name

    @classmethod
    def get_item_pk_name(cls):
        """Compose the URL parameter name for this model's primary key.

        Convention: `model_name_pk`, e.g., `sensor_pk` for the Sensor model.
        This is used in URL patterns and view kwargs.
        """
        return f"{cls._get_url_model_name()}_pk"

    def _return_items(self, fields):
        """Returns a list of tuples with field names and their corresponding verbose names."""
        if not fields:
            return []
        return [
            (field_name_verb, getattr(self, field))
            for field_name_verb, field in fields.items()
        ]

    @property
    def detail_view_items(self):
        """Process the dictionary of detail view fields."""
        return self._return_items(self._detail_view_fields)

    @property
    def list_view_items(self):
        """Process the dictionary of list view fields."""
        return self._return_items(self._list_view_fields)


# Keep old name for backwards compatibility
InterfaceModelTemplate = ModelViewConfigMixin


class TimeSeriesModel(models.Model):
    """Abstract base class for timeseries measurement models.

    Provides common structure and methods for models that store time-indexed
    measurements: SensorRecord, GWLManualMeasurement, and Measurement.

    Standardized fields:
        - value: DecimalField - The primary measured value
        - timestamp_field: str - Name of the field that returns the timestamp
        - location_field: str - Path to get the location (e.g., 'location' or 'deployment__location')

    Subclasses may add computed properties for derived values (e.g., groundwater_elevation).

    Provides:
        - Common ordering by timestamp (descending)
        - Queryset helpers for time range filtering
        - Export utilities for CSV/DataFrame conversion
    """

    # The primary measured value - all timeseries models use this
    value = models.DecimalField(max_digits=10, decimal_places=3)

    # Subclasses must override these for filtering
    timestamp_field: str = "timestamp"
    location_field: str = "location"

    class Meta:
        abstract = True

    @classmethod
    def get_for_location(cls, location, start=None, end=None):
        """Get records for a specific location within an optional time range.

        Args:
            location: Location instance to filter by
            start: Optional start datetime
            end: Optional end datetime

        Returns:
            QuerySet of records
        """
        # Build the location filter dynamically
        location_filter = {cls.location_field: location}
        qs = cls.objects.filter(**location_filter)

        if start:
            timestamp_gte = {f"{cls.timestamp_field}__gte": start}
            qs = qs.filter(**timestamp_gte)
        if end:
            timestamp_lte = {f"{cls.timestamp_field}__lte": end}
            qs = qs.filter(**timestamp_lte)

        return qs.order_by(cls.timestamp_field)

    @classmethod
    def get_date_range(cls, queryset=None):
        """Get the min and max timestamps from a queryset.

        Args:
            queryset: Optional queryset to analyze. Uses all records if None.

        Returns:
            tuple: (min_timestamp, max_timestamp) or (None, None) if empty
        """
        qs = queryset if queryset is not None else cls.objects.all()
        aggregation = qs.aggregate(
            min_ts=models.Min(cls.timestamp_field),
            max_ts=models.Max(cls.timestamp_field),
        )
        return aggregation["min_ts"], aggregation["max_ts"]

    @classmethod
    def get_statistics(cls, queryset=None):
        """Get basic statistics for the value field.

        Args:
            queryset: Optional queryset to analyze. Uses all records if None.

        Returns:
            dict with min, max, avg, count
        """
        qs = queryset if queryset is not None else cls.objects.all()
        return qs.aggregate(
            min_value=models.Min("value"),
            max_value=models.Max("value"),
            avg_value=models.Avg("value"),
            count=models.Count("id"),
        )

    @classmethod
    def to_values_list(cls, queryset=None, include_location=False):
        """Convert queryset to a list of (timestamp, value) tuples.

        Efficient for plotting and data export.

        Args:
            queryset: Optional queryset. Uses all records if None.
            include_location: If True, returns (timestamp, value, location_str)

        Returns:
            ValuesListQuerySet of tuples
        """
        qs = queryset if queryset is not None else cls.objects.all()
        fields = [cls.timestamp_field, "value"]

        if include_location:
            fields.append(cls.location_field)

        return qs.values_list(*fields)