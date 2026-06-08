from rest_framework import serializers

from watersync.core.models import Fieldwork, Location, Project


class ProjectSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class FieldworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fieldwork
        fields = "__all__"
