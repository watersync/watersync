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
from watersync.core.views.base import WatersyncListView, WatersyncCreateView, WatersyncDeleteView, WatersyncUpdateView
from watersync.core.mixins import HTMXFormMixin, RenderToResponseMixin
from watersync.core.models import Location, Fieldwork, Project


class FieldworkCreateView(WatersyncCreateView):
    model = Fieldwork
    form_class = FieldworkForm

    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])


class FieldworkUpdateView(WatersyncUpdateView):
    model = Fieldwork
    form_class = FieldworkForm
    
    def update_form_instance(self, form):
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])


class FieldworkDeleteView(WatersyncDeleteView):
    model = Fieldwork

    def get_object(self):
        return get_object_or_404(Fieldwork, pk=self.kwargs["fieldwork_pk"])


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
