from rest_framework import serializers
from ..models import Project, LocationStatus, Location


class ProjectSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationStatus
        fields = "__all__"
