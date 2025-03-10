# ========================= Fieldwork views ============================ #
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.forms import ModelForm
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    DetailView,
)

from watersync.core.forms import FieldworkForm
from watersync.core.views.base import WatersyncListView
from watersync.core.mixins import HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, Fieldwork, Project


class FieldworkCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Fieldwork
    form_class = FieldworkForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "fieldworkChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])


class FieldworkUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Fieldwork
    form_class = FieldworkForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "FieldworkChanged"
    htmx_render_template = "shared/simple_form.html"

    def update_form_instance(self, form: ModelForm):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )

    def get_object(self):
        return get_object_or_404(Fieldwork, pk=self.kwargs["fieldwork_pk"])


class FieldworkDeleteView(LoginRequiredMixin, RenderToResponseMixin, DeleteView):
    model = Fieldwork
    template_name = "confirm_delete.html"
    htmx_template = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(Fieldwork, pk=self.kwargs["fieldwork_pk"])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])

        if request.headers.get("HX-Request"):
            sensors_url = reverse(
                "core:fieldworks",
                kwargs={"user_id": self.kwargs["user_id"], "project_pk": project.pk},
            )
            return HttpResponse(
                status=204,
                headers={
                    "HX-Trigger": "configRequest",
                    "HX-Redirect": sensors_url,
                },
            )
        return super().delete(request, *args, **kwargs)


class FieldworkListView(WatersyncListView):
    model = Fieldwork
    detail_type = "offcanvas"

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return project.fieldworks.order_by("-created")


class FieldworkDetailView(LoginRequiredMixin, RenderToResponseMixin, DetailView):
    model = Fieldwork
    template_name = "core/fieldwork_detail.html"
    htmx_template = "core/fieldwork_detail.html"

    def get_object(self):
        return get_object_or_404(Fieldwork, pk=self.kwargs["fieldwork_pk"])


fieldwork_create_view = FieldworkCreateView.as_view()
fieldwork_detail_view = FieldworkDetailView.as_view()
fieldwork_list_view = FieldworkListView.as_view()
fieldwork_delete_view = FieldworkDeleteView.as_view()
fieldwork_update_view = FieldworkUpdateView.as_view()
