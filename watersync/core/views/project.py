from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from watersync.core.forms import ProjectForm
from watersync.core.mixins import HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Project


class ProjectCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "projectChanged"
    htmx_render_template = "shared/simple_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user not in form.instance.user.all():
            form.instance.user.add(self.request.user)
        return response


class ProjectListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = Project
    template_name = "core/partial/project_list.html"
    htmx_template = "core/partial/project_table.html"

    def get_queryset(self):
        return self.request.user.projects.all()


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "core/project_detail.html"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])


class ProjectUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "core/project_form.html"

    htmx_trigger_header = "locationChanged"
    htmx_render_template = "core/location_form.html"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])

    def update_form_instance(self, form):
        instance = form.instance

        selected_users = form.cleaned_data.get("users", [])

        requesting_user = self.request.user
        if requesting_user not in selected_users:
            selected_users.append(requesting_user)

        instance.user.set(selected_users)

        return instance


class ProjectDeleteView(LoginRequiredMixin, RenderToResponseMixin, DeleteView):
    model = Project
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"
    htmx_redirect = ""

    def get_object(self):
        return get_object_or_404(
            Project, pk=self.kwargs["project_pk"], user=self.request.user
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get("HX-Request"):
            projects_url = reverse(
                "core:projects", kwargs={"user_id": self.kwargs["user_id"]}
            )
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "configRequest",
                    "HX-Redirect": projects_url,
                },
            )
        return super().delete(request, *args, **kwargs)


project_create_view = ProjectCreateView.as_view()
project_delete_view = ProjectDeleteView.as_view()
project_update_view = ProjectUpdateView.as_view()
project_detail_view = ProjectDetailView.as_view()
project_list_view = ProjectListView.as_view()
