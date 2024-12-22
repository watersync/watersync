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

class WatersyncDeleteView()