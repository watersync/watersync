from watersync.core.models import Location, Project
from watersync.groundwater.forms import GWLForm
from watersync.groundwater.models import GWLManualMeasurement
from watersync.core.generics.views import WatersyncCreateView, WatersyncUpdateView, WatersyncDeleteView, WatersyncListView
from watersync.core.generics.decorators import filter_by_location

from django.shortcuts import get_list_or_404


class GWLCreateView(WatersyncCreateView):
    model = GWLManualMeasurement
    form_class = GWLForm

class GWLUpdateView(WatersyncUpdateView):
    model = GWLManualMeasurement
    form_class = GWLForm


class GWLDeleteView(WatersyncDeleteView):
    model = GWLManualMeasurement


class GWLListView(WatersyncListView):
    model = GWLManualMeasurement
    detail_type = "popover"

    @filter_by_location
    def get_queryset(self):
        """Get the queryset for the list view."""
        project = self.get_project()
        locations = project.locations.all()
        return GWLManualMeasurement.objects.filter(
            location_visit__location__in=locations
        ).order_by("-location_visit__date")



gwl_list_view = GWLListView.as_view()
gwl_create_view = GWLCreateView.as_view()
gwl_update_view = GWLUpdateView.as_view()
gwl_delete_view = GWLDeleteView.as_view()
