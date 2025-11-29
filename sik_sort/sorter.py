"""File sorter module for coordinating the sorting process."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from .classifier import FileCategory


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
        pass


def sort_files(source_path: Path, progress_callback: Callable) -> SortingStats:
    """Main sorting orchestrator.
    
    Args:
        source_path: Root directory to sort files from
        progress_callback: Callback function for progress updates
        
    Returns:
        SortingStats: Statistics about the sorting operation
    """
    pass


def move_file_with_conflict_resolution(src: Path, dest: Path) -> None:
    """Moves file and handles naming conflicts.
    
    Args:
        src: Source file path
        dest: Destination file path
    """
    pass


def generate_unique_filename(dest_path: Path, filename: str) -> str:
    """Creates unique filename when conflicts occur.
    
    Args:
        dest_path: Destination directory path
        filename: Original filename
        
    Returns:
        str: Unique filename
    """
    pass
