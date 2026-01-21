"""Module for the base views of the application.

The idea is to abstract as much as possible the common logic between the
views for the different models.

TODO:
    - I implemented a smarter check of the base template. Now it's done in
    the view itself and does not require passing the blank template. Simply
    when the htmx_context is "block", we set the list template_name to one
    that has only the html element in it. list_page.html contains a reference
    to the base template and includes the list.html template. The base_template
    is not required in the with -- include statement in the template. Would be
    good to unify these two approaches a bit.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from docstring_parser import parse_from_object

from watersync.core.generics.context import ListContext
from watersync.core.generics.htmx import HTMXFormMixin
from watersync.core.generics.mixins import CreateUpdateDetailMixin, ExportCsvMixin, StandardURLMixin
from django.utils import timezone


class WatersyncListView(
    LoginRequiredMixin,
    StandardURLMixin,
    ExportCsvMixin,
    ListView,
):
    """Base view for listing objects.

    It contains the basic setup that is shared between all list views.
    The individual list view can override default settings by setting
    the class attributes.

    This view relies on use of generic names for items in the apps.

    For now, it all works on the premise that all the views are under
    the project view.

    Template selection is handled via context processor setting `base_template`:
    - HTMX requests: base_template = 'layouts/partial.html' (no wrapper)
    - Full page: base_template = appropriate dashboard layout
    
    Within the template, list_page.html uses conditional includes:
    - HTMX without HX-Context: renders table.html (just table rows)
    - All other cases: renders list.html (full list component)

    Attributes:
        detail_type: The type of the detail view. It can be either "page"
            or "modal".
        template_name: The name of the template used for the list view.

    Properties:
        model_name: The model name of the object.
        model_name_plural: The plural model name of the object.
        app_label: The app label of the object.
        action: The HTMX action name of the view.
        list_url: The URL name for the list view.
        add_url: The URL name for the add view.
        update_url: The URL name for the update view.
        delete_url: The URL name for the delete view.
        detail_url: The URL name for the detail view.
        item_pk_name: The primary key of the item.
        item_pk: The primary key of the item.
        item: The item object from the URL.
    """

    detail_type: str
    template_name = "list_page.html"
    docstr: str | None = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.docstr = parse_from_object(self.model)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["type"].widget.attrs["hx-get"] = self.request.path
        return form
    
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

        base_kwargs = self.get_base_url_kwargs()
        
        # Get config from model or fall back to view-level detail_type
        detail_type = getattr(self.model, "_detail_type", None) or self.detail_type

        list_context = ListContext(
            add_url=self.get_add_url(**base_kwargs),
            has_bulk_create=getattr(self.model, "_has_bulk_create", False),
            list_url=self.get_list_url(**base_kwargs),
            has_update=getattr(self.model, "_has_update", True),
            has_delete=getattr(self.model, "_has_delete", True),
            has_detail=detail_type == "modal",
            has_detail_page=detail_type == "page",
            has_detail_popover=detail_type == "popover",
            action=self.htmx_trigger,
            columns=self._get_list_view_fields().keys(),
            explanation=self.docstr.short_description,
            explanation_detail=self.docstr.long_description,
            title=self.model_verbose_name_plural,
        )

        context["list_context"] = list_context
        return context


class WatersyncCreateView(
    LoginRequiredMixin,
    HTMXFormMixin,
    StandardURLMixin,
    CreateUpdateDetailMixin,
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

    def get(self, request, *args, **kwargs):
        # Check if this is a request for the detail form
        # This had to be done here because the swap of the form is handled by
        # HTMX and via the hx-get attribute in the form field
        if request.htmx and request.GET.get("type"):
            return self.swap_detail_form(request)

        return super().get(request, *args, **kwargs)


class WatersyncDeleteView(
    LoginRequiredMixin,
    StandardURLMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """Delete logic for watersync DeleteViews.

    The largest chunk here is about redirecting after the delete. After the delete,
    the user will be redirected to the list view, if the request is made from the detail
    view of the deleted object, or to the current URL if the request is made
    from elswhere."""

    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs[self.item_pk_name])

    def get_redirect_url(self, request):
        """Get the URL from htmx request to redirect to after the delete.
        
        For now, I am going return None in the case of the request being made from
        elswhere than the detail view. This is because normally upon deletion a trigger
        is sent to the client to request the new list of objects. This is done by the
        configRequest trigger.
        """
        list_kwargs = self.get_base_url_kwargs()

        current_url = request.htmx.current_url

        is_detail_view = (
            current_url.endswith(f"/{self.object.pk}/")
        )
        is_overview_view = (
            current_url.endswith(f"/{self.object.pk}/overview/")
        )
        is_location_overview = (
            self.model_name == "location"
        )

        if not is_detail_view and not is_overview_view and not is_location_overview:
            return None
        
        return self.get_list_url()(kwargs=list_kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        redirect_url = self.get_redirect_url(request)

        if request.htmx:
            self.object.delete()

            headers = {
                "HX-Trigger": "configRequest",
            }

            if redirect_url:
                headers["HX-Redirect"] = redirect_url

            return HttpResponse(
                status=204,
                headers=headers,
            )

        return super().delete(request, *args, **kwargs)


class WatersyncUpdateView(
    LoginRequiredMixin,
    HTMXFormMixin,
    StandardURLMixin,
    CreateUpdateDetailMixin,
    SuccessMessageMixin,
    UpdateView,
):
    
    template_name = "shared/form.html"
    htmx_render_template = "shared/form.html"

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs[self.item_pk_name])
    
    def get(self, request, *args, **kwargs):
        # Check if this is a request for the detail form
        if request.htmx and request.GET.get("type"):
            return self.swap_detail_form(request, initial=self.get_object().detail)
            
        return super().get(request, *args, **kwargs)


class WatersyncDetailView(
    LoginRequiredMixin,
    StandardURLMixin,
    DetailView,
):
    
    template_name = "detail.html"

    def get_object(self):
        # If the model has 'history', return the object as_of now()
        obj = get_object_or_404(self.model, pk=self.kwargs[self.item_pk_name])
        if hasattr(obj, "history"):
            return obj.history.as_of(timezone.now())
        return obj