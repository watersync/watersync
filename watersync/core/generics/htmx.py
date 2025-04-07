from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from watersync.core.models import Location


def is_htmx_request(request):
    """Utility to detect HTMX requests."""
    return request.headers.get("HX-Request")


class RenderToResponseMixin:
    """Mixin for rendering HTMX responses."""
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(self.htmx_template, context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)


class UpdateFormMixin:
    """Mixin for updating form instances."""

    # def get_initial(self):
    #     """Get initial data for the form."""
    #     initial = super().get_initial()
    #     if 'project_pk' in self.kwargs and self.model_name != 'project':
    #         initial['project'] = self.kwargs['project_pk']
    #     if 'location_pk' in self.kwargs and self.model_name != 'location':
    #         initial['location'] = self.kwargs['location_pk']
    #     if 'user_pk' in self.kwargs:
    #         initial['user'] = self.kwargs['user_pk']

    #     return initial

    def update_user(self, instance):
        """Updating user field in forms."""
        # If the instance doesn't have a user field or the requesting user is None
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

    def update_project(self, form):
        """Hook for updating project in forms.

        note: the project is never m2m so we don't need to check for add method. The
        project is also not ambiguous, like location, because most of items have to be
        linked to a project.
        """
        if not hasattr(form.instance, 'project'):
            return

        form.instance.project = self.get_project()

    def update_location(self, form):
        """Hook for updating location in subclasses."""
        if "location_pk" in self.kwargs and self.model_name != "location":
            form.instance.location = get_object_or_404(
                Location, pk=self.kwargs["location_pk"]
            )


class HTMXFormMixin(UpdateFormMixin):
    """Mixin for handling HTMX forms."""

    htmx_response_status: int | None = 204
    htmx_invalid_status: int | None = 400
    htmx_render_template: str | None = None


    def update_form_instance(self, form):
        """Hook for updating form.instance in subclasses.

        Logic overriding this method should use the form and update the form
        instance. Do not call super().update_form_instance(form) and do not call
        form.save() in this method. This is handled in the form_valid method further.
        """


    def form_valid(self, form):
        """Handle a valid form submission."""

        self.update_form_instance(form)

        self.update_project(form)
        self.update_location(form)

        # Save the instance to the database
        instance = form.save()
        if hasattr(form, "save_m2m"):
            form.save_m2m()

        # Update user AFTER saving m2m relationships
        self.update_user(instance)

        if is_htmx_request(self.request):
            headers = (
                {"Hx-Trigger": self.htmx_trigger}
                if self.htmx_trigger
                else {}
            )

            return HttpResponse(status=self.htmx_response_status, headers=headers)
        return JsonResponse({"message": "Success"}, status=self.htmx_response_status)

    def form_invalid(self, form):
        if is_htmx_request(self.request):
            self.update_form_instance(form)
            context = self.get_context_data(form=form)
            html = render_to_string(
                self.htmx_render_template, context, request=self.request
            )
            return HttpResponse(
                html, status=self.htmx_invalid_status, content_type="text/html"
            )
        return super().form_invalid(form)


class DeleteHTMX:
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("HX-Request"):
            headers = {"HX-Trigger": "configRequest"}
            if hasattr(self, "htmx_redirect"):
                headers["HX-Redirect"] = self.htmx_redirect

            return HttpResponse(status=204, headers=headers)
        return super().delete(request, *args, **kwargs)