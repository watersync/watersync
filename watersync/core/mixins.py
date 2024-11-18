from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse


def is_htmx_request(request):
    """Utility to detect HTMX requests."""
    return request.headers.get("HX-Request")


class RenderToResponseMixin:
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(self.htmx_template, context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)


class HTMXFormMixin:
    htmx_trigger_header: str | None = None
    htmx_response_status: int | None = 204
    htmx_invalid_status: int | None = 400
    htmx_render_template: str | None = None

    def update_form_instance(self, form):
        """Hook for updating form.instance in subclasses."""
        pass

    def form_valid(self, form):
        self.update_form_instance(form)
        form.save()

        if is_htmx_request(self.request):
            headers = (
                {"HX-Trigger": self.htmx_trigger_header}
                if self.htmx_trigger_header
                else {}
            )
            return HttpResponse(status=self.htmx_response_status, headers=headers)
        return JsonResponse({"message": "Success"}, status=self.htmx_response_status)

    def form_invalid(self, form):
        if is_htmx_request(self.request):
            self.update_form_instance(form)

            # Render the invalid form with error messages
            context = self.get_context_data(form=form)
            html = render_to_string(
                self.htmx_render_template, context, request=self.request
            )
            return HttpResponse(
                html, status=self.htmx_invalid_status, content_type="text/html"
            )

        return super().form_invalid(form)
