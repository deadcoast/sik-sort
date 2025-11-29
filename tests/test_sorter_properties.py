"""Property-based tests for file sorter module."""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.sorter import (
    move_file_with_conflict_resolution,
    generate_unique_filename,
    sort_files,
    SortingStats
)
from sik_sort.classifier import FileCategory


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


# Feature: file-sorter-cli, Property 9: Filename preservation
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf'])
)
def test_filename_preservation(filename, extension):
    """
    Property 9: Filename preservation
    
    For any file being moved (excluding conflict resolution cases),
    the basename of the file should remain unchanged after the move operation.
    
    Validates: Requirements 3.3
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directories for source and destination
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        dest_dir = root / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()
        
        # Create source file
        full_filename = f"{filename}.{extension}"
        src_file = src_dir / full_filename
        src_file.write_text("test content")
        
        # Move file (no conflict case)
        dest_file = dest_dir / full_filename
        move_file_with_conflict_resolution(src_file, dest_file)
        
        # Assert the file exists at destination with same name
        assert dest_file.exists(), f"File {full_filename} was not moved to destination"
        assert dest_file.name == full_filename, (
            f"Filename changed from {full_filename} to {dest_file.name}"
        )
        
        # Assert source file no longer exists
        assert not src_file.exists(), f"Source file {src_file} still exists after move"



# Feature: file-sorter-cli, Property 14: No file overwriting
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf']),
    original_content=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(min_codepoint=32, max_codepoint=126)  # ASCII printable
    ),
    new_content=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(min_codepoint=32, max_codepoint=126)  # ASCII printable
    )
)
def test_no_file_overwriting(filename, extension, original_content, new_content):
    """
    Property 14: No file overwriting
    
    For any file being moved to a destination where a file with the same name exists,
    the original file at the destination should remain unchanged and the incoming file
    should be renamed.
    
    Validates: Requirements 7.1
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    # Ensure contents are different so we can verify no overwriting
    assume(original_content != new_content)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        dest_dir = root / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()
        
        # Create destination file with original content
        full_filename = f"{filename}.{extension}"
        dest_file = dest_dir / full_filename
        dest_file.write_text(original_content)
        
        # Create source file with new content
        src_file = src_dir / full_filename
        src_file.write_text(new_content)
        
        # Move file (conflict case)
        move_file_with_conflict_resolution(src_file, dest_file)
        
        # Assert original file still exists with original content
        assert dest_file.exists(), f"Original file {dest_file} was removed"
        assert dest_file.read_text() == original_content, (
            f"Original file content was changed"
        )
        
        # Assert source file was moved (doesn't exist at source)
        assert not src_file.exists(), f"Source file {src_file} still exists"
        
        # Assert a renamed file exists in destination with new content
        renamed_files = [f for f in dest_dir.iterdir() if f.name != full_filename]
        assert len(renamed_files) == 1, (
            f"Expected 1 renamed file, found {len(renamed_files)}"
        )
        assert renamed_files[0].read_text() == new_content, (
            f"Renamed file doesn't have the expected content"
        )


# Feature: file-sorter-cli, Property 15: Conflict resolution preserves extensions
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf'])
)
def test_conflict_resolution_preserves_extensions(filename, extension):
    """
    Property 15: Conflict resolution preserves extensions
    
    For any file renamed due to conflict, the file extension should remain
    unchanged from the original.
    
    Validates: Requirements 7.2
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_dir = Path(temp_dir)
        
        # Create existing file
        full_filename = f"{filename}.{extension}"
        existing_file = dest_dir / full_filename
        existing_file.write_text("existing")
        
        # Generate unique filename
        unique_filename = generate_unique_filename(dest_dir, full_filename)
        
        # Assert extension is preserved
        unique_path = Path(unique_filename)
        assert unique_path.suffix == f".{extension}", (
            f"Extension changed from .{extension} to {unique_path.suffix}"
        )


# Feature: file-sorter-cli, Property 16: Unique names for all conflicts
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf']),
    num_conflicts=st.integers(min_value=2, max_value=10)
)
def test_unique_names_for_all_conflicts(filename, extension, num_conflicts):
    """
    Property 16: Unique names for all conflicts
    
    For any set of files with identical names being moved to the same destination,
    each file should receive a unique final name.
    
    Validates: Requirements 7.3
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        dest_dir = root / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()
        
        full_filename = f"{filename}.{extension}"
        
        # Create multiple source files with same name in different subdirectories
        src_files = []
        for i in range(num_conflicts):
            subdir = src_dir / f"sub{i}"
            subdir.mkdir()
            src_file = subdir / full_filename
            src_file.write_text(f"content_{i}")
            src_files.append(src_file)
        
        # Move all files to destination
        dest_file = dest_dir / full_filename
        for src_file in src_files:
            move_file_with_conflict_resolution(src_file, dest_file)
        
        # Get all files in destination
        dest_files = list(dest_dir.iterdir())
        
        # Assert we have the correct number of files
        assert len(dest_files) == num_conflicts, (
            f"Expected {num_conflicts} files in destination, found {len(dest_files)}"
        )
        
        # Assert all filenames are unique
        filenames = [f.name for f in dest_files]
        assert len(filenames) == len(set(filenames)), (
            f"Duplicate filenames found: {filenames}"
        )
        
        # Assert all files have the correct extension
        for dest_file in dest_files:
            assert dest_file.suffix == f".{extension}", (
                f"File {dest_file.name} has wrong extension {dest_file.suffix}"
            )
