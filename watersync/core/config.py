"""
Configuration Loader for Parameter Definitions

This module loads parameter configurations from YAML files and provides
helper functions for accessing parameter/variable data, unit choices,
and validation utilities.

The YAML files use anchors for reusable unit groups, making it easy to
maintain consistent unit definitions across parameters.
"""

import yaml
from pathlib import Path
from functools import lru_cache
from django.conf import settings


# =============================================================================
# CONFIG FILE PATHS
# =============================================================================

CONFIG_DIR = Path(__file__).parent.parent.parent / "config" / "parameters"
WATER_QUALITY_CONFIG = CONFIG_DIR / "water_quality.yaml"


# =============================================================================
# YAML LOADING
# =============================================================================

@lru_cache(maxsize=None)
def load_water_quality_config():
    """Load water quality parameters and sensor variables from YAML config.
    
    Returns:
        dict with 'parameter_groups', 'parameters', 'pint_definitions', 
        and 'sensor_variables' keys
    """
    with open(WATER_QUALITY_CONFIG, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return {
        "parameter_groups": config.get("parameter_groups", {}),
        "parameters": config.get("parameters", {}),
        "pint_definitions": config.get("pint_definitions", []),
        "sensor_variables": config.get("sensor_variables", {}),
    }


def reload_configs():
    """Clear cached configs and reload from files.
    
    Use this after modifying YAML files to pick up changes.
    """
    load_water_quality_config.cache_clear()


# =============================================================================
# WATER QUALITY HELPERS
# =============================================================================

def get_parameter_groups():
    """Get all parameter groups."""
    return load_water_quality_config()["parameter_groups"]


def get_parameters():
    """Get all water quality parameters."""
    return load_water_quality_config()["parameters"]


def get_pint_definitions():
    """Get Pint unit definitions for the UnitRegistry.
    
    Returns:
        List of Pint definition strings ready to load into a UnitRegistry.
    """
    return load_water_quality_config()["pint_definitions"]


def load_pint_definitions(ureg):
    """Load custom unit definitions into a Pint UnitRegistry.
    
    Args:
        ureg: A Pint UnitRegistry instance
        
    Returns:
        The UnitRegistry with custom definitions loaded
    """
    for definition in get_pint_definitions():
        try:
            ureg.define(definition)
        except Exception:
            # Skip definitions that already exist or have errors
            pass
    return ureg


def get_parameter_group_choices():
    """Return choices for parameter group select fields."""
    groups = get_parameter_groups()
    return [(key, data["label"]) for key, data in groups.items()]


def get_parameter_choices(group=None):
    """Return choices for parameter select fields.
    
    Args:
        group: Optional group key to filter parameters by group.
    """
    params = get_parameters()
    choices = []
    for key, data in params.items():
        if group is None or data["group"] == group:
            choices.append((key, data["label"]))
    return sorted(choices, key=lambda x: x[1])


def get_parameters_by_group():
    """Return parameters organized by group for grouped select widgets."""
    params = get_parameters()
    groups = get_parameter_groups()
    grouped = {}
    
    for key, data in params.items():
        group_key = data["group"]
        group_label = groups[group_key]["label"]
        if group_label not in grouped:
            grouped[group_label] = []
        grouped[group_label].append((key, data["label"]))
    
    # Sort parameters within each group
    for group_label in grouped:
        grouped[group_label].sort(key=lambda x: x[1])
    
    return grouped


def get_wq_unit_choices(parameter):
    """Return unit choices for a specific water quality parameter."""
    params = get_parameters()
    if parameter not in params:
        return []
    return [
        (unit, label) 
        for unit, label in params[parameter]["units"].items()
    ]


def get_all_wq_unit_choices():
    """Return all possible water quality unit choices."""
    params = get_parameters()
    all_units = {}
    for param_data in params.values():
        for unit, label in param_data["units"].items():
            all_units[unit] = label
    return sorted([(u, l) for u, l in all_units.items()], key=lambda x: x[1])


def get_parameter_label(parameter):
    """Get human-readable label for a water quality parameter."""
    params = get_parameters()
    if parameter in params:
        return params[parameter]["label"]
    return parameter


def get_wq_unit_label(unit):
    """Get human-readable label for a water quality unit."""
    params = get_parameters()
    for param_data in params.values():
        if unit in param_data["units"]:
            return param_data["units"][unit]
    return unit


def get_parameter_default_unit(parameter):
    """Get the default unit for a water quality parameter."""
    params = get_parameters()
    if parameter in params:
        return params[parameter]["default_unit"]
    return None


def is_valid_unit_for_parameter(parameter, unit):
    """Check if a unit is valid for the given water quality parameter."""
    params = get_parameters()
    if parameter not in params:
        return False
    return unit in params[parameter]["units"]


def get_parameter_info(parameter):
    """Get full info dict for a water quality parameter."""
    return get_parameters().get(parameter)


def get_group_info(group):
    """Get full info dict for a parameter group."""
    return get_parameter_groups().get(group)


def get_parameters_json():
    """Return parameters config as JSON-serializable dict for JavaScript."""
    params = get_parameters()
    return {
        key: {
            "label": data["label"],
            "group": data["group"],
            "units": data["units"],
            "default_unit": data["default_unit"],
        }
        for key, data in params.items()
    }


# =============================================================================
# SENSOR VARIABLE HELPERS
# =============================================================================

def get_sensor_variables():
    """Get all sensor variables."""
    return load_water_quality_config()["sensor_variables"]


def get_variable_choices():
    """Return choices for sensor variable select fields."""
    variables = get_sensor_variables()
    return [(key, data["label"]) for key, data in variables.items()]


def get_sensor_unit_choices(variable):
    """Return unit choices for a specific sensor variable."""
    variables = get_sensor_variables()
    if variable not in variables:
        return []
    return [
        (unit, label) 
        for unit, label in variables[variable]["units"].items()
    ]


def get_all_sensor_unit_choices():
    """Return all possible sensor unit choices."""
    variables = get_sensor_variables()
    all_units = {}
    for var_data in variables.values():
        for unit, label in var_data["units"].items():
            all_units[unit] = label
    return sorted([(u, l) for u, l in all_units.items()], key=lambda x: x[1])


def get_variable_label(variable):
    """Get human-readable label for a sensor variable."""
    variables = get_sensor_variables()
    if variable in variables:
        return variables[variable]["label"]
    return variable


def get_sensor_unit_label(unit):
    """Get human-readable label for a sensor unit."""
    variables = get_sensor_variables()
    for var_data in variables.values():
        if unit in var_data["units"]:
            return var_data["units"][unit]
    return unit


def get_variable_default_unit(variable):
    """Get the default unit for a sensor variable."""
    variables = get_sensor_variables()
    if variable in variables:
        return variables[variable]["default_unit"]
    return None


def is_valid_unit_for_variable(variable, unit):
    """Check if a unit is valid for the given sensor variable."""
    variables = get_sensor_variables()
    if variable not in variables:
        return False
    return unit in variables[variable]["units"]


def get_variable_info(variable):
    """Get full info dict for a sensor variable."""
    return get_sensor_variables().get(variable)


def get_variables_json():
    """Return sensor variables config as JSON-serializable dict for JavaScript."""
    variables = get_sensor_variables()
    return {
        key: {
            "label": data["label"],
            "units": data["units"],
            "default_unit": data["default_unit"],
        }
        for key, data in variables.items()
    }


# =============================================================================
# PINT INTEGRATION HELPERS
# =============================================================================

def create_quantity(value, unit):
    """Create a Pint Quantity from value and unit string.
    
    Args:
        value: Numeric value
        unit: Unit string (must be valid Pint unit)
    
    Returns:
        Pint Quantity object
    """
    return settings.UREG.Quantity(float(value), unit)


def quantity_to_dict(quantity):
    """Convert a Pint Quantity to a JSON-serializable dict.
    
    Args:
        quantity: Pint Quantity object
        
    Returns:
        Dict with magnitude, unit, and dimensionality
    """
    if quantity is None:
        return None
    return {
        "magnitude": float(quantity.magnitude),
        "unit": str(quantity.units),
        "dimensionality": str(quantity.dimensionality),
    }


def dict_to_quantity(data):
    """Convert a dict back to a Pint Quantity.
    
    Args:
        data: Dict with magnitude and unit keys
        
    Returns:
        Pint Quantity object or None
    """
    if not data:
        return None
    try:
        magnitude = data.get("magnitude")
        unit = data.get("unit")
        if magnitude is not None and unit:
            return settings.UREG.Quantity(magnitude, unit)
    except (ValueError, TypeError, KeyError):
        pass
    return None
