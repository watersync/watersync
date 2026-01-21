

import csv

from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from watersync.core.models import Project
from watersync.core.permissions import ApprovalRequiredMixin

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
    """Provide standardized URL handling for views.

    This mixin delegates URL generation to ModelURLMixin on models,
    maintaining a single source of truth for URL conventions.
    
    All models should inherit from ModelURLMixin which provides the
    actual URL generation logic.

    Properties:
        model_name: The name of the model.
        htmx_trigger: The HTMX trigger name for this model.
        item_pk_name: The URL parameter name for this model's pk.
    """

    @property
    def model_name(self):
        """Get the model name from the model's URL mixin."""
        return self.model._get_url_model_name()

    @property
    def model_verbose_name_plural(self):
        """Get the verbose name plural for display."""
        return self.model._get_verbose_name_plural()

    @property
    def htmx_trigger(self):
        """Get the HTMX trigger name from the model."""
        return self.model.get_htmx_trigger()

    @property
    def item_pk_name(self):
        """Get the URL parameter name for this model's pk."""
        return self.model.get_item_pk_name()

    @property
    def item_pk(self):
        """Get the primary key of the item from URL kwargs."""
        return self.kwargs.get(self.item_pk_name)

    def get_list_url(self, **kwargs):
        """Get the resolved list URL."""
        url_name = self.model._get_url_name("list")
        return reverse(url_name, kwargs=kwargs)

    def get_add_url(self, **kwargs):
        """Get the resolved add URL."""
        url_name = self.model._get_url_name("add")
        return reverse(url_name, kwargs=kwargs)

    def get_project(self):
        """Get the project object from the URL kwargs."""
        if project_pk := self.kwargs.get("project_pk"):
            return get_object_or_404(Project, pk=project_pk)
        return None

    def get_base_url_kwargs(self):
        """Build base URL kwargs from the current request's URL parameters."""
        base_kwargs = {}
        if project_pk := self.kwargs.get("project_pk"):
            if self.model_name != "project":
                base_kwargs["project_pk"] = project_pk
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


