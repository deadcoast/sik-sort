"""Property-based tests for archive mode sorting functionality.

Feature: advanced-file-operations
"""

import tempfile
import os
import time
import re
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings
from sik_sort.sorter import sort_files_archive_mode, EnhancedSortingStats


# Strategy for generating filenames
filenames = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
    min_size=1,
    max_size=20
).map(lambda s: s + ".txt")

# Strategy for generating timestamps (last 5 years)
timestamps = st.integers(min_value=int(time.time()) - (5 * 365 * 24 * 60 * 60), max_value=int(time.time()))


@given(
    filename=filenames,
    timestamp=timestamps
)
@settings(max_examples=100, deadline=None)
def test_archive_folder_naming(filename, timestamp):
    """Property 33: Archive folder naming
    
    For any archive mode operation, all created folders should be named 
    in YYYY-MM format based on file dates
    
    **Validates: Requirements 8.1**
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Create a test file
        test_file = source_path / filename
        test_file.write_text("test content")
        
        # Set the modification time
        os.utime(test_file, (timestamp, timestamp))
        
        # Sort files in archive mode
        stats = sort_files_archive_mode(source_path, use_creation=False, date_format="%Y-%m", dry_run=False)
        
        # Verify the file was moved
        assert stats.total_files == 1
        assert len(stats.operations) == 1
        
        operation = stats.operations[0]
        dest_path = operation.destination
        
        # Get the date folder from the destination path
        relative_path = dest_path.relative_to(source_path)
        date_folder = relative_path.parts[0]
        
        # Verify the date folder matches YYYY-MM format
        assert re.match(r'^\d{4}-\d{2}$', date_folder), \
            f"Date folder should match YYYY-MM format, got {date_folder}"
        
        # Verify it matches the expected date
        expected_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m")
        assert date_folder == expected_date


@given(
    filename=filenames,
    timestamp=timestamps
)
@settings(max_examples=100, deadline=None)
def test_archive_flat_structure(filename, timestamp):
    """Property 34: Archive mode flat structure
    
    For any file sorted in archive mode without type categorization, 
    the file should be directly in the date folder
    
    **Validates: Requirements 8.2**
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Create a test file
        test_file = source_path / filename
        test_file.write_text("test content")
        
        # Set the modification time
        os.utime(test_file, (timestamp, timestamp))
        
        # Sort files in archive mode WITHOUT type hierarchy
        stats = sort_files_archive_mode(
            source_path, 
            use_creation=False, 
            date_format="%Y-%m", 
            with_type_hierarchy=False,
            dry_run=False
        )
        
        # Verify the file was moved
        assert stats.total_files == 1
        assert len(stats.operations) == 1
        
        operation = stats.operations[0]
        dest_path = operation.destination
        
        # Get the path structure
        relative_path = dest_path.relative_to(source_path)
        parts = relative_path.parts
        
        # Should have exactly 2 parts: date_folder and filename (no type category)
        assert len(parts) == 2, \
            f"Expected 2 path parts (date/file), got {len(parts)}: {parts}"
        
        # First part should be date folder
        date_folder = parts[0]
        assert re.match(r'^\d{4}-\d{2}$', date_folder), \
            f"Date folder should match YYYY-MM format, got {date_folder}"


@given(
    filename=filenames,
    timestamp=timestamps
)
@settings(max_examples=100, deadline=None)
def test_archive_with_type_hierarchy(filename, timestamp):
    """Property 35: Archive mode with type hierarchy
    
    For any file sorted in archive mode with type categorization, 
    the file's path should match {date_folder}/{type_category}
    
    **Validates: Requirements 8.3**
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Create a test file
        test_file = source_path / filename
        test_file.write_text("test content")
        
        # Set the modification time
        os.utime(test_file, (timestamp, timestamp))
        
        # Sort files in archive mode WITH type hierarchy
        stats = sort_files_archive_mode(
            source_path, 
            use_creation=False, 
            date_format="%Y-%m", 
            with_type_hierarchy=True,
            dry_run=False
        )
        
        # Verify the file was moved
        assert stats.total_files == 1
        assert len(stats.operations) == 1
        
        operation = stats.operations[0]
        dest_path = operation.destination
        
        # Get the path structure
        relative_path = dest_path.relative_to(source_path)
        parts = relative_path.parts
        
        # Should have 3 parts: date_folder, type_category, and filename
        assert len(parts) == 3, \
            f"Expected 3 path parts (date/type/file), got {len(parts)}: {parts}"
        
        # First part should be date folder
        date_folder = parts[0]
        assert re.match(r'^\d{4}-\d{2}$', date_folder), \
            f"Date folder should match YYYY-MM format, got {date_folder}"
        
        # Second part should be type category
        type_part = parts[1]
        assert type_part in ['img', 'vid', 'arc', 'msk'], \
            f"Expected type category, got {type_part}"


@given(
    num_files=st.integers(min_value=1, max_value=5),
    timestamps=st.lists(timestamps, min_size=1, max_size=5)
)
@settings(max_examples=50, deadline=None)
def test_archive_statistics_accuracy(num_files, timestamps):
    """Property 36: Archive statistics accuracy
    
    For any archive mode operation, the displayed counts per month 
    should match the actual files in each archive folder
    
    **Validates: Requirements 8.4**
    """
    # Ensure we have enough timestamps
    if len(timestamps) < num_files:
        timestamps = timestamps * ((num_files // len(timestamps)) + 1)
    timestamps = timestamps[:num_files]
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Count expected date categories
        expected_counts = {}
        for ts in timestamps:
            dt = datetime.fromtimestamp(ts)
            date_str = dt.strftime("%Y-%m")
            expected_counts[date_str] = expected_counts.get(date_str, 0) + 1
        
        # Create test files with specific timestamps
        for i, ts in enumerate(timestamps):
            test_file = source_path / f"file_{i}.txt"
            test_file.write_text("test content")
            os.utime(test_file, (ts, ts))
        
        # Sort files in archive mode
        stats = sort_files_archive_mode(source_path, use_creation=False, date_format="%Y-%m", dry_run=False)
        
        # Verify total files count
        assert stats.total_files == num_files
        
        # Verify date category counts match
        for date_folder, expected_count in expected_counts.items():
            actual_count = stats.date_categories.get(date_folder, 0)
            assert actual_count == expected_count, \
                f"Date category {date_folder}: expected {expected_count}, got {actual_count}"
        
        # Verify all files are accounted for
        total_in_categories = sum(stats.date_categories.values())
        assert total_in_categories == num_files


@given(
    filename=filenames,
    timestamp=timestamps,
    date_format=st.sampled_from(["%Y-%m", "%Y-%m-%d", "%Y/%m", "%Y%m"])
)
@settings(max_examples=100, deadline=None)
def test_custom_date_format_support(filename, timestamp, date_format):
    """Property 37: Custom date format support
    
    For any custom date format specified, archive folders should be 
    named using that format
    
    **Validates: Requirements 8.5**
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Create a test file
        test_file = source_path / filename
        test_file.write_text("test content")
        
        # Set the modification time
        os.utime(test_file, (timestamp, timestamp))
        
        # Sort files in archive mode with custom date format
        stats = sort_files_archive_mode(
            source_path, 
            use_creation=False, 
            date_format=date_format, 
            dry_run=False
        )
        
        # Verify the file was moved
        assert stats.total_files == 1
        assert len(stats.operations) == 1
        
        operation = stats.operations[0]
        dest_path = operation.destination
        
        # Get the date folder from the destination path
        relative_path = dest_path.relative_to(source_path)
        date_folder = relative_path.parts[0]
        
        # Verify it matches the expected date format
        expected_date = datetime.fromtimestamp(timestamp).strftime(date_format)
        assert date_folder == expected_date, \
            f"Expected date folder {expected_date}, got {date_folder}"
