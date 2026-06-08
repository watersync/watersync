"""Factories for core models."""

import factory
from django.contrib.gis.geos import Point, Polygon
from factory.django import DjangoModelFactory

from watersync.core.models import Fieldwork, Location, Project
from watersync.users.tests.factories import UserFactory


class ProjectFactory(DjangoModelFactory):
    """Factory for Project model."""

    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker("paragraph")
    start_date = factory.Faker("date_object")

    class Meta:
        model = Project

    @factory.post_generation
    def user(self, create, extracted, **kwargs):
        """Add users to project after creation."""
        if not create:
            return
        if extracted:
            for user in extracted:
                self.user.add(user)
        else:
            # Add a default user
            self.user.add(UserFactory())


class LocationFactory(DjangoModelFactory):
    """Factory for Location model."""

    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f"Location {n}")
    geom = factory.LazyFunction(lambda: Point(0, 0, 0, srid=4326))
    type = Location.LocationTypes.PIEZOMETER
    status = Location.StatusChoices.OPERATIONAL

    class Meta:
        model = Location


class FieldworkFactory(DjangoModelFactory):
    """Factory for Fieldwork model."""

    project = factory.SubFactory(ProjectFactory)
    date = factory.Faker("date_object")
    start_time = factory.Faker("time_object")
    end_time = factory.Faker("time_object")
    weather = Fieldwork.WeatherConditions.SUNNY

    class Meta:
        model = Fieldwork

    @factory.post_generation
    def user(self, create, extracted, **kwargs):
        """Add users to fieldwork after creation."""
        if not create:
            return
        if extracted:
            for user in extracted:
                self.user.add(user)
