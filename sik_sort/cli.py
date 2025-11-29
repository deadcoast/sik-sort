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
    while True:
        path_str = Prompt.ask("[bold cyan]Enter the source directory path[/bold cyan]")
        path = Path(path_str)
        
        if not path.exists():
            display_error(f"Path does not exist: {path_str}")
            continue
        
        if not path.is_dir():
            display_error(f"Path is not a directory: {path_str}")
            continue
        
        return path


def display_statistics(stats) -> None:
    """Show sorting results using Rich tables.
    
    Args:
        stats: SortingStats object containing file counts
    """
    table = Table(title="Sorting Statistics", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="cyan", justify="left")
    table.add_column("Count", style="green", justify="right")
    
    table.add_row("Images (img)", str(stats.img_count))
    table.add_row("Videos (vid)", str(stats.vid_count))
    table.add_row("Archives (arc)", str(stats.arc_count))
    table.add_row("Miscellaneous (msk)", str(stats.msk_count))
    table.add_row("[bold]Total[/bold]", f"[bold]{stats.total_files}[/bold]")
    
    console.print()
    console.print(table)
    console.print()


def confirm_cleanup() -> bool:
    """Prompt user for empty folder cleanup confirmation.
    
    Returns:
        bool: True if user confirms cleanup, False otherwise
    """
    return Confirm.ask("[bold yellow]Do you want to clean up empty folders?[/bold yellow]")


def show_progress(total: int) -> Progress:
    """Create Rich progress bar for file operations.
    
    Args:
        total: Total number of items to process
        
    Returns:
        Progress: Rich progress bar instance
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )
    return progress


def display_error(message: str) -> None:
    """Show formatted error messages.
    
    Args:
        message: Error message to display
    """
    console.print(f"[bold red]Error:[/bold red] {message}")
