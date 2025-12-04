"""File sorter module for coordinating the sorting process."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Union
from datetime import datetime
import shutil
from .classifier import FileCategory, classify_file
from .scanner import scan_directory
from .operation_logger import log_file_operation
from .size_classifier import SizeCategory, SizeThresholds, classify_by_size
from .date_classifier import classify_by_date, DateMode
from .duplicates import find_duplicates, calculate_space_saved


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
class FileOperation:
    """Record of a file operation for undo functionality."""
    source: Path
    destination: Path
    timestamp: datetime
    category: str
    size: int
    hash: Optional[str] = None


@dataclass
class EnhancedSortingStats:
    """Enhanced statistics for file sorting operations with advanced features."""
    # Existing fields
    total_files: int = 0
    img_count: int = 0
    vid_count: int = 0
    arc_count: int = 0
    msk_count: int = 0
    
    # New fields for advanced features
    excluded_by_filters: int = 0
    duplicates_found: int = 0
    space_saved: int = 0
    size_categories: dict = field(default_factory=dict)
    date_categories: dict = field(default_factory=dict)
    operations: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    
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


def sort_files(source_path: Path, dry_run: bool = False, progress_callback: Callable = None, ascii_progress_callback: Callable = None, record_operations: bool = False) -> Union[SortingStats, EnhancedSortingStats]:
    """Main sorting orchestrator.
    
    Args:
        source_path: Root directory to sort files from
        dry_run: If True, simulate operations without modifying files
        progress_callback: Callback function for progress updates (Rich progress)
        ascii_progress_callback: Callback function for ASCII progress bar updates
        record_operations: If True, return EnhancedSortingStats with FileOperation records
        
    Returns:
        SortingStats or EnhancedSortingStats: Statistics about the sorting operation
    """
    if record_operations:
        stats = EnhancedSortingStats()
    else:
        stats = SortingStats()
    
    # Define category folders to exclude from scanning
    exclude_dirs = {'img', 'vid', 'arc', 'msk'}
    
    # Scan for all files
    files = scan_directory(source_path, exclude_dirs)
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        # Classify the file
        category = classify_file(file_path)
        
        # Log the operation
        log_file_operation(file_path.name, category, dry_run=dry_run)
        
        # Determine destination folder
        dest_folder = source_path / category.value
        if not dry_run:
            dest_folder.mkdir(exist_ok=True)
        
        # Move file with conflict resolution
        dest_path = dest_folder / file_path.name
        actual_dest = move_file_with_conflict_resolution(file_path, dest_path, dry_run=dry_run)
        
        # Record operation if requested
        if record_operations and isinstance(stats, EnhancedSortingStats):
            file_size = file_path.stat().st_size if file_path.exists() else 0
            operation = FileOperation(
                source=file_path,
                destination=actual_dest,
                timestamp=datetime.now(),
                category=category.value,
                size=file_size
            )
            stats.operations.append(operation)
        
        # Update statistics
        stats.increment(category)
        
        # Call progress callbacks
        if progress_callback:
            progress_callback()
        
        if ascii_progress_callback:
            ascii_progress_callback(i, len(files))
    
    return stats


def move_file_with_conflict_resolution(src: Path, dest: Path, dry_run: bool = False) -> Path:
    """Moves file and handles naming conflicts.
    
    Args:
        src: Source file path
        dest: Destination file path
        dry_run: If True, simulate the move without actually moving files
        
    Returns:
        Path: Actual destination path (may differ from dest if conflict occurred)
    """
    if dry_run:
        # In dry-run mode, don't actually move files
        return dest
    
    # If destination doesn't exist, move directly
    if not dest.exists():
        shutil.move(str(src), str(dest))
        return dest
    
    # Handle conflict by generating unique filename
    unique_filename = generate_unique_filename(dest.parent, dest.name)
    unique_dest = dest.parent / unique_filename
    shutil.move(str(src), str(unique_dest))
    return unique_dest


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



def sort_files_with_size(
    source_path: Path,
    thresholds: SizeThresholds = None,
    dry_run: bool = False,
    progress_callback: Callable = None,
    ascii_progress_callback: Callable = None
) -> EnhancedSortingStats:
    """Sort files with size-based hierarchy (size/type).
    
    Args:
        source_path: Root directory to sort files from
        thresholds: Custom size thresholds (uses defaults if None)
        dry_run: If True, simulate operations without modifying files
        progress_callback: Callback function for progress updates
        ascii_progress_callback: Callback function for ASCII progress bar updates
        
    Returns:
        EnhancedSortingStats: Statistics about the sorting operation
    """
    stats = EnhancedSortingStats()
    
    if thresholds is None:
        thresholds = SizeThresholds()
    
    # Define category folders to exclude from scanning
    exclude_dirs = {'img', 'vid', 'arc', 'msk', 'small', 'medium', 'large'}
    
    # Scan for all files
    files = scan_directory(source_path, exclude_dirs)
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        try:
            # Classify by size and type
            size_category = classify_by_size(file_path, thresholds)
            type_category = classify_file(file_path)
            
            # Determine destination folder: size/type
            dest_folder = source_path / size_category.value / type_category.value
            if not dry_run:
                dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Move file with conflict resolution
            dest_path = dest_folder / file_path.name
            actual_dest = move_file_with_conflict_resolution(file_path, dest_path, dry_run=dry_run)
            
            # Record operation
            file_size = file_path.stat().st_size if file_path.exists() else 0
            operation = FileOperation(
                source=file_path,
                destination=actual_dest,
                timestamp=datetime.now(),
                category=f"{size_category.value}/{type_category.value}",
                size=file_size
            )
            stats.operations.append(operation)
            
            # Update statistics
            stats.increment(type_category)
            
            # Track size category counts
            size_key = size_category.value
            if size_key not in stats.size_categories:
                stats.size_categories[size_key] = 0
            stats.size_categories[size_key] += 1
            
            # Call progress callbacks
            if progress_callback:
                progress_callback()
            
            if ascii_progress_callback:
                ascii_progress_callback(i, len(files))
                
        except Exception as e:
            stats.errors.append(f"Error processing {file_path}: {str(e)}")
    
    return stats


def sort_files_with_date(
    source_path: Path,
    use_creation: bool = False,
    date_format: str = "%Y-%m",
    dry_run: bool = False,
    progress_callback: Callable = None,
    ascii_progress_callback: Callable = None
) -> EnhancedSortingStats:
    """Sort files with date-based hierarchy (date/type).
    
    Args:
        source_path: Root directory to sort files from
        use_creation: If True, use creation date; otherwise use modification date
        date_format: Format string for date folders (default: "%Y-%m")
        dry_run: If True, simulate operations without modifying files
        progress_callback: Callback function for progress updates
        ascii_progress_callback: Callback function for ASCII progress bar updates
        
    Returns:
        EnhancedSortingStats: Statistics about the sorting operation
    """
    stats = EnhancedSortingStats()
    
    # Define category folders to exclude from scanning
    exclude_dirs = {'img', 'vid', 'arc', 'msk'}
    
    # Scan for all files
    files = scan_directory(source_path, exclude_dirs)
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        try:
            # Classify by date and type
            date_folder = classify_by_date(file_path, use_creation, date_format)
            type_category = classify_file(file_path)
            
            # Determine destination folder: date/type
            dest_folder = source_path / date_folder / type_category.value
            if not dry_run:
                dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Move file with conflict resolution
            dest_path = dest_folder / file_path.name
            actual_dest = move_file_with_conflict_resolution(file_path, dest_path, dry_run=dry_run)
            
            # Record operation
            file_size = file_path.stat().st_size if file_path.exists() else 0
            operation = FileOperation(
                source=file_path,
                destination=actual_dest,
                timestamp=datetime.now(),
                category=f"{date_folder}/{type_category.value}",
                size=file_size
            )
            stats.operations.append(operation)
            
            # Update statistics
            stats.increment(type_category)
            
            # Track date category counts
            if date_folder not in stats.date_categories:
                stats.date_categories[date_folder] = 0
            stats.date_categories[date_folder] += 1
            
            # Call progress callbacks
            if progress_callback:
                progress_callback()
            
            if ascii_progress_callback:
                ascii_progress_callback(i, len(files))
                
        except Exception as e:
            stats.errors.append(f"Error processing {file_path}: {str(e)}")
    
    return stats


def sort_files_archive_mode(
    source_path: Path,
    use_creation: bool = False,
    date_format: str = "%Y-%m",
    with_type_hierarchy: bool = False,
    dry_run: bool = False,
    progress_callback: Callable = None,
    ascii_progress_callback: Callable = None
) -> EnhancedSortingStats:
    """Sort files into dated archive folders.
    
    Args:
        source_path: Root directory to sort files from
        use_creation: If True, use creation date; otherwise use modification date
        date_format: Format string for date folders (default: "%Y-%m")
        with_type_hierarchy: If True, create date/type hierarchy; otherwise flat date structure
        dry_run: If True, simulate operations without modifying files
        progress_callback: Callback function for progress updates
        ascii_progress_callback: Callback function for ASCII progress bar updates
        
    Returns:
        EnhancedSortingStats: Statistics about the sorting operation
    """
    stats = EnhancedSortingStats()
    
    # Define category folders to exclude from scanning
    exclude_dirs = {'img', 'vid', 'arc', 'msk'}
    
    # Scan for all files
    files = scan_directory(source_path, exclude_dirs)
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        try:
            # Classify by date
            date_folder = classify_by_date(file_path, use_creation, date_format)
            
            if with_type_hierarchy:
                # Create date/type hierarchy
                type_category = classify_file(file_path)
                dest_folder = source_path / date_folder / type_category.value
                category_str = f"{date_folder}/{type_category.value}"
            else:
                # Flat structure: just date folder
                dest_folder = source_path / date_folder
                type_category = classify_file(file_path)  # Still classify for stats
                category_str = date_folder
            
            if not dry_run:
                dest_folder.mkdir(parents=True, exist_ok=True)
            
            # Move file with conflict resolution
            dest_path = dest_folder / file_path.name
            actual_dest = move_file_with_conflict_resolution(file_path, dest_path, dry_run=dry_run)
            
            # Record operation
            file_size = file_path.stat().st_size if file_path.exists() else 0
            operation = FileOperation(
                source=file_path,
                destination=actual_dest,
                timestamp=datetime.now(),
                category=category_str,
                size=file_size
            )
            stats.operations.append(operation)
            
            # Update statistics
            stats.increment(type_category)
            
            # Track date category counts
            if date_folder not in stats.date_categories:
                stats.date_categories[date_folder] = 0
            stats.date_categories[date_folder] += 1
            
            # Call progress callbacks
            if progress_callback:
                progress_callback()
            
            if ascii_progress_callback:
                ascii_progress_callback(i, len(files))
                
        except Exception as e:
            stats.errors.append(f"Error processing {file_path}: {str(e)}")
    
    return stats


def sort_files_with_duplicates(
    source_path: Path,
    hash_algorithm: str = "md5",
    dry_run: bool = False,
    progress_callback: Callable = None,
    ascii_progress_callback: Callable = None
) -> EnhancedSortingStats:
    """Sort files with duplicate detection.
    
    Args:
        source_path: Root directory to sort files from
        hash_algorithm: Hash algorithm to use ("md5" or "sha256")
        dry_run: If True, simulate operations without modifying files
        progress_callback: Callback function for progress updates
        ascii_progress_callback: Callback function for ASCII progress bar updates
        
    Returns:
        EnhancedSortingStats: Statistics about the sorting operation
    """
    stats = EnhancedSortingStats()
    
    # Define category folders to exclude from scanning
    exclude_dirs = {'img', 'vid', 'arc', 'msk', 'duplicates'}
    
    # Scan for all files
    files = scan_directory(source_path, exclude_dirs)
    
    # Find duplicates
    duplicates = find_duplicates(files, hash_algorithm)
    duplicate_files = set()
    for file_list in duplicates.values():
        # Keep first file, mark rest as duplicates
        for file_path in file_list[1:]:
            duplicate_files.add(file_path)
    
    # Calculate space saved
    stats.space_saved = calculate_space_saved(duplicates)
    stats.duplicates_found = len(duplicate_files)
    
    # Process each file
    for i, file_path in enumerate(files, 1):
        try:
            if file_path in duplicate_files:
                # Move to duplicates folder
                dest_folder = source_path / "duplicates"
                if not dry_run:
                    dest_folder.mkdir(exist_ok=True)
                
                # Add duplicate suffix to filename
                dest_path = dest_folder / f"{file_path.stem}_duplicate{file_path.suffix}"
                category_str = "duplicates"
                type_category = classify_file(file_path)  # Still classify for stats
            else:
                # Normal classification
                type_category = classify_file(file_path)
                dest_folder = source_path / type_category.value
                if not dry_run:
                    dest_folder.mkdir(exist_ok=True)
                dest_path = dest_folder / file_path.name
                category_str = type_category.value
            
            # Move file with conflict resolution
            actual_dest = move_file_with_conflict_resolution(file_path, dest_path, dry_run=dry_run)
            
            # Record operation
            file_size = file_path.stat().st_size if file_path.exists() else 0
            operation = FileOperation(
                source=file_path,
                destination=actual_dest,
                timestamp=datetime.now(),
                category=category_str,
                size=file_size
            )
            stats.operations.append(operation)
            
            # Update statistics (only count non-duplicates in category counts)
            if file_path not in duplicate_files:
                stats.increment(type_category)
            
            # Call progress callbacks
            if progress_callback:
                progress_callback()
            
            if ascii_progress_callback:
                ascii_progress_callback(i, len(files))
                
        except Exception as e:
            stats.errors.append(f"Error processing {file_path}: {str(e)}")
    
    return stats
