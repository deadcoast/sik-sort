"""Date classifier module for categorizing files by date."""

from datetime import datetime
from enum import Enum
from pathlib import Path


class DateMode(Enum):
    """Date mode enumeration for choosing which timestamp to use."""
    CREATION = "creation"
    MODIFICATION = "modification"


def classify_by_date(file_path: Path, use_creation: bool = False, date_format: str = "%Y-%m") -> str:
    """Categorizes a file by its date and returns a formatted date string.
    
    Args:
        file_path: Path to the file to classify
        use_creation: If True, use creation date; otherwise use modification date
        date_format: Format string for the date (default: "%Y-%m" for YYYY-MM)
        
    Returns:
        str: Formatted date string for folder naming
    """
    date = get_file_date(file_path, use_creation)
    return format_date(date, date_format)


def get_file_date(file_path: Path, use_creation: bool = False) -> datetime:
    """Retrieves the creation or modification timestamp of a file.
    
    Args:
        file_path: Path to the file
        use_creation: If True, return creation date; otherwise return modification date
        
    Returns:
        datetime: File timestamp
    """
    stat = file_path.stat()
    
    if use_creation:
        # st_ctime on Unix is the last metadata change time, not creation time
        # st_birthtime is creation time on some systems (macOS, BSD)
        # On Windows, st_ctime is creation time
        # For cross-platform compatibility, we use st_ctime
        timestamp = stat.st_ctime
    else:
        # st_mtime is modification time
        timestamp = stat.st_mtime
    
    return datetime.fromtimestamp(timestamp)


def format_date(date: datetime, format_string: str = "%Y-%m") -> str:
    """Formats a date for folder naming.
    
    Args:
        date: The datetime object to format
        format_string: Format string (default: "%Y-%m" for YYYY-MM)
        
    Returns:
        str: Formatted date string
    """
    return date.strftime(format_string)
