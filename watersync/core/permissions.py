from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Project


class IsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied
        return super().handle_no_permission()


class HasProjectAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        project = request.query_params.get("project")
        if not project:
            return False

        if not Project.objects.filter(name=project).exists():
            raise NotFound("Project not found!")

        if not Project.objects.filter(name=project, user=request.user).exists():
            raise PermissionDenied("You do not have permission to access this project.")

        return True
