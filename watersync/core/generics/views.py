"""Watersync generic views.

This module provides base views for listing, creating, updating,
deleting, and detailing objects within the Watersync application.
"""

import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

logger = logging.getLogger(__name__)

from docstring_parser import parse_from_object

from watersync.core.generics.context import ListConfig
from watersync.core.generics.forms import WatersyncBulkForm, WatersyncForm
from watersync.core.generics.mixins import DetailFormMixin, ExportCsvMixin
from watersync.core.models import Project
from watersync.core.permissions import ProjectPermissionMixin


class WatersyncListView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    ExportCsvMixin,
    ListView,
):
    """Base view for listing objects.

    The same view is used for both full page loads (e.g., list of all locations) and
    HTMX lazy-loaded content in overview pages (e.g., measurements for a specific location).

    # Template behavior
        The template_name is set to `list_page.html`. Then the actual rendering
        is handled conditionally within the template depending on whether the
        request is an HTMX request or a full page load.
    
    # Context
        In this generic view we set the scene for list pages across the app. We
        include here the template context through `list_config`
        (see watersync.core.generics.context.ListConfig).

    # Docstring parsing
        The model's docstring is parsed using `docstring_parser` to extract
        short and long descriptions for use in the template. The models should
        have meaningful and properly structured docstrings for this to be effective.
        (see watersync.core.generics.models.WatersyncBaseModel).
    """

    detail_type: str = None
    template_name = "list_page.html"
    docstr: str | None = None

    def _get_list_view_fields(self):
        """Get list view fields safely."""
        return getattr(self.model, "_list_view_fields", {})

    def get(self, request, *args, **kwargs):
        """Handle a specific case where a CSV export is requested.
        
        Normally a get request is made to render the list view template. However,
        in the list page there might be a button which will send a request with
        the `HX-Download` header to trigger a CSV export of the current queryset.
        """
        if request.headers.get("HX-Download"):
            queryset = self.get_queryset()
            return self.export_as_csv(request, queryset)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add common context data to the template."""
        context = super().get_context_data(**kwargs)
        
        docstr = parse_from_object(self.model)

        # ListConfig with all values needed by templates
        list_config = ListConfig(
            tbody_id=f"{self.model._meta.model_name}-tbody",
            columns=list(self._get_list_view_fields().keys()),
            title=self.model._meta.verbose_name_plural,
            detail_type=self.detail_type or None,
            has_bulk_create=getattr(self.model, "_has_bulk_create", False),
            has_update=getattr(self.model, "_has_update", False),
            explanation=docstr.short_description,
            explanation_detail=docstr.long_description,
        )

        context["list_config"] = list_config
        
        return context


class WatersyncFormView:
    """Base mixin for HTMX-only form handling."""
    
    htmx_response_status = 204
    template_name = "shared/form.html"
    
    def get_form_kwargs(self):
        """Pass parent instances and user to form if it supports them."""
        kwargs = super().get_form_kwargs()
        
        # Check if form can handle custom kwargs
        form_class = self.get_form_class()
        try:
            supports_custom_kwargs = issubclass(form_class, (WatersyncForm, WatersyncBulkForm))
        except TypeError:
            supports_custom_kwargs = False
        
        # Pass custom kwargs to forms that support them
        if supports_custom_kwargs:
            # Extract parent PKs from URL kwargs and GET params
            parent_pks = {}
            all_params = {**self.kwargs, **self.request.GET.dict()}
            
            for param_name, pk_value in all_params.items():
                if param_name.endswith('_pk') and pk_value:
                    field_name = param_name[:-3]
                    parent_pks[field_name] = pk_value
            
            if parent_pks:
                kwargs['parent_instances'] = parent_pks  # Form expects this key name
            
            # Pass current user
            if self.request.user.is_authenticated:
                kwargs['current_user'] = self.request.user
        
        return kwargs
    
    def form_valid(self, form):
        """Handle valid form submission (HTMX only)."""
        is_bulk = (
            self.request.GET.get("bulk") == "true" or 
            form.data.get("bulk") == "true"
        )
        
        if is_bulk:
            self.handle_bulk_create(form, None)
        else:
            self.pre_save(form)
            instance = form.save()
            
            if hasattr(form, "save_m2m"):
                form.save_m2m()
            
            # Save detail form if this view uses DetailFormMixin
            if hasattr(self, 'save_detail_form'):
                self.object = instance  # Ensure object is set for get_detail_instance
                self.save_detail_form(instance)
            
            self.post_save(form, instance)
        
        # Return 204 with refreshList trigger
        return HttpResponse(
            status=self.htmx_response_status,
            headers={
                "HX-Trigger": "refreshList"  # Simple string is fine
            }
        )
    
    def form_invalid(self, form):
        """Re-render form with errors (HTMX only)."""
        context = self.get_context_data(form=form)
        template = self.get_template_names()[0] if hasattr(self, 'get_template_names') else self.template_name
        
        return render(
            self.request,
            template,
            context,
            status=200  # Must be 2xx for HTMX to swap content
        )
    
    # Hooks for subclasses
    def pre_save(self, form):
        """Override to modify form.instance before save."""
        pass
    
    def post_save(self, form, instance):
        """Override for actions after save."""
        pass
    
    def handle_bulk_create(self, form, instance):
        """Override to implement bulk creation logic."""
        pass


class WatersyncCreateView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    WatersyncFormView,
    DetailFormMixin,
    CreateView,
):
    """Generic HTMX create view."""
    
    def get_form_class(self):
        """Use bulk form if bulk=true in GET or POST."""
        is_bulk = (
            self.request.GET.get("bulk") == "true" or
            self.request.POST.get("bulk") == "true"
        )

        if is_bulk and hasattr(self, "bulk_form_class"):
            return self.bulk_form_class
        return self.form_class
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # Remove instance for non-ModelForm bulk forms
        if hasattr(self, "bulk_form_class") and self.get_form_class() == self.bulk_form_class:
            kwargs.pop("instance", None)
        
        return kwargs
    
class WatersyncUpdateView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    WatersyncFormView,
    DetailFormMixin,
    UpdateView,
):
    """Generic HTMX update view."""
    
    def get_object(self):
        """Get object using standardized URL pattern."""
        model_name = self.model._meta.model_name
        return get_object_or_404(self.model, pk=self.kwargs[f"{model_name}_pk"])

class WatersyncDeleteView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    DeleteView,
):
    """Delete view with HTMX support.
    
    - From list pages: triggers 'refreshList' to update the table
    - From detail/overview pages: redirects to list view via HX-Redirect
    - Checks for protected relationships and disables delete if found
    """

    template_name = "confirm_delete.html"
    cascade_warning = None

    def _get_protected_related_objects(self, obj):
        """Check for related objects that would prevent deletion (PROTECT).
        
        Returns a list of (model_name, count) tuples for protected relations with objects.
        """
        from django.db.models import PROTECT
        
        protected = []
        for rel in obj._meta.related_objects:
            if rel.on_delete == PROTECT:
                related_name = rel.get_accessor_name()
                related_manager = getattr(obj, related_name, None)
                if related_manager is not None:
                    count = related_manager.count()
                    if count > 0:
                        model_name = rel.related_model._meta.verbose_name_plural
                        protected.append((model_name, count))
        return protected

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.cascade_warning:
            context['cascade_warning'] = self.cascade_warning
        
        # Check for protected relationships
        protected = self._get_protected_related_objects(self.object)
        if protected:
            context['protected_objects'] = protected
            
        return context

    def get_object(self):
        return get_object_or_404(
            self.model, 
            pk=self.kwargs[self.model._meta.model_name + "_pk"]
        )

    def _is_viewing_this_object(self, current_url: str) -> bool:
        """Check if we're on a page dedicated to this specific object."""
        if not current_url:
            return False
        return (
            current_url.endswith(f"/{self.object.pk}/") or
            current_url.endswith(f"/{self.object.pk}/overview/")
        )
    
    def truncate_url_to_list(self, url: str) -> str:
        """Truncate a detail/overview URL to the corresponding list URL."""
        if not url:
            return ""
        
        # Ensure trailing slash for consistent handling
        if not url.endswith('/'):
            url += '/'

        # Remove 'overview/' if present
        if url.endswith("/overview/"):
            url = url[:-len("overview/")]
        
        # Remove the pk segment
        return url.rsplit("/", 2)[0] + "/"

    def post(self, request, *args, **kwargs):
        """Handle POST - bypass Django 5's form-based deletion for HTMX-only flow."""
        from django.db.models import ProtectedError
        
        self.object = self.get_object()
        
        # Check for protected relationships before attempting delete
        protected = self._get_protected_related_objects(self.object)
        if protected:
            context = self.get_context_data()
            context['delete_error'] = "Cannot delete: related objects exist."
            return render(request, self.template_name, context, status=400)
        
        current_url = getattr(request.htmx, 'current_url', None)
        is_viewing_object = self._is_viewing_this_object(current_url)

        try:
            self.object.delete()
        except ProtectedError:
            context = self.get_context_data()
            context['delete_error'] = "Cannot delete: protected by database constraint."
            return render(request, self.template_name, context, status=400)

        headers = {}
        if is_viewing_object:
            headers["HX-Redirect"] = self.truncate_url_to_list(current_url)
        else:
            headers["HX-Trigger"] = "refreshList"

        return HttpResponse(status=204, headers=headers)

class WatersyncDetailView(
    LoginRequiredMixin,
    ProjectPermissionMixin,
    DetailView,
):
    """Generic detail view with optional type-based detail support."""
    
    template_name = "detail.html"
    detail_related_names = {}  # Override: {"type_value": "related_name", ...}

    def get_object(self):
        """Get object using standardized URL pattern."""
        pk_kwarg = f"{self.model._meta.model_name}_pk"
        return get_object_or_404(self.model, pk=self.kwargs[pk_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add detail object to context if this model has type-based details
        if self.detail_related_names:
            obj_type = getattr(self.object, 'type', None)
            related_name = self.detail_related_names.get(obj_type)
            if related_name:
                context['detail'] = getattr(self.object, related_name, None)
        
        return context
    
class WatersyncHistoryListView(WatersyncListView):
    """Base view for listing historical records with diffs.
    
    Uses the historical model's `instance_type` (set by django-simple-history)
    and the parent's `get_history_with_diffs()` (from SetupSimpleHistory).
    """
    template_name = "shared/list_history.html"
    detail_type = "popover"

    def get_queryset(self):
        parent_model = self.model.instance_type
        pk_kwarg = f"{parent_model._meta.model_name}_pk"
        parent = get_object_or_404(parent_model, pk=self.kwargs[pk_kwarg])
        return parent.get_history_with_diffs()

    def get_context_data(self, **kwargs):
        return ListView.get_context_data(self, **kwargs)