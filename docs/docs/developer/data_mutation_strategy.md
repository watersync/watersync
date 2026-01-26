# Data Mutation Strategy

## Overview

WaterSync implements a two-tier data mutation strategy that distinguishes between **metadata models** and **record models**. This approach aligns with scientific data collection best practices, ensuring data integrity while allowing necessary corrections to contextual information.

## Philosophy

In environmental monitoring and scientific data collection:

1. **Measurements are immutable** - Once recorded, raw data should not be modified. If data needs correction, the original should be deleted and new data uploaded.
2. **Metadata is mutable** - Contextual information (who, where, when, how) can be corrected as errors are discovered.
3. **All changes must be tracked** - History tracking provides an audit trail for accountability and reproducibility.

## Model Classification

### Metadata Models (Mutable)

These models describe the context of data collection. They support full CRUD operations with history tracking:

| Model | App | Description |
|-------|-----|-------------|
| `Project` | core | Research projects that organize all work |
| `Location` | core | Sampling/monitoring locations |
| `Fieldwork` | core | Field campaign records |
| `Sensor` | sensor | Sensor devices and their specifications |
| `Deployment` | sensor | Sensor deployment periods at locations |
| `Sample` | waterquality | Physical samples collected |
| `Protocol` | waterquality | Analysis protocols and methods |

**Operations allowed:**
- ✅ Create
- ✅ Read (list, detail)
- ✅ Update
- ✅ Delete (with cascading considerations)
- ✅ History tracking via `django-simple-history`

### Record Models (Immutable)

These models store actual measured values. They only support create and delete:

| Model | App | Description |
|-------|-----|-------------|
| `SensorRecord` | sensor | Automated sensor measurements |
| `Measurement` | waterquality | Lab/field analysis results |
| `GWLManualMeasurement` | groundwater | Manual groundwater level readings |

**Operations allowed:**
- ✅ Create (including bulk create)
- ✅ Read (list, detail)
- ❌ **Update not allowed**
- ✅ Delete (for data correction workflows)

## Correction Workflow

When data needs to be corrected:

1. **Identify incorrect data** - Use filters and search to find problematic records
2. **Delete incorrect records** - Can be individual or via cascade (e.g., delete deployment deletes all its records)
3. **Upload corrected data** - Use bulk create to upload the corrected dataset

This maintains a clean audit trail: the original data existed, was deleted, and replaced with corrected data.

## Technical Implementation

### History Tracking

Metadata models include `HistoricalRecords()` from django-simple-history:

```python
from simple_history.models import HistoricalRecords

class Sample(models.Model):
    # ... fields ...
    history = HistoricalRecords()
```

History can be viewed at:
- `app:list-historicalmodelname` (e.g., `waterquality:list-historicalsample`)

### URL Patterns

Record models exclude update URLs:

```python
# Records are immutable - update not allowed
sensorrecord_urlpatterns = [
    path("", sensorrecord_list_view, name="sensorrecords"),
    path("add/", sensorrecord_create_view, name="add-sensorrecord"),
    # No update URL
    path("<int:pk>/delete/", sensorrecord_delete_view, name="delete-sensorrecord"),
]
```

### View Configuration

Record models only have create, list, detail, and delete views:

```python
# ✅ Correct for record models
class MeasurementCreateView(WatersyncCreateView):
    model = Measurement

class MeasurementListView(WatersyncListView):
    model = Measurement

class MeasurementDeleteView(WatersyncDeleteView):
    model = Measurement

# ❌ No UpdateView for record models
```

## Soft Delete

Record models implement soft delete via `SoftDeleteMixin` to preserve data for audit trails while appearing deleted to users. This is built into the `TimeSeriesModel` abstract base.

### Implementation

```python
# watersync/core/generics/models.py
class SoftDeleteMixin(models.Model):
    """Mixin for soft delete functionality on record models."""

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
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
```

### TimeSeriesModel

Record models inherit from `TimeSeriesModel` which includes both `SoftDeleteMixin` and creation tracking:

```python
class TimeSeriesModel(SoftDeleteMixin, models.Model):
    """Abstract base class for timeseries measurement models."""
    
    value = models.DecimalField(max_digits=10, decimal_places=3)
    
    # Record creation tracking
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
    
    # Inherited from SoftDeleteMixin:
    # is_deleted, deleted_at, deleted_by

    _has_update = False  # Records are immutable

    objects = TimeSeriesManager()  # Excludes deleted by default

    class Meta:
        abstract = True
```

### Manager Behavior

The `TimeSeriesManager` automatically excludes soft-deleted records:

```python
# Default - only non-deleted records
SensorRecord.objects.all()

# Include deleted records
SensorRecord.objects.all_with_deleted()

# Only deleted records  
SensorRecord.objects.deleted_only()
```

### Measurement Model

The `Measurement` model (not a timeseries) uses `SoftDeleteMixin` directly with `SoftDeleteLocationScopedManager`:

```python
class Measurement(SoftDeleteMixin, models.Model):
    # ...fields...
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(...)
    
    objects = SoftDeleteLocationScopedManager()
    _has_update = False
```

## Summary

| Aspect | Metadata Models | Record Models |
|--------|-----------------|---------------|
| Can be created | ✅ | ✅ |
| Can be updated | ✅ | ❌ |
| Can be deleted | ✅ (hard delete) | ✅ (soft delete) |
| History tracked | ✅ (django-simple-history) | ✅ (created_at/by, deleted_at/by) |
| Correction method | Edit in place | Delete & recreate |
| Examples | Project, Location, Sample | Measurement, SensorRecord |
| Base class | `SetupSimpleHistory` | `TimeSeriesModel` / `SoftDeleteMixin` |
