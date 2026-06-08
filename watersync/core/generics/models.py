from abc import ABC

from django.conf import settings
from django.db import models
from django.utils.timezone import now

from watersync.core.generics.managers import TimeSeriesManager


class SetupSimpleHistory:
    """Provides a simple history setup for models.

    All models with history have update functionality. 
    You still need to add the history field to the model:

        >>> history = HistoricalRecords()
    """
    _has_update = True
    __history_date = None

    @property
    def _history_date(self):
        return self.__history_date or now()

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    def get_history_with_diffs(self):
        """Return history records with computed diffs between consecutive records.
        
        Returns:
            List of dicts with 'record', 'prev_record', and 'changes' keys.
            'changes' is None for the oldest record (no previous to compare).
        """
        if not hasattr(self, 'history'):
            return []
        
        history = list(self.history.all().order_by("-history_date"))
        result = []

        for i, record in enumerate(history):
            prev_record = history[i + 1] if i + 1 < len(history) else None
            changes = record.diff_against(prev_record).changes if prev_record else None
            result.append({
                'record': record,
                'prev_record': prev_record,
                'changes': changes,
            })

        return result


class SoftDeleteMixin(models.Model):
    """Mixin for soft delete functionality on record models.

    Instead of permanently deleting records, marks them as deleted
    while preserving the data for audit trails and potential recovery.

    Soft-deleted records are excluded from default querysets via manager.
    Use `.all_with_deleted()` or `.deleted_only()` for including them.
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """Mark this record as deleted without removing from database."""
        self.is_deleted = True
        self.deleted_at = now()
        self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])


class TimeSeriesModel(SoftDeleteMixin, models.Model):
    """Abstract base class for timeseries measurement models.

    Provides common structure for models that store time-indexed measurements:
    SensorRecord, GWLManualMeasurement, and Measurement.

    Immutable records: These models do not support update operations.
    Use delete and recreate workflow for corrections.

    Standardized fields:
        - value: DecimalField - The primary measured value
        - created_at: DateTimeField - When the record was created
        - created_by: ForeignKey - User who created the record
        - is_deleted, deleted_at, deleted_by: Soft delete fields

    Configuration attributes:
        - timestamp_field: str - Name of the field containing the timestamp
        - location_field: str - Path to the location (e.g., 'location' or 'deployment__location')

    Manager methods (via TimeSeriesManager):
        - date_range(): Get (min, max) timestamps
        - statistics(): Get min, max, avg, count for values
        - for_plotting(): Get (timestamp, value) tuples for charting

    All methods are chainable after filter():
        stats = Model.objects.filter(location=loc).statistics()
        min_date, max_date = Model.objects.filter(x=y).date_range()
    """

    # The primary measured value - all timeseries models have this
    value = models.DecimalField(max_digits=10, decimal_places=3)

    # Record creation tracking
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )

    # Records are immutable - no update allowed
    _has_update = False

    # Use the custom manager
    objects = TimeSeriesManager()

    class Meta:
        abstract = True


class WatersyncBaseModel(ABC):
    """Abstract base class enforcing implementation of core methods and properties.
    
    # Docstring structure
        Docstrings of models are used for explanations in the UI. They are
        parsed using the parse_docstring package to extract short and long descriptions.
        This means, that each model should have a docstring structured as follows:

        >>> ModelName(models.Model):
        ...     \"""Short description of the model.
        ...
        ...     Long description of the model that can span multiple lines.
        ...     This description will be shown in detail views and other places
        ...     where more context is needed.
        ...     \"""

    # Inheritance
        The models in Watersync should inherit functionality from either the SetupSimpleHistory
        or the TimeSeriesModel abstract base classes, depending on the level of audit trail
        and history tracking required.

    # Class attributes to define
        _list_view_fields: Dict defining fields for list views rendered in tables.
        _detail_view_fields: Dict defining what will be shown in detail views.
        _csv_columns: Dict defining columns for CSV export.
        _count_fields: List of items from related fields to count for overview pages.
    """
    _list_view_fields = {}
    _detail_view_fields = {}
    _csv_columns = {}
    _count_fields = []