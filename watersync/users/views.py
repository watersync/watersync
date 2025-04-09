from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, TemplateView, UpdateView

from watersync.users.models import User
from watersync.waterquality.forms import ProtocolForm
from watersync.waterquality.views import ProtocolListView
from watersync.core.generics.utils import get_resource_list_context
from watersync.core.permissions import ApprovalRequiredMixin


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


class SettingsView(LoginRequiredMixin, ApprovalRequiredMixin, TemplateView):
    template_name = "users/settings/settings.html"

    def get_resource_list_context(self, **kwargs):
        views = {"protocols": ProtocolListView}
        return get_resource_list_context(self.request, self.kwargs, views)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_resource_list_context())
        return context

class ApprovalPendingView(TemplateView):
    template_name = 'users/approval_pending.html'


settings_view = SettingsView.as_view()
approval_pending_view = ApprovalPendingView.as_view()