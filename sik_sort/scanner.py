"""Directory scanner module for recursive file traversal."""

from pathlib import Path


def scan_directory(path: Path, exclude_dirs: set[str]) -> list[Path]:
    """Returns list of all files to process.
    
    Args:
        path: Root directory to scan
        exclude_dirs: Set of directory names to exclude from scanning
        
    Returns:
        list[Path]: List of file paths found
    """
    pass


def is_excluded_directory(path: Path, exclude_dirs: set[str]) -> bool:
    """Checks if directory should be skipped.
    
    Args:
        path: Directory path to check
        exclude_dirs: Set of directory names to exclude
        
    Returns:
        bool: True if directory should be excluded, False otherwise
    """
    pass
