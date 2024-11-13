from django.urls import path

from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view
from .views import SettingsView

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
]

urlpatterns += [
    path("<int:user_id>/settings/", SettingsView.as_view(template_name="users/settings/settings.html"), name="settings")
]
