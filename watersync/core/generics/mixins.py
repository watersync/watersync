

import csv

from django.http import HttpResponse
from django.shortcuts import render


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


class DetailFormMixin:
    """Handle dynamic detail forms based on a type selection.

    Provides a clean pattern for forms with type-dependent detail sections:
    1. On initial render (create/update), the detail form is included in context
    2. On type change, HTMX requests swap just the detail section
    
    Views using this mixin should define:
    - detail_forms: dict mapping type value -> ModelForm class
    - detail_related_names: dict mapping type value -> related name on model
    
    The mixin handles:
    - Setting hx-get/hx-include on the type field for HTMX swapping
    - Responding to HTMX detail form requests
    - Loading existing detail instances for update views
    """

    detail_form_template = "shared/form_detail.html"
    detail_forms = {}  # Override in view: {"piezometer": PiezometerDetailForm, ...}
    detail_related_names = {}  # Override in view: {"piezometer": "piezometer_detail", ...}

    def get_detail_form_class(self, type_value):
        """Return the detail form class for the given type."""
        if not type_value:
            return None
        return self.detail_forms.get(type_value)

    def get_detail_instance(self, type_value):
        """Get existing detail instance for update views.
        
        Override or extend in subclass if needed.
        """
        if not hasattr(self, 'object') or not self.object:
            return None
        
        related_name = self.detail_related_names.get(type_value)
        if not related_name:
            return None
        
        try:
            return getattr(self.object, related_name)
        except Exception:
            return None

    def save_detail_form(self, instance):
        """Save the detail form after the main object is saved.
        
        Args:
            instance: The main model instance (e.g., Location)
            
        Returns:
            The saved detail instance, or None if no detail form.
        """
        if not self.detail_forms:
            return None
        
        type_value = getattr(instance, 'type', None)
        form_class = self.detail_forms.get(type_value)
        
        if not form_class:
            return None
        
        # Get existing detail instance for updates
        detail_instance = self.get_detail_instance(type_value)
        
        detail_form = form_class(data=self.request.POST, instance=detail_instance)
        if detail_form.is_valid():
            detail_obj = detail_form.save(commit=False)
            # Set the FK to the parent instance
            # The FK field name is typically the lowercase model name
            parent_field_name = instance._meta.model_name
            setattr(detail_obj, parent_field_name, instance)
            detail_obj.save()
            return detail_obj
        
        return None

    def get_detail_form(self, type_value, instance=None):
        """Instantiate the appropriate detail form."""
        form_class = self.get_detail_form_class(type_value)
        if not form_class:
            return None
        return form_class(instance=instance)

    def get_context_data(self, **kwargs):
        """Add detail_form and detail_form_url to context."""
        context = super().get_context_data(**kwargs)
        form = context.get('form')

        # Check if this view has detail forms configured
        if not self.detail_forms:
            return context

        # For update views, load existing detail based on current type
        if hasattr(self, 'object') and self.object:
            type_value = getattr(self.object, 'type', None)
            if type_value:
                detail_instance = self.get_detail_instance(type_value)
                detail_form = self.get_detail_form(type_value, instance=detail_instance)
                if detail_form:
                    context['detail_form'] = detail_form

        # Set HTMX attrs on type field for dynamic detail form swapping
        if form and 'type' in form.fields:
            form.fields['type'].widget.attrs.update({
                'hx-get': self.request.get_full_path(),
                'hx-trigger': 'change',
                'hx-target': '#detail_form_container',
                'hx-include': '[name="type"]',
                'hx-swap': 'innerHTML',
            })

        return context

    def handle_detail_form_request(self, request):
        """Handle HTMX request for detail form swap."""
        type_value = request.GET.get('type')
        
        # For update views, try to get existing detail instance
        detail_instance = None
        if hasattr(self, 'get_object'):
            try:
                self.object = self.get_object()
                # Only use existing instance if type matches
                current_type = getattr(self.object, 'type', None)
                if current_type == type_value:
                    detail_instance = self.get_detail_instance(type_value)
            except Exception:
                pass

        detail_form = self.get_detail_form(type_value, instance=detail_instance)

        if not detail_form:
            return HttpResponse('')

        return render(
            request,
            self.detail_form_template,
            {'form': detail_form}
        )

    def get(self, request, *args, **kwargs):
        """Check if this is an HTMX request for detail form."""
        if request.headers.get('HX-Request') and 'type' in request.GET:
            return self.handle_detail_form_request(request)
        return super().get(request, *args, **kwargs)


class FilterMixin:
    """Mixin that integrates django-filter with ListView.
    
    Provides automatic filtering based on a filterset_class.
    Works with ProjectScopedFilterSet to limit choices to current project.
    
    Attributes:
        filterset_class: The django-filter FilterSet class to use
        
    Template context:
        filter: The filterset instance (use filter.form in template)
        
    Example:
        class SampleListView(FilterMixin, WatersyncListView):
            model = Sample
            filterset_class = SampleFilter
            
        In template:
            <form hx-get="{{ request.path }}" hx-target="#table-container">
                {{ filter.form }}
                <button type="submit">Filter</button>
            </form>
    """
    
    filterset_class = None
    
    def get_filterset_kwargs(self):
        """Get kwargs for filterset instantiation."""
        kwargs = {
            'data': self.request.GET or None,
            'queryset': self.get_base_queryset(),
            'request': self.request,
        }
        
        # Pass project to project-scoped filtersets
        if hasattr(self, 'get_project'):
            kwargs['project'] = self.get_project()
            
        return kwargs
    
    def get_base_queryset(self):
        """Get the base queryset before filtering.
        
        Override this instead of get_queryset when using FilterMixin.
        """
        return super().get_queryset()
    
    def get_queryset(self):
        """Apply filterset to queryset."""
        if self.filterset_class is None:
            return super().get_queryset()
            
        self.filterset = self.filterset_class(**self.get_filterset_kwargs())
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        """Add filterset to context."""
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'filterset'):
            context['filter'] = self.filterset
        return context


