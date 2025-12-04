"""CLI module for handling user interaction with Rich library components."""

import argparse
from pathlib import Path
from typing import Callable, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

console = Console()


def parse_arguments() -> tuple[Optional[Path], bool]:
    """Parse command-line arguments for path and dry-run flag.
    
    Returns:
        tuple: (path or None, dry_run flag)
    """
    parser = argparse.ArgumentParser(
        prog='sik',
        description='Sik Sort - Organize files into categorized folders'
    )
    parser.add_argument(
        'path',
        nargs='?',
        help='Source directory path to sort'
    )
    parser.add_argument(
        '--dry',
        '--dry-run',
        action='store_true',
        dest='dry_run',
        help='Simulate operations without modifying files'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Bypass safety checks (USE WITH EXTREME CAUTION!)'
    )
    
    args = parser.parse_args()
    
    # If path is provided, validate it
    if args.path:
        path = Path(args.path)
        if not path.exists():
            display_error(f"Path does not exist: {args.path}")
            raise SystemExit(1)
        if not path.is_dir():
            display_error(f"Path is not a directory: {args.path}")
            raise SystemExit(1)
        return path, args.dry_run
    
    # No path provided, will need to prompt
    return None, args.dry_run


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


def display_statistics(stats, dry_run: bool = False) -> None:
    """Show sorting results using Rich tables.
    
    Args:
        stats: SortingStats object containing file counts
        dry_run: If True, indicate these are simulated statistics
    """
    title = "Sorting Statistics (DRY RUN)" if dry_run else "Sorting Statistics"
    table = Table(title=title, show_header=True, header_style="bold magenta")
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


def display_safety_warnings(warnings: list[str]) -> bool:
    """Display safety warnings and get user confirmation.
    
    Args:
        warnings: List of warning messages
        
    Returns:
        bool: True if user confirms to proceed, False otherwise
    """
    console.print()
    console.print("[bold red]⚠️  SAFETY WARNING ⚠️[/bold red]")
    console.print()
    console.print("[yellow]The following concerns were detected:[/yellow]")
    console.print()
    
    for i, warning in enumerate(warnings, 1):
        console.print(f"  [red]{i}.[/red] {warning}")
    
    console.print()
    console.print("[bold yellow]Sorting this directory may reorganize important development files![/bold yellow]")
    console.print("[yellow]This could break your project or make files difficult to find.[/yellow]")
    console.print()
    
    return Confirm.ask(
        "[bold red]Are you ABSOLUTELY SURE you want to proceed?[/bold red]",
        default=False
    )


def display_ascii_progress(current: int, total: int) -> None:
    """Shows ASCII progress bar with █ and ░ characters.
    
    Args:
        current: Current number of items processed
        total: Total number of items to process
    """
    if total == 0:
        percentage = 100
    else:
        percentage = int((current / total) * 100)
    
    # Fixed bar width of 20 characters
    bar_width = 20
    filled = int((current / total) * bar_width) if total > 0 else bar_width
    empty = bar_width - filled
    
    # Build the progress bar
    bar = '█' * filled + '░' * empty
    
    # Print with carriage return for in-place update
    print(f'\r[{bar}] {percentage}%', end='', flush=True)


def display_dry_run_banner() -> None:
    """Show prominent banner indicating dry-run mode."""
    console.print()
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
    console.print("[bold yellow]                    DRY RUN MODE                           [/bold yellow]")
    console.print("[bold yellow]           No files will be modified                       [/bold yellow]")
    console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
    console.print()
