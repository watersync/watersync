from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from watersync.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls
