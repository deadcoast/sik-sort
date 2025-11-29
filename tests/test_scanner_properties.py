"""Property-based tests for directory scanner module."""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.scanner import scan_directory


# Windows reserved names that cannot be used as file or directory names
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}


def is_valid_windows_name(name: str) -> bool:
    """Check if a name is valid on Windows."""
    if not name or name.upper() in WINDOWS_RESERVED_NAMES:
        return False
    # Check if name ends with space or period (invalid on Windows)
    if name.endswith(' ') or name.endswith('.'):
        return False
    return True


# Feature: file-sorter-cli, Property 8: Recursive traversal finds all files
@settings(max_examples=100)
@given(
    # Generate a list of file paths with varying depths
    file_paths=st.lists(
        st.tuples(
            # Directory depth (0-5 levels)
            st.integers(min_value=0, max_value=5),
            # Directory names at each level
            st.lists(
                st.text(
                    min_size=1, 
                    max_size=10, 
                    alphabet=st.characters(
                        whitelist_categories=('Lu', 'Ll', 'Nd'),
                        blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|']
                    )
                ),
                min_size=0,
                max_size=5
            ),
            # Filename
            st.text(
                min_size=1, 
                max_size=15, 
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
                )
            ),
            # File extension
            st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf'])
        ),
        min_size=1,
        max_size=20
    )
)
def test_recursive_traversal_finds_all_files(file_paths):
    """
    Property 8: Recursive traversal finds all files
    
    For any directory structure with files at various depths,
    the scanner should find all files regardless of their nesting level.
    
    Validates: Requirements 3.1
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        created_files = []
        
        # Create the directory structure and files
        for depth, dir_names, filename, extension in file_paths:
            # Skip invalid filenames
            if not is_valid_windows_name(filename):
                continue
            
            # Build the directory path
            current_path = root
            
            # Use the actual depth value to determine how many dir_names to use
            actual_dirs = dir_names[:depth] if depth > 0 else []
            
            for dir_name in actual_dirs:
                if dir_name and is_valid_windows_name(dir_name):  # Skip empty or invalid directory names
                    current_path = current_path / dir_name
                    current_path.mkdir(exist_ok=True)
            
            # Create the file
            file_path = current_path / f"{filename}.{extension}"
            
            # Skip if this exact file already exists (avoid duplicates)
            if file_path in created_files:
                continue
                
            try:
                file_path.write_text("test content")
                created_files.append(file_path)
            except (OSError, FileNotFoundError):
                # Skip files that can't be created due to OS restrictions
                continue
        
        # Assume we created at least one file
        assume(len(created_files) > 0)
        
        # Scan the directory (no exclusions for this test)
        found_files = scan_directory(root, set())
        
        # Convert to sets for comparison
        created_set = set(created_files)
        found_set = set(found_files)
        
        # Assert all created files were found
        assert created_set == found_set, (
            f"Expected to find {len(created_files)} files, but found {len(found_files)}. "
            f"Missing: {created_set - found_set}, Extra: {found_set - created_set}"
        )
