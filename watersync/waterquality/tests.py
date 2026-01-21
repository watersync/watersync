"""
Tests for water quality models (Sample and Measurement).

Tests cover:
- Model creation and validation
- Config-based parameter and unit choices
- Pint unit integration
- Unit validation for parameters
"""

from decimal import Decimal

import pytest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError

from watersync.core.config import (
    get_all_wq_unit_choices,
    get_parameter_choices,
    get_parameter_group_choices,
    is_valid_unit_for_parameter,
)
from watersync.core.models import Fieldwork, Location, Project
from watersync.waterquality.models import Measurement, Sample
from watersync.waterquality.models_setup import Protocol


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def project(db):
    """Create a test project."""
    return Project.objects.create(name="Test Water Quality Project")


@pytest.fixture
def location(db, project):
    """Create a test location."""
    return Location.objects.create(
        project=project,
        name="Test Well",
        geom=Point(0, 0, 0, srid=4326),
        type="piezometer"
    )


@pytest.fixture
def fieldwork(db, project, location):
    """Create a test fieldwork entry."""
    from datetime import date
    return Fieldwork.objects.create(
        project=project,
        date=date(2025, 1, 15),
        description="Test fieldwork"
    )


@pytest.fixture
def protocol(db):
    """Create a test protocol."""
    return Protocol.objects.create(
        method_name="Standard Water Quality",
        description="Standard water quality analysis protocol"
    )


@pytest.fixture
def sample(db, fieldwork, location, protocol):
    """Create a test sample."""
    return Sample.objects.create(
        fieldwork=fieldwork,
        location=location,
        protocol=protocol,
        parameter_group="physicochemical",
        measured_on="2025-01-15",
    )


# =============================================================================
# Config Helper Tests
# =============================================================================

@pytest.mark.django_db
class TestConfigHelpers:
    """Tests for config-based parameter/unit helpers."""

    def test_get_parameter_group_choices(self):
        """Parameter group choices should be available from config."""
        choices = get_parameter_group_choices()
        assert len(choices) > 0
        # Should have physicochemical group
        group_keys = [k for k, _ in choices]
        assert "physicochemical" in group_keys

    def test_get_parameter_choices(self):
        """Parameter choices should be available from config."""
        choices = get_parameter_choices()
        assert len(choices) > 0
        # Should have common parameters
        param_keys = [k for k, _ in choices]
        assert "ph" in param_keys
        assert "temperature" in param_keys

    def test_get_parameter_choices_filtered_by_group(self):
        """Parameter choices can be filtered by group."""
        choices = get_parameter_choices(group="physicochemical")
        assert len(choices) > 0
        # Should have common physicochemical params
        param_keys = [k for k, _ in choices]
        assert "ph" in param_keys
        assert "temperature" in param_keys

    def test_get_all_wq_unit_choices(self):
        """All unit choices should be available."""
        choices = get_all_wq_unit_choices()
        assert len(choices) > 0
        unit_keys = [k for k, _ in choices]
        assert "mg/L" in unit_keys

    def test_is_valid_unit_for_parameter_valid(self):
        """Valid unit for parameter should return True."""
        # pH should accept pH_unit
        assert is_valid_unit_for_parameter("ph", "pH_unit")
        # Temperature should accept degC
        assert is_valid_unit_for_parameter("temperature", "degC")

    def test_is_valid_unit_for_parameter_invalid(self):
        """Invalid unit for parameter should return False."""
        # pH should not accept mg/L
        assert not is_valid_unit_for_parameter("ph", "mg/L")
        # Temperature should not accept mg/L
        assert not is_valid_unit_for_parameter("temperature", "mg/L")


# =============================================================================
# Protocol Model Tests
# =============================================================================

@pytest.mark.django_db
class TestProtocol:
    """Tests for Protocol model."""

    def test_create_protocol(self):
        """Can create a protocol."""
        protocol = Protocol.objects.create(
            method_name="ISO Standard",
            description="ISO water quality standard"
        )
        assert protocol.pk is not None
        assert str(protocol) == "ISO Standard"

    def test_protocol_method_name_required(self):
        """Protocol method_name is required."""
        protocol = Protocol(description="No name")
        with pytest.raises(ValidationError):
            protocol.full_clean()


# =============================================================================
# Sample Model Tests
# =============================================================================

@pytest.mark.django_db
class TestSample:
    """Tests for Sample model."""

    def test_create_sample(self, fieldwork, location, protocol):
        """Can create a sample with required fields."""
        sample = Sample.objects.create(
            fieldwork=fieldwork,
            location=location,
            protocol=protocol,
            parameter_group="physicochemical",
        )
        assert sample.pk is not None

    def test_sample_str_representation(self, sample):
        """Sample string representation is correct."""
        str_repr = str(sample)
        assert "physicochemical" in str_repr
        assert "test-well" in str_repr.lower()

    def test_sample_with_optional_fields(self, fieldwork, location, protocol):
        """Sample can have optional fields."""
        sample = Sample.objects.create(
            fieldwork=fieldwork,
            location=location,
            protocol=protocol,
            parameter_group="nutrients",
            container_type="HDPE 500mL",
            volume_collected=500.0,
            replica_number=1,
            description="Duplicate sample",
        )
        assert sample.container_type == "HDPE 500mL"
        assert sample.volume_collected == 500.0
        assert sample.replica_number == 1

    def test_sample_external_source(self, protocol):
        """External samples can be created without fieldwork."""
        sample = Sample.objects.create(
            protocol=protocol,
            parameter_group="metals",
            is_external=True,
            source="External Lab ABC",
            date="2025-01-10",
        )
        assert sample.is_external is True
        assert sample.source == "External Lab ABC"


# =============================================================================
# Measurement Model Tests
# =============================================================================

@pytest.mark.django_db
class TestMeasurement:
    """Tests for Measurement model."""

    def test_create_measurement(self, sample):
        """Can create a measurement with valid parameter and unit."""
        measurement = Measurement.objects.create(
            sample=sample,
            parameter="ph",
            value=Decimal("7.5"),
            unit="pH_unit",
        )
        assert measurement.pk is not None

    def test_measurement_str_representation(self, sample):
        """Measurement string representation is correct."""
        measurement = Measurement.objects.create(
            sample=sample,
            parameter="temperature",
            value=Decimal("15.5"),
            unit="degC",
        )
        str_repr = str(measurement)
        assert "Temperature" in str_repr
        assert "15.5" in str_repr

    def test_measurement_parameter_display(self, sample):
        """Parameter display returns human-readable label."""
        measurement = Measurement(
            sample=sample,
            parameter="electrical_conductivity",
            value=Decimal("500"),
            unit="uS/cm",
        )
        assert measurement.parameter_display == "Electrical Conductivity"

    def test_measurement_formatted_value(self, sample):
        """Formatted value includes unit."""
        measurement = Measurement(
            sample=sample,
            parameter="dissolved_oxygen",
            value=Decimal("8.5"),
            unit="mg/L",
        )
        assert measurement.formatted_value == "8.5 mg/L"

    def test_measurement_with_detection_limit(self, sample):
        """Measurement can have a detection limit."""
        measurement = Measurement.objects.create(
            sample=sample,
            parameter="arsenic",
            value=Decimal("0.5"),
            unit="ug/L",
            detection_limit=Decimal("0.1"),
        )
        assert measurement.detection_limit == Decimal("0.1")
        assert "< 0.1" in measurement.formatted_detection_limit

    def test_measurement_unique_per_sample_parameter(self, sample):
        """Only one measurement per sample/parameter combination."""
        Measurement.objects.create(
            sample=sample,
            parameter="ph",
            value=Decimal("7.0"),
            unit="pH_unit",
        )
        # Creating another measurement with same sample/parameter should fail
        with pytest.raises(Exception):  # IntegrityError
            Measurement.objects.create(
                sample=sample,
                parameter="ph",
                value=Decimal("7.5"),
                unit="pH_unit",
            )


# =============================================================================
# Measurement Unit Validation Tests
# =============================================================================

@pytest.mark.django_db
class TestMeasurementUnitValidation:
    """Tests for unit validation on Measurement model."""

    def test_valid_unit_for_parameter(self, sample):
        """Valid unit for parameter passes validation."""
        measurement = Measurement(
            sample=sample,
            parameter="temperature",
            value=Decimal("20.0"),
            unit="degC",
        )
        # Should not raise
        measurement.full_clean()

    def test_invalid_unit_for_parameter(self, sample):
        """Invalid unit for parameter fails validation."""
        measurement = Measurement(
            sample=sample,
            parameter="ph",
            value=Decimal("7.0"),
            unit="mg/L",  # Invalid for pH
        )
        with pytest.raises(ValidationError) as exc_info:
            measurement.full_clean()
        assert "unit" in exc_info.value.message_dict

    def test_turbidity_ntu_unit(self, sample):
        """Custom NTU unit is valid for turbidity."""
        measurement = Measurement(
            sample=sample,
            parameter="turbidity",
            value=Decimal("5.0"),
            unit="NTU",
        )
        measurement.full_clean()
        measurement.save()
        assert measurement.pk is not None

    def test_bacterial_count_units(self, sample):
        """CFU/100mL is valid for microbiology parameters."""
        # Need a sample with microbiology group
        sample.parameter_group = "microbiology"
        sample.save()
        
        measurement = Measurement(
            sample=sample,
            parameter="e_coli",
            value=Decimal("100"),
            unit="CFU/100mL",
        )
        measurement.full_clean()
        measurement.save()
        assert measurement.pk is not None


# =============================================================================
# Measurement Pint Integration Tests
# =============================================================================

@pytest.mark.django_db
class TestMeasurementPintIntegration:
    """Tests for Pint quantity integration on Measurement model."""

    def test_measurement_property_returns_quantity(self, sample):
        """Measurement property returns Pint Quantity."""
        measurement = Measurement(
            sample=sample,
            parameter="temperature",
            value=Decimal("25.0"),
            unit="degC",
        )
        quantity = measurement.measurement
        assert quantity is not None
        assert quantity.magnitude == 25.0
        assert "degC" in str(quantity.units) or "degree_Celsius" in str(quantity.units)

    def test_convert_to_valid_unit(self, sample):
        """Can convert measurement to compatible unit."""
        from django.conf import settings
        
        measurement = Measurement(
            sample=sample,
            parameter="temperature",
            value=Decimal("100.0"),  # Use 100°C to avoid Pint zero-quantity issues
            unit="degC",
        )
        # Convert 100°C to Fahrenheit (should be 212°F)
        converted = measurement.convert_to("degF")
        assert converted is not None
        assert abs(converted.magnitude - 212.0) < 0.1

    def test_convert_to_invalid_unit_raises(self, sample):
        """Converting to incompatible unit raises ValueError."""
        measurement = Measurement(
            sample=sample,
            parameter="temperature",
            value=Decimal("25.0"),
            unit="degC",
        )
        with pytest.raises(ValueError):
            measurement.convert_to("mg/L")  # Can't convert temp to concentration

    def test_is_compatible_with(self, sample):
        """Can check unit compatibility."""
        measurement = Measurement(
            sample=sample,
            parameter="dissolved_oxygen",
            value=Decimal("8.0"),
            unit="mg/L",
        )
        # mg/L should be compatible with g/L
        assert measurement.is_compatible_with("g/L")
        # mg/L should not be compatible with degC
        assert not measurement.is_compatible_with("degC")

    def test_detection_limit_quantity(self, sample):
        """Detection limit returns Pint Quantity."""
        measurement = Measurement(
            sample=sample,
            parameter="lead",
            value=Decimal("0.5"),
            unit="ug/L",
            detection_limit=Decimal("0.1"),
        )
        dl_quantity = measurement.detection_limit_quantity
        assert dl_quantity is not None
        assert dl_quantity.magnitude == 0.1


# =============================================================================
# Form Tests
# =============================================================================

@pytest.mark.django_db
class TestMeasurementForm:
    """Tests for MeasurementForm validation."""

    def test_form_valid_data(self, sample):
        """Form accepts valid data."""
        from watersync.waterquality.forms import MeasurementForm
        
        form = MeasurementForm(data={
            "sample": sample.pk,
            "parameter": "ph",
            "value": "7.5",
            "unit": "pH_unit",
        })
        assert form.is_valid(), form.errors

    def test_form_invalid_unit_for_parameter(self, sample):
        """Form rejects invalid unit for parameter."""
        from watersync.waterquality.forms import MeasurementForm
        
        form = MeasurementForm(data={
            "sample": sample.pk,
            "parameter": "ph",
            "value": "7.5",
            "unit": "mg/L",  # Invalid for pH
        })
        assert not form.is_valid()
        assert "unit" in form.errors

    def test_form_negative_detection_limit_invalid(self, sample):
        """Form rejects negative detection limit."""
        from watersync.waterquality.forms import MeasurementForm
        
        form = MeasurementForm(data={
            "sample": sample.pk,
            "parameter": "temperature",
            "value": "20.0",
            "unit": "degC",
            "detection_limit": "-1.0",
        })
        assert not form.is_valid()
        assert "detection_limit" in form.errors


@pytest.mark.django_db
class TestMeasurementBulkForm:
    """Tests for MeasurementBulkForm."""

    def test_bulk_form_valid_data(self, sample):
        """Bulk form parses valid tab-separated data."""
        from watersync.waterquality.forms import MeasurementBulkForm
        
        data_str = "ph\t7.5\tpH_unit\ntemperature\t20.0\tdegC"
        form = MeasurementBulkForm(data={
            "sample": sample.pk,
            "data": data_str,
        })
        assert form.is_valid(), form.errors
        assert len(form.cleaned_data["processed_data"]) == 2

    def test_bulk_form_valid_csv_data(self, sample):
        """Bulk form parses valid comma-separated data."""
        from watersync.waterquality.forms import MeasurementBulkForm
        
        data_str = "ph,7.5,pH_unit\ntemperature,20.0,degC"
        form = MeasurementBulkForm(data={
            "sample": sample.pk,
            "data": data_str,
        })
        assert form.is_valid(), form.errors

    def test_bulk_form_invalid_parameter(self, sample):
        """Bulk form rejects unknown parameter."""
        from watersync.waterquality.forms import MeasurementBulkForm
        
        data_str = "unknown_param\t7.5\tmg/L"
        form = MeasurementBulkForm(data={
            "sample": sample.pk,
            "data": data_str,
        })
        assert not form.is_valid()

    def test_bulk_form_invalid_value(self, sample):
        """Bulk form rejects non-numeric value."""
        from watersync.waterquality.forms import MeasurementBulkForm
        
        data_str = "ph\tnot_a_number\tpH_unit"
        form = MeasurementBulkForm(data={
            "sample": sample.pk,
            "data": data_str,
        })
        assert not form.is_valid()

    def test_bulk_form_invalid_unit_for_param(self, sample):
        """Bulk form rejects invalid unit for parameter."""
        from watersync.waterquality.forms import MeasurementBulkForm
        
        data_str = "ph\t7.5\tmg/L"  # mg/L invalid for pH
        form = MeasurementBulkForm(data={
            "sample": sample.pk,
            "data": data_str,
        })
        assert not form.is_valid()

    def test_bulk_form_wrong_field_count(self, sample):
        """Bulk form rejects lines with wrong number of fields."""
        from watersync.waterquality.forms import MeasurementBulkForm
        
        data_str = "ph\t7.5"  # Missing unit field
        form = MeasurementBulkForm(data={
            "sample": sample.pk,
            "data": data_str,
        })
        assert not form.is_valid()
