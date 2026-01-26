# Filters

WaterSync uses [django-filter](https://django-filter.readthedocs.io/) for queryset filtering in list views. This provides a declarative, reusable approach to filtering that integrates well with HTMX for dynamic updates.

## Architecture

The filtering system consists of three components:

1. **Base FilterSet classes** (`watersync/core/generics/filters.py`) - Reusable base classes
2. **App-specific filters** (`{app}/filters.py`) - Filter definitions per app
3. **FilterMixin** (`watersync/core/generics/mixins.py`) - View integration

## Base Classes

### ProjectScopedFilterSet

The primary base class for filters in WaterSync. It automatically limits filter choices to items within the current project.

```python
from watersync.core.generics.filters import ProjectScopedFilterSet

class SampleFilter(ProjectScopedFilterSet):
    class Meta:
        model = Sample
        fields = ['location', 'fieldwork']
```

**Features:**

- Accepts a `project` parameter to scope filter choices
- Automatically limits `location` and `fieldwork` dropdowns to the current project
- Inherits from `django_filters.FilterSet`

### TimeseriesFilterSet

Extended base class for timeseries data with built-in date range filters.

```python
from watersync.core.generics.filters import TimeseriesFilterSet

class SensorRecordFilter(TimeseriesFilterSet):
    class Meta:
        model = SensorRecord
        fields = ['deployment']
```

**Includes:**

- `date_from` - Filter records from this date
- `date_to` - Filter records until this date

## Creating a New Filter

### Step 1: Create the filter class

Create a `filters.py` file in your app:

```python
# myapp/filters.py
import django_filters
from watersync.core.generics.filters import ProjectScopedFilterSet
from myapp.models import MyModel


class MyModelFilter(ProjectScopedFilterSet):
    """Filter for MyModel.
    
    Supports filtering by location and date range.
    """
    
    # Custom date filters (if needed)
    date_from = django_filters.DateFilter(
        field_name='created_at',  # or 'fieldwork__date' for related fields
        lookup_expr='gte',
        label='From',
    )
    date_to = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='To',
    )
    
    class Meta:
        model = MyModel
        fields = ['location', 'fieldwork']  # Model fields to filter by
```

### Step 2: Add FilterMixin to your view

```python
# myapp/views.py
from watersync.core.generics.mixins import FilterMixin
from watersync.core.generics.views import WatersyncListView
from myapp.filters import MyModelFilter
from myapp.models import MyModel


class MyModelListView(FilterMixin, WatersyncListView):
    model = MyModel
    filterset_class = MyModelFilter
    
    def get_base_queryset(self):
        """Override this instead of get_queryset when using FilterMixin."""
        project = self.get_project()
        return MyModel.objects.filter(
            location__in=project.locations.all()
        )
```

!!! note "Important"
    When using `FilterMixin`, override `get_base_queryset()` instead of `get_queryset()`. The mixin applies filters on top of the base queryset.

### Step 3: Add filter form to template (optional)

The filter form is available in templates via `{{ filter.form }}`:

```html
<form hx-get="{{ request.path }}" hx-target="#table-container" hx-swap="innerHTML">
    {{ filter.form }}
    <button type="submit" class="btn btn-primary btn-sm">Filter</button>
</form>
```

## Filter Types

django-filter provides many filter types:

| Filter Type | Use Case | Example |
|-------------|----------|---------|
| `ModelChoiceFilter` | Foreign key fields | `fields = ['location']` |
| `CharFilter` | Text fields | `fields = ['name']` |
| `DateFilter` | Date fields | `date_from = DateFilter(lookup_expr='gte')` |
| `DateTimeFilter` | DateTime fields | `timestamp_from = DateTimeFilter(...)` |
| `NumberFilter` | Numeric fields | `value_min = NumberFilter(lookup_expr='gte')` |
| `ChoiceFilter` | Choice fields | `status = ChoiceFilter(choices=STATUS_CHOICES)` |

## Implemented Filters

### Groundwater App

**GWLMeasurementFilter** (`watersync/groundwater/filters.py`)

| Field | Type | Description |
|-------|------|-------------|
| `location` | ModelChoice | Filter by location |
| `fieldwork` | ModelChoice | Filter by fieldwork event |
| `date_from` | Date | Measurements from this date |
| `date_to` | Date | Measurements until this date |

### Water Quality App

**SampleFilter** (`watersync/waterquality/filters.py`)

| Field | Type | Description |
|-------|------|-------------|
| `location` | ModelChoice | Filter by location |
| `fieldwork` | ModelChoice | Filter by fieldwork event |
| `date_from` | Date | Samples from this date |
| `date_to` | Date | Samples until this date |

**MeasurementFilter** (`watersync/waterquality/filters.py`)

| Field | Type | Description |
|-------|------|-------------|
| `sample` | ModelChoice | Filter by sample |
| `parameter` | Char | Filter by parameter name |

### Sensor App

**DeploymentFilter** (`watersync/sensor/filters.py`)

| Field | Type | Description |
|-------|------|-------------|
| `location` | ModelChoice | Filter by location |
| `sensor` | ModelChoice | Filter by sensor |
| `deployed_from` | Date | Deployments from this date |
| `deployed_to` | Date | Deployments until this date |

**SensorRecordFilter** (`watersync/sensor/filters.py`)

| Field | Type | Description |
|-------|------|-------------|
| `deployment` | ModelChoice | Filter by deployment |
| `timestamp_from` | DateTime | Records from this timestamp |
| `timestamp_to` | DateTime | Records until this timestamp |

## HTMX Integration

Filters work seamlessly with HTMX for dynamic table updates without page reload:

1. Filter form submits via `hx-get`
2. View applies filters to queryset
3. Table partial is returned and swapped

The `FilterMixin` automatically passes the filter context to templates, and `WatersyncListView` handles HTMX partial responses.

## Best Practices

1. **Always inherit from ProjectScopedFilterSet** - Ensures filter choices are scoped to the current project
2. **Use `get_base_queryset()`** - Override this method, not `get_queryset()`, when using FilterMixin
3. **Add date range filters for timeseries** - Users commonly need to filter by date
4. **Keep filter fields minimal** - Only expose filters that users actually need
5. **Use meaningful labels** - Set `label` parameter for clarity in the UI
