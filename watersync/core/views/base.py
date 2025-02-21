from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from watersync.core.mixins import HTMXFormMixin, RenderToResponseMixin


class WatersyncCreateView(LoginRequiredMixin, HTMXFormMixin, CreateView):
    class Meta:
        abstract = True


class WatersyncListView(LoginRequiredMixin, RenderToResponseMixin, ListView):
    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        if "projects" in self.request.path:
            base_template = "project_dashboard.html"
        else:
            base_template = "base_dashboard.html"

        return super().get_context_data(
            base_template=base_template,
            **kwargs,
        )
