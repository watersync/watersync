from dataclasses import dataclass


@dataclass
class ListContext:
    """Context for list views.
    
    Provides configuration and URLs for the list view template.
    Most per-object URLs are now handled by ModelURLMixin on models.
    
    Attributes:
        add_url: URL to add a new object.
        list_url: URL for the list view.
        has_bulk_create: Whether the model supports bulk creation.
        has_update: Whether objects have an update action.
        has_delete: Whether objects have a delete action.
        has_detail: Whether objects have a modal detail view.
        has_detail_page: Whether objects have a page-based detail view.
        has_detail_popover: Whether detail is shown as a popover.
        action: HTMX trigger action name.
        columns: List of column names to display.
        explanation: Short description from model docstring.
        explanation_detail: Long description from model docstring.
        title: Title for the list view.
    """

    add_url: str | None = None
    list_url: str | None = None
    has_bulk_create: bool = False
    has_update: bool = True
    has_delete: bool = True
    has_detail: bool = False
    has_detail_page: bool = False
    has_detail_popover: bool = False
    action: str | None = None
    columns: list | None = None
    explanation: str | None = None
    explanation_detail: str | None = None
    title: str | None = None
