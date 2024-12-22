from django.urls import path

from .views import SettingsView, user_detail_view, user_redirect_view, user_update_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
]

urlpatterns += [
    path(
        "<int:user_id>/settings/",
        SettingsView.as_view(template_name="users/settings/settings.html"),
        name="settings",
    )
]
