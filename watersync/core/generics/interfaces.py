from django.db import models
from django.urls import reverse, NoReverseMatch


class ModelURLMixin:
    """Mixin that provides URL generation methods for models.

    This eliminates the need for views to construct URLs with placeholders.
    Models inherit this mixin and can generate their own full URLs according to a consistent pattern.

    Configuration (class attributes):
        _url_app_label: Override the app label for URLs (default: model's app_label)
        _url_model_name: Override the model name for URLs (default: model's model_name)
        _url_parent_field: Field name that points to parent (e.g., 'project', 'location')
        _url_parent_param: URL parameter name for parent (e.g., 'project_pk')

    URL naming convention follows the existing pattern:
        - detail: app:detail-modelname
        - update: app:update-modelname
        - delete: app:delete-modelname
        - list: app:modelnames (plural)
        - overview: app:overview-modelname
        - history: app:list-historicalmodelname

    Properties for URL names (without resolution):
        - list_url_name: URL name for list view
        - add_url_name: URL name for add view
        - detail_url_name: URL name for detail view
        - update_url_name: URL name for update view
        - delete_url_name: URL name for delete view

    Properties for view integration:
        - htmx_trigger: HTMX trigger name for this model
        - item_pk_name: URL parameter name for this model's pk
        - verbose_name_plural: The verbose plural name (for display)
    """

    # Override these in subclasses if needed
    _url_app_label: str = None
    _url_model_name: str = None
    _url_parent_field: str = None  # e.g., 'project' or 'location'
    _url_parent_param: str = None  # e.g., 'project_pk'

    @classmethod
    def _get_url_app_label(cls):
        """Get the app label for URL construction."""
        if cls._url_app_label:
            return cls._url_app_label
        return cls._meta.app_label

    @classmethod
    def _get_url_model_name(cls):
        """Get the model name for URL construction."""
        if cls._url_model_name:
            return cls._url_model_name
        return cls._meta.model_name

    @classmethod
    def _get_url_model_name_plural(cls):
        """Get the plural model name for URL construction."""
        return cls._meta.verbose_name_plural.replace(" ", "")

    @classmethod
    def _get_verbose_name_plural(cls):
        """Get the verbose name plural of the model (for display purposes)."""
        return cls._meta.verbose_name_plural

    # -------------------------------------------------------------------------
    # URL Name Properties (unresolved - useful for views and templates)
    # -------------------------------------------------------------------------

    @classmethod
    def _get_url_name(cls, action):
        """Compose the URL pattern name for a given action.

        Standardized URL naming convention:
        - For listing: `app_label:model_name_plural`, e.g., `sensors:sensors`
        - For history: `app_label:list-historicalmodel_name`
        - For other actions: `app_label:action-model_name`, e.g., `sensors:add-sensor`
        """
        app = cls._get_url_app_label()
        model = cls._get_url_model_name()

        if action == "list":
            return f"{app}:{cls._get_url_model_name_plural()}"
        if action == "history":
            return f"{app}:list-historical{model}"
        return f"{app}:{action}-{model}"

    @classmethod
    def get_list_url_name(cls):
        """Get the URL name for the list view."""
        return cls._get_url_name("list")

    @classmethod
    def get_add_url_name(cls):
        """Get the URL name for the add view."""
        return cls._get_url_name("add")

    @classmethod
    def get_detail_url_name(cls):
        """Get the URL name for the detail view."""
        return cls._get_url_name("detail")

    @classmethod
    def get_update_url_name(cls):
        """Get the URL name for the update view."""
        return cls._get_url_name("update")

    @classmethod
    def get_delete_url_name(cls):
        """Get the URL name for the delete view."""
        return cls._get_url_name("delete")

    @classmethod
    def get_history_url_name(cls):
        """Get the URL name for the history view."""
        return cls._get_url_name("history")

    # -------------------------------------------------------------------------
    # View Integration Properties
    # -------------------------------------------------------------------------

    @classmethod
    def get_htmx_trigger(cls):
        """Compose the HTMX change action name for this model.

        Returns a string like 'sensorChanged' that can be used as an
        HX-Trigger header value to notify other components of changes.
        """
        return f"{cls._get_url_model_name()}Changed"

    @classmethod
    def get_item_pk_name(cls):
        """Compose the URL parameter name for this model's primary key.

        Convention: `model_name_pk`, e.g., `sensor_pk` for the Sensor model.
        This is used in URL patterns and view kwargs.
        """
        return f"{cls._get_url_model_name()}_pk"

    def _get_url_kwargs(self):
        """Build URL kwargs including parent hierarchy.

        Returns dict like {'project_pk': 1, 'location_pk': 5}
        """
        kwargs = {f"{self._get_url_model_name()}_pk": self.pk}

        # Add parent kwargs if configured
        if self._url_parent_field and self._url_parent_param:
            parent = getattr(self, self._url_parent_field, None)
            if parent:
                kwargs[self._url_parent_param] = parent.pk
                # Recursively add grandparent kwargs if parent has URL mixin
                if hasattr(parent, '_get_url_kwargs'):
                    parent_kwargs = parent._get_url_kwargs()
                    # Remove the parent's own pk (we already have it)
                    parent_kwargs.pop(f"{parent._get_url_model_name()}_pk", None)
                    kwargs.update(parent_kwargs)

        return kwargs

    @classmethod
    def _get_base_url_kwargs(cls, parent=None):
        """Get base URL kwargs for list/add views (no object pk).

        Args:
            parent: Optional parent object for hierarchical URLs
        """
        kwargs = {}
        if parent and cls._url_parent_param:
            kwargs[cls._url_parent_param] = parent.pk
            # Recursively add grandparent kwargs
            if hasattr(parent, '_get_url_kwargs'):
                parent_kwargs = parent._get_url_kwargs()
                parent_kwargs.pop(f"{parent._get_url_model_name()}_pk", None)
                kwargs.update(parent_kwargs)
        return kwargs

    def _build_url(self, action, raise_on_error=True):
        """Build URL for a given action.
        
        Args:
            action: The URL action (detail, update, delete, list, history, overview)
            raise_on_error: If False, return None instead of raising NoReverseMatch
        """
        url_name = self._get_url_name(action)

        try:
            return reverse(url_name, kwargs=self._get_url_kwargs())
        except NoReverseMatch:
            if raise_on_error:
                raise
            return None

    def get_detail_url(self):
        """Return URL for detail view."""
        return self._build_url("detail")

    def get_update_url(self):
        """Return URL for update view."""
        return self._build_url("update")

    def get_delete_url(self):
        """Return URL for delete view."""
        return self._build_url("delete")

    def get_overview_url(self):
        """Return URL for overview view."""
        return self._build_url("overview")

    def get_history_url(self):
        """Return URL for history view, or None if not available."""
        # Only try to generate history URL if model has history
        if not hasattr(self, 'history'):
            return None
        return self._build_url("history", raise_on_error=False)

    @classmethod
    def get_list_url(cls, parent=None):
        """Return URL for list view.

        Args:
            parent: Parent object if URLs are hierarchical
        """
        app = cls._get_url_app_label()
        url_name = f"{app}:{cls._get_url_model_name_plural()}"
        kwargs = cls._get_base_url_kwargs(parent)
        return reverse(url_name, kwargs=kwargs)

    @classmethod
    def get_add_url(cls, parent=None):
        """Return URL for add/create view.

        Args:
            parent: Parent object if URLs are hierarchical
        """
        app = cls._get_url_app_label()
        model = cls._get_url_model_name()
        url_name = f"{app}:add-{model}"
        kwargs = cls._get_base_url_kwargs(parent)
        return reverse(url_name, kwargs=kwargs)


class ModelViewConfigMixin:
    """Configuration for how models appear in list and detail views.

    This mixin centralizes view configuration at the model level, reducing
    the need for context objects and view-level configuration.

    Class Attributes:
        _list_view_fields: dict mapping verbose names to field names for list display.
        _detail_view_fields: dict mapping verbose names to field names for detail display.
        _has_update: Whether the model supports update operations.
        _has_delete: Whether the model supports delete operations.
        _has_bulk_create: Whether the model supports bulk creation.
        _detail_type: How detail is displayed ('modal', 'page', 'popover', or None).
    """

    _list_view_fields: dict = None
    _detail_view_fields: dict = None
    _has_update: bool = True
    _has_delete: bool = True
    _has_bulk_create: bool = False
    _detail_type: str | None = None  # 'modal', 'page', 'popover', or None

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

    @property
    def has_history(self):
        """Check if this model has history tracking."""
        return hasattr(self, "history")


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