from django.http import HttpRequest, HttpResponse
from watersync.users.models import User
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView)
from watersync.groundwater.views import GWLListView
from watersync.sensor.views import DeploymentListView
from .models import Project, Location
from .forms import ProjectForm, LocationForm
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

# Project views


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)

        if not self.object.user.filter(pk=self.request.user.pk).exists():
            self.object.user.add(self.request.user)

        return response

    def get_success_url(self):
        return reverse('core:projects',
                       kwargs={'user_id': self.request.user.id})


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 6
    template_name = 'core/project_list.html'

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(user=user)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'core/project_detail.html'

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])

    def get_success_url(self):
        return reverse('core:detail-project',
                       kwargs={'user_id': self.request.user.id,
                               'project_pk': self.kwargs['project_pk']})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'confirm_delete.html'

    def get_object(self):
        return get_object_or_404(Project,
                                 pk=self.kwargs['project_pk'],
                                 user=self.request.user)

    def get_success_url(self):
        return reverse('core:projects',
                       kwargs={'user_id': self.request.user.pk})


# Exporting just the .as_view() elements
project_create_view = ProjectCreateView.as_view()
project_delete_view = ProjectDeleteView.as_view()
project_update_view = ProjectUpdateView.as_view()
project_detail_view = ProjectDetailView.as_view()
project_list_view = ProjectListView.as_view()

# ========================= Location views ============================ #


class LocationCreateView(CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'core/location_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(
            Project, pk=self.kwargs['project_pk'])
        return context

    def form_valid(self, form):
        form.instance.project = get_object_or_404(
            Project, pk=self.kwargs['project_pk'])
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('core:locations', kwargs={
            'user_id': self.request.user.id,
            'project_pk': self.kwargs['project_pk']
        })


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = 'core/location_confirm_delete.html'

    def get_object(self):
        return get_object_or_404(Location, pk=self.kwargs['location_pk'], project__pk=self.kwargs['project_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure 'user' is passed to the template
        context['user'] = self.request.user
        context['project'] = get_object_or_404(
            Project, pk=self.kwargs['project_pk'])  # Add project to context
        return context

    def get_success_url(self):
        return reverse('core:locations', kwargs={
            'user_id': self.request.user.id,
            'project_pk': self.kwargs['project_pk']
        })


class LocationUpdateView(UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'core/location_update_form.html'
    success_url = reverse_lazy('core:list')


class LocationListView(ListView):
    model = Location
    template_name = 'core/location_list.html'

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        user = self.request.user

        # Retrieve the project and check if the user has access
        project = get_object_or_404(Project, id=project_id, user=user)

        # Filter locations by the project
        return Location.objects.filter(project=project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created_at'] = timezone.now()
        context['project'] = get_object_or_404(
            Project, id=self.kwargs['project_pk'])
        return context


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = 'core/location_detail.html'

    def get_object(self):
        # Retrieve the location object based on the project and location primary keys
        return get_object_or_404(Location, pk=self.kwargs['location_pk'], project__pk=self.kwargs['project_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = self.get_object()  # Get the location object

        # Reuse the GWLListView's get_queryset method to get the measurements
        gwl_list_view = GWLListView()
        deployment_view = DeploymentListView()
        gwl_list_view.request = self.request  # Pass the request to the list view
        gwl_list_view.kwargs = self.kwargs  # Pass the kwargs to the list view
        deployment_view.request = self.request
        deployment_view.kwargs = self.kwargs
        # Get the queryset
        context['gwlmanualmeasurements_list'] = gwl_list_view.get_queryset()
        context['deployment_list'] = deployment_view.get_queryset()

        context['project'] = location.project  # Add the project to the context
        return context


# Exporting just the .as_view() elements
location_create_view = LocationCreateView.as_view()
location_delete_view = LocationDeleteView.as_view()
location_update_view = LocationUpdateView.as_view()
location_detail_view = LocationDetailView.as_view()
location_list_view = LocationListView.as_view()
