"""Tests for ModelURLMixin functionality.

These tests verify that models using ModelURLMixin correctly generate
URLs for CRUD operations, eliminating the need for placeholder-based
URL building in templates.
"""

import pytest
from datetime import date
from django.urls import reverse, NoReverseMatch
from django.contrib.gis.geos import Point
from django.utils import timezone

from watersync.core.models import Project, Location, Fieldwork
from watersync.waterquality.models import Sample, Measurement
from watersync.sensor.models import Sensor, Deployment
from watersync.groundwater.models import GWLManualMeasurement
from watersync.waterquality.models_setup import Protocol
from watersync.users.tests.factories import UserFactory


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
        unit="degC",  # Valid unit from config
        deployed_at=timezone.now(),
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


class TestProjectURLMixin:
    """Tests for Project model URL generation.
    
    Note: Project uses 'projects' not 'list-project' and 'detail-project' for detail.
    """

    def test_get_update_url(self, project):
        expected = reverse("core:update-project", kwargs={"project_pk": project.pk})
        assert project.get_update_url() == expected

    def test_get_delete_url(self, project):
        expected = reverse("core:delete-project", kwargs={"project_pk": project.pk})
        assert project.get_delete_url() == expected

    def test_get_detail_url(self, project):
        expected = reverse("core:detail-project", kwargs={"project_pk": project.pk})
        assert project.get_detail_url() == expected


class TestLocationURLMixin:
    """Tests for Location model URL generation."""

    def test_get_update_url(self, location):
        expected = reverse(
            "core:update-location",
            kwargs={"project_pk": location.project.pk, "location_pk": location.pk}
        )
        assert location.get_update_url() == expected

    def test_get_delete_url(self, location):
        expected = reverse(
            "core:delete-location",
            kwargs={"project_pk": location.project.pk, "location_pk": location.pk}
        )
        assert location.get_delete_url() == expected

    def test_get_detail_url(self, location):
        expected = reverse(
            "core:detail-location",
            kwargs={"project_pk": location.project.pk, "location_pk": location.pk}
        )
        assert location.get_detail_url() == expected

    def test_get_overview_url(self, location):
        expected = reverse(
            "core:overview-location",
            kwargs={"project_pk": location.project.pk, "location_pk": location.pk}
        )
        assert location.get_overview_url() == expected

    def test_get_add_url(self, project):
        expected = reverse("core:add-location", kwargs={"project_pk": project.pk})
        assert Location.get_add_url(parent=project) == expected


class TestFieldworkURLMixin:
    """Tests for Fieldwork model URL generation."""

    def test_get_update_url(self, fieldwork):
        expected = reverse(
            "core:update-fieldwork",
            kwargs={"project_pk": fieldwork.project.pk, "fieldwork_pk": fieldwork.pk}
        )
        assert fieldwork.get_update_url() == expected

    def test_get_delete_url(self, fieldwork):
        expected = reverse(
            "core:delete-fieldwork",
            kwargs={"project_pk": fieldwork.project.pk, "fieldwork_pk": fieldwork.pk}
        )
        assert fieldwork.get_delete_url() == expected

    def test_get_detail_url(self, fieldwork):
        expected = reverse(
            "core:detail-fieldwork",
            kwargs={"project_pk": fieldwork.project.pk, "fieldwork_pk": fieldwork.pk}
        )
        assert fieldwork.get_detail_url() == expected

    def test_get_overview_url(self, fieldwork):
        expected = reverse(
            "core:overview-fieldwork",
            kwargs={"project_pk": fieldwork.project.pk, "fieldwork_pk": fieldwork.pk}
        )
        assert fieldwork.get_overview_url() == expected


class TestSampleURLMixin:
    """Tests for Sample model URL generation."""

    def test_get_update_url(self, sample):
        expected = reverse(
            "waterquality:update-sample",
            kwargs={"project_pk": sample.location.project.pk, "sample_pk": sample.pk}
        )
        assert sample.get_update_url() == expected

    def test_get_delete_url(self, sample):
        expected = reverse(
            "waterquality:delete-sample",
            kwargs={"project_pk": sample.location.project.pk, "sample_pk": sample.pk}
        )
        assert sample.get_delete_url() == expected

    def test_get_detail_url(self, sample):
        expected = reverse(
            "waterquality:detail-sample",
            kwargs={"project_pk": sample.location.project.pk, "sample_pk": sample.pk}
        )
        assert sample.get_detail_url() == expected


class TestMeasurementURLMixin:
    """Tests for Measurement model URL generation."""

    def test_get_update_url(self, measurement):
        expected = reverse(
            "waterquality:update-measurement",
            kwargs={
                "project_pk": measurement.sample.location.project.pk,
                "measurement_pk": measurement.pk
            }
        )
        assert measurement.get_update_url() == expected

    def test_get_delete_url(self, measurement):
        expected = reverse(
            "waterquality:delete-measurement",
            kwargs={
                "project_pk": measurement.sample.location.project.pk,
                "measurement_pk": measurement.pk
            }
        )
        assert measurement.get_delete_url() == expected


class TestSensorURLMixin:
    """Tests for Sensor model URL generation (user-level, no parent)."""

    def test_get_update_url(self, sensor):
        expected = reverse("sensor:update-sensor", kwargs={"sensor_pk": sensor.pk})
        assert sensor.get_update_url() == expected

    def test_get_delete_url(self, sensor):
        expected = reverse("sensor:delete-sensor", kwargs={"sensor_pk": sensor.pk})
        assert sensor.get_delete_url() == expected

    def test_get_add_url(self, db):
        expected = reverse("sensor:add-sensor")
        assert Sensor.get_add_url() == expected


class TestDeploymentURLMixin:
    """Tests for Deployment model URL generation."""

    def test_get_update_url(self, deployment):
        expected = reverse(
            "sensor:update-deployment",
            kwargs={
                "project_pk": deployment.location.project.pk,
                "deployment_pk": deployment.pk
            }
        )
        assert deployment.get_update_url() == expected

    def test_get_delete_url(self, deployment):
        expected = reverse(
            "sensor:delete-deployment",
            kwargs={
                "project_pk": deployment.location.project.pk,
                "deployment_pk": deployment.pk
            }
        )
        assert deployment.get_delete_url() == expected


class TestGWLManualMeasurementURLMixin:
    """Tests for GWLManualMeasurement model URL generation."""

    def test_get_update_url(self, gwl_measurement):
        expected = reverse(
            "groundwater:update-gwlmanualmeasurement",
            kwargs={
                "project_pk": gwl_measurement.location.project.pk,
                "gwlmanualmeasurement_pk": gwl_measurement.pk
            }
        )
        assert gwl_measurement.get_update_url() == expected

    def test_get_delete_url(self, gwl_measurement):
        expected = reverse(
            "groundwater:delete-gwlmanualmeasurement",
            kwargs={
                "project_pk": gwl_measurement.location.project.pk,
                "gwlmanualmeasurement_pk": gwl_measurement.pk
            }
        )
        assert gwl_measurement.get_delete_url() == expected


class TestProtocolURLMixin:
    """Tests for Protocol model URL generation (user-level, no parent)."""

    def test_get_update_url(self, protocol):
        expected = reverse(
            "waterquality:update-protocol",
            kwargs={"protocol_pk": protocol.pk}
        )
        assert protocol.get_update_url() == expected

    def test_get_delete_url(self, protocol):
        expected = reverse(
            "waterquality:delete-protocol",
            kwargs={"protocol_pk": protocol.pk}
        )
        assert protocol.get_delete_url() == expected


class TestHistoryURLGracefulFailure:
    """Tests that history URLs fail gracefully when not available."""

    def test_history_url_returns_none_for_non_historical_model(self, sensor):
        # Sensors don't have history URLs configured - should return None
        result = sensor.get_history_url()
        assert result is None

    def test_history_url_returns_url_for_historical_model(self, location):
        # Locations have history - should return valid URL
        result = location.get_history_url()
        expected = reverse(
            "core:list-historicallocation",
            kwargs={"project_pk": location.project.pk, "location_pk": location.pk}
        )
        assert result == expected
