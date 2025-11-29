"""CLI module for handling user interaction with Rich library components."""

from pathlib import Path
from typing import Callable
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

console = Console()


def prompt_for_path() -> Path:
    """Prompt user for source directory path with validation.
    
    Returns:
        Path: Validated directory path
    """
    pass


def display_statistics(stats) -> None:
    """Show sorting results using Rich tables.
    
    Args:
        stats: SortingStats object containing file counts
    """
    pass


def confirm_cleanup() -> bool:
    """Prompt user for empty folder cleanup confirmation.
    
    Returns:
        bool: True if user confirms cleanup, False otherwise
    """
    pass


def show_progress(total: int) -> Progress:
    """Create Rich progress bar for file operations.
    
    Args:
        total: Total number of items to process
        
    Returns:
        Progress: Rich progress bar instance
    """
    pass


def display_error(message: str) -> None:
    """Show formatted error messages.
    
    Args:
        message: Error message to display
    """
    pass
