"""Module for the base views of the application.
"""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from docstring_parser import parse_from_object

from watersync.core.generics.context import ListConfig
from watersync.core.generics.mixins import DetailFormMixin, ExportCsvMixin
from watersync.core.models import Project


class HTMXFormMixin:
    """Mixin providing HTMX form handling with automatic parent prefilling.
    
    This mixin handles:
    1. Auto-detecting parent PKs from request params (e.g., location_pk → location field)
    2. Pre-filling and hiding parent fields in forms
    3. HTMX-compatible form_valid/form_invalid responses
    4. User field auto-population
    
    Parent detection works by:
    - Finding request params ending in '_pk' (e.g., location_pk, fieldwork_pk)
    - Matching to form fields (stripping '_pk' suffix)
    - Getting the model class from the field's queryset
    
    Attributes:
        htmx_response_status: HTTP status code for successful HTMX responses (default: 204)
        htmx_invalid_status: HTTP status code for invalid form HTMX responses (default: 400)
        htmx_render_template: Template for re-rendering form on validation errors
    """
    
    htmx_response_status: int = 204
    htmx_invalid_status: int = 400
    htmx_render_template: str = None
    
    # Cache for detected parent PKs
    _parent_pks_cache = None

    def _get_parent_pks(self, form=None):
        """Auto-detect parent PKs from request params.
        
        Looks for params ending in '_pk', matches them to form fields,
        and returns dict of {field_name: (param_name, pk_value, model_class)}.
        """
        if self._parent_pks_cache is not None:
            return self._parent_pks_cache
            
        pks = {}
        
        # Combine GET and POST params, POST takes precedence
        params = {**self.request.GET.dict(), **self.request.POST.dict()}
        
        for param_name, pk_value in params.items():
            if not param_name.endswith('_pk') or not pk_value:
                continue
                
            # Derive field name from param (location_pk → location)
            field_name = param_name[:-3]  # strip '_pk'
            
            # Get model class from form field if available
            model_class = None
            if form and field_name in form.fields:
                field = form.fields[field_name]
                if hasattr(field, 'queryset'):
                    model_class = field.queryset.model
            
            if model_class:
                pks[field_name] = (param_name, pk_value, model_class)
        
        self._parent_pks_cache = pks
        return pks

    def get_initial(self):
        """Get initial data for the form from request parameters."""
        initial = super().get_initial()

        # User handling
        if self.request.user.is_authenticated:
            initial["user"] = self.request.user.pk

        return initial
    
    def get_form(self, form_class=None):
        """Pre-fill parent fields and disable them."""
        form = super().get_form(form_class)
        
        # Now that we have the form, detect and apply parent PKs
        parent_pks = self._get_parent_pks(form)
        
        for field_name, (param_name, pk, model_class) in parent_pks.items():
            if field_name in form.fields:
                # Set initial value
                try:
                    form.initial[field_name] = model_class.objects.get(pk=pk)
                except model_class.DoesNotExist:
                    continue
                    
                # Disable the field so user can see but not change
                form.fields[field_name].disabled = True
        
        return form

    def get_context_data(self, **kwargs):
        """Add parent PKs to context for hidden inputs in template."""
        context = super().get_context_data(**kwargs)
        
        # Get form from context to detect parent PKs
        form = context.get('form')
        parent_pks = self._get_parent_pks(form)
        
        # Pass parent PKs to template for hidden inputs
        context['parent_pks'] = [
            (param_name, pk) 
            for field_name, (param_name, pk, model_class) in parent_pks.items()
        ]
        
        return context

    def _update_user(self, instance):
        """Update user field on instance if applicable.
        
        Handles both ForeignKey and ManyToMany user fields.
        """
        if not instance or not hasattr(instance, 'user') or not self.request.user:
            return
 
        # ManyToMany field (has 'add' method)
        if hasattr(instance.user, 'add'):
            if self.request.user not in instance.user.all():
                instance.user.add(self.request.user)
        # ForeignKey field
        elif not instance.user:
            instance.user = self.request.user
            instance.save()

    def update_form_instance(self, form):
        """Hook for updating form.instance in subclasses.
        
        Override to modify form.instance before save. Do not call form.save() here.
        """
        pass

    def handle_bulk_create(self, form):
        """Hook for handling bulk creation of objects.
        
        Override to implement bulk creation logic. Do not call form.save() here.
        """
        pass

    def form_valid(self, form):
        """Handle a valid form submission with HTMX support."""
        self.update_form_instance(form)
        
        # Save the instance
        instance = form.save() if hasattr(form, "save") else None
            
        if hasattr(form, "save_m2m"):
            form.save_m2m()

        # Handle bulk creation if applicable
        if form.data.get("bulk") == "true":
            self.handle_bulk_create(form)

        # Update user AFTER saving m2m relationships
        self._update_user(instance)

        if self.request.htmx:
            return HttpResponse(
                status=self.htmx_response_status, 
                headers={"HX-Trigger": "refreshList"}
            )
        return JsonResponse({"message": "Success"}, status=self.htmx_response_status)

    def form_invalid(self, form):
        """Handle an invalid form submission with HTMX support."""
        if self.request.htmx:
            self.update_form_instance(form)
            context = self.get_context_data(form=form)
            html = render_to_string(
                self.htmx_render_template, context, request=self.request
            )
            return HttpResponse(
                html, status=self.htmx_invalid_status, content_type="text/html"
            )
        return super().form_invalid(form)


class WatersyncListView(
    LoginRequiredMixin,
    ExportCsvMixin,
    ListView,
):
    """Base view for listing objects.

    Template context includes:
        - list_config: ListConfig with URLs, columns, title, descriptions,
          and feature flags (has_bulk_create, detail_type)
        
    Template selection is handled via context processor setting `base_template`:
    - HTMX requests: base_template = 'layouts/partial.html' (no wrapper)
    - Full page: base_template = appropriate dashboard layout
    
    Within the template, list_page.html uses conditional includes:
    - HTMX without HX-Context: renders table.html (just table rows)
    - All other cases: renders list.html (full list component)
    """

    detail_type: str = None
    template_name = "list_page.html"
    docstr: str | None = None

    def get_project(self):
        """Get the project object from the URL kwargs."""
        if project_pk := self.kwargs.get("project_pk"):
            return get_object_or_404(Project, pk=project_pk)
        return None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.docstr = parse_from_object(self.model)

    def _get_list_view_fields(self):
        """Get list view fields safely."""
        return getattr(self.model, "_list_view_fields", {})

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Download"):
            queryset = self.get_queryset()
            return self.export_as_csv(request, queryset)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add common context data to the template."""
        context = super().get_context_data(**kwargs)
        
        if self.docstr is None:
            self.docstr = parse_from_object(self.model)

        # ListConfig with all values needed by templates
        list_config = ListConfig(
            tbody_id=f"{self.model._meta.model_name}-tbody",
            columns=list(self._get_list_view_fields().keys()),
            title=self.model._meta.verbose_name_plural,
            detail_type=self.detail_type or None,
            has_bulk_create=getattr(self.model, "_has_bulk_create", False),
            has_update=getattr(self.model, "_has_update", False),
            explanation=self.docstr.short_description,
            explanation_detail=self.docstr.long_description,
        )

        context["list_config"] = list_config
        
        # Build hx_vals from filter parameters (location_pk, fieldwork_pk, sample_pk)
        # These are passed via hx-vals in lazy-load requests and used for add button
        filter_keys = ["location_pk", "fieldwork_pk", "sample_pk"]
        hx_vals = {k: v for k, v in self.request.GET.items() if k in filter_keys}
        if hx_vals:
            context["hx_vals"] = json.dumps(hx_vals)
        
        return context


class WatersyncCreateView(
    LoginRequiredMixin,
    HTMXFormMixin,
    DetailFormMixin,
    CreateView,
):

    template_name = "shared/form.html"
    htmx_render_template = "shared/form.html"

    def get_form_class(self):
        """Return the form class to use based on the request parameters.
        If 'bulk' is in the request parameters or POST data, return the bulk form class.
        """

        if "bulk" in self.request.GET or self.request.POST.get("bulk") == "true":
            return self.bulk_form_class
        return self.form_class
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not hasattr(self, "bulk_form_class"):
            return kwargs
        if self.get_form_class() == self.bulk_form_class:
            # This has to be done for non-ModelForm
            kwargs.pop("instance", None)
        return kwargs


class WatersyncDeleteView(
    LoginRequiredMixin,
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

    def delete(self, request, *args, **kwargs):

        self.object = self.get_object()

        if request.htmx:
            current_url = request.htmx.current_url
            is_viewing_object = self._is_viewing_this_object(current_url)

            self.object.delete()

            headers = {}
            if is_viewing_object:
                headers["HX-Redirect"] = self.truncate_url_to_list(current_url)
            else:
                headers["HX-Trigger"] = "refreshList"

            return HttpResponse(status=204, headers=headers)

        return super().delete(request, *args, **kwargs)


class WatersyncUpdateView(
    LoginRequiredMixin,
    HTMXFormMixin,
    DetailFormMixin,
    SuccessMessageMixin,
    UpdateView,
):
    
    template_name = "shared/form.html"
    htmx_render_template = "shared/form.html"

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs[self.model._meta.model_name + "_pk"])

    def get_detail_form_initial(self):
        """Return the existing detail data for update forms."""
        obj = self.get_object()
        return getattr(obj, 'detail', None) or {}


class WatersyncDetailView(
    LoginRequiredMixin,
    DetailView,
):
    
    template_name = "detail.html"

    def get_object(self):
        # If the model has 'history', return the object as_of now()
        obj = get_object_or_404(self.model, pk=self.kwargs[self.model._meta.model_name + "_pk"])
        if hasattr(obj, "history"):
            return obj.history.as_of(timezone.now())
        return obj
    
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