"""File parsing utilities for bulk fieldwork import.

Extends the base parsers from waterquality for fieldwork-specific needs.
"""
from datetime import datetime, time

from watersync.waterquality.parsers import (
    parse_tabular_text,
    parse_uploaded_file,
    skip_header_row,
)


def parse_date(value: str) -> tuple[datetime | None, str | None]:
    """Parse a date string into a date object.
    
    Supports common formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
    
    Args:
        value: Date string to parse
        
    Returns:
        Tuple of (date, error_message)
    """
    if not value or not str(value).strip():
        return None, "Date is required"
    
    value = str(value).strip()
    
    formats = [
        "%Y-%m-%d",      # ISO format: 2024-01-15
        "%d/%m/%Y",      # European: 15/01/2024
        "%m/%d/%Y",      # US: 01/15/2024
        "%d-%m-%Y",      # European with dashes
        "%Y/%m/%d",      # Alternative ISO
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date(), None
        except ValueError:
            continue
    
    return None, f"Invalid date format '{value}'. Use YYYY-MM-DD"


def parse_time(value: str) -> tuple[time | None, str | None]:
    """Parse a time string into a time object.
    
    Supports: HH:MM, HH:MM:SS, with optional AM/PM
    
    Args:
        value: Time string to parse
        
    Returns:
        Tuple of (time, error_message)
    """
    if not value or not str(value).strip():
        return None, None  # Time is optional
    
    value = str(value).strip()
    
    formats = [
        "%H:%M",         # 24-hour: 14:30
        "%H:%M:%S",      # 24-hour with seconds: 14:30:00
        "%I:%M %p",      # 12-hour: 02:30 PM
        "%I:%M:%S %p",   # 12-hour with seconds
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).time(), None
        except ValueError:
            continue
    
    return None, f"Invalid time format '{value}'. Use HH:MM"


def parse_weather(value: str) -> tuple[str | None, str | None]:
    """Parse and validate weather condition.
    
    Args:
        value: Weather string to validate
        
    Returns:
        Tuple of (weather_code, error_message)
    """
    from watersync.core.models import Fieldwork
    
    if not value or not str(value).strip():
        return "sunny", None  # Default to sunny
    
    value = str(value).strip().lower()
    
    # Map of common variations to valid choices
    weather_map = {
        "sunny": "sunny",
        "sun": "sunny",
        "clear": "sunny",
        "cloudy": "cloudy",
        "clouds": "cloudy",
        "overcast": "cloudy",
        "rainy": "rainy",
        "rain": "rainy",
        "raining": "rainy",
        "snowy": "snowy",
        "snow": "snowy",
        "snowing": "snowy",
        "windy": "windy",
        "wind": "windy",
        "stormy": "stormy",
        "storm": "stormy",
        "thunderstorm": "stormy",
    }
    
    if value in weather_map:
        return weather_map[value], None
    
    # Check if it's already a valid choice
    valid_choices = [c[0] for c in Fieldwork.WeatherConditions.choices]
    if value in valid_choices:
        return value, None
    
    return None, f"Invalid weather '{value}'. Valid: sunny, cloudy, rainy, snowy, windy, stormy"


def validate_fieldwork_row(
    date_str: str,
    start_time_str: str,
    end_time_str: str,
    weather_str: str,
    description: str = "",
) -> dict:
    """Validate a single fieldwork row.
    
    Args:
        date_str: Date string
        start_time_str: Start time string
        end_time_str: End time string
        weather_str: Weather condition string
        description: Optional description
        
    Returns:
        Dict with validation results
    """
    result = {
        'is_valid': True,
        'error': None,
        'date': None,
        'date_str': date_str,
        'start_time': None,
        'start_time_str': start_time_str,
        'end_time': None,
        'end_time_str': end_time_str,
        'weather': None,
        'weather_str': weather_str,
        'description': description.strip() if description else "",
    }
    
    # Parse date
    parsed_date, date_error = parse_date(date_str)
    if date_error:
        result['is_valid'] = False
        result['error'] = date_error
        return result
    result['date'] = parsed_date
    
    # Parse start time
    parsed_start, start_error = parse_time(start_time_str)
    if start_error:
        result['is_valid'] = False
        result['error'] = start_error
        return result
    result['start_time'] = parsed_start
    
    # Parse end time
    parsed_end, end_error = parse_time(end_time_str)
    if end_error:
        result['is_valid'] = False
        result['error'] = end_error
        return result
    result['end_time'] = parsed_end
    
    # Validate times make sense
    if parsed_start and parsed_end and parsed_start >= parsed_end:
        result['is_valid'] = False
        result['error'] = "End time must be after start time"
        return result
    
    # Parse weather
    parsed_weather, weather_error = parse_weather(weather_str)
    if weather_error:
        result['is_valid'] = False
        result['error'] = weather_error
        return result
    result['weather'] = parsed_weather
    
    return result


def parse_bulk_fieldwork_data(data_str: str) -> list[dict]:
    """Parse bulk fieldwork data from pasted text.
    
    Expected columns: date, start_time, end_time, weather, description (optional)
    
    Args:
        data_str: Tab or comma separated text
        
    Returns:
        List of validated row dicts
    """
    rows = []
    parsed_rows = parse_tabular_text(data_str)
    
    for i, fields in enumerate(parsed_rows, 1):
        row = {
            "line_num": i,
            "is_valid": True,
            "error": None,
        }
        
        if len(fields) < 4:
            row["is_valid"] = False
            row["error"] = f"Expected at least 4 fields (date, start_time, end_time, weather), got {len(fields)}"
            row["raw"] = ", ".join(fields)
            rows.append(row)
            continue
        
        date_str = fields[0]
        start_time_str = fields[1]
        end_time_str = fields[2]
        weather_str = fields[3]
        description = fields[4] if len(fields) > 4 else ""
        
        validation = validate_fieldwork_row(
            date_str, start_time_str, end_time_str, weather_str, description
        )
        row.update(validation)
        row["line_num"] = i
        
        rows.append(row)
    
    return rows


def parse_bulk_fieldwork_file(file) -> tuple[list[dict], str | None]:
    """Parse uploaded file for fieldwork data.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Tuple of (rows, error_message)
    """
    file_rows, error = parse_uploaded_file(file)
    if error:
        return [], error
    
    # Use fieldwork-specific header indicators
    header_indicators = ['date', 'datum', 'fecha', 'start', 'start_time']
    start_idx = skip_header_row(file_rows, header_indicators)
    
    rows = []
    
    for i, file_row in enumerate(file_rows[start_idx:], start=start_idx + 1):
        if not file_row or not any(file_row):
            continue
        
        row = {
            "line_num": i,
            "is_valid": True,
            "error": None,
        }
        
        if len(file_row) < 4:
            row["is_valid"] = False
            row["error"] = f"Expected at least 4 columns, got {len(file_row)}"
            rows.append(row)
            continue
        
        date_str = str(file_row[0]).strip() if file_row[0] else ""
        start_time_str = str(file_row[1]).strip() if file_row[1] else ""
        end_time_str = str(file_row[2]).strip() if file_row[2] else ""
        weather_str = str(file_row[3]).strip() if file_row[3] else ""
        description = str(file_row[4]).strip() if len(file_row) > 4 and file_row[4] else ""
        
        validation = validate_fieldwork_row(
            date_str, start_time_str, end_time_str, weather_str, description
        )
        row.update(validation)
        row["line_num"] = i
        
        rows.append(row)
    
    return rows, None


def check_duplicate_fieldwork_dates(project, dates: list) -> list:
    """Check which dates already have fieldwork entries.
    
    Args:
        project: Project instance
        dates: List of date objects to check
        
    Returns:
        List of dates that already exist
    """
    from watersync.core.models import Fieldwork
    
    existing_dates = set(
        Fieldwork.objects.filter(project=project, date__in=dates)
        .values_list("date", flat=True)
    )
    
    return [d for d in dates if d in existing_dates]


def validate_bulk_fieldwork_for_project(project, rows: list[dict]) -> list[dict]:
    """Add project-specific validation to parsed rows.
    
    Checks for duplicate dates within the project.
    
    Args:
        project: Project instance
        rows: List of parsed row dicts
        
    Returns:
        Updated rows with additional validation errors
    """
    if not project:
        return rows
    
    valid_dates = [r["date"] for r in rows if r["is_valid"] and r.get("date")]
    duplicates = set(check_duplicate_fieldwork_dates(project, valid_dates))
    
    # Also check for duplicates within the uploaded data itself
    seen_dates = set()
    internal_duplicates = set()
    for d in valid_dates:
        if d in seen_dates:
            internal_duplicates.add(d)
        seen_dates.add(d)
    
    for row in rows:
        if not row["is_valid"]:
            continue
        
        date = row.get("date")
        if date in duplicates:
            row["is_valid"] = False
            row["error"] = f"Fieldwork for {date} already exists in this project"
        elif date in internal_duplicates:
            row["is_valid"] = False
            row["error"] = f"Duplicate date {date} in uploaded data"
    
    return rows
