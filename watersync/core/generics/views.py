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
from functools import partial

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from docstring_parser import parse_from_object

from watersync.core.generics.context import DetailContext, ListContext
from watersync.core.generics.htmx import HTMXFormMixin, RenderToResponseMixin
from watersync.core.generics.mixins import ExportCsvMixin
from watersync.core.models import Project
from watersync.core.permissions import ApprovalRequiredMixin

class WatersyncGenericViewProperties(ApprovalRequiredMixin):
    """Mixin to add shortcuts to the views."""

    blank_template = "layouts/blank.html"
    base_template = "layouts/base_dashboard.html"
    project_base_template = "layouts/project_dashboard.html"

    class Meta:
        abstract = True

    def _get_model_meta(self):
        """Get model metadata safely."""
        return getattr(self.model, "_meta", None)

    def _get_list_view_fields(self):
        """Get list view fields safely."""
        return getattr(self.model, "_list_view_fields", {})

    @property
    def model_name(self):
        """Shortcut to get the model name."""
        meta = self._get_model_meta()
        return meta.model_name if meta else ""

    @property
    def model_name_plural(self):
        """Shortcut to get the plural model name."""
        meta = self._get_model_meta()
        if meta:
            return meta.verbose_name_plural.replace(" ", "")
        return ""

    @property
    def app_label(self):
        """Shortcut to get the app label."""
        meta = self._get_model_meta()
        return meta.app_label if meta else ""

    @property
    def model_verbose_name_plural(self):
        """Get the verbose name plural of the model."""
        meta = self._get_model_meta()
        return meta.verbose_name_plural if meta else ""

    @property
    def htmx_trigger(self):
        """Get the HTMX action name of the view."""
        return f"{self.model_name}Changed"

    def _get_url_name(self, action):
        """Generate URL name for a given action."""
        if action == "list":
            return f"{self.app_label}:{self.model_name_plural}"
        return f"{self.app_label}:{action}-{self.model_name}"

    @property
    def list_url(self):
        """Url name for the list view."""
        return self._get_url_name("list")

    @property
    def add_url(self):
        """Url name for the add view."""
        return self._get_url_name("add")

    @property
    def update_url(self):
        """Url name for the update view."""
        return self._get_url_name("update")

    @property
    def delete_url(self):
        """Url name for the delete view."""
        return self._get_url_name("delete")

    @property
    def detail_url(self):
        """Url name for the detail view."""
        return self._get_url_name("detail")
    
    @property
    def overview_url(self):
        """Url name for the overview view."""
        return self._get_url_name("overview")

    @property
    def item_pk_name(self):
        """Get the primary key of the item."""
        return f"{self.model_name}_pk"

    @property
    def item_pk(self):
        """Get the primary key of the item."""
        return self.kwargs.get(self.item_pk_name)

    @property
    def item(self):
        """Get the item object from the URL."""
        return {f"{self.item_pk_name}": "__placeholder__"}
    
    def _get_url_reverse(self, url_name):
        """Get a partial reverse function for the given URL name."""
        return partial(reverse, url_name)

    def get_list_url(self):
        return self._get_url_reverse(self.list_url)

    def get_add_url(self):
        return self._get_url_reverse(self.add_url)

    def get_update_url(self):
        return self._get_url_reverse(self.update_url)

    def get_delete_url(self):
        return self._get_url_reverse(self.delete_url)

    def get_detail_url(self):
        return self._get_url_reverse(self.detail_url)
    
    def get_overview_url(self):
        return self._get_url_reverse(self.overview_url)

    def get_project(self):
        """Get the project object from the URL."""
        return (
            get_object_or_404(Project, pk=self.kwargs.get("project_pk"))
            if "projects" in self.request.path
            else None
        )
        
    def get_base_url_kwargs(self):
        base_kwargs = {"user_id": self.request.user.id}
        project = self.get_project()
        if project and self.model_name != "project":
            base_kwargs["project_pk"] = project.pk
        return base_kwargs


class WatersyncListView(
    LoginRequiredMixin,
    RenderToResponseMixin,
    WatersyncGenericViewProperties,
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

    I am not sure how to inject an additional url param to the reverse
    function kwargs. Now it automatically adds the user_id, project and
    item_pk to the kwargs. The item pk is normally called by the model
    name + _pk. Here it's computed from the generic model name. Then,
    a placeholder is added to the kwargs instead of the actual item pk.
    This is replaced in the template by the actual item pk from objects.

    Attributes:
        detail_type: The type of the detail view. It can be either "page"
            or "modal".
        template_name: The name of the template used for the list view.
        htmx_template: The name of the template used for the HTMX response.
            (it's normally the same as the template_name)

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
    template_name = "list.html"
    htmx_template = "table.html"
    docstr: str | None = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.template_name = self.determine_template_name()
        self.docstr = parse_from_object(self.model)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["type"].widget.attrs["hx-get"] = self.request.path
        return form
        

    def determine_template_name(self):
        """Determine the template name dynamically.

        If it's a block list (HTMX), use list.html. Otherwise,
        use list_page.html.
        """
        if self.request.headers.get("HX-Context") == "block":
            return "list.html"
        return "list_page.html"

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
        item_kwargs = {**base_kwargs, **self.item}

        list_context = ListContext(
            add_url=self.get_add_url()(kwargs=base_kwargs),
            has_bulk_create=getattr(self.model, "create_bulk", False),
            list_url=self.get_list_url()(kwargs=base_kwargs),
            update_url=self.get_update_url()(kwargs=item_kwargs),
            delete_url=self.get_delete_url()(kwargs=item_kwargs),
            action=self.htmx_trigger,
            columns=self._get_list_view_fields().keys(),
            explanation=self.docstr.short_description,
            explanation_detail=self.docstr.long_description,
            title=self.model_verbose_name_plural,
        )

        self._configure_detail_context(list_context, item_kwargs)
        context["list_context"] = list_context
        return context

    def _configure_detail_context(self, list_context, item_kwargs):
        """Configure detail-specific context based on detail_type."""
        if self.detail_type == "page":
            list_context.detail_page_url = self.get_overview_url()(kwargs=item_kwargs)
        elif self.detail_type == "popover":
            list_context.detail_popover = True
        elif self.detail_type == "modal":
            list_context.detail_url = self.get_detail_url()(kwargs=item_kwargs)


class CreateUpdateDetailMixin:
    """Handle swapping the detail form based on the selected type.
    
    When a form has a type field that user can select from, the form will
    have a detail section. That section is swapped by the HTMX request
    to the appropriate detail form based on the selected type.
    """
    partial_form_template = "shared/form_detail.html"

    def get_detail_form_class(self, request):
        """Return the appropriate detail form class based on the selected type
        or empty response.
        """
        item_type = request.GET.get("type")

        if not item_type:
            return HttpResponse("")

        return self.form_class.detail_forms.get(item_type) or HttpResponse("")

    def add_hx_get(self, response):
        """Add hx-get attribute to the form field from the request.
        
        This is needed to automate the form rendering. It allows to configure the
        form in a standard way, with crispy forms, and then just alter the type field
        to contain hx-get attribute triggering a get request for the right detail form.
        """

        if isinstance(response, TemplateResponse) and not response.is_rendered:
            context_is_right = (
                "form" in response.context_data and
                "detail" in response.context_data["form"].fields and
                "type" in response.context_data["form"].fields
            )
            if context_is_right:
                # Set hx-get to the current path with a query parameter to
                # account for both updates and creates
                form_field = response.context_data["form"].fields["type"]
                form_field.widget.attrs["hx-get"] = f"{self.request.path}"

        return response
    
    def swap_detail_form(self, request, initial=None) -> HttpResponse:
        """Swap the detail form in the main form template based on selected type."""

        detail_form_class = self.get_detail_form_class(request)

        if not initial:
            initial = {}
        
        # THis is a week point, it might fail if the form is not bound
        detail_form = detail_form_class(initial=initial)
        
        # Render the detail form template
        return render(
            request,
            self.partial_form_template,
            {"form": detail_form}
        )
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.add_hx_get(response)
        return response
    

    
class WatersyncCreateView(
    LoginRequiredMixin,
    HTMXFormMixin,
    WatersyncGenericViewProperties,
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

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial["user"] = self.request.user.pk
        return initial

    
    def get(self, request, *args, **kwargs):
        # Check if this is a request for the detail form
        # This had to be done here because the swap of the form is handled by
        # HTMX and via the hx-get attribute in the form field
        if request.htmx and request.GET.get("type"):
            return self.swap_detail_form(request)
        
        return super().get(request, *args, **kwargs)


class WatersyncDeleteView(
    LoginRequiredMixin,
    RenderToResponseMixin,
    WatersyncGenericViewProperties,
    SuccessMessageMixin,
    DeleteView,
):
    """Delete logic for watersync DeleteViews.

    The largest chunk here is about redirecting after the delete. After the delete,
    the user will be redirected to the list view, if the request is made from the detail
    view of the deleted object, or to the current URL if the request is made
    from elswhere."""

    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

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
    WatersyncGenericViewProperties,
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
    RenderToResponseMixin,
    WatersyncGenericViewProperties,
    DetailView,
):
    
    template_name = "detail.html"
    htmx_template = "detail.html"
    detail_type: str | None = None

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs[self.item_pk_name])

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        base_kwargs = self.get_base_url_kwargs()
        item_kwargs = {**base_kwargs, **self.item}

        detail_context = DetailContext(
            delete_url=self.get_delete_url()(kwargs=item_kwargs),
            update_url=self.get_update_url()(kwargs=item_kwargs),
        )

        context["detail_context"] = detail_context

        return context
