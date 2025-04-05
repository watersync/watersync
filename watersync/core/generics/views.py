"""Module for the base views of the application.

The idea is to abstract as much as possible the common logic between the views for the different models.

TODO:
    - I implemented a smarter check of the base template. Now it's done in the view itself and does not
    require passing the blank template. Simply when the htmx_context is "block", we set the list template_name to
    one that has only the html element in it. list_page.html contains a reference to the base template and includes the
    list.html template. The base_template is not required in the with -- include statement in the template. Would be good to
    unify these two approaches a bit.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView,
)
from watersync.core.generics.htmx import HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Project
from watersync.core.generics.mixins import ExportCsvMixin, ListContext
from watersync.core.generics.mixins import DetailContext
from functools import partial
from django.urls import reverse


class WatersyncGenericViewProperties:
    """Mixin to add shortcuts to the views."""

    blank_template = "layouts/blank.html"
    base_template = "layouts/base_dashboard.html"
    project_base_template = "layouts/project_dashboard.html"

    class Meta:
        abstract = True

    @property
    def model_name(self):
        """Shortcut to get the model name."""
        return self.model._meta.model_name

    @property
    def model_name_plural(self):
        """Shortcut to get the plural model name."""
        return self.model._meta.verbose_name_plural.replace(" ", "")

    @property
    def app_label(self):
        """Shortcut to get the app label."""
        return self.model._meta.app_label

    @property
    def htmx_trigger(self):
        """Get the HTMX action name of the view."""
        return f"{self.model_name}Changed"

    @property
    def list_url(self):
        """Url name for the list view."""
        return f"{self.app_label}:{self.model_name_plural}"

    @property
    def add_url(self):
        """Url name for the add view."""
        return f"{self.app_label}:add-{self.model_name}"

    @property
    def update_url(self):
        """Url name for the update view."""
        return f"{self.app_label}:update-{self.model_name}"

    @property
    def delete_url(self):
        """Url name for the delete view."""
        return f"{self.app_label}:delete-{self.model_name}"

    @property
    def detail_url(self):
        """Url name for the detail view."""
        return f"{self.app_label}:detail-{self.model_name}"

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
    
    def get_list_url(self):
        return partial(reverse, self.list_url)

    def get_add_url(self):
        return partial(reverse, self.add_url)

    def get_update_url(self):
        return partial(reverse, self.update_url)

    def get_delete_url(self):
        return partial(reverse, self.delete_url)

    def get_detail_url(self):
        return partial(reverse, self.detail_url)

    def get_project(self):
        """Get the project object from the URL."""
        if "projects" in self.request.path:
            return get_object_or_404(Project, pk=self.kwargs.get("project_pk"))
        else:
            return None
        
    def get_base_url_kwargs(self):
        base_kwargs = {"user_id": self.request.user.id}
        project = self.get_project()
        if project and self.model_name != "project":
            base_kwargs["project_pk"] = project.pk
        return base_kwargs
    
    def get_base_template(self, htmx_context: str) -> str:
        """Determine the appropriate base template based on context.
        
        For now we only check if htmx_context is "block". Then we return the blank template.
        In other cases, we check if projects is present in the URL. If it is, we return the project_base_template.
        Otherwise, we return the base_template.
        """
        if htmx_context == "block":
            return self.blank_template

        if "projects" in self.request.path:
            return self.project_base_template

        return self.base_template


class WatersyncListView(LoginRequiredMixin, RenderToResponseMixin, WatersyncGenericViewProperties, ExportCsvMixin, ListView):
    """Base view for listing objects.

    It contains the basic setup that is shared between all list views. The individual list view can override default
    settings by setting the class attributes.

    This view relies on use of generic names for items in the apps.

    For now, it all works on the premise that all the views are under the project view.

    I am not sure how to inject an additional url param to the reverse function kwargs. Now it automatically adds the
    user_id, project and item_pk to the kwargs. The item pk is normally called by the model name + _pk. Here it's computed
    from the generic model name. Then, a placeholder is added to the kwargs instead of the actual item pk. This is
    replaced in the template by the actual item pk from objects.

    Attributes:
        detail_type: The type of the detail view. It can be either "page" or "modal".
        template_name: The name of the template used for the list view.
        htmx_template: The name of the template used for the HTMX response. (it's normally the same as the template_name)

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

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.template_name = self.determine_template_name()

    def determine_template_name(self):
        """Determine the template name dynamically.

        If it's a page list, take a template called page_list.html. If it is an
        inserted list, take the template called list.html.
        """
        if self.request.headers.get("HX-Context") == "block":
            print("THIS IS A BLOCK LIST")
            return "list.html"
        print("THIS IS A PAGE LIST")
        return "list_page.html"

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Download"):
            queryset = self.get_queryset()
            return self.export_as_csv(request, queryset)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add common context data to the template.

        Resolves which base template is used for a given view and adds it to the context.
        Here we also add the project object, which is necessary to many views of models linked to the project.

        Base template is essentially the layout of the page.
        """
        context = super().get_context_data(**kwargs)

        project = self.get_project()

        if project:
            context["project"] = project

        htmx_context = self.request.headers.get("HX-Context")

        list_context = ListContext(
            add_url=self.get_add_url()(kwargs=self.get_base_url_kwargs()),
            list_url=self.get_list_url()(kwargs=self.get_base_url_kwargs()),
            update_url=self.get_update_url()(kwargs={**self.get_base_url_kwargs(), **self.item}),
            delete_url=self.get_delete_url()(kwargs={**self.get_base_url_kwargs(), **self.item}),
            action=self.htmx_trigger,
            columns=self.model._list_view_fields.keys(),
            explanation=self.model.__doc__.split("\n\n")[0],
            explanation_detail=self.model.__doc__.split("\n\n")[1],
            title=self.model._meta.verbose_name_plural,
        )

        if self.detail_type == "page":
            list_context.detail_page_url = self.get_detail_url()(
                kwargs={**self.get_base_url_kwargs(), **self.item}
            )

        elif self.detail_type == "popover":
            list_context.detail_popover = True

        elif self.detail_type == "modal":
            list_context.detail_url = self.get_detail_url()(
                kwargs={**self.get_base_url_kwargs(), **self.item}
            )

        context["base_template"] = self.get_base_template(htmx_context)
        context["list_context"] = list_context

        return context


class WatersyncCreateView(LoginRequiredMixin, HTMXFormMixin, WatersyncGenericViewProperties, CreateView):

    template_name = "shared/simple_form.html"
    htmx_render_template = "shared/simple_form.html"


class WatersyncDeleteView(LoginRequiredMixin, RenderToResponseMixin, WatersyncGenericViewProperties, DeleteView):
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

        current_url = request.headers.get("HX-Current-Url")

        if current_url and not current_url.endswith(f'/{self.object.pk}/'):
            return None
        else:
            return self.get_list_url()(kwargs=list_kwargs)



    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        redirect_url = self.get_redirect_url(request)

        if request.headers.get("HX-Request"):

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

        self.object.delete()

        return super().delete(request, *args, **kwargs)


class WatersyncUpdateView(LoginRequiredMixin, HTMXFormMixin, WatersyncGenericViewProperties, UpdateView):
    
    template_name = "shared/simple_form.html"
    htmx_render_template = "shared/simple_form.html"

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs[self.item_pk_name])
    

class WatersyncDetailView(LoginRequiredMixin, RenderToResponseMixin, WatersyncGenericViewProperties, DetailView):
    
    template_name = "detail.html"
    htmx_template = "detail.html"
    detail_type: str | None = None

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs[self.item_pk_name])
    
    def get_base_template(self, htmx_context: str) -> str:
        """Determine the appropriate base template based on context.
        
        For now we only check if htmx_context is "block". Then we return the blank template.
        In other cases, we check if projects is present in the URL. If it is, we return the project_base_template.
        Otherwise, we return the base_template.
        """
        if htmx_context == "block" or self.detail_type == "modal":
            return self.blank_template

        if "projects" in self.request.path:
            return self.project_base_template

        return self.base_template

    def get_context_data(self, **kwargs):
        """Add common context data to the template.

        Resolves which base template is used for a given view and adds it to the context.
        Here we also add the project object, which is necessary to many views of models linked to the project.

        Base template is essentially the layout of the page.
        """
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        
        if project:
            context["project"] = project

        htmx_context = self.request.headers.get("HX-Context")

        detail_context = DetailContext(
            delete_url=self.get_delete_url()(kwargs={**self.get_base_url_kwargs(), **self.item}),
            update_url=self.get_update_url()(kwargs={**self.get_base_url_kwargs(), **self.item}),
        )

        context["base_template"] = self.get_base_template(htmx_context)
        context["detail_context"] = detail_context
        
        return context
