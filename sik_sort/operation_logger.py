"""Operation logger module for real-time console logging during file operations."""

from pathlib import Path
from rich.console import Console
from .classifier import FileCategory


# Create a global console instance for logging
console = Console()


def log_file_operation(filename: str, category: FileCategory, dry_run: bool = False) -> None:
    """Logs a file being moved to a category with color coding.
    
    Args:
        filename: Name of the file being moved
        category: Destination category for the file
        dry_run: Whether this is a dry-run simulation
    """
    # Define category-specific colors
    category_colors = {
        FileCategory.IMAGE: "green",
        FileCategory.VIDEO: "blue",
        FileCategory.ARCHIVE: "yellow",
        FileCategory.MISC: "white"
    }
    
    color = category_colors.get(category, "white")
    prefix = "[DRY RUN] " if dry_run else ""
    
    # Format: [CATEGORY] filename → category_folder
    console.print(
        f"{prefix}[{color}][{category.value.upper()}][/{color}] {filename} → {category.value}/",
        highlight=False
    )


def log_scan_complete(file_count: int) -> None:
    """Logs completion of directory scan with file count.
    
    Args:
        file_count: Total number of files found during scan
    """
    console.print(
        f"\n[bold cyan]Scan complete:[/bold cyan] Found {file_count} file(s) to process\n",
        highlight=False
    )


def log_conflict_resolution(original_name: str, new_name: str) -> None:
    """Logs when a filename conflict is resolved.
    
    Args:
        original_name: Original filename that had a conflict
        new_name: New unique filename after resolution
    """
    console.print(
        f"[bold yellow][CONFLICT][/bold yellow] {original_name} → {new_name}",
        highlight=False
    )


def log_error(filename: str, error_message: str) -> None:
    """Logs errors during file operations with red/bold styling.
    
    Args:
        filename: Name of the file that caused the error
        error_message: Description of the error
    """
    console.print(
        f"[bold red][ERROR][/bold red] {filename}: {error_message}",
        highlight=False
    )
