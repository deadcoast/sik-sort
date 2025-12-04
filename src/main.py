"""Main entry point for Sik Sort application."""

import argparse
from pathlib import Path
from rich.console import Console
from .classifier import FileCategory
from .cli import (
    prompt_for_path,
    display_statistics,
    confirm_cleanup,
    show_progress,
    display_error,
    display_safety_warnings
)
from .sorter import sort_files
from .scanner import scan_directory
from .cleaner import find_empty_directories, remove_empty_directories
from .safety import run_safety_checks

console = Console()


def setup_category_folders(source_path: Path) -> None:
    """Creates target category folders.
    
    Args:
        source_path: Root directory where category folders should be created
    """
    category_folders = ['img', 'vid', 'arc', 'msk']
    for folder_name in category_folders:
        folder_path = source_path / folder_name
        folder_path.mkdir(exist_ok=True)


def main() -> None:
    """Main application flow."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Sik Sort - Organize files into categorized folders"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Bypass safety checks (USE WITH EXTREME CAUTION!)'
    )
    args = parser.parse_args()
    
    try:
        # Display welcome message
        console.print("[bold green]Welcome to Sik Sort![/bold green]")
        console.print()
        
        # Prompt for path
        source_path = prompt_for_path()
        
        # Run safety checks unless --force is used
        if not args.force:
            warnings = run_safety_checks(source_path)
            if warnings:
                if not display_safety_warnings(warnings):
                    console.print("[yellow]Operation cancelled for safety.[/yellow]")
                    return
        else:
            console.print()
            console.print("[bold red]⚠️  SAFETY CHECKS BYPASSED ⚠️[/bold red]")
            console.print("[red]Proceeding without safety checks - use at your own risk![/red]")
            console.print()
        
        # Setup category folders
        console.print("[cyan]Setting up category folders...[/cyan]")
        setup_category_folders(source_path)
        
        # Scan directory to count files
        console.print("[cyan]Scanning directory...[/cyan]")
        exclude_dirs = {'img', 'vid', 'arc', 'msk'}
        files = scan_directory(source_path, exclude_dirs)
        
        if not files:
            console.print("[yellow]No files found to sort.[/yellow]")
            return
        
        console.print(f"[green]Found {len(files)} files to sort.[/green]")
        console.print()
        
        # Sort files with progress display
        console.print("[cyan]Sorting files...[/cyan]")
        progress = show_progress(len(files))
        
        with progress:
            task = progress.add_task("[cyan]Processing files...", total=len(files))
            
            def progress_callback():
                progress.update(task, advance=1)
            
            stats = sort_files(source_path, progress_callback)
        
        console.print()
        console.print("[bold green]Sorting complete![/bold green]")
        
        # Display statistics
        display_statistics(stats)
        
        # Prompt for cleanup
        if confirm_cleanup():
            console.print("[cyan]Cleaning up empty directories...[/cyan]")
            preserve_dirs = {'img', 'vid', 'arc', 'msk'}
            empty_dirs = find_empty_directories(source_path, preserve_dirs)
            removed_count = remove_empty_directories(empty_dirs)
            console.print(f"[green]Removed {removed_count} empty directories.[/green]")
        else:
            console.print("[yellow]Skipping cleanup.[/yellow]")
        
        console.print()
        console.print("[bold green]Done![/bold green]")
        
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        display_error(f"An unexpected error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
