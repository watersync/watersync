"""
Tests for Pint unit definitions and conversions.

This module tests the custom unit definitions in config/parameters/water_quality.yaml
(pint_definitions section) to ensure all hydrogeological and water quality units 
are properly defined and can be converted between each other.
"""

import pytest
from django.conf import settings


class TestUnitRegistryLoading:
    """Test that the unit registry loads correctly."""

    def test_ureg_is_available(self):
        """The UREG should be available in Django settings."""
        assert hasattr(settings, "UREG")
        assert settings.UREG is not None

    def test_custom_units_file_loaded(self):
        """Custom units should be loaded from the definitions file."""
        ureg = settings.UREG
        # Test a custom unit that only exists in our definitions file
        quantity = ureg("1 NTU")
        assert quantity.magnitude == 1


class TestHydraulicConductivityUnits:
    """Test hydraulic conductivity unit conversions."""

    def test_m_per_day_to_ft_per_day(self):
        """Convert m/day to ft/day."""
        ureg = settings.UREG
        k = ureg("1 m/day")
        k_ft = k.to("ft/day")
        assert abs(k_ft.magnitude - 3.28084) < 0.001

    def test_m_per_s_to_m_per_day(self):
        """Convert m/s to m/day."""
        ureg = settings.UREG
        k = ureg("1e-5 m/s")
        k_day = k.to("m/day")
        assert abs(k_day.magnitude - 0.864) < 0.001

    def test_cm_per_s_to_m_per_day(self):
        """Convert cm/s to m/day."""
        ureg = settings.UREG
        k = ureg("1 cm/s")
        k_day = k.to("m/day")
        assert abs(k_day.magnitude - 864) < 1

    def test_gpd_per_ft2_exists(self):
        """gpd/ft² (Meinzer units) should be defined."""
        ureg = settings.UREG
        k = ureg("1 gpd_per_ft2")
        assert k.dimensionality == ureg("m/s").dimensionality


class TestTransmissivityUnits:
    """Test transmissivity unit conversions."""

    def test_m2_per_day_to_ft2_per_day(self):
        """Convert m²/day to ft²/day."""
        ureg = settings.UREG
        t = ureg("100 m**2/day")
        t_ft = t.to("ft**2/day")
        assert abs(t_ft.magnitude - 1076.39) < 1

    def test_m2_per_s_to_m2_per_day(self):
        """Convert m²/s to m²/day."""
        ureg = settings.UREG
        t = ureg("1e-4 m**2/s")
        t_day = t.to("m**2/day")
        assert abs(t_day.magnitude - 8.64) < 0.01


class TestPermeabilityUnits:
    """Test permeability (darcy) unit definitions."""

    def test_darcy_defined(self):
        """Darcy unit should be defined."""
        ureg = settings.UREG
        perm = ureg("1 darcy")
        assert perm.magnitude == 1

    def test_millidarcy_defined(self):
        """Millidarcy should be defined."""
        ureg = settings.UREG
        perm = ureg("1000 millidarcy")
        perm_d = perm.to("darcy")
        assert abs(perm_d.magnitude - 1) < 0.001


class TestFlowRateUnits:
    """Test volumetric flow rate conversions."""

    def test_lps_to_gpm(self):
        """Convert L/s to gallons per minute."""
        ureg = settings.UREG
        q = ureg("10 L/s")
        q_gpm = q.to("gpm")
        assert abs(q_gpm.magnitude - 158.5) < 0.5

    def test_gpm_to_lps(self):
        """Convert gpm to L/s."""
        ureg = settings.UREG
        q = ureg("100 gpm")
        q_lps = q.to("L/s")
        assert abs(q_lps.magnitude - 6.31) < 0.01

    def test_m3_per_day_to_lps(self):
        """Convert m³/day to L/s."""
        ureg = settings.UREG
        q = ureg("86.4 m**3/day")
        q_lps = q.to("L/s")
        assert abs(q_lps.magnitude - 1) < 0.001

    def test_mgd_defined(self):
        """Million gallons per day should be defined."""
        ureg = settings.UREG
        q = ureg("1 MGD")
        q_lps = q.to("L/s")
        assert q_lps.magnitude > 40  # ~43.8 L/s

    def test_cfs_to_lps(self):
        """Convert cubic feet per second to L/s."""
        ureg = settings.UREG
        q = ureg("1 cfs")
        q_lps = q.to("L/s")
        assert abs(q_lps.magnitude - 28.32) < 0.1


class TestRechargeUnits:
    """Test recharge/precipitation rate units."""

    def test_mm_per_year_defined(self):
        """mm/year should be usable."""
        ureg = settings.UREG
        recharge = ureg("200 mm/year")
        assert recharge.magnitude == 200

    def test_mm_per_year_to_m_per_year(self):
        """Convert mm/year to m/year."""
        ureg = settings.UREG
        recharge = ureg("1000 mm/year")
        recharge_m = recharge.to("m/year")
        assert abs(recharge_m.magnitude - 1) < 0.001


class TestWaterQualityUnits:
    """Test water quality specific units."""

    def test_turbidity_ntu(self):
        """NTU (Nephelometric Turbidity Units) should be defined."""
        ureg = settings.UREG
        turb = ureg("5 NTU")
        assert turb.magnitude == 5

    def test_turbidity_fnu_equals_ntu(self):
        """FNU should be equivalent to NTU."""
        ureg = settings.UREG
        turb_ntu = ureg("10 NTU")
        turb_fnu = ureg("10 FNU")
        assert turb_ntu == turb_fnu

    def test_bacterial_cfu(self):
        """CFU (Colony Forming Units) should be defined."""
        ureg = settings.UREG
        bacteria = ureg("100 CFU")
        assert bacteria.magnitude == 100

    def test_ph_unit(self):
        """pH unit should be defined."""
        ureg = settings.UREG
        ph = ureg("7 pH_unit")
        assert ph.magnitude == 7

    def test_conductivity_us_per_cm(self):
        """Conductivity in µS/cm should convert to mS/cm."""
        ureg = settings.UREG
        cond = ureg("500 uS/cm")
        cond_ms = cond.to("mS/cm")
        assert abs(cond_ms.magnitude - 0.5) < 0.001

    def test_milliequivalents(self):
        """meq/L should be defined."""
        ureg = settings.UREG
        alk = ureg("2.5 meq_per_L")
        assert alk.magnitude == 2.5


class TestPressureUnits:
    """Test pressure and head units."""

    def test_kpa_to_mbar(self):
        """Convert kPa to mbar."""
        ureg = settings.UREG
        p = ureg("100 kPa")
        p_mbar = p.to("mbar")
        assert abs(p_mbar.magnitude - 1000) < 1

    def test_m_water_column(self):
        """Meters of water column should be usable."""
        ureg = settings.UREG
        head = ureg("10 m_H2O")
        assert head.magnitude == 10


class TestSpecificCapacityUnits:
    """Test specific capacity units."""

    def test_lps_per_m(self):
        """L/s per meter of drawdown."""
        ureg = settings.UREG
        sc = ureg("5 L/s/m")
        assert sc.magnitude == 5

    def test_gpm_per_ft(self):
        """gpm per foot of drawdown."""
        ureg = settings.UREG
        sc = ureg("10 gpm_per_ft")
        assert sc.magnitude == 10


class TestDimensionlessUnits:
    """Test dimensionless quantities."""

    def test_storativity(self):
        """Storativity should be defined and usable as a ratio."""
        ureg = settings.UREG
        s = ureg("0.001 storativity")
        # storativity is a named dimensionless unit
        assert s.magnitude == 0.001
        assert "storativity" in str(s.units)

    def test_porosity(self):
        """Porosity should be defined and usable as a ratio."""
        ureg = settings.UREG
        n = ureg("0.3 porosity")
        assert n.magnitude == 0.3
        assert "porosity" in str(n.units)

    def test_specific_yield(self):
        """Specific yield should be defined and usable as a ratio."""
        ureg = settings.UREG
        sy = ureg("0.2 specific_yield")
        assert sy.magnitude == 0.2
        assert "specific_yield" in str(sy.units)


class TestIsotopeUnits:
    """Test isotope hydrology units."""

    def test_tritium_units(self):
        """Tritium Units (TU) should be defined."""
        ureg = settings.UREG
        tritium = ureg("10 TU")
        assert tritium.magnitude == 10

    def test_permil(self):
        """Per mil (‰) should be defined for isotope ratios."""
        ureg = settings.UREG
        delta = ureg("-50 permil")
        assert delta.magnitude == -50

    def test_pmc(self):
        """Percent Modern Carbon should be defined."""
        ureg = settings.UREG
        c14 = ureg("85 pMC")
        assert c14.magnitude == 85


class TestContaminantTransportUnits:
    """Test contaminant transport related units."""

    def test_partition_coefficient_l_per_kg(self):
        """Partition coefficient in L/kg."""
        ureg = settings.UREG
        kd = ureg("10 L/kg")
        assert kd.magnitude == 10

    def test_diffusion_coefficient(self):
        """Diffusion coefficient in cm²/s."""
        ureg = settings.UREG
        d = ureg("1e-5 cm**2/s")
        d_m2 = d.to("m**2/s")
        assert abs(d_m2.magnitude - 1e-9) < 1e-12


class TestUnitDimensionalConsistency:
    """Test that units have correct dimensions."""

    def test_hydraulic_conductivity_dimensions(self):
        """K should have dimensions of [length]/[time]."""
        ureg = settings.UREG
        k = ureg("1 m/day")
        assert k.dimensionality == {"[length]": 1, "[time]": -1}

    def test_transmissivity_dimensions(self):
        """T should have dimensions of [length]²/[time]."""
        ureg = settings.UREG
        t = ureg("1 m**2/day")
        assert t.dimensionality == {"[length]": 2, "[time]": -1}

    def test_flow_rate_dimensions(self):
        """Q should have dimensions of [length]³/[time]."""
        ureg = settings.UREG
        q = ureg("1 L/s")
        assert q.dimensionality == {"[length]": 3, "[time]": -1}
