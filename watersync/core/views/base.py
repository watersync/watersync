from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_list_or_404, get_object_or_404, redirect

from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from watersync.core.models import Project
from watersync.core.mixins import HTMXFormMixin, RenderToResponseMixin, ListContext
from functools import partial
from django.urls import reverse


class WatersyncListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    """Base view for listing objects.

    It contains the basic setup that is shared between all list views. The individual list view can override default
    settings by setting the class attributes.

    This view relies on use of generic names for items in the apps.

    For now, it all works on the premise that all the views are under the project view.

    I am not sure how to inject an additional url param to the reverse function kwargs. Now it automatically adds the
    user_id, project and item_pk to the kwargs. The item pk is normally called by the model name + _pk. Here it's computed
    from the generic model name. Then, a placeholder is added to the kwargs instead of the actual item pk. This is
    replaced in the template by the actual item pk from objects.

    action: The HTMX action name that is triggered when the list is updated. Computed from the model name.
    urls: partial functions to generate the URLs for the views. Also rely on the generic names.
    """

    detail_type: str
    template_name = "list.html"
    htmx_template = "table.html"

    class Meta:
        abstract = True

    @property
    def model_name(self):
        """Shortcut to get the model name."""
        return self.model._meta.model_name

    @property
    def model_name_plural(self):
        """Shortcut to get the plural model name."""
        return self.model._meta.verbose_name_plural

    @property
    def app_label(self):
        """Shortcut to get the app label."""
        return self.model._meta.app_label

    @property
    def action(self):
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
        return get_object_or_404(Project, pk=self.kwargs.get("project_pk"))

    def get_context_data(self, **kwargs):
        """Add common context data to the template.

        Resolves which base template is used for a given view and adds it to the context.
        Here we also add the project object, which is necessary to many views of models linked to the project.

        Base template is essentially the layout of the page.
        """
        context = super().get_context_data(**kwargs)

        base_url_kwargs = {"user_id": self.request.user.id}

        if "projects" in self.request.path:
            base_template = "project_dashboard.html"
            context["project"] = self.get_project()
            base_url_kwargs["project_pk"] = context["project"].pk
        else:
            base_template = "base_dashboard.html"

        list_context = ListContext(
            add_url=self.get_add_url()(kwargs=base_url_kwargs),
            list_url=self.get_list_url()(kwargs=base_url_kwargs),
            update_url=self.get_update_url()(kwargs={**base_url_kwargs, **self.item}),
            delete_url=self.get_delete_url()(kwargs={**base_url_kwargs, **self.item}),
            action=self.action,
            columns=self.model.table_view_fields().keys(),
        )

        if self.detail_type == "page":
            list_context.detail_page_url = self.get_detail_url()(
                kwargs={**base_url_kwargs, **self.item}
            )
        else:
            list_context.detail_url = self.get_detail_url()(
                kwargs={**base_url_kwargs, **self.item}
            )

        context["base_template"] = base_template
        context["list_context"] = list_context

        return context


class WatersyncCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    class Meta:
        abstract = True
