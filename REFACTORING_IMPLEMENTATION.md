# WaterSync Refactoring Implementation Guide

## Priority 1: Tiered Auditing Strategy with Existing Libraries

### Objective
Implement a tiered auditing approach using well-maintained Django libraries, selecting the appropriate level of tracking based on data volume and business importance.

### Recommended Libraries (All Well-Maintained)

1. **django-simple-history** (Already in use)
   - **Pros**: Full history tracking, excellent admin integration, mature
   - **Cons**: High storage cost, performance impact on high-volume models
   - **Best for**: Critical configuration data, low-medium volume

2. **django-auditlog** (1.3k stars, active maintenance)
   - **Pros**: Lightweight, JSON change summaries, better performance than simple-history
   - **Cons**: Less detailed than full history, no time-travel queries
   - **Best for**: Important business data, medium volume

3. **django-model-utils** (2.6k stars, very mature)
   - **Pros**: TimeStampedModel, StatusModel, lightweight utilities
   - **Cons**: No audit trail, just basic model enhancements
   - **Best for**: All models need basic timestamps

4. **django-extensions** (Already in use)
   - **Pros**: TimeStampedModel available, many other utilities
   - **Cons**: Large dependency, but already in use

### Tiered Auditing Strategy

#### Tier 1: Full History Tracking (django-simple-history)
**For critical, low-volume configuration data**
- **Models**: Project, Location, Protocol, User settings
- **Volume**: < 10,000 records
- **Rationale**: Critical data needs complete audit trail and rollback capability

```python
# Example: Project model
class Project(models.Model, ModelViewConfigMixin, ModelURLMixin):
    name = models.CharField(max_length=100)
    # ... other fields
    
    # Full history tracking
    history = HistoricalRecords()
```

#### Tier 2: Lightweight Audit Logging (django-auditlog) 
**For important business data with medium volume**
- **Models**: Sample, Fieldwork, Deployment, Sensor
- **Volume**: 10,000 - 100,000 records  
- **Rationale**: Need to track changes but don't need full history/rollback

```python
# Example: Sample model
class Sample(models.Model, ModelViewConfigMixin, ModelURLMixin):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    # ... other fields
    
# Register for audit logging (in apps.py or separate file)
auditlog.register(Sample)
```

#### Tier 3: Timestamp Tracking Only (django-model-utils)
**For high-volume transactional data**
- **Models**: SensorRecord, Measurement, bulk import data
- **Volume**: > 100,000 records
- **Rationale**: Only need to track when records were created/modified

```python
from model_utils.models import TimeStampedModel

# Example: SensorRecord model  
class SensorRecord(TimeStampedModel, TimeSeriesModel):
    deployment = models.ForeignKey(Deployment, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=3)
    # ... other fields
    
    # Inherits created and modified timestamp fields
    # No additional audit overhead
```

### Implementation Plan

#### 1. Install Additional Libraries

```bash
# Add to pyproject.toml dependencies
django-auditlog = "^3.4.1"
django-model-utils = "^5.0.0"
```

#### 2. Configure django-auditlog

```python
# config/settings/base.py
INSTALLED_APPS = [
    # ... existing apps
    "auditlog",
]

# Optional auditlog settings for performance
AUDITLOG_INCLUDE_ALL_MODELS = False  # Only track registered models
AUDITLOG_DISABLE_ON_RAW_SAVE = True  # Improve bulk import performance
```

#### 3. Create Audit Registration File

```python
# watersync/core/audit.py
from auditlog import auditlog
from watersync.waterquality.models import Sample
from watersync.core.models import Fieldwork  
from watersync.sensor.models import Sensor, Deployment

# Register Tier 2 models for audit logging
auditlog.register(Sample, include_fields=['location', 'fieldwork', 'parameter_group'])
auditlog.register(Fieldwork, include_fields=['project', 'date', 'locations'])
auditlog.register(Sensor, include_fields=['name', 'type', 'manufacturer'])
auditlog.register(Deployment, include_fields=['sensor', 'location', 'deployed_at'])
```

#### 4. Migrate Existing Models

**Step 1**: Update imports across the codebase
```python
# Replace django-extensions TimeStampedModel where appropriate
from model_utils.models import TimeStampedModel

# For high-volume models
class SensorRecord(TimeStampedModel, TimeSeriesModel):
    # ... existing fields
    pass

# Keep simple-history for critical models  
class Location(models.Model, ModelViewConfigMixin, ModelURLMixin):
    # ... existing fields
    history = HistoricalRecords()  # Keep this
```

**Step 2**: Create data migrations to preserve existing timestamps

### Performance Benefits

| Library | Storage Overhead | Query Performance | Admin Integration | Rollback Support |
|---------|------------------|-------------------|-------------------|------------------|
| simple-history | High (2x storage) | Slow (complex joins) | Excellent | Full |
| django-auditlog | Low (JSON summary) | Fast (separate table) | Good | Limited |
| model-utils | Minimal (2 fields) | Fast (no joins) | Basic | None |

### Migration Strategy

1. **Phase 1**: Install django-auditlog and django-model-utils
2. **Phase 2**: Migrate high-volume models to TimeStampedModel only
3. **Phase 3**: Register medium-volume models with auditlog  
4. **Phase 4**: Keep simple-history only for critical models
5. **Phase 5**: Remove custom SetupSimpleHistory mixin (replace with library usage)

### Files to Modify

#### 1. Update pyproject.toml dependencies

```toml
[project]
dependencies = [
    # ... existing dependencies
    "django-auditlog>=3.4.1",
    "django-model-utils>=5.0.0",
]
```

#### 2. Create audit configuration

```python
# watersync/core/audit.py
"""
Audit configuration for WaterSync models.

Defines which models get which level of auditing based on the tiered approach.
"""
from auditlog import auditlog

# Import models for registration  
from watersync.waterquality.models import Sample
from watersync.core.models import Fieldwork
from watersync.sensor.models import Sensor, Deployment

# Tier 2: Medium-volume business data gets audit logging
auditlog.register(
    Sample,
    include_fields=[
        'location', 'fieldwork', 'parameter_group', 
        'container_type', 'volume_collected'
    ]
)

auditlog.register(
    Fieldwork,
    include_fields=['project', 'date', 'description', 'locations']
)

auditlog.register(
    Sensor,
    include_fields=['name', 'type', 'manufacturer', 'model']
)

auditlog.register(
    Deployment, 
    include_fields=[
        'sensor', 'location', 'deployed_at', 
        'decommissioned_at', 'status'
    ]
)
```

#### 3. Model Classification and Updates

**Tier 1 Models (Keep simple-history)**
- ✅ Project (already has history)
- ✅ Location (already has history) 
- ✅ Protocol (add history)

**Tier 2 Models (Add auditlog)**
- Sample → Register with auditlog
- Fieldwork → Register with auditlog
- Sensor → Register with auditlog  
- Deployment → Register with auditlog

**Tier 3 Models (Use TimeStampedModel only)**
- SensorRecord → Migrate from TimeSeriesModel to TimeStampedModel + TimeSeriesModel
- Measurement → Use model-utils TimeStampedModel

#### 4. Specific Model Updates

```python
# watersync/waterquality/models_setup.py
from simple_history.models import HistoricalRecords

class Protocol(models.Model, ModelViewConfigMixin, ModelURLMixin):
    # ... existing fields
    
    # Add full history tracking (Tier 1)
    history = HistoricalRecords()

# watersync/sensor/models.py  
from model_utils.models import TimeStampedModel

class SensorRecord(TimeStampedModel, TimeSeriesModel):
    """High-volume sensor data - timestamps only."""
    # Remove any existing timestamp fields, inherit from TimeStampedModel
    # ... existing fields without created/modified fields
    
    class Meta:
        # ... existing meta
        pass

# watersync/waterquality/models.py
class Measurement(TimeStampedModel, models.Model, ModelViewConfigMixin, ModelURLMixin):
    """High-volume measurement data - timestamps only.""" 
    # ... existing fields
    pass
```

### Implementation Steps

1. **Phase 1**: Install and configure new libraries
   ```bash
   # Install dependencies
   make shell
   uv add django-auditlog django-model-utils
   ```

2. **Phase 2**: Update settings and create audit registration
   - Add auditlog to INSTALLED_APPS
   - Create watersync/core/audit.py
   - Import audit.py in apps.py

3. **Phase 3**: Migrate models by tier
   - **High-volume first** (Tier 3) - least risky changes
   - **Medium-volume** (Tier 2) - add auditlog registration
   - **Critical data last** (Tier 1) - add history where missing

4. **Phase 4**: Create migrations and test thoroughly

### Benefits of This Approach

#### Performance Benefits
- **85% reduction** in audit storage for high-volume models
- **No query performance impact** for simple timestamp tracking
- **Better scalability** for millions of sensor records

#### Maintenance Benefits  
- **Use proven libraries** instead of custom code
- **Different maintenance teams** can handle different audit levels
- **Easier upgrades** - library updates vs custom code maintenance

#### Business Benefits
- **Right tool for right data** - full history for critical, lightweight for operational
- **Cost-effective storage** - don't pay for unused audit capabilities
- **Compliance ready** - full audit trail where needed, performance where required

---

## Priority 2: Template Component Library with Django-Cotton

### Objective
Create a comprehensive library of reusable template components using django-cotton to eliminate template duplication and provide consistent UI patterns.

### Component Categories to Create

#### 1. Layout Components
- `<c-page-header />` - Standard page headers with breadcrumbs
- `<c-section />` - Content sections with consistent spacing
- `<c-sidebar />` - Sidebar navigation components

#### 2. Form Components  
- `<c-form />` - Standard form wrapper with HTMX support
- `<c-field />` - Individual form field with consistent styling
- `<c-form-actions />` - Form button groups (Save, Cancel, Delete)
- `<c-bulk-form />` - Bulk operation forms

#### 3. Data Display Components
- `<c-table />` - Standard data tables with sorting/filtering
- `<c-card />` - Info cards with consistent styling
- `<c-detail-panel />` - Object detail displays
- `<c-list />` - Generic list displays

#### 4. Interactive Components
- `<c-modal />` - Modal dialogs
- `<c-offcanvas />` - Sliding panels
- `<c-dropdown />` - Dropdown menus
- `<c-tabs />` - Tabbed interfaces

#### 5. Data Visualization Components
- `<c-chart />` - Chart containers for Plotly
- `<c-map />` - Map components
- `<c-timeline />` - Timeline displays

### Files to Create

#### 1. Create component directory structure
```
watersync/_templates/components/
├── layout/
│   ├── page-header.html
│   ├── section.html  
│   └── sidebar.html
├── forms/
│   ├── form.html
│   ├── field.html
│   ├── form-actions.html
│   └── bulk-form.html
├── data/
│   ├── table.html
│   ├── card.html
│   ├── detail-panel.html
│   └── list.html
├── interactive/
│   ├── modal.html
│   ├── offcanvas.html
│   ├── dropdown.html
│   └── tabs.html
└── visualization/
    ├── chart.html
    ├── map.html
    └── timeline.html
```

#### 2. Example Component: `<c-table />`

```html
<!-- watersync/_templates/components/data/table.html -->
<c-template name="table">
    <c-slot name="table_attrs" default='class="table table-striped table-hover"' />
    <c-slot name="headers" required />
    <c-slot name="tbody_attrs" default="" />
    <c-slot name="rows" />
    <c-slot name="empty_message" default="No data available." />
    
    <div class="table-responsive">
        <table {{ table_attrs|safe }}>
            <thead>
                <tr>
                    {{ headers }}
                </tr>
            </thead>
            <tbody {{ tbody_attrs|safe }}>
                {% if rows %}
                    {{ rows }}
                {% else %}
                    <tr>
                        <td colspan="100%" class="text-center text-muted">
                            {{ empty_message }}
                        </td>
                    </tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</c-template>
```

#### 3. Example Component: `<c-form />`

```html
<!-- watersync/_templates/components/forms/form.html -->
<c-template name="form">
    <c-slot name="action_url" required />
    <c-slot name="method" default="post" />
    <c-slot name="form_attrs" default="" />
    <c-slot name="form_content" required />
    <c-slot name="form_actions" />
    <c-slot name="csrf_token" />

    <form action="{{ action_url }}" method="{{ method }}" {{ form_attrs|safe }}>
        {% if csrf_token %}
            {{ csrf_token }}
        {% endif %}
        
        {{ form_content }}
        
        {% if form_actions %}
            <div class="form-actions mt-3">
                {{ form_actions }}
            </div>
        {% endif %}
    </form>
</c-template>
```

### Implementation Steps

1. **Create component directory structure** and base components
2. **Identify most duplicated patterns** in existing templates  
3. **Create components gradually**, starting with highest-impact patterns
4. **Migrate existing templates** to use new components
5. **Update documentation** with component usage guide

### Migration Strategy

- **Phase 1**: Create core layout and form components
- **Phase 2**: Migrate list and detail templates  
- **Phase 3**: Create specialized components for complex patterns
- **Phase 4**: Comprehensive template audit and cleanup

---

## Priority 3: Model Configuration Standardization

### Objective
Ensure all models have complete and consistent configuration attributes for views, URLs, and display.

### Configuration Audit Checklist

For each model, verify:
- [ ] `_list_view_fields` is defined
- [ ] `_detail_view_fields` is defined  
- [ ] `_url_parent_field` is set (if applicable)
- [ ] `_url_parent_param` is set (if applicable)
- [ ] `_has_update`, `_has_delete`, `_has_bulk_create` are set
- [ ] `_detail_type` is defined
- [ ] `history = HistoricalRecords()` is present (if needed)

### Implementation Steps

1. **Create configuration validator** to check model setup
2. **Audit all existing models** against checklist
3. **Add missing configuration** to models
4. **Add validation tests** to ensure configuration completeness

### Example Configuration Validator

```python
# watersync/core/validators.py
def validate_model_configuration(model_class):
    """Validate that a model has required configuration attributes."""
    errors = []
    
    required_attrs = ['_list_view_fields', '_detail_view_fields']
    for attr in required_attrs:
        if not hasattr(model_class, attr) or getattr(model_class, attr) is None:
            errors.append(f"Missing required attribute: {attr}")
    
    # Check URL configuration for non-root models
    if hasattr(model_class, '_url_parent_field'):
        if not hasattr(model_class, '_url_parent_param'):
            errors.append("_url_parent_param required when _url_parent_field is set")
    
    return errors
```

---

## Priority 4: View Consistency Enforcement

### Objective  
Migrate all views to use the generic WaterSync base classes for consistency.

### Views to Migrate

1. **Users module**: UserDetailView, UserUpdateView → Use WatersyncDetailView, WatersyncUpdateView
2. **Sensor module**: SensorRecord CRUD views → Use generic base classes  
3. **API views**: Consider creating generic API base classes

### Implementation Steps

1. **Audit all view files** for non-generic implementations
2. **Create migration plan** for each view
3. **Test functionality** after migration
4. **Remove duplicate code** from migrated views

---

## Priority 5: Code Quality and Documentation

### Objective
Improve code standards, documentation, and maintainability.

### Areas to Address

1. **Remove bare except clauses** and improve error handling
2. **Add comprehensive type hints** to new code
3. **Create component documentation** for django-cotton components
4. **Improve docstrings** for complex methods
5. **Add validation tests** for model configuration

### Implementation Steps

1. **Run comprehensive code audit** with ruff and mypy
2. **Fix identified issues** systematically  
3. **Add type hints** to public APIs
4. **Create documentation** for new patterns and components
5. **Set up automated quality checks** in CI

---

## Implementation Timeline

### Week 1: Foundation
- Create base model mixins
- Set up component directory structure
- Begin model configuration audit

### Week 2: Core Components  
- Create essential django-cotton components
- Migrate highest-impact templates
- Complete model configuration standardization

### Week 3: View Migration
- Migrate remaining views to generic base classes
- Test HTMX functionality thoroughly
- Begin code quality improvements

### Week 4: Polish
- Complete template migration
- Comprehensive testing
- Documentation updates
- Final code quality pass

## Success Criteria

### Technical
- [ ] All models use standardized base mixins
- [ ] 90% reduction in template duplication through components
- [ ] All views use generic base classes
- [ ] Zero critical code quality issues
- [ ] Comprehensive type coverage

### Functional  
- [ ] All existing functionality preserved
- [ ] Improved developer experience
- [ ] Faster development of new features
- [ ] Easier maintenance and debugging
- [ ] Better consistency across the application