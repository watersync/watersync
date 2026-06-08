import logging

from django import forms
from django.utils import timezone

logger = logging.getLogger(__name__)


def inject_into_form_data(form, field_name, value):
    """Inject a value into bound form data, handling QueryDict immutability.
    
    Django's request.POST is an immutable QueryDict. This utility temporarily
    unlocks it to inject a value (e.g., parent FK from URL kwargs), then locks
    it again. Safe to call on regular dicts (in tests) which don't have _mutable.
    
    Args:
        form: The form instance with self.data
        field_name: The field name to set
        value: The value to inject (will be converted to string)
    """
    if hasattr(form.data, '_mutable'):
        form.data._mutable = True
    form.data[field_name] = str(value)
    if hasattr(form.data, '_mutable'):
        form.data._mutable = False


class FormWithHistory(forms.ModelForm):
    """Allows the user to explicitly set the modification date in the history table when updating an object."""
    history_date = forms.DateTimeField(
        label="Modification Date",
        required=False,
        initial=timezone.now,
        help_text="Set the modification date for this change (optional).",
    )

    history_change_reason = forms.CharField(
        label="Change Reason",
        required=False,
        initial="",
        widget=forms.Textarea(attrs={"rows": 2}),
        max_length=255,
        help_text="Reason for the change (optional).",
    )

    def save(self, commit=True):
        """Save the instance with custom history metadata."""
        instance = super().save(commit=False)

        history_date_value = self.cleaned_data.get("history_date")
        history_change_reason = self.cleaned_data.get("history_change_reason")

        if history_date_value:
            instance._history_date = history_date_value

        if history_change_reason:
            instance._change_reason = history_change_reason

        if commit:
            instance.save()

        return instance

class WatersyncForm(forms.ModelForm):
    """Base form with automatic parent prefilling, user pre-selection, and scoped querysets.
    
    Features:
    - Automatically hides and prefills parent ForeignKey fields based on
      URL parameters (e.g., project_pk, location_pk) passed from views.
    - Pre-selects the current user in 'user' M2M fields for new objects.
    - Filters related querysets (user, location, fieldwork) to project scope.
    """
    
    def __init__(self, *args, **kwargs):
        # Extract custom kwargs before calling super()
        parent_instances = kwargs.pop('parent_instances', {})
        current_user = kwargs.pop('current_user', None)
        
        super().__init__(*args, **kwargs)
        
        # Store for use in queryset filtering
        self._parent_instances = parent_instances
        self._current_user = current_user
        
        # Get project PK and filter related querysets by project scope
        project_pk = self._get_project_pk()
        if project_pk:
            self._apply_project_scoped_querysets(project_pk)
        
        # Pre-select current user in 'user' field for new objects (CREATE)
        if current_user and 'user' in self.fields and not self.instance.pk:
            field = self.fields['user']
            if hasattr(field, 'queryset'):  # ModelMultipleChoiceField
                self.initial['user'] = [current_user.pk]
        
        # Handle parent field prefilling
        for field_name, pk in parent_instances.items():
            if field_name not in self.fields:
                continue
                
            field = self.fields[field_name]
            if not hasattr(field, 'queryset'):
                continue
            
            # Fetch the parent instance
            model = field.queryset.model
            try:
                instance = model.objects.get(pk=pk)
                
                # For CREATE (no bound data yet), set initial
                if not self.is_bound:
                    self.initial[field_name] = instance
                # For UPDATE (bound data), inject into data dict
                else:
                    inject_into_form_data(self, field_name, pk)
                
                # Hide the field
                field.widget = forms.HiddenInput()
                
            except model.DoesNotExist:
                logger.warning(f"Parent {field_name} with pk={pk} not found")
    
    def _get_project_pk(self):
        """Get project PK from parent_instances or from instance."""
        # Try to get from parent_instances (URL kwargs)
        project_pk = self._parent_instances.get('project')
        if project_pk:
            return project_pk
        
        # Try to get from instance's project FK
        if self.instance and hasattr(self.instance, 'project_id') and self.instance.project_id:
            return self.instance.project_id
        
        # Try to get from instance's location -> project
        if self.instance and hasattr(self.instance, 'location') and self.instance.location_id:
            return self.instance.location.project_id
        
        return None
    
    def _apply_project_scoped_querysets(self, project_pk):
        """Filter related field querysets to project scope using managers."""
        from watersync.core.models import Fieldwork, Location, Project
        
        # Filter 'user' field to project members
        if 'user' in self.fields:
            field = self.fields['user']
            if hasattr(field, 'queryset'):
                try:
                    project = Project.objects.get(pk=project_pk)
                    field.queryset = project.user.all()
                except Project.DoesNotExist:
                    pass
        
        # Filter 'location' field using manager
        if 'location' in self.fields:
            field = self.fields['location']
            if hasattr(field, 'queryset'):
                field.queryset = Location.objects.for_project(project_pk)
        
        # Filter 'fieldwork' field using manager
        if 'fieldwork' in self.fields:
            field = self.fields['fieldwork']
            if hasattr(field, 'queryset'):
                field.queryset = Fieldwork.objects.for_project(project_pk)


class WatersyncBulkForm(forms.Form):
    """Base form for bulk data entry operations.
    
    Provides common functionality for bulk forms including:
    - Parent field prefilling (like WatersyncFormMixin)
    - Automatic 'bulk' hidden field
    - Input mode selection (paste/file/manual)
    """
    
    INPUT_MODE_CHOICES = [
        ("paste", "Paste Data"),
        ("manual", "Manual Entry"),
        ("file", "Upload File"),
    ]
    
    bulk = forms.CharField(widget=forms.HiddenInput(), initial="true", required=False)
    
    input_mode = forms.ChoiceField(
        choices=INPUT_MODE_CHOICES,
        initial="paste",
        widget=forms.HiddenInput(),
        required=False,
    )
    
    def __init__(self, *args, **kwargs):
        # Handle custom kwargs from view
        parent_instances = kwargs.pop('parent_instances', {})
        current_user = kwargs.pop('current_user', None)
        
        super().__init__(*args, **kwargs)
        
        # Store for subclass use
        self.parent_instances = parent_instances
        self.current_user = current_user
        
        # Prefill and hide parent fields
        for field_name, pk in parent_instances.items():
            if field_name not in self.fields:
                continue
            
            field = self.fields[field_name]
            
            # Handle ModelChoiceField
            if hasattr(field, 'queryset'):
                model = field.queryset.model
                try:
                    instance = model.objects.get(pk=pk)
                    
                    # For unbound forms (GET), set initial
                    if not self.is_bound:
                        self.initial[field_name] = instance
                    # For bound forms (POST), inject into data dict
                    else:
                        inject_into_form_data(self, field_name, pk)
                    
                    field.widget = forms.HiddenInput()
                except model.DoesNotExist:
                    logger.warning(f"Parent {field_name} with pk={pk} not found")
 