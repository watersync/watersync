"""Utility functions for water quality measurements.

High-level functions that combine parsing and validation.
For lower-level utilities, see parsers.py and validators.py.
"""
from typing import List, Optional

from watersync.waterquality.parsers import parse_tabular_text, parse_uploaded_file, skip_header_row
from watersync.waterquality.validators import (
    check_duplicate_measurements,
    get_allowed_parameters_for_sample,
    validate_measurement_row,
    validate_parameters_for_sample,
)


def parse_bulk_measurement_data(
    data_str: str, 
    parameter_group: Optional[str] = None
) -> List[dict]:
    """Parse bulk measurement data and return rows with validation status.
    
    Args:
        data_str: Tab or comma separated text with columns: parameter, value, unit
        parameter_group: Optional group to restrict valid parameters
        
    Returns:
        List of dicts with keys: line_num, parameter, parameter_label, value, unit, 
        is_valid, error
    """
    rows = []
    parsed_rows = parse_tabular_text(data_str)
    
    for i, fields in enumerate(parsed_rows, 1):
        row = {
            "line_num": i,
            "parameter": "",
            "parameter_label": "",
            "value": "",
            "unit": "",
            "is_valid": True,
            "error": None,
        }
        
        if len(fields) != 3:
            row["is_valid"] = False
            row["error"] = f"Expected 3 fields, got {len(fields)}"
            row["raw"] = ", ".join(fields)
            rows.append(row)
            continue
            
        parameter, value, unit = fields
        
        # Use the validation utility
        validation = validate_measurement_row(parameter, value, unit, parameter_group)
        row.update({
            "parameter": validation["parameter"],
            "parameter_label": validation["parameter_label"],
            "value": validation["value"],
            "unit": validation["unit"],
            "is_valid": validation["is_valid"],
            "error": validation["error"],
        })
        
        rows.append(row)
        
    return rows


def parse_bulk_file(file, parameter_group: Optional[str] = None) -> tuple:
    """Parse uploaded file and validate measurement data.
    
    Args:
        file: Uploaded file object
        parameter_group: Optional group to restrict valid parameters
        
    Returns:
        Tuple of (rows, error_message)
    """
    file_rows, error = parse_uploaded_file(file)
    if error:
        return [], error
    
    start_idx = skip_header_row(file_rows)
    rows = []
    
    for i, file_row in enumerate(file_rows[start_idx:], start=start_idx + 1):
        if not file_row or not any(file_row):
            continue
        
        row = {
            "line_num": i,
            "parameter": "",
            "parameter_label": "",
            "value": "",
            "unit": "",
            "is_valid": True,
            "error": None,
        }
        
        if len(file_row) < 3:
            row["is_valid"] = False
            row["error"] = f"Expected 3 columns, got {len(file_row)}"
            rows.append(row)
            continue
        
        parameter = str(file_row[0]).strip() if file_row[0] else ""
        value = str(file_row[1]).strip() if file_row[1] else ""
        unit = str(file_row[2]).strip() if file_row[2] else ""
        
        validation = validate_measurement_row(parameter, value, unit, parameter_group)
        row.update({
            "parameter": validation["parameter"],
            "parameter_label": validation["parameter_label"],
            "value": validation["value"],
            "unit": validation["unit"],
            "is_valid": validation["is_valid"],
            "error": validation["error"],
        })
        
        rows.append(row)
    
    return rows, None


def validate_bulk_data_for_sample(sample, rows: List[dict]) -> List[dict]:
    """Add sample-specific validation to parsed rows.
    
    Checks:
    - Parameters belong to sample's parameter group
    - No duplicate measurements exist
    
    Args:
        sample: Sample instance
        rows: List of parsed row dicts (from parse_bulk_measurement_data or parse_bulk_file)
        
    Returns:
        Updated rows with additional validation errors
    """
    if not sample:
        return rows
    
    # Get allowed parameters and existing measurements
    allowed_params = get_allowed_parameters_for_sample(sample)
    duplicates = set(check_duplicate_measurements(
        sample, 
        [r["parameter"] for r in rows if r["is_valid"]]
    ))
    
    for row in rows:
        if not row["is_valid"]:
            continue
        
        # Check parameter group
        if row["parameter"] not in allowed_params:
            row["is_valid"] = False
            row["error"] = f"Parameter '{row['parameter']}' not in sample's group ({sample.parameter_group})"
        # Check duplicates
        elif row["parameter"] in duplicates:
            row["is_valid"] = False
            row["error"] = f"Measurement for '{row['parameter']}' already exists"
    
    return rows

