"""Folder cleaner module for removing empty directories."""

from pathlib import Path


def find_empty_directories(root_path: Path, preserve_dirs: set[str]) -> list[Path]:
    """Finds all empty directories.
    
    Args:
        root_path: Root directory to search
        preserve_dirs: Set of directory names to preserve even if empty
        
    Returns:
        list[Path]: List of empty directory paths
    """
    empty_dirs = []
    
    # Walk the directory tree bottom-up so we can detect empty directories
    # after their subdirectories have been processed
    for dirpath, dirnames, filenames in root_path.walk(top_down=False):
        current_dir = Path(dirpath)
        
        # Skip if this is a preserved directory
        if current_dir.name in preserve_dirs:
            continue
        
        # Skip the root directory itself
        if current_dir == root_path:
            continue
        
        # Check if directory is empty (no files and no subdirectories)
        try:
            # A directory is empty if it has no items
            if not any(current_dir.iterdir()):
                empty_dirs.append(current_dir)
        except (PermissionError, OSError):
            # Skip directories we can't access
            continue
    
    return empty_dirs


def remove_empty_directories(directories: list[Path]) -> int:
    """Removes empty folders and returns count.
    
    Repeatedly removes empty directories until no more can be removed.
    This handles nested empty directories where a parent becomes empty
    after its empty child is removed.
    
    Args:
        directories: List of directory paths to remove
        
    Returns:
        int: Number of directories removed
    """
    removed_count = 0
    
    for directory in directories:
        try:
            directory.rmdir()
            removed_count += 1
        except (PermissionError, OSError, FileNotFoundError):
            # Skip directories we can't remove or that no longer exist
            continue
    
    return removed_count
