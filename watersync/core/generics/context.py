from dataclasses import dataclass
from typing import Literal


@dataclass
class ListConfig:
    """Configuration for rendering list views.
    
    ListConfig object is passed to to the context and is used in automated
    rendering of list views (tables and page views). Values come from model
    class attributes and view computations.
    
    Attributes:
        tbody_id: Unique ID for the table body element.
        title: Title for the list view (model's verbose_name_plural).
        columns: List of column names for table headers.
        explanation: Short description from model docstring.
        explanation_detail: Long description from model docstring.
        detail_type: How detail is displayed ('modal', 'page', 'popover', or None).
        has_bulk_create: Whether bulk creation is supported.
    """

    # Required fields (no defaults) must come first
    tbody_id: str
    title: str
    columns: list[str]
    # Optional fields with defaults
    detail_type: Literal['modal', 'page', 'popover'] | None = None
    has_bulk_create: bool = False
    has_update: bool = False
    explanation: str | None = None
    explanation_detail: str | None = None