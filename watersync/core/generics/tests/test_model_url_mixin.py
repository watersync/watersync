"""Tests for ModelURLMixin functionality.

These tests verify that models using ModelURLMixin correctly generate
URLs for CRUD operations, eliminating the need for placeholder-based
URL building in templates.
"""

from datetime import date

from django.contrib.gis.geos import Point

import pytest

from watersync.core.models import Fieldwork, Location, Project
from watersync.groundwater.models import GWLManualMeasurement
from watersync.sensor.models import Deployment, Sensor
from watersync.users.tests.factories import UserFactory
from watersync.waterquality.models import Measurement, Sample
from watersync.waterquality.models_setup import Protocol


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def project(db, user):
    project = Project.objects.create(name="Test Project")
    project.user.add(user)
    return project


@pytest.fixture
def location(db, project):
    return Location.objects.create(
        project=project,
        name="Test Location",
        geom=Point(0, 0, 0),
        type=Location.LocationTypes.WELL,
    )


@pytest.fixture
def fieldwork(db, project, user):
    fw = Fieldwork.objects.create(
        project=project,
        date=date.today(),
    )
    fw.user.add(user)  # M2M field needs .add()
    return fw


@pytest.fixture
def measurement(db, sample):
    return Measurement.objects.create(
        sample=sample,
        parameter="pH",
        value=7.0,
    )


@pytest.fixture
def sensor(db, user):
    s = Sensor.objects.create(
        identifier="TEST-SENSOR-001",
    )
    s.user.add(user)  # M2M field needs .add()
    return s


@pytest.fixture
def deployment(db, location, sensor):
    return Deployment.objects.create(
        location=location,
        sensor=sensor,
        variable="temperature",
        unit="degC",
    )


@pytest.fixture
def gwl_measurement(db, location, fieldwork):
    return GWLManualMeasurement.objects.create(
        location=location,
        fieldwork=fieldwork,
        value=5.0,
    )


@pytest.fixture
def protocol(db):
    return Protocol.objects.create(
        method_name="Test Protocol",
    )


@pytest.fixture
def sample(db, location, fieldwork, protocol):
    return Sample.objects.create(
        location=location,
        fieldwork=fieldwork,
        protocol=protocol,
        parameter_group="physico_chemical",
    )

