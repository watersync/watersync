from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from rest_framework.exceptions import PermissionDenied

from watersync.users.models import User


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
    
    For views without project_pk in the URL (e.g., creating a new project),
    the check is skipped and access is allowed.
    """
    def test_func(self):
        project_pk = self.kwargs.get("project_pk")
        if not project_pk:
            # No project_pk means this isn't a project-scoped view
            # (e.g., creating a new project) - allow access
            return True

        return self.request.user.projects.filter(pk=project_pk).exists()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied
        return super().handle_no_permission()


class UserOwnershipMixin(UserPassesTestMixin):
    """
    Mixin that verifies the user owns the object (via user M2M).
    
    Used for models with direct user relationship like Sensor.
    For list views (no object pk), always passes - queryset filtering handles access.
    For detail/update/delete views, checks user is in object's user M2M.
    """
    # Override in subclass to specify the pk kwarg name
    object_pk_kwarg = None
    
    def test_func(self):
        # Determine pk kwarg name from model if not set
        pk_kwarg = self.object_pk_kwarg
        if not pk_kwarg and hasattr(self, 'model'):
            pk_kwarg = f"{self.model._meta.model_name}_pk"
        
        object_pk = self.kwargs.get(pk_kwarg)
        
        # List views don't have object pk - rely on queryset filtering
        if not object_pk:
            return True
        
        # Check user owns the object
        model = self.model if hasattr(self, 'model') else self.get_queryset().model
        return model.objects.filter(pk=object_pk, user=self.request.user).exists()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied
        return super().handle_no_permission()

