from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string


class UpdateFormMixin:
    """Mixin for updating form instances with HTMX support.
    
    This mixin provides automatic form pre-filling from request parameters
    passed via hx-vals. Configure which fields to prefill by setting
    `prefill_from_parent` on the view.
    
    Attributes:
        prefill_from_parent: Dict mapping form field names to (param_name, model_class).
            Example: {'location': ('location_pk', Location)}
    
    How it works:
        1. GET request: Parent PKs come via query params (from hx-vals)
        2. Form is prefilled and parent fields are hidden (not editable)
        3. POST request: Parent PKs come via hidden form fields  
        4. form_valid() saves the instance with parent values included
    """

    # Override in subclass to configure parent object prefilling
    # Format: {'form_field': ('request_param', ModelClass)}
    prefill_from_parent: dict = None

    def _get_parent_pks(self):
        """Get parent PKs from GET (initial load) or POST (form submission)."""
        pks = {}
        if not self.prefill_from_parent:
            return pks
            
        for field_name, (param_name, model_class) in self.prefill_from_parent.items():
            # Check POST first (form submission), then GET (initial load)
            pk = self.request.POST.get(param_name) or self.request.GET.get(param_name)
            if pk:
                pks[field_name] = (param_name, pk, model_class)
        return pks

    def get_initial(self):
        """Get initial data for the form from request parameters."""
        initial = super().get_initial()

        # User handling
        if self.request.user.is_authenticated:
            initial["user"] = self.request.user.pk

        # Parent object prefilling from request params
        for field_name, (param_name, pk, model_class) in self._get_parent_pks().items():
            try:
                initial[field_name] = model_class.objects.get(pk=pk)
            except model_class.DoesNotExist:
                pass

        return initial

    def get_form(self, form_class=None):
        """Hide pre-filled parent fields (values come via hidden inputs)."""
        form = super().get_form(form_class)
        
        # Hide parent fields that are prefilled
        parent_pks = self._get_parent_pks()
        for field_name in parent_pks.keys():
            if field_name in form.fields:
                form.fields[field_name].widget = form.fields[field_name].hidden_widget()
        
        return form

    def get_context_data(self, **kwargs):
        """Add parent PKs to context for hidden inputs in template."""
        context = super().get_context_data(**kwargs)
        
        # Pass parent PKs to template for hidden inputs
        context['parent_pks'] = [
            (param_name, pk) 
            for field_name, (param_name, pk, model_class) in self._get_parent_pks().items()
        ]
        
        return context

    def update_user(self, instance):
        """Update user field in forms, if applicable.

        If the instance has a many-to-many user field, use the add method, otherwise
        set the user field directly. If the user field is not present, do nothing.
        """
        # If the instance is None, we don't need to do anything
        if not instance:
            return

        # If the instance doesn't have a user field or the requesting user is None do nothing
        if not hasattr(instance, 'user') or not self.request.user:
            return

        # if the user field has add method (i.e., it's a m2m field) and the requesting
        # user is not in the list
        elif hasattr(instance.user, 'add') and self.request.user not in instance.user.all():
            instance.user.add(self.request.user)

        # if the instance has a user field as a foreign key and the requesting user is
        # not in the list
        elif not instance.user:
            instance.user = self.request.user
            instance.save()


class HTMXFormMixin(UpdateFormMixin):
    """Mixin for handling HTMX forms.
    
    Practically all views use this mixin to handle HTMX requests.
    """

    htmx_response_status: int | None = 204
    htmx_invalid_status: int | None = 400
    htmx_render_template: str | None = None


    def update_form_instance(self, form):
        """Hook for updating form.instance in subclasses.

        Logic overriding this method should use the form and update the form
        instance. Do not call super().update_form_instance(form) and do not call
        form.save() in this method. This is handled in the form_valid method further.
        """

    def handle_bulk_create(self, form):
        """Hook for handling bulk creation of objects.

        This method should be overridden in subclasses to handle bulk creation
        logic. Do not call super().handle_bulk_create(form) and do not call
        form.save() in this method. This is handled in the form_valid method further.
        """

    def form_valid(self, form):
        """Handle a valid form submission."""
        
        self.update_form_instance(form)
        
        # Save the instance
        if hasattr(form, "save"):            
            instance = form.save()
        else:
            instance = None
            
        if hasattr(form, "save_m2m"):
            form.save_m2m()

        # Handle bulk creation if applicable
        if form.data.get("bulk") == "true":
            self.handle_bulk_create(form)

        # Update user AFTER saving m2m relationships
        self.update_user(instance)

        if self.request.htmx:
            return HttpResponse(
                status=self.htmx_response_status, 
                headers={"HX-Trigger": "refreshList"}
            )
        return JsonResponse({"message": "Success"}, status=self.htmx_response_status)

    def form_invalid(self, form):
        """Handle an invalid form submission.

        !!TODO!!: This method needs improvement to handle returning the form with errors
        in a way that is compatible with HTMX.
        """

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
