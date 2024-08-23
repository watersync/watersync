from watersync.users.models import User
from django.views.generic import (
    CreateView, UpdateView, ListView, DeleteView, DetailView)
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
        # Save the project instance to get the primary key
        response = super().form_valid(form)

        # Add the current user to the project's user field
        self.object.user.add(self.request.user)

        return response

    def get_success_url(self):
        return reverse('core:projects', kwargs={'user_id': self.kwargs['user_id']})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])

    def get_success_url(self):
        return reverse('core:projects', kwargs={'user_id': self.kwargs['user_id']})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_update_form.html'

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])

    def get_success_url(self):
        return reverse('core:projects', kwargs={'user_id': self.kwargs['user_id']})


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 6
    template_name = 'core/project_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created_at'] = timezone.now()
        context['user'] = User.objects.get(pk=self.kwargs['user_id'])
        return context

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Project.objects.filter(user__id=user_id)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'core/project_detail.html'

    def get_object(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])

# Location views


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
    model = Project
    template_name = 'core/location_detail.html'

    def get_object(self):
        # Retrieve the location object based on the project and location primary keys
        return get_object_or_404(Location, pk=self.kwargs['location_pk'], project__pk=self.kwargs['project_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created_at'] = timezone.now()
        context['project'] = get_object_or_404(
            Project, pk=self.kwargs['project_pk'])
        return context
