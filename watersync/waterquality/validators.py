"""Validation utilities for water quality data.

These validators can be reused across forms, views, and API endpoints
for consistent validation logic.
"""
from typing import List, Optional, Set, Tuple

from watersync.core.config import (
    get_parameter_choices,
    get_parameter_label,
    is_valid_unit_for_parameter,
)


def validate_parameter(
    parameter: str, 
    group: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate a parameter code.
    
    Args:
        parameter: Parameter code to validate
        group: Optional parameter group to restrict validation to
        
    Returns:
        Tuple of (is_valid, error_message, parameter_label)
    """
    valid_params = dict(get_parameter_choices(group=group))
    
    if parameter not in valid_params:
        if group:
            return False, f"Parameter '{parameter}' not in group '{group}'", None
        return False, f"Unknown parameter '{parameter}'", None
    
    return True, None, get_parameter_label(parameter)


def validate_unit(parameter: str, unit: str) -> Tuple[bool, Optional[str]]:
    """Validate that a unit is valid for a parameter.
    
    Args:
        parameter: Parameter code
        unit: Unit code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not is_valid_unit_for_parameter(parameter, unit):
        label = get_parameter_label(parameter) or parameter
        return False, f"Unit '{unit}' not valid for {label}"
    return True, None


def validate_numeric_value(value: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """Validate and convert a string value to float.
    
    Args:
        value: String representation of a number
        
    Returns:
        Tuple of (is_valid, parsed_value, error_message)
    """
    try:
        parsed = float(value)
        return True, parsed, None
    except (ValueError, TypeError):
        return False, None, f"Invalid number '{value}'"


def check_duplicate_measurements(
    sample, 
    parameters: List[str]
) -> List[str]:
    """Check which parameters already have measurements for a sample.
    
    Args:
        sample: Sample instance
        parameters: List of parameter codes to check
        
    Returns:
        List of parameter codes that already exist
    """
    from watersync.waterquality.models import Measurement
    
    existing_params = set(
        Measurement.objects.filter(sample=sample)
        .values_list("parameter", flat=True)
    )
    
    return [p for p in parameters if p in existing_params]


def get_allowed_parameters_for_sample(sample) -> Set[str]:
    """Get the set of allowed parameter codes for a sample's group.
    
    Args:
        sample: Sample instance with parameter_group attribute
        
    Returns:
        Set of allowed parameter codes
    """
    return set(k for k, v in get_parameter_choices(group=sample.parameter_group))


def validate_parameters_for_sample(
    sample, 
    parameters: List[str]
) -> Tuple[List[str], List[str]]:
    """Validate that parameters belong to a sample's parameter group.
    
    Args:
        sample: Sample instance
        parameters: List of parameter codes to validate
        
    Returns:
        Tuple of (valid_params, invalid_params)
    """
    allowed = get_allowed_parameters_for_sample(sample)
    valid = [p for p in parameters if p in allowed]
    invalid = [p for p in parameters if p not in allowed]
    return valid, invalid


def validate_measurement_row(
    parameter: str,
    value: str,
    unit: str,
    parameter_group: Optional[str] = None,
) -> dict:
    """Validate a single measurement row.
    
    Args:
        parameter: Parameter code
        value: Value as string
        unit: Unit code
        parameter_group: Optional group to restrict parameters to
        
    Returns:
        Dict with validation results:
        {
            'is_valid': bool,
            'error': Optional[str],
            'parameter': str,
            'parameter_label': Optional[str],
            'value': str (original) or float (if valid),
            'unit': str
        }
    """
    result = {
        'is_valid': True,
        'error': None,
        'parameter': parameter,
        'parameter_label': None,
        'value': value,
        'unit': unit,
    }
    
    # Validate parameter
    param_valid, param_error, param_label = validate_parameter(parameter, parameter_group)
    if not param_valid:
        result['is_valid'] = False
        result['error'] = param_error
        return result
    result['parameter_label'] = param_label
    
    # Validate value
    value_valid, parsed_value, value_error = validate_numeric_value(value)
    if not value_valid:
        result['is_valid'] = False
        result['error'] = value_error
        return result
    result['value'] = parsed_value
    
    # Validate unit
    unit_valid, unit_error = validate_unit(parameter, unit)
    if not unit_valid:
        result['is_valid'] = False
        result['error'] = unit_error
        return result
    
    return result
