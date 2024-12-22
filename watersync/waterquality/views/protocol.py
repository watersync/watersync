from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from watersync.core.mixins import DeleteHTMX, HTMXFormMixin, RenderToResponseMixin
from watersync.waterquality.forms import (
    ProtocolForm,
)
from watersync.waterquality.models import Protocol


class ProtocolCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    model = Protocol
    form_class = ProtocolForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "protocolChanged"
    htmx_render_template = "shared/simple_form.html"


class ProtocolUpdateView(LoginRequiredMixin, HTMXFormMixin, UpdateView):
    model = Protocol
    form_class = ProtocolForm
    template_name = "shared/simple_form.html"

    htmx_trigger_header = "protocolChanged"
    htmx_render_template = "shared/simple_form.html"

    def get_object(self):
        return get_object_or_404(Protocol, pk=self.kwargs["protocol_pk"])


class ProtocolDeleteView(LoginRequiredMixin, DeleteHTMX, DeleteView):
    model = Protocol
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(Protocol, pk=self.kwargs["protocol_pk"])


class ProtocolListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    model = Protocol
    template_name = "waterquality/partial/protocol_list.html"
    htmx_template = "waterquality/partial/protocol_table.html"

    def get_queryset(self):
        return Protocol.objects.all()


class ProtocolDetailView(LoginRequiredMixin, DetailView):
    model = Protocol
    template_name = "waterquality/partial/protocol_detail.html"

    def get_object(self):
        return get_object_or_404(Protocol, pk=self.kwargs["protocol_pk"])


protocol_create_view = ProtocolCreateView.as_view()
protocol_update_view = ProtocolUpdateView.as_view()
protocol_delete_view = ProtocolDeleteView.as_view()
protocol_list_view = ProtocolListView.as_view()
protocol_detail_view = ProtocolDetailView.as_view()
