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
