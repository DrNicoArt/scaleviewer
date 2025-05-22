"""
Helper functions used throughout the application.
"""

import re
import os
import datetime
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from utils.constants import SCALE_NAMES, SCALE_COLORS, DATETIME_FORMAT


def get_scale_color(scale_name):
    """
    Get the color associated with a scale.
    
    Args:
        scale_name: Name of the scale
        
    Returns:
        QColor: Color for the scale
    """
    if scale_name in SCALE_COLORS:
        return QColor(SCALE_COLORS[scale_name])
    return QColor(Qt.gray)


def format_datetime(dt=None):
    """
    Format a datetime object or current datetime.
    
    Args:
        dt: Datetime object to format (or None for current time)
        
    Returns:
        str: Formatted datetime string
    """
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime(DATETIME_FORMAT)


def extract_numeric_value(value):
    """
    Extract a numeric value from a string or other data.
    
    Args:
        value: Value to extract numeric part from
        
    Returns:
        float: Extracted numeric value or None if not possible
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Try to extract a number with scientific notation (e.g. 1.2 × 10^31)
        sci_notation_pattern = r'(\d+\.?\d*|\.\d+)\s*(?:×|x)\s*10\^?(-?\d+)'
        sci_match = re.search(sci_notation_pattern, value)
        
        if sci_match:
            base = float(sci_match.group(1))
            exponent = int(sci_match.group(2))
            return base * (10 ** exponent)
        
        # Try to extract a simple number
        numeric_str = ''.join(c for c in value if c.isdigit() or c == '.' or c == '-')
        if numeric_str:
            try:
                return float(numeric_str)
            except:
                pass
    
    return None


def compare_objects(obj1, obj2, fields=None):
    """
    Compare two objects based on specific fields or all numeric fields.
    
    Args:
        obj1: First object
        obj2: Second object
        fields: List of fields to compare (or None for all numeric fields)
        
    Returns:
        dict: Comparison results with similarity scores
    """
    if not obj1 or not obj2:
        return {"similarity": 0, "matching_fields": 0, "total_fields": 0, "details": {}}
    
    # Extract data dictionaries
    data1 = obj1.get("data", {})
    data2 = obj2.get("data", {})
    
    # If no fields specified, use all fields present in both objects
    if fields is None:
        fields = set(data1.keys()).intersection(set(data2.keys()))
    
    # Find numeric fields to compare
    numeric_fields = []
    field_values = {}
    
    for field in fields:
        # Skip if field not in both objects
        if field not in data1 or field not in data2:
            continue
        
        # Get values
        value1 = extract_numeric_value(data1[field])
        value2 = extract_numeric_value(data2[field])
        
        # If both values are numeric, add to comparison
        if value1 is not None and value2 is not None:
            numeric_fields.append(field)
            field_values[field] = {"value1": value1, "value2": value2}
    
    # Compare each field
    similarity_scores = {}
    total_similarity = 0
    
    for field in numeric_fields:
        value1 = field_values[field]["value1"]
        value2 = field_values[field]["value2"]
        
        # Calculate similarity (1 - normalized difference)
        # Use log-scale for very different values
        max_val = max(abs(value1), abs(value2))
        min_val = min(abs(value1), abs(value2))
        
        if max_val == 0:  # Both values are 0
            field_similarity = 1.0
        elif max_val / min_val > 1000:  # Very different, use log scale
            field_similarity = 1.0 - min(1.0, abs(np.log10(value1 / value2) / 10)) if min_val > 0 else 0.0
        else:  # More similar, use linear scale
            field_similarity = 1.0 - min(1.0, abs(value1 - value2) / max_val)
        
        similarity_scores[field] = field_similarity
        total_similarity += field_similarity
    
    # Calculate overall similarity
    overall_similarity = total_similarity / len(numeric_fields) if numeric_fields else 0
    
    return {
        "similarity": overall_similarity,
        "matching_fields": len(numeric_fields),
        "total_fields": len(fields),
        "details": similarity_scores
    }


def sort_objects_by_scale(objects):
    """
    Sort objects by scale (from cosmic to quantum).
    
    Args:
        objects: List of objects to sort
        
    Returns:
        list: Sorted list of objects
    """
    def get_scale_index(obj):
        scale = obj.get("scale", "")
        try:
            return SCALE_NAMES.index(scale)
        except ValueError:
            return len(SCALE_NAMES)  # Put unknown scales at the end
    
    return sorted(objects, key=get_scale_index)


def sanitize_filename(filename):
    """
    Sanitize a string to be used as a filename.
    
    Args:
        filename: String to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Ensure the filename is not too long
    max_length = 255
    if len(sanitized) > max_length:
        base, ext = os.path.splitext(sanitized)
        sanitized = base[:max_length - len(ext)] + ext
    
    return sanitized


def validate_json_object(obj):
    """
    Validate if an object has the required structure for the application.
    
    Args:
        obj: Object to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(obj, dict):
        return False
    
    # Check required fields
    if 'id' not in obj or 'scale' not in obj or 'name' not in obj:
        return False
    
    # Check if scale is valid
    if obj['scale'] not in SCALE_NAMES:
        return False
    
    # Check if data field exists and is a dictionary
    if 'data' not in obj or not isinstance(obj['data'], dict):
        return False
    
    return True
