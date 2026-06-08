"""
Tests for sensor models and Pint unit validation.
"""

from django.core.exceptions import ValidationError

import pytest

from watersync.sensor.models import Deployment, Sensor, SensorVariable


@pytest.fixture
def sensor_variable(db):
    """Create a test sensor variable."""
    return SensorVariable.objects.create(
        name="Water Level",
        code="WL",
        description="Water level measurement"
    )


@pytest.fixture
def sensor(db):
    """Create a test sensor."""
    return Sensor.objects.create(
        identifier="TEST-SENSOR-001",
    )


@pytest.mark.django_db
class TestSensorVariable:
    """Tests for SensorVariable model."""

    def test_create_sensor_variable(self):
        """Can create a sensor variable."""
        var = SensorVariable.objects.create(
            name="Temperature",
            code="TEMP",
            description="Water temperature"
        )
        assert var.pk is not None
        assert str(var) == "Temperature (TEMP)"

    def test_sensor_variable_code_unique(self, sensor_variable):
        """Sensor variable code must be unique."""
        with pytest.raises(Exception):  # IntegrityError
            SensorVariable.objects.create(
                name="Different Name",
                code="WL",  # Same code as fixture
                description="Test"
            )


@pytest.mark.django_db
class TestSensor:
    """Tests for Sensor model."""

    def test_create_sensor(self):
        """Can create a sensor."""
        sensor = Sensor.objects.create(
            identifier="TEST-001",
        )
        assert sensor.pk is not None
        assert str(sensor) == "TEST-001"

    def test_sensor_identifier_unique(self, sensor):
        """Sensor identifier must be unique."""
        with pytest.raises(Exception):  # IntegrityError
            Sensor.objects.create(
                identifier="TEST-SENSOR-001",  # Same as fixture
            )

    def test_sensor_can_have_variables(self, sensor, sensor_variable):
        """Sensor can be linked to variables."""
        sensor.variables.add(sensor_variable)
        assert sensor_variable in sensor.variables.all()


@pytest.mark.django_db
class TestDeploymentUnitValidation:
    """Tests for Pint unit validation on Deployment model."""

    @pytest.fixture
    def location(self, db):
        """Create a test location."""
        from django.contrib.gis.geos import Point

        from watersync.core.models import Location, Project
        
        project = Project.objects.create(name="Test Project")
        return Location.objects.create(
            project=project,
            name="Test Location",
            geom=Point(0, 0, 0, srid=4326),
            type="piezometer"
        )

    def test_valid_pint_unit_meter(self, sensor, sensor_variable, location):
        """Valid Pint unit 'meter' should pass validation."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="meter"
        )
        # Should not raise
        deployment.full_clean()
        deployment.save()
        assert deployment.pk is not None

    def test_valid_pint_unit_mg_per_l(self, sensor, sensor_variable, location):
        """Valid Pint unit 'mg/L' should pass validation."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="mg/L"
        )
        deployment.full_clean()
        deployment.save()
        assert deployment.pk is not None

    def test_valid_pint_unit_degc(self, sensor, sensor_variable, location):
        """Valid Pint unit 'degC' should pass validation."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="degC"
        )
        deployment.full_clean()
        deployment.save()
        assert deployment.pk is not None

    def test_valid_custom_unit_ntu(self, sensor, sensor_variable, location):
        """Custom unit 'NTU' from water_quality.yaml pint_definitions should pass."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="NTU"
        )
        deployment.full_clean()
        deployment.save()
        assert deployment.pk is not None

    def test_valid_pint_unit_m_per_s(self, sensor, sensor_variable, location):
        """Valid Pint unit 'm/s' should pass validation."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="m/s"
        )
        deployment.full_clean()
        deployment.save()
        assert deployment.pk is not None

    def test_invalid_pint_unit_raises_error(self, sensor, sensor_variable, location):
        """Invalid unit string should raise ValidationError."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="not_a_valid_unit_xyz"
        )
        with pytest.raises(ValidationError) as exc_info:
            deployment.full_clean()
        
        assert "unit" in exc_info.value.message_dict
        assert "Invalid unit" in str(exc_info.value.message_dict["unit"])

    def test_invalid_unit_gibberish(self, sensor, sensor_variable, location):
        """Gibberish unit should raise ValidationError."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="asdfghjkl"
        )
        with pytest.raises(ValidationError):
            deployment.full_clean()

    def test_empty_unit_fails(self, sensor, sensor_variable, location):
        """Empty unit string should fail validation."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit=""
        )
        with pytest.raises(ValidationError):
            deployment.full_clean()

    def test_save_validates_unit(self, sensor, sensor_variable, location):
        """Save should validate unit (full_clean is called in save)."""
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="invalid_unit_abc"
        )
        with pytest.raises(ValidationError):
            deployment.save()


@pytest.mark.django_db
class TestDeploymentVariableFK:
    """Tests for SensorVariable foreign key on Deployment."""

    @pytest.fixture
    def location(self, db):
        """Create a test location."""
        from django.contrib.gis.geos import Point

        from watersync.core.models import Location, Project
        
        project = Project.objects.create(name="Test Project 2")
        return Location.objects.create(
            project=project,
            name="Test Location 2",
            geom=Point(0, 0, 0, srid=4326),
            type="piezometer"
        )

    def test_deployment_requires_variable_fk(self, sensor, location):
        """Deployment requires a SensorVariable FK, not just a string."""
        # Create a proper variable
        var = SensorVariable.objects.create(
            name="Pressure",
            code="PRES",
            description="Pressure measurement"
        )
        
        deployment = Deployment(
            sensor=sensor,
            location=location,
            variable=var,
            unit="mbar"
        )
        deployment.full_clean()
        deployment.save()
        
        # Reload and verify
        deployment.refresh_from_db()
        assert deployment.variable == var
        assert deployment.variable.code == "PRES"

    def test_deployment_variable_is_fk_not_string(self, sensor, sensor_variable, location):
        """Deployment.variable should be a FK to SensorVariable."""
        deployment = Deployment.objects.create(
            sensor=sensor,
            location=location,
            variable=sensor_variable,
            unit="meter"
        )
        
        # variable should be a SensorVariable instance, not a string
        assert isinstance(deployment.variable, SensorVariable)
        assert deployment.variable.code == "WL"
