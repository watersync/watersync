

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
    
    Subclasses need:
    - form_class with `detail_forms` dict mapping type -> form class
    - Template with `<div id="detail_form">` target
    
    The mixin handles:
    - Setting hx-get URL on the type field
    - Responding to HTMX detail form requests
    - Pre-populating detail form for updates
    """
    
    detail_form_template = "shared/form_detail.html"

    def get_detail_form_class(self, type_value):
        """Return the detail form class for the given type."""
        if not type_value or not hasattr(self.form_class, 'detail_forms'):
            return None
        return self.form_class.detail_forms.get(type_value)

    def get_detail_form_initial(self):
        """Return initial data for the detail form.
        
        Override in UpdateView to return instance.detail.
        """
        return {}

    def get_detail_form(self, type_value, initial=None):
        """Instantiate the appropriate detail form."""
        form_class = self.get_detail_form_class(type_value)
        if not form_class:
            return None
        return form_class(initial=initial or {})

    def get_context_data(self, **kwargs):
        """Add detail_form to context if type is selected."""
        context = super().get_context_data(**kwargs)
        form = context.get('form')
        
        if form and hasattr(form, 'detail_form') and form.detail_form:
            # Form already has detail_form (from FormWithDetailMixin)
            context['detail_form'] = form.detail_form
        
        # Set all HTMX attrs on type field for dynamic detail form swapping
        if form and 'type' in form.fields:
            form.fields['type'].widget.attrs.update({
                'hx-get': self.request.path,
                'hx-trigger': 'change',
                'hx-target': '#detail_form',
                'hx-swap': 'innerHTML',
            })
        
        return context

    def handle_detail_form_request(self, request):
        """Handle HTMX request for detail form swap."""
        type_value = request.GET.get('type')
        initial = self.get_detail_form_initial()
        detail_form = self.get_detail_form(type_value, initial=initial)
        
        if not detail_form:
            return HttpResponse('')
        
        return render(
            request,
            self.detail_form_template,
            {'form': detail_form}
        )

    def get(self, request, *args, **kwargs):
        """Check if this is an HTMX request for detail form."""
        if request.htmx and 'type' in request.GET:
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


