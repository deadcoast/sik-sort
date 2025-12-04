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


@dataclass
class EnhancedSortingStats:
    """Enhanced statistics for file sorting operations with size tracking."""
    total_files: int = 0
    img_count: int = 0
    vid_count: int = 0
    arc_count: int = 0
    msk_count: int = 0
    img_size: int = 0
    vid_size: int = 0
    arc_size: int = 0
    msk_size: int = 0
    conflicts_resolved: int = 0
    largest_img: tuple[str, int] | None = None
    largest_vid: tuple[str, int] | None = None
    largest_arc: tuple[str, int] | None = None
    largest_msk: tuple[str, int] | None = None
    duration: float = 0.0
    excluded_count: int = 0
    
    def increment(self, category: FileCategory, size: int, filename: str, conflict: bool) -> None:
        """Increment counters with size tracking.
        
        Args:
            category: The file category to increment
            size: Size of the file in bytes
            filename: Name of the file
            conflict: Whether a conflict was resolved for this file
        """
        self.total_files += 1
        
        if conflict:
            self.conflicts_resolved += 1
        
        if category == FileCategory.IMAGE:
            self.img_count += 1
            self.img_size += size
            if self.largest_img is None or size > self.largest_img[1]:
                self.largest_img = (filename, size)
        elif category == FileCategory.VIDEO:
            self.vid_count += 1
            self.vid_size += size
            if self.largest_vid is None or size > self.largest_vid[1]:
                self.largest_vid = (filename, size)
        elif category == FileCategory.ARCHIVE:
            self.arc_count += 1
            self.arc_size += size
            if self.largest_arc is None or size > self.largest_arc[1]:
                self.largest_arc = (filename, size)
        elif category == FileCategory.MISC:
            self.msk_count += 1
            self.msk_size += size
            if self.largest_msk is None or size > self.largest_msk[1]:
                self.largest_msk = (filename, size)
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format bytes to human-readable string.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            str: Human-readable size string (e.g., "1.50 MB")
        """
        if size_bytes < 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.2f} {units[unit_index]}"


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
