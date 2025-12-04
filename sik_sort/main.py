"""Main entry point for Sik Sort application."""

from pathlib import Path
from rich.console import Console
from .classifier import FileCategory
from .cli import (
    parse_arguments,
    prompt_for_path,
    display_statistics,
    confirm_cleanup,
    show_progress,
    display_error,
    display_safety_warnings,
    display_ascii_progress,
    display_dry_run_banner
)
from .sorter import sort_files
from .scanner import scan_directory
from .cleaner import find_empty_directories, remove_empty_directories
from .safety import run_safety_checks

console = Console()


def setup_category_folders(source_path: Path, dry_run: bool = False) -> None:
    """Creates target category folders.
    
    Args:
        source_path: Root directory where category folders should be created
        dry_run: If True, simulate folder creation without actually creating them
    """
    if dry_run:
        # In dry-run mode, don't actually create folders
        return
    
    category_folders = ['img', 'vid', 'arc', 'msk']
    for folder_name in category_folders:
        folder_path = source_path / folder_name
        folder_path.mkdir(exist_ok=True)


def main() -> None:
    """Main application flow."""
    try:
        # Parse command line arguments
        source_path, dry_run = parse_arguments()
        
        # Display welcome message
        console.print("[bold green]Welcome to Sik Sort![/bold green]")
        console.print()
        
        # Display dry-run banner if in dry-run mode
        if dry_run:
            display_dry_run_banner()
        
        # If no path provided via command line, prompt for it
        if source_path is None:
            source_path = prompt_for_path()
        
        # Run safety checks (always run them for now, --force can be added later if needed)
        warnings = run_safety_checks(source_path)
        if warnings:
            if not display_safety_warnings(warnings):
                console.print("[yellow]Operation cancelled for safety.[/yellow]")
                return
        
        # Setup category folders
        console.print("[cyan]Setting up category folders...[/cyan]")
        setup_category_folders(source_path, dry_run=dry_run)
        
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
        
        # Use ASCII progress bar
        stats = sort_files(source_path, dry_run=dry_run, ascii_progress_callback=display_ascii_progress)
        
        # Print newline after progress bar completes
        print()
        
        console.print()
        console.print("[bold green]Sorting complete![/bold green]")
        
        # Display statistics
        display_statistics(stats, dry_run=dry_run)
        
        # Skip cleanup prompt in dry-run mode
        if not dry_run:
            # Prompt for cleanup
            if confirm_cleanup():
                console.print("[cyan]Cleaning up empty directories...[/cyan]")
                preserve_dirs = {'img', 'vid', 'arc', 'msk'}
                empty_dirs = find_empty_directories(source_path, preserve_dirs)
                removed_count = remove_empty_directories(empty_dirs)
                console.print(f"[green]Removed {removed_count} empty directories.[/green]")
            else:
                console.print("[yellow]Skipping cleanup.[/yellow]")
        
        # Display dry-run completion banner
        if dry_run:
            console.print()
            console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
            console.print("[bold yellow]              DRY RUN COMPLETE                           [/bold yellow]")
            console.print("[bold yellow]           No changes were made                          [/bold yellow]")
            console.print("[bold yellow]" + "=" * 60 + "[/bold yellow]")
        
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
