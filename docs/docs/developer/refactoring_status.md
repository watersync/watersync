# WaterSync Refactoring Status

**Started:** January 20, 2026  
**Based on:** [Code Review](code_review.md)

---

## Progress Tracker

| Phase | Task | Status | Date Completed | Notes |
|-------|------|--------|----------------|-------|
| **1** | Consolidate Unit system (Pint-centric) | ✅ Done | Jan 20, 2026 | Expanded units file, tested all conversions |
| **1** | Remove Unit model views/forms/URLs | ✅ Done | Jan 20, 2026 | Deprecated Unit model, removed all UI references |
| **1** | Change `Deployment.variable` to FK | ⬜ Not Started | - | |
| **1** | Add `FieldworkLocation` through table | ⬜ Not Started | - | |
| **1** | Add validation in `clean()` methods | ⬜ Not Started | - | |
| **2** | Create `ParameterUnit` junction table | ⬜ Not Started | - | |
| **2** | Migrate `Measurement.measurement_data` | ⬜ Not Started | - | |
| **3** | Create `LocationAttributeDefinition` | ⬜ Not Started | - | |
| **3** | Migrate `Location.detail` JSON | ⬜ Not Started | - | |
| **4** | Add `DataQualityFlag` model | ⬜ Not Started | - | |
| **4** | Add `ExternalDataSource` model | ⬜ Not Started | - | |

**Legend:** ✅ Done | 🔄 In Progress | ⬜ Not Started | ❌ Blocked

---

## Detailed Task Log

### Task 1.1: Consolidate Unit System (Pint-centric)

**Date Started:** January 20, 2026  
**Date Completed:** January 20, 2026

**Objective:** Standardize on Pint for all unit handling, deprecate the `Unit` database model.

**Actions Taken:**

1. ✅ **Expanded Pint unit definitions** - Added comprehensive hydrogeological units to `config/units/water_quality_units.txt`:
   - Hydraulic conductivity (gpd/ft²)
   - Flow rates (gpm, cfs, MGD)
   - Transmissivity (gpd/ft)
   - Specific capacity (gpm/ft)
   - Dimensionless parameters (storativity, porosity, specific_yield)
   - Isotope units (permil, pMC, TU)
   - Water quality (turbidity, conductivity, bacterial counts, pH)

2. ✅ **Created comprehensive unit tests** (`tests/test_units.py`):
   - 38 test cases covering all custom units
   - Tests for unit conversions (m/s ↔ ft/day, L/s ↔ gpm, etc.)
   - Tests for water quality units (NTU, CFU, pH_unit)
   - Tests for dimensionless parameters

3. ✅ **Deprecated `Unit` model** in `core/models.py`:
   - Added `DEPRECATED` docstring warning
   - Updated Meta class with deprecation notice
   - Model remains for migration planning

4. ✅ **Removed Unit-related UI code**:
   - Removed `UnitForm` from `core/forms.py`
   - Removed all Unit views from `core/views.py`
   - Removed `unit_urlpatterns` from `core/urls.py`
   - Removed `UnitListView` usage from `users/views.py` (SettingsView)

**Verification:**
- All 73 tests pass (`make test`)
- No template references to unit URLs
- No admin registrations for Unit model

---

## Files Modified

| File | Modification | Date |
|------|--------------|------|
| `config/units/water_quality_units.txt` | Expanded with hydrogeological units (gpd/ft², gpm, MGD, cfs, etc.) | Jan 20, 2026 |
| `tests/test_units.py` | Created comprehensive unit tests (38 tests) | Jan 20, 2026 |
| `watersync/core/models.py` | Marked `Unit` model as deprecated | Jan 20, 2026 |
| `watersync/core/forms.py` | Removed `UnitForm` | Jan 20, 2026 |
| `watersync/core/views.py` | Removed all Unit-related views | Jan 20, 2026 |
| `watersync/core/urls.py` | Removed `unit_urlpatterns` | Jan 20, 2026 |
| `watersync/users/views.py` | Removed `UnitListView` from `SettingsView` | Jan 20, 2026 |
| `docs/docs/developer/refactoring_status.md` | Created and updated this file | Jan 20, 2026 |

---

## Decisions Made

### Decision 1: Pint over Unit Model

**Date:** January 20, 2026

**Decision:** Use Pint exclusively for unit handling.

**Rationale:**
- Pint provides automatic unit conversion
- Pint validates dimensional compatibility
- Pint has a large built-in unit library
- The `Unit` model adds no value over Pint's capabilities
- Reduces code complexity (one approach, not three)

**Migration Path:**
1. Ensure all needed units are defined in Pint registry
2. Store Pint unit strings (e.g., "meter / second") instead of FK
3. Validate unit strings against Pint registry on save
4. Eventually remove `Unit` model when no longer referenced

