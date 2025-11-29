"""File sorter module for coordinating the sorting process."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import shutil
from .classifier import FileCategory, classify_file
from .scanner import scan_directory


@dataclass
class SortingStats:
    """Statistics for file sorting operations."""
    total_files: int = 0
    img_count: int = 0
    vid_count: int = 0
    arc_count: int = 0
    msk_count: int = 0
    
    def increment(self, category: FileCategory) -> None:
        """Increment counter for given category.
        
        Args:
            category: The file category to increment
        """
        self.total_files += 1
        if category == FileCategory.IMAGE:
            self.img_count += 1
        elif category == FileCategory.VIDEO:
            self.vid_count += 1
        elif category == FileCategory.ARCHIVE:
            self.arc_count += 1
        elif category == FileCategory.MISC:
            self.msk_count += 1


def sort_files(source_path: Path, progress_callback: Callable) -> SortingStats:
    """Main sorting orchestrator.
    
    Args:
        source_path: Root directory to sort files from
        progress_callback: Callback function for progress updates
        
    Returns:
        SortingStats: Statistics about the sorting operation
    """
    stats = SortingStats()
    
    # Define category folders to exclude from scanning
    exclude_dirs = {'img', 'vid', 'arc', 'msk'}
    
    # Scan for all files
    files = scan_directory(source_path, exclude_dirs)
    
    # Process each file
    for file_path in files:
        # Classify the file
        category = classify_file(file_path)
        
        # Determine destination folder
        dest_folder = source_path / category.value
        dest_folder.mkdir(exist_ok=True)
        
        # Move file with conflict resolution
        dest_path = dest_folder / file_path.name
        move_file_with_conflict_resolution(file_path, dest_path)
        
        # Update statistics
        stats.increment(category)
        
        # Call progress callback
        if progress_callback:
            progress_callback()
    
    return stats


def move_file_with_conflict_resolution(src: Path, dest: Path) -> None:
    """Moves file and handles naming conflicts.
    
    Args:
        src: Source file path
        dest: Destination file path
    """
    # If destination doesn't exist, move directly
    if not dest.exists():
        shutil.move(str(src), str(dest))
        return
    
    # Handle conflict by generating unique filename
    unique_filename = generate_unique_filename(dest.parent, dest.name)
    unique_dest = dest.parent / unique_filename
    shutil.move(str(src), str(unique_dest))


def generate_unique_filename(dest_path: Path, filename: str) -> str:
    """Creates unique filename when conflicts occur.
    
    Args:
        dest_path: Destination directory path
        filename: Original filename
        
    Returns:
        str: Unique filename
    """
    # Split filename into name and extension
    path = Path(filename)
    name = path.stem
    ext = path.suffix
    
    # Try incrementing numbers until we find a unique name
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not (dest_path / new_filename).exists():
            return new_filename
        counter += 1
