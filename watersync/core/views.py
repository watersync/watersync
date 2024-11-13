from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.http import HttpResponse
from django.template.loader import render_to_string
from watersync.groundwater.views import GWLListView
from watersync.sensor.views import DeploymentListView
from watersync.waterquality.views import SampleListView, SamplingEventListView
from django.http import JsonResponse, HttpResponse
from .forms import LocationForm
from .forms import LocationStatusForm
from .forms import ProjectForm
from .models import Location
from .models import LocationStatus
from .models import Project
from watersync.waterquality.forms import SamplingEventForm
from watersync.groundwater.forms import GWLForm



class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "core/project_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        if not self.object.user.filter(pk=self.request.user.pk).exists():
            self.object.user.add(self.request.user)

        return response

    def get_success_url(self):
        return reverse("core:projects", kwargs={"user_id": self.request.user.id})


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 6
    template_name = "core/project_list.html"

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(user=user)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "core/project_detail.html"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "core/project_form.html"

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs["project_pk"])

    def get_success_url(self):
        return reverse(
            "core:detail-project",
            kwargs={
                "user_id": self.request.user.id,
                "project_pk": self.kwargs["project_pk"],
            },
        )


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(
            Project, pk=self.kwargs["project_pk"], user=self.request.user
        )

    def get_success_url(self):
        return reverse("core:projects", kwargs={"user_id": self.request.user.pk})


# Exporting just the .as_view() elements
project_create_view = ProjectCreateView.as_view()
project_delete_view = ProjectDeleteView.as_view()
project_update_view = ProjectUpdateView.as_view()
project_detail_view = ProjectDetailView.as_view()
project_list_view = ProjectListView.as_view()


# ========================= Location status views ============================ #
class LocationStatusCreateView(LoginRequiredMixin, CreateView):
    model = LocationStatus
    form_class = LocationStatusForm
    template_name = "core/location_status_form.html"

    def form_valid(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )
        response = super().form_valid(form)
        
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={"HX-Trigger": "locationStatusChanged"})
        
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            # Render the form again if it is invalid, as part of the modal content
            context = self.get_context_data(form=form)
            html = render_to_string(self.template_name, context, request=self.request)
            return HttpResponse(html, status=400)

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])

        return context

    def get_success_url(self):
        return reverse(
            "core:detail-location",
            kwargs={
                "user_id": self.request.user.id,
                "project_pk": self.kwargs["project_pk"],
                "location_pk": self.kwargs["location_pk"],
            },
        )


class LocationStatusListView(LoginRequiredMixin, ListView):
    model = LocationStatus
    template_name = "core/location_status_list.html"

    def get_queryset(self):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        return LocationStatus.objects.filter(location=location).order_by("-created_at")

    def render_to_response(self, context, **response_kwargs):
        location = get_object_or_404(Location, pk=self.kwargs["location_pk"])
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context['project'] = project
        context['location'] = location

        if self.request.headers.get('HX-Request'):
            html = render_to_string("core/partial/locationstatus_table.html", context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)


class LocationStatusDeleteView(LoginRequiredMixin, DeleteView):
    model = LocationStatus

    def get_object(self):
        return get_object_or_404(
            LocationStatus,
            pk=self.kwargs["locationstatus_pk"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={"HX-Trigger": "configRequest"})
        return super().delete(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            html = render_to_string("confirm_delete.html", context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)

class LocationStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = LocationStatus
    form_class = LocationStatusForm
    template_name = "core/location_status_form.html"

    def form_valid(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )
        response = super().form_valid(form)
        
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={"HX-Trigger": "locationStatusChanged"})
        
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            # Render the form again if it is invalid, as part of the modal content
            context = self.get_context_data(form=form)
            html = render_to_string(self.template_name, context, request=self.request)
            return HttpResponse(html, status=400)

        return super().form_invalid(form)

    def get_object(self):
        return get_object_or_404(LocationStatus, pk=self.kwargs["locationstatus_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context["location"] = get_object_or_404(Location, pk=self.kwargs["location_pk"])

        return context

    def get_success_url(self):
        return reverse(
            "core:detail-location",
            kwargs={
                "user_id": self.request.user.id,
                "project_pk": self.kwargs["project_pk"],
                "location_pk": self.kwargs["location_pk"],
            },
        )


location_status_create_view = LocationStatusCreateView.as_view()
location_status_list_view = LocationStatusListView.as_view()
location_status_delete_view = LocationStatusDeleteView.as_view()
location_status_update_view = LocationStatusUpdateView.as_view()


# ========================= Location views ============================ #


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "core/location_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return context
    
    def form_valid(self, form):
        form.instance.location = get_object_or_404(
            Location, pk=self.kwargs["location_pk"]
        )
        response = super().form_valid(form)
        
        if self.request.headers.get('HX-Request'):
            return HttpResponse(status=204, headers={"HX-Trigger": "locationChanged"})
        
        return response

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            # Render the form again if it is invalid, as part of the modal content
            context = self.get_context_data(form=form)
            html = render_to_string(self.template_name, context, request=self.request)
            return HttpResponse(html, status=400)

        return super().form_invalid(form)

class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = "confirm_delete.html"

    def get_object(self):
        return get_object_or_404(
            Location,
            pk=self.kwargs["location_pk"],
            project__pk=self.kwargs["project_pk"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])

    def get_success_url(self):
        return reverse(
            "core:locations",
            kwargs={
                "user_id": self.request.user.id,
                "project_pk": self.kwargs["project_pk"],
            },
        )


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "core/location_form.html"

    def get_object(self):
        return get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def get_success_url(self):
        return reverse(
            "core:detail-location",
            kwargs={
                "user_id": self.request.user.id,
                "project_pk": self.kwargs["project_pk"],
                "location_pk": self.kwargs["location_pk"],
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])

        return context


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = "core/partial/location_list.html"

    def get_queryset(self):
        project_id = self.kwargs.get("project_pk")
        user = self.request.user

        project = get_object_or_404(Project, id=project_id, user=user)

        return Location.objects.filter(project=project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["created_at"] = timezone.now()
        context["project"] = get_object_or_404(Project, id=self.kwargs["project_pk"])
        return context
    
    def render_to_response(self, context, **response_kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        context['project'] = project

        if self.request.headers.get('HX-Request'):
            html = render_to_string("core/partial/location_table.html", context, request=self.request)
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)



class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = "core/location_detail.html"

    def get_object(self):
        # Retrieve the location object based on the project and location primary keys
        return get_object_or_404(
            Location,
            pk=self.kwargs["location_pk"],
            project__pk=self.kwargs["project_pk"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = self.get_object()

        location_status_view = LocationStatusListView()
        gwl_list_view = GWLListView()
        deployment_view = DeploymentListView()
        sample_view = SampleListView()
        samplingevent_list_view = SamplingEventListView()
        samplingevent_list_view.request = self.request
        samplingevent_list_view.kwargs = self.kwargs
        location_status_view.request = self.request
        location_status_view.kwargs = self.kwargs
        gwl_list_view.request = self.request
        gwl_list_view.kwargs = self.kwargs
        deployment_view.request = self.request
        deployment_view.kwargs = self.kwargs
        sample_view.request = self.request
        sample_view.kwargs = self.kwargs

        context["project"] = location.project
        context["deployment_list"] = deployment_view.get_queryset()
        
        context["locationstatus_list"] = location_status_view.get_queryset()
        context["locationstatus_form"] = LocationStatusForm()
        
        context["gwlmanualmeasurements_list"] = gwl_list_view.get_queryset()
        context["gwlmeasurement_form"] = GWLForm()
        
        context["samplingevent_list"] = samplingevent_list_view.get_queryset()
        context["samplingevent_form"] = SamplingEventForm()

        context["sample_list"] = sample_view.get_queryset()

        return context

# Exporting just the .as_view() elements
location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_list_view = LocationListView.as_view()
