from django import forms
from django.forms import ChoiceField


class FormWithDetailMixin(forms.ModelForm):
    detail_forms: dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.detail_form = None

        is_update =(
            hasattr(self, 'instance') and self.instance and self.instance.pk
        )

        instance_type = getattr(self.instance, 'type', None)

        if not instance_type:
            try:
                instance_type = self.instance.sensor.type
            except:
                pass

        # For existing instances (GET requests)
        if is_update and instance_type and not self.is_bound:
            detail_form_class = self.detail_forms.get(instance_type)
            if detail_form_class:
                self.detail_form = detail_form_class(initial=self.instance.detail or {})
        
        # For POST requests
        elif self.is_bound and 'type' in self.data:
            selected_type = self.data.get('type')
            detail_form_class = self.detail_forms.get(selected_type)
            if detail_form_class:
                # Create detail form with POST data
                self.detail_form = detail_form_class(data=self.data)

    def is_valid(self):
        """Validate both the main form and the detail form"""
        main_valid = super().is_valid()
        
        # Get the selected type
        selected_type = self.cleaned_data.get('type') if self.is_bound and hasattr(self, 'cleaned_data') else None
        
        # If we have a type but no detail form yet, create one
        if selected_type and not self.detail_form:
            detail_form_class = self.detail_forms.get(selected_type)
            if detail_form_class:
                # Extract detail form data from the request
                detail_data = {}
                for field_name in detail_form_class().fields.keys():
                    if field_name in self.data:
                        detail_data[field_name] = self.data.get(field_name)
                self.detail_form = detail_form_class(data=detail_data or None)
        
        # Validate detail form if we have one
        detail_valid = self.detail_form.is_valid() if self.detail_form else True

        
        return main_valid and detail_valid

    def save(self, commit=True):
        """Save the main form and convert detail form to JSON"""
        instance = super().save(commit=False)

        # Convert detail form data to JSON
        if self.detail_form and self.detail_form.is_valid():
            instance.detail = self.detail_form.cleaned_data

        if commit:
            instance.save()
        return instance


class HTMXChoiceField(ChoiceField):
    """Custom ChoiceField to handle HTMX requests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.attrs.update(
            {
                "hx-trigger": "change, revealed",
                "hx-target": "#detail_form",
                "hx-swap": "innerHTML",
            }
        )