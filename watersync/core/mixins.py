from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from dataclasses import dataclass


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
    """Mixin for handling HTMX forms."""

    htmx_trigger: str | None = None
    htmx_response_status: int | None = 204
    htmx_invalid_status: int | None = 400
    htmx_render_template: str | None = None

    def update_form_instance(self, form):
        """Hook for updating form.instance in subclasses."""

    def form_valid(self, form):
        self.update_form_instance(form)
        if hasattr(form, "save"):
            form.save()

        if is_htmx_request(self.request):
            headers = (
                {"HX-Trigger": self.htmx_trigger}
                if self.htmx_trigger
                else {}
            )
            return HttpResponse(status=self.htmx_response_status, headers=headers)
        return JsonResponse({"message": "Success"}, status=self.htmx_response_status)

    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")
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


@dataclass
class ListContext:
    """Custom object helping to provide the right information in the context objects of ListViews."""

    add_url: str | None = None
    base_url_kwargs: dict | None = None
    list_url: str | None = None
    update_url: str | None = None
    delete_url: str | None = None
    columns: list | None = None
    action: str | None = None
    detail_url: str | None = None
    detail_popover: bool | None = None
    detail_page_url: str | None = None


@dataclass
class DetailContext:
    delete_url: str
    update_url: str
    