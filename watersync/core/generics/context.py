from dataclasses import dataclass


@dataclass
class ListConfig:
    """Configuration for list views.
    
    A simplified dataclass that holds all configuration needed by list templates.
    Values come from model class attributes and view computations.
    
    Attributes:
        add_url: Resolved URL to add a new object.
        list_url: Resolved URL for the list view.
        htmx_trigger: HTMX trigger action name (e.g., 'sensorChanged').
        columns: List of column names for table headers.
        title: Title for the list view (model's verbose_name_plural).
        explanation: Short description from model docstring.
        explanation_detail: Long description from model docstring.
        detail_type: How detail is displayed ('modal', 'page', 'popover', or None).
        has_bulk_create: Whether bulk creation is supported.
        has_update: Whether update is supported.
        has_delete: Whether delete is supported.
    """

    add_url: str
    list_url: str
    htmx_trigger: str
    columns: list
    title: str
    detail_type: str | None = None
    has_bulk_create: bool = False
    has_update: bool = True
    has_delete: bool = True
    explanation: str | None = None
    explanation_detail: str | None = None
