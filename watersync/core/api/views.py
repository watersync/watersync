from rest_framework import permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from watersync.users.models import User

from watersync.core.models import Location, LocationVisit, Project, Fieldwork
from watersync.core.api.serializers import (
    LocationSerializer,
    ProjectSerializer,
    VisitSerializer,
    FieldworkSerializer,
)


class BaseListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]


class LocationViewSet(BaseListViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class FieldworkViewSet(BaseListViewSet):
    queryset = Fieldwork.objects.all()
    serializer_class = FieldworkSerializer


class VisitViewSet(BaseListViewSet):
    queryset = LocationVisit.objects.all()
    serializer_class = VisitSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """Fetch project based on the name."""

        try:
            project = Project.objects.get(name=kwargs["pk"])
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(project)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_emails = request.data.pop("user", [])

        if not user_emails:
            user_emails = [request.user.email]

        users = []
        for email in user_emails:
            user, created = User.objects.get_or_create(email=email)
            users.append(user)

        project_data = request.data
        project_data["user"] = [user.id for user in users]

        serializer = self.get_serializer(data=project_data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()

        # Associate users with the project
        project.user.set(users)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
