"""Property-based tests for folder cleaner module."""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.cleaner import find_empty_directories, remove_empty_directories


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


# Feature: file-sorter-cli, Property 11: Empty directories are removed
@settings(max_examples=100)
@given(
    # Generate directory structure with some empty and some non-empty directories
    dir_structure=st.lists(
        st.tuples(
            # Directory path components
            st.lists(
                st.text(
                    min_size=1,
                    max_size=10,
                    alphabet=st.characters(
                        whitelist_categories=('Lu', 'Ll', 'Nd'),
                        blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|']
                    )
                ),
                min_size=1,
                max_size=3
            ),
            # Whether this directory should have a file (True = has file, False = empty)
            st.booleans()
        ),
        min_size=1,
        max_size=15
    )
)
def test_empty_directories_are_removed(dir_structure):
    """
    Property 11: Empty directories are removed
    
    For any directory structure after sorting, when cleanup is selected,
    all empty directories (except category folders) should be removed.
    
    Validates: Requirements 5.2
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        
        # Category folders to preserve
        preserve_dirs = {'img', 'vid', 'arc', 'msk'}
        
        # Create preserved category folders (some empty, some with files)
        for category in preserve_dirs:
            (root / category).mkdir()
        
        # Track which directories should be empty after cleanup
        expected_empty_dirs = set()
        expected_non_empty_dirs = set()
        
        # Create the directory structure
        for dir_components, has_file in dir_structure:
            # Filter out invalid directory names
            valid_components = [d for d in dir_components if d and is_valid_windows_name(d)]
            
            # Skip if no valid components
            if not valid_components:
                continue
            
            # Build the directory path
            current_path = root
            for component in valid_components:
                current_path = current_path / component
                try:
                    current_path.mkdir(exist_ok=True)
                except (OSError, FileNotFoundError):
                    # Skip if we can't create the directory
                    break
            else:
                # Only process if we successfully created all directories
                if has_file:
                    # Create a file in this directory
                    try:
                        (current_path / "file.txt").write_text("content")
                        # Mark this directory and all its parents as non-empty
                        temp_path = current_path
                        while temp_path != root:
                            expected_non_empty_dirs.add(temp_path)
                            temp_path = temp_path.parent
                    except (OSError, FileNotFoundError):
                        # If we can't create the file, treat as empty
                        if current_path not in expected_non_empty_dirs:
                            expected_empty_dirs.add(current_path)
                else:
                    # This directory should be empty (if not already marked as non-empty)
                    if current_path not in expected_non_empty_dirs:
                        expected_empty_dirs.add(current_path)
        
        # Find and remove empty directories iteratively until none are left
        # This handles nested empty directories
        total_removed = 0
        while True:
            empty_dirs = find_empty_directories(root, preserve_dirs)
            if not empty_dirs:
                break
            removed_count = remove_empty_directories(empty_dirs)
            total_removed += removed_count
            if removed_count == 0:
                break
        
        # Verify that empty directories were removed
        for empty_dir in expected_empty_dirs:
            if empty_dir.exists():
                # Check if it's actually empty
                try:
                    is_empty = not any(empty_dir.iterdir())
                    assert not is_empty, (
                        f"Empty directory {empty_dir} was not removed"
                    )
                except (PermissionError, OSError):
                    # Can't check, skip
                    pass
        
        # Verify that non-empty directories still exist
        for non_empty_dir in expected_non_empty_dirs:
            assert non_empty_dir.exists(), (
                f"Non-empty directory {non_empty_dir} was incorrectly removed"
            )
        
        # Verify that preserved directories still exist
        for category in preserve_dirs:
            category_dir = root / category
            assert category_dir.exists(), (
                f"Preserved category directory {category} was removed"
            )
