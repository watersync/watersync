# WaterSync - Repository Instructions for GitHub Copilot

## Project Overview

WaterSync is a Django-based hydrological data management platform for tracking water quality, groundwater levels, and sensor data. Built with Django 5.0, PostgreSQL/PostGIS, and a modern HTMX-based frontend.

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework, Celery
- **Database**: PostgreSQL with PostGIS extension
- **Frontend**: HTMX, Bootstrap 5, Crispy Forms, django-cotton components
- **Task Queue**: Celery with Redis
- **Package Manager**: uv (via Docker)
- **Containerization**: Docker Compose

## Project Structure

```
watersync/                  # Main application package
├── core/                   # Core models (Project, Location, Fieldwork)
│   ├── generics/           # Reusable base views, mixins, forms
│   └── ...
├── groundwater/            # Groundwater level tracking
├── sensor/                 # Sensor data management
├── waterquality/           # Water quality samples and analyses
├── users/                  # User management
├── utils/                  # Shared utilities
└── _templates/             # Global templates
config/                     # Django settings and configuration
tests/                      # Project-level tests
```

## Coding Conventions

### Django Models
0. What still does not exist but should: A set of base model mixins and abstract models to encapsulate common functionality (e.g., timestamped models, soft delete, user tracking) - similar to the generic views and mixins already in place.

1. **Inherit from standard mixins**: Models should inherit from `ModelViewConfigMixin` and `ModelURLMixin` for consistent URL generation:
   ```python
   class MyModel(models.Model, ModelViewConfigMixin, ModelURLMixin, SetupSimpleHistory):
   ```

2. **Model configuration attributes**:
   - `_url_parent_field`: Parent relationship field name (e.g., `"project"`)
   - `_url_parent_param`: URL parameter name (e.g., `"project_pk"`)
   - `_list_view_fields`: Dict of column headers to field names for list views
   - `_detail_view_fields`: Dict for detail view display
   - `_detail_type`: Either `"page"` or `"offcanvas"` for detail display style
   - `_has_bulk_create`, `_has_update`, `_has_delete`: Feature flags

3. **Use django-simple-history** for model history tracking with `HistoricalRecords()`

4. **GeoDjango fields**: Use `django.contrib.gis.db.models` for spatial data (PointField, PolygonField with `srid=4326`)

### Views
0. Overarching principle: Leverage generic views and mixins from. We can adapt them, extend or create new ones as needed to maintain consistency and reduce boilerplate.

1. **Use generic base views** from `watersync.core.generics.views`:
   - `WatersyncListView` - For list views with CSV export, HTMX support
   - `WatersyncCreateView` - For create views with HTMX form handling
   - `WatersyncUpdateView` - For update views
   - `WatersyncDeleteView` - For delete views
   - `WatersyncDetailView` - For detail views

2. **View mixins** (in `watersync.core.generics`):
   - `StandardURLMixin` (mixins.py): Provides URL helper methods
   - `HTMXFormMixin` (views.py): Handles HTMX form submissions and parent object prefilling
   - `ExportCsvMixin` (mixins.py): Adds CSV export capability

3. **HTMX support**: Views should work with both full page loads and HTMX partial requests. The context processor handles `base_template` selection.

### URL Patterns

Follow consistent naming convention:
- List: `app:modelnames` (plural, e.g., `core:locations`)
- Add: `app:add-modelname` (e.g., `core:add-location`)
- Detail: `app:detail-modelname`
- Update: `app:update-modelname`
- Delete: `app:delete-modelname`
- History: `app:list-historicalmodelname`

URL parameters use `_pk` suffix: `project_pk`, `location_pk`, `fieldwork_pk`

### Forms

1. **Use Crispy Forms** with Bootstrap 5: `crispy_bootstrap5`
2. **Date/Time pickers**: Use `bootstrap_datepicker_plus.widgets.DatePickerInput` and `TimePickerInput`. Tempus Dominus JS/CSS is loaded in base.html.
3. **Dynamic detail forms**: Use `FormWithDetailMixin` for forms with type-dependent detail sections
4. **Form validation**: Include `FormWithHistory` mixin for history change reason support

### Templates
0. Templates should also have some layer of abstraction. At a point I would like to start abstracting common patterns into reusable components either via django-cotton.

1. **Template hierarchy**:
   - `base.html` - Top-level layout
   - `layouts/` - Dashboard layouts with navbars/sidebars
   - App-specific templates in `_templates/{app}/`
   - Partials for HTMX in subdirectories

2. **Use django-cotton** for reusable components: `{% load cotton %}` and `<c-component />`

3. **HTMX patterns**:
   - Use `hx-get`, `hx-post`, `hx-target`, `hx-swap`
   - Tables use `hx-trigger="revealed"` for lazy loading
   - Forms return partials on HTMX requests

4. **List views** use `list_page.html` → includes `list.html` → includes `table.html`

### Testing

1. **Use pytest** with pytest-django
2. **Factories**: Use factory_boy with `DjangoModelFactory`
   ```python
   class MyModelFactory(DjangoModelFactory):
       class Meta:
           model = MyModel
   ```
3. **Fixtures** in `conftest.py` at app level
4. Run tests: `make test` or `pytest`

### Code Quality

1. **Linting**: Ruff with Django-specific rules
2. **Formatting**: Ruff formatter (88 char line length)
3. **Template linting**: djLint
4. **Type checking**: mypy with django-stubs
5. **Pre-commit hooks** configured

Run checks:
```bash
make lint        # Run all linters
make format      # Format code
make typecheck   # Run mypy
```

## Development Workflow

### Docker Commands (via Makefile)
All interactions with Docker are done through the Makefile. If a command is missing, add it there.

```bash
make up              # Start all services
make down            # Stop services
make shell           # Bash shell in Django container
make django-shell    # Django shell_plus
make test            # Run tests
make migrate         # Run migrations
make makemigrations  # Create migrations
make logs            # Follow all logs
```

### Database

- PostgreSQL with PostGIS
- Migrations in each app's `migrations/` directory
- Use `make dbshell` for direct database access

### Adding New Features

1. **New model**: Add to appropriate app, inherit mixins, add `_*` configuration attributes
2. **New views**: Extend generic views from `core.generics.views`
3. **New URLs**: Follow naming convention, add to app's `urls.py`
4. **New templates**: Place in `_templates/{app}/`, use partials for HTMX

## API

- REST API uses Django REST Framework - we will implement it later
- API routes in `config/api_router.py`
- API documentation via drf-spectacular at `/api/schema/`

## Key Patterns

### Parent-Child Relationships

Models use FK relationships with URL patterns reflecting hierarchy:
```
/projects/{project_pk}/locations/{location_pk}/
```

Views use `get_base_url_kwargs()` to build URLs with parent PKs.

### HTMX Form Handling

Forms return:
- Full page on non-HTMX requests
- Partial template on HTMX requests
- JSON response with redirect on success

### History Tracking

Use `simple_history` for audit trail:
```python
history = HistoricalRecords()
```

Access via `model.history.all()` or history list views.

## Environment
- There is no local environment file in the repo. the environment is present and active inside the django docker container.
- Settings in `config/settings/` (base, local, production, test)
- Environment variables via `django-environ`
- Docker Compose for local development

## Documentation

- MkDocs with Material theme
- Docs in `docs/docs/`
- Build: `make docs`
