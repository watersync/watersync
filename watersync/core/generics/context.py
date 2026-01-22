from dataclasses import dataclass


@dataclass
class ListConfig:
    """Configuration for list views.
    
    A simplified dataclass that holds all configuration needed by list templates.
    Values come from model class attributes and view computations.
    
    Attributes:
        tbody_id: Unique ID for the table body element.
        columns: List of column names for table headers.
        title: Title for the list view (model's verbose_name_plural).
        explanation: Short description from model docstring.
        explanation_detail: Long description from model docstring.
        detail_type: How detail is displayed ('modal', 'page', 'popover', or None).
        has_bulk_create: Whether bulk creation is supported.
    """

    # Required fields (no defaults) must come first
    tbody_id: str
    columns: list
    title: str
    # Optional fields with defaults
    detail_type: str | None = None
    has_bulk_create: bool = False
    explanation: str | None = None
    explanation_detail: str | None = None
