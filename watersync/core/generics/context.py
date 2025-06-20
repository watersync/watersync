from dataclasses import dataclass


@dataclass
class ListContext:
    """Custom object helping to provide the right information in the context objects of ListViews.
    
    add_url: URL to add a new object.
    has_bulk_create: Whether the view supports bulk creation of objects.
    base_url_kwargs: Additional keyword arguments for the base URL.
    list_url: URL for the list view.
    update_url: URL for updating an object.
    delete_url: URL for deleting an object.
    columns: List of columns to display in the list view.
    action: ???
    detail_url: URL for the detail view of an object.
    detail_popover: Whether the detail is shown in the form of a popover.
    detail_page_url: URL for the detail page of an object (in case it's a page).
    explanation: Explanation text for the list view - populated from the docstring.
    explanation_detail: Detailed explanation text for the list view - populated from the docstring.
    title: Title of the list view - populated from the model name.
    """

    add_url: str | None = None
    has_bulk_create: bool | None = None
    base_url_kwargs: dict | None = None
    list_url: str | None = None
    update_url: str | None = None
    delete_url: str | None = None
    columns: list | None = None
    action: str | None = None
    detail_url: str | None = None
    detail_popover: bool | None = None
    detail_page_url: str | None = None
    explanation: str | None = None
    explanation_detail: str | None = None
    title: str | None = None


@dataclass
class DetailContext:
    delete_url: str
    update_url: str
