"""File parsing utilities for bulk data import.

These parsers can be reused across different models that need
CSV/Excel file import or tabular text parsing.
"""
import csv
import io
from typing import List, Optional, Tuple


def parse_csv_content(content: str) -> List[List[str]]:
    """Parse CSV content string into list of rows.
    
    Args:
        content: CSV file content as string
        
    Returns:
        List of rows, where each row is a list of string values
    """
    reader = csv.reader(io.StringIO(content))
    return list(reader)


def parse_csv_file(file, encoding: str = 'utf-8-sig') -> List[List[str]]:
    """Parse uploaded CSV file into list of rows.
    
    Args:
        file: File-like object (e.g., from request.FILES)
        encoding: File encoding. Default 'utf-8-sig' strips BOM from Excel files
        
    Returns:
        List of rows, where each row is a list of string values
    """
    content = file.read().decode(encoding)
    return parse_csv_content(content)


def parse_excel_file(file) -> List[List]:
    """Parse uploaded Excel file into list of rows.
    
    Args:
        file: File-like object (e.g., from request.FILES)
        
    Returns:
        List of rows, where each row is a list of cell values
        
    Raises:
        ImportError: If openpyxl is not installed
    """
    try:
        import openpyxl
    except ImportError:
        raise ImportError("Excel support requires openpyxl. Please use CSV format.")
    
    wb = openpyxl.load_workbook(file)
    ws = wb.active
    return [[cell.value for cell in row] for row in ws.iter_rows()]


def parse_uploaded_file(file) -> Tuple[List[List], Optional[str]]:
    """Auto-detect file type and parse uploaded file.
    
    Args:
        file: File-like object with .name attribute
        
    Returns:
        Tuple of (rows, error_message). error_message is None on success.
    """
    filename = file.name.lower()
    
    try:
        if filename.endswith('.csv'):
            return parse_csv_file(file), None
        elif filename.endswith(('.xls', '.xlsx')):
            return parse_excel_file(file), None
        else:
            return [], "Unsupported file format. Please use CSV or Excel (.xlsx)."
    except ImportError as e:
        return [], str(e)
    except Exception as e:
        return [], f"Error reading file: {str(e)}"


def parse_tabular_text(text: str, delimiter: Optional[str] = None) -> List[List[str]]:
    """Parse tab or comma-separated text into list of rows.
    
    Args:
        text: Multi-line text with delimited values
        delimiter: Optional delimiter. If None, auto-detects tab or comma.
        
    Returns:
        List of rows, where each row is a list of stripped string values
    """
    rows = []
    lines = text.splitlines()
    
    for line in lines:
        if not line.strip():
            continue
        
        # Auto-detect delimiter if not specified
        if delimiter is None:
            delim = "\t" if "\t" in line else ","
        else:
            delim = delimiter
            
        fields = [f.strip() for f in line.split(delim)]
        rows.append(fields)
        
    return rows


def skip_header_row(rows: List[List], header_indicators: List[str] = None) -> int:
    """Determine the starting index, skipping header if present.
    
    Args:
        rows: List of parsed rows
        header_indicators: List of strings that indicate a header row.
            Defaults to common header names.
            
    Returns:
        Index to start processing from (0 if no header, 1 if header detected)
    """
    if header_indicators is None:
        header_indicators = ['parameter', 'param', 'variable', 'name', 'field']
    
    if rows and rows[0]:
        first_cell = str(rows[0][0]).lower().strip() if rows[0][0] else ""
        if first_cell in header_indicators:
            return 1
    return 0
