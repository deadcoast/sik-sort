"""Directory scanner module for recursive file traversal."""

from pathlib import Path
from sik_sort.filters import FilterConfig, apply_filters


def scan_directory(path: Path, exclude_dirs: set[str]) -> list[Path]:
    """Returns list of all files to process.
    
    Args:
        path: Root directory to scan
        exclude_dirs: Set of directory names to exclude from scanning
        
    Returns:
        list[Path]: List of file paths found
    """
    files = []
    
    for item in path.rglob('*'):
        # Skip if any parent directory is excluded
        if any(is_excluded_directory(parent, exclude_dirs) for parent in item.parents):
            continue
        
        # Skip if the item itself is an excluded directory
        if item.is_dir() and is_excluded_directory(item, exclude_dirs):
            continue
            
        # Add files only
        if item.is_file():
            files.append(item)
    
    return files


def is_excluded_directory(path: Path, exclude_dirs: set[str]) -> bool:
    """Checks if directory should be skipped.
    
    Args:
        path: Directory path to check
        exclude_dirs: Set of directory names to exclude
        
    Returns:
        bool: True if directory should be excluded, False otherwise
    """
    return path.name in exclude_dirs


def scan_with_filters(path: Path, exclude_dirs: set[str], filters: FilterConfig) -> tuple[list[Path], int]:
    """Scans directory and applies filters to the file list.
    
    Args:
        path: Root directory to scan
        exclude_dirs: Set of directory names to exclude from scanning
        filters: Filter configuration to apply
        
    Returns:
        tuple: (filtered_files, excluded_count)
            - filtered_files: List of file paths that passed all filters
            - excluded_count: Number of files excluded by filters
    """
    # First scan all files
    all_files = scan_directory(path, exclude_dirs)
    
    # Apply filters to the scanned files
    filtered_files, excluded_count = apply_filters(all_files, filters)
    
    return filtered_files, excluded_count


def scan_multiple_directories(paths: list[Path], exclude_dirs: set[str], filters: FilterConfig) -> dict[Path, list[Path]]:
    """Scans multiple directories and applies filters to each.
    
    Args:
        paths: List of root directories to scan
        exclude_dirs: Set of directory names to exclude from scanning
        filters: Filter configuration to apply
        
    Returns:
        dict: Dictionary mapping each source path to its filtered file list
    """
    results = {}
    
    for path in paths:
        filtered_files, _ = scan_with_filters(path, exclude_dirs, filters)
        results[path] = filtered_files
    
    return results
