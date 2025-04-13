from dataclasses import dataclass


@dataclass
class ListContext:
    """Custom object helping to provide the right information in the context objects of ListViews."""

    add_url: str | None = None
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