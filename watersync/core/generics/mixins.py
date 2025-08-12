

import csv
from functools import partial
from django.http import HttpResponse
from django.template.response import TemplateResponse

from watersync.core.models import Project
from watersync.core.permissions import ApprovalRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

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


class StandardURLMixin(ApprovalRequiredMixin):
    """Provide standardized URL handling for views and templates.

    The properties included in this mixin are used in automated controll mostly over the
    templates and the URLs interaction. This should in principle reduce boilerplate code
    in the views and allow to focus on important customization of the views.

    Attributes:
        blank_template: The template used for the blank layout.
        base_template: The template used for the base layout (i.e. the base dashboard,
            before selecting the project).
        project_base_template: The template used for the project dashboard.

    Properties:
        model_name: The name of the model.
        model_name_plural: The plural name of the model with spaces removed.
        app_label: The app label of the model.
        model_verbose_name_plural: The verbose name plural of the model.

    Methods:
        _get_model_meta: Get model metadata safely.
        _get_list_view_fields: Get list view fields safely.
    """

    blank_template = "layouts/blank.html"
    base_template = "layouts/base_dashboard.html"
    project_base_template = "layouts/project_dashboard.html"

    class Meta:
        abstract = True

    def _get_model_meta(self):
        """Get model metadata safely."""
        return getattr(self.model, "_meta", None)

    @property
    def model_name(self):
        """Shortcut to get the model name."""
        meta = self._get_model_meta()
        return meta.model_name if meta else ""

    @property
    def model_name_plural(self):
        """Shortcut to get the plural model name.

        As this is used further to get the list URL.
        """
        meta = self._get_model_meta()
        if meta:
            return meta.verbose_name_plural.replace(" ", "")
        return ""

    @property
    def model_verbose_name_plural(self):
        """Get the verbose name plural of the model.

        This is used as title in the list view and other places.
        """
        meta = self._get_model_meta()
        return meta.verbose_name_plural if meta else ""

    @property
    def app_label(self):
        """Shortcut to get the app label."""
        meta = self._get_model_meta()
        return meta.app_label if meta else ""

    @property
    def htmx_trigger(self):
        """Compose the HTMX change action name for the view."""
        return f"{self.model_name}Changed"

    def _get_url_name(self, action):
        """Compose the URL pattern for a given action.

        Standardized URL naming convention:
        - For listing: `app_label:model_name_plural`, e.g., `sensors:sensors`
        - For other actions: `app_label:action-model_name`, e.g., `sensors:add-sensor`

        Standardizing URL names helps in maintaining consistency across the application
        and reduces boilerplate code in the views. The urls are passed in the
        ListContext object to the templates and are then assigned to the right buttons.
        """
        if action == "list":
            return f"{self.app_label}:{self.model_name_plural}"
        return f"{self.app_label}:{action}-{self.model_name}"

    @property
    def list_url(self):
        """Url for the list view."""
        return self._get_url_name("list")

    @property
    def add_url(self):
        """Url for the add view."""
        return self._get_url_name("add")

    @property
    def update_url(self):
        """Url for the update view."""
        return self._get_url_name("update")

    @property
    def delete_url(self):
        """Url for the delete view."""
        return self._get_url_name("delete")

    @property
    def detail_url(self):
        """Url for the detail view."""
        return self._get_url_name("detail")

    @property
    def overview_url(self):
        """Url for the overview view."""
        return self._get_url_name("overview")

    @property
    def item_pk_name(self):
        """Compose item's url parameter name.

        As part of standardization, the model names are singular, and can be used
        to compose the url parameter name representing the primary keys of item.
        The convention here is to use the tag for an item as `model_name_pk`,
        e.g., `sensor_pk` for the Sensor model records.
        """
        return f"{self.model_name}_pk"

    @property
    def item_pk(self):
        """Get the primary key of the item."""
        return self.kwargs.get(self.item_pk_name)

    @property
    def item(self):
        """Get the item object from the URL."""
        return {f"{self.item_pk_name}": "__placeholder__"}

    def _get_url_reverse(self, url_name):
        """Get a partial reverse function for the given URL name."""
        return partial(reverse, url_name)

    def get_list_url(self):
        return self._get_url_reverse(self.list_url)

    def get_add_url(self):
        return self._get_url_reverse(self.add_url)

    def get_update_url(self):
        return self._get_url_reverse(self.update_url)

    def get_delete_url(self):
        return self._get_url_reverse(self.delete_url)

    def get_detail_url(self):
        return self._get_url_reverse(self.detail_url)

    def get_overview_url(self):
        return self._get_url_reverse(self.overview_url)

    def get_project(self):
        """Get the project object from the URL."""
        return (
            get_object_or_404(Project, pk=self.kwargs.get("project_pk"))
            if "projects" in self.request.path
            else None
        )

    def get_base_url_kwargs(self):
        base_kwargs = {}
        project = self.get_project()
        if project and self.model_name != "project":
            base_kwargs["project_pk"] = project.pk
        return base_kwargs


class CreateUpdateDetailMixin:
    """Handle swapping the detail form based on the selected type.

    When a form has a type field that user can select from, the form will
    have a detail section. That section is swapped by the HTMX request
    to the appropriate detail form based on the selected type.
    """
    partial_form_template = "shared/form_detail.html"

    def get_detail_form_class(self, request):
        """Return the appropriate detail form class based on the selected type
        or empty response.
        """
        item_type = request.GET.get("type")

        if not item_type:
            return HttpResponse("")

        return self.form_class.detail_forms.get(item_type) or HttpResponse("")

    def add_hx_get(self, response):
        """Add hx-get attribute to the form field from the request.

        This is needed to automate the form rendering. It allows to configure the
        form in a standard way, with crispy forms, and then just alter the type field
        to contain hx-get attribute triggering a get request for the right detail form.
        """

        if isinstance(response, TemplateResponse) and not response.is_rendered:
            context_is_right = (
                "form" in response.context_data and
                "detail" in response.context_data["form"].fields and
                "type" in response.context_data["form"].fields
            )
            if context_is_right:
                # Set hx-get to the current path with a query parameter to
                # account for both updates and creates
                form_field = response.context_data["form"].fields["type"]
                form_field.widget.attrs["hx-get"] = f"{self.request.path}"

        return response

    def swap_detail_form(self, request, initial=None) -> HttpResponse:
        """Swap the detail form in the main form template based on selected type."""

        detail_form_class = self.get_detail_form_class(request)

        if not initial:
            initial = {}

        # THis is a week point, it might fail if the form is not bound
        detail_form = detail_form_class(initial=initial)

        # Render the detail form template
        return render(
            request,
            self.partial_form_template,
            {"form": detail_form}
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.add_hx_get(response)
        return response


