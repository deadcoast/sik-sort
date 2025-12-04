"""Filter engine module for filtering files based on patterns and extensions."""

from dataclasses import dataclass, field
from pathlib import Path
from fnmatch import fnmatch


@dataclass
class FilterConfig:
    """Configuration for file filtering.
    
    Attributes:
        include_patterns: List of glob patterns to include (e.g., "*.jpg")
        exclude_patterns: List of glob patterns to exclude (e.g., "*_backup*")
        include_extensions: Set of file extensions to include (e.g., {".pdf", ".doc"})
        exclude_extensions: Set of file extensions to exclude (e.g., {".tmp"})
    """
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    include_extensions: set[str] = field(default_factory=set)
    exclude_extensions: set[str] = field(default_factory=set)


def apply_filters(files: list[Path], config: FilterConfig) -> tuple[list[Path], int]:
    """Filters file list based on patterns and extensions.
    
    Applies filters in the following order:
    1. Include patterns (if specified)
    2. Include extensions (if specified)
    3. Exclude patterns (if specified)
    4. Exclude extensions (if specified)
    
    Args:
        files: List of file paths to filter
        config: Filter configuration
        
    Returns:
        tuple: (filtered_files, excluded_count)
            - filtered_files: List of files that passed all filters
            - excluded_count: Number of files excluded by filters
    """
    total_files = len(files)
    filtered = files.copy()
    
    # Apply include patterns first (if any)
    if config.include_patterns:
        filtered = [f for f in filtered if any(matches_pattern(f, pattern) for pattern in config.include_patterns)]
    
    # Apply include extensions (if any)
    if config.include_extensions:
        filtered = [f for f in filtered if matches_extensions(f, config.include_extensions)]
    
    # Apply exclude patterns (if any)
    if config.exclude_patterns:
        filtered = [f for f in filtered if not any(matches_pattern(f, pattern) for pattern in config.exclude_patterns)]
    
    # Apply exclude extensions (if any)
    if config.exclude_extensions:
        filtered = [f for f in filtered if not matches_extensions(f, config.exclude_extensions)]
    
    excluded_count = total_files - len(filtered)
    return filtered, excluded_count


def matches_pattern(file_path: Path, pattern: str) -> bool:
    """Checks if file matches a glob pattern.
    
    Args:
        file_path: Path to the file
        pattern: Glob pattern (e.g., "*.jpg", "*_backup*")
        
    Returns:
        bool: True if file matches pattern, False otherwise
    """
    return fnmatch(file_path.name, pattern)


def matches_extensions(file_path: Path, extensions: set[str]) -> bool:
    """Checks if file has one of the specified extensions.
    
    Args:
        file_path: Path to the file
        extensions: Set of extensions to check (e.g., {".pdf", ".doc"})
        
    Returns:
        bool: True if file has one of the extensions, False otherwise
    """
    file_ext = file_path.suffix.lower()
    # Normalize extensions to lowercase for comparison
    normalized_extensions = {ext.lower() for ext in extensions}
    return file_ext in normalized_extensions
