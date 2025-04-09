from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied
from watersync.users.models import User
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class ApprovalRequiredMixin(AccessMixin):
    """
    Mixin that verifies the user is approved by admin.
    """
    def get_approval_pending_url(self):
        from django.urls import reverse
        return reverse("users:approval-pending")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user = request.user
        is_approved = User.objects.filter(id=user.id, is_approved=True).exists()
        
        if not is_approved:
            return redirect(self.get_approval_pending_url())
        
        return super().dispatch(request, *args, **kwargs)

class ProjectPermissionMixin(UserPassesTestMixin):
    """
    Mixin that verifies the user has permission to access the project.
    """
    def test_func(self):
        project_id = self.kwargs.get("project_id")
        if not project_id:
            return False

        return self.request.user.projects.filter(id=project_id).exists()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied
        return super().handle_no_permission()

