"""Size classifier module for categorizing files by size."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SizeCategory(Enum):
    """Size category enumeration."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class SizeThresholds:
    """Size thresholds for categorizing files.
    
    Attributes:
        small_max: Maximum size in bytes for small files (default: 1 MB)
        medium_max: Maximum size in bytes for medium files (default: 100 MB)
    """
    small_max: int = 1_048_576  # 1 MB
    medium_max: int = 104_857_600  # 100 MB


def classify_by_size(file_path: Path, thresholds: SizeThresholds = None) -> SizeCategory:
    """Categorizes a file by its size.
    
    Args:
        file_path: Path to the file to classify
        thresholds: Custom size thresholds (uses defaults if None)
        
    Returns:
        SizeCategory: The size category the file belongs to
    """
    if thresholds is None:
        thresholds = SizeThresholds()
    
    size = get_file_size(file_path)
    
    if size <= thresholds.small_max:
        return SizeCategory.SMALL
    elif size <= thresholds.medium_max:
        return SizeCategory.MEDIUM
    else:
        return SizeCategory.LARGE


def get_file_size(file_path: Path) -> int:
    """Retrieves the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: File size in bytes
    """
    return file_path.stat().st_size


def format_size(bytes: int) -> str:
    """Converts bytes to human-readable format.
    
    Args:
        bytes: Size in bytes
        
    Returns:
        str: Human-readable size string (e.g., "1.50 MB")
    """
    if bytes < 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes)
    unit_index = 0
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"
