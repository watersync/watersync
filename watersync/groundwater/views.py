from watersync.core.generics.mixins import FilterMixin
from watersync.core.generics.views import (
    WatersyncCreateView,
    WatersyncDeleteView,
    WatersyncListView,
)
from watersync.groundwater.filters import GWLMeasurementFilter
from watersync.groundwater.forms import GWLForm
from watersync.groundwater.models import GWLManualMeasurement


class GWLCreateView(WatersyncCreateView):
    model = GWLManualMeasurement
    form_class = GWLForm


class GWLDeleteView(WatersyncDeleteView):
    model = GWLManualMeasurement


class GWLListView(FilterMixin, WatersyncListView):
    model = GWLManualMeasurement
    detail_type = "popover"
    filterset_class = GWLMeasurementFilter

    def get_base_queryset(self):
        """Get the base queryset before filtering."""
        return GWLManualMeasurement.objects.for_project(
            self.kwargs["project_pk"]
        ).order_by("-fieldwork__date")



gwl_list_view = GWLListView.as_view()
gwl_create_view = GWLCreateView.as_view()
gwl_delete_view = GWLDeleteView.as_view()
