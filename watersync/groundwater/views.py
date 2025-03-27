from watersync.core.models import Location, Project
from watersync.groundwater.forms import GWLForm
from watersync.groundwater.models import GWLManualMeasurement
from watersync.core.generics.base import WatersyncCreateView, WatersyncUpdateView, WatersyncDeleteView, WatersyncListView


from django.shortcuts import get_object_or_404, get_list_or_404


class GWLCreateView(WatersyncCreateView):
    model = GWLManualMeasurement
    form_class = GWLForm

    def update_form_instance(self, form):
        if "location_pk" in self.kwargs:
            form.instance.location = get_object_or_404(
                Location, pk=self.kwargs["location_pk"]
            )


class GWLUpdateView(WatersyncUpdateView):
    model = GWLManualMeasurement
    form_class = GWLForm

    def update_form_instance(self, form):
        if "location_pk" in self.kwargs:
            form.instance.location = get_object_or_404(
                Location, pk=self.kwargs["location_pk"]
            )


class GWLDeleteView(WatersyncDeleteView):
    model = GWLManualMeasurement


class GWLListView(WatersyncListView):
    model = GWLManualMeasurement
    detail_type = "popover"

    def get_queryset(self):
        if "location_pk" in self.kwargs:
            location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
            return location.gwlmeasurements.order_by("-measured_at")
        else:
            project = self.get_project()
            location = get_list_or_404(Location, project=project)
            return GWLManualMeasurement.objects.filter(location__in=location).order_by(
                "-measured_at"
            )


gwl_list_view = GWLListView.as_view()
gwl_create_view = GWLCreateView.as_view()
gwl_update_view = GWLUpdateView.as_view()
gwl_delete_view = GWLDeleteView.as_view()
