from dataclasses import dataclass
from django.utils.timezone import now


class ModelTemplateInterface:
    """Add attributes that are used in generic templates."""

    _list_view_fields: dict = None
    _detail_view_fields: dict = None

    def _return_items(self, fields):
        """
        Helper method that returns a list of tuples containing field names and their corresponding values.
        """
        return [
            (field_name_verb, getattr(self, field))
            for field_name_verb, field in fields.items()
        ]

    @property
    def detail_view_items(self):
        """
        Property that returns a list of tuples containing field names and their corresponding values.
        """
        return self._return_items(self._detail_view_fields)

    @property
    def list_view_items(self):
        """
        Property that returns a list of tuples containing field names and their corresponding values.
        """
        return self._return_items(self._list_view_fields)


class SimpleHistorySetup:
    """
    Mixin class that provides a simple history setup for the models.

    You still need to add the history field to the model:

        >>> history = HistoricalRecords()
    """
    __history_date = None

    @property
    def _history_date(self):
        return self.__history_date or now()

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

import csv
from django.http import HttpResponse

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        response["HX-Trigger"] = "csvDownloaded"
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
            
        return response


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
