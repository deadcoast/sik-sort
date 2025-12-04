"""Property-based tests for date-based sorting functionality.

Feature: advanced-file-operations
"""

import tempfile
import os
import time
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings
from sik_sort.sorter import sort_files_with_date, EnhancedSortingStats
from sik_sort.date_classifier import classify_by_date


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
def test_date_hierarchy_structure(filename, timestamp):
    """Property 18: Date hierarchy structure
    
    For any file sorted by date, the file's destination path should match 
    the pattern {date_folder}/{type_category}
    
    **Validates: Requirements 4.5**
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Create a test file
        test_file = source_path / filename
        test_file.write_text("test content")
        
        # Set the modification time
        os.utime(test_file, (timestamp, timestamp))
        
        # Get expected date folder before sorting
        expected_date_folder = classify_by_date(test_file, use_creation=False, date_format="%Y-%m")
        
        # Sort files with date-based sorting
        stats = sort_files_with_date(source_path, use_creation=False, date_format="%Y-%m", dry_run=False)
        
        # Verify the file was moved
        assert stats.total_files == 1
        assert len(stats.operations) == 1
        
        operation = stats.operations[0]
        dest_path = operation.destination
        
        # Verify the destination path matches {date_folder}/{type_category} pattern
        relative_path = dest_path.relative_to(source_path)
        parts = relative_path.parts
        
        # Should have at least 3 parts: date_folder, type_category, filename
        assert len(parts) >= 3, f"Expected at least 3 path parts, got {len(parts)}: {parts}"
        
        # First part should be date folder in YYYY-MM format
        date_part = parts[0]
        assert len(date_part) >= 7, f"Date folder should be at least 7 chars (YYYY-MM), got {date_part}"
        assert date_part == expected_date_folder, f"Expected date folder {expected_date_folder}, got {date_part}"
        
        # Second part should be type category
        type_part = parts[1]
        assert type_part in ['img', 'vid', 'arc', 'msk'], f"Expected type category, got {type_part}"


@given(
    num_files=st.integers(min_value=1, max_value=5),
    timestamps=st.lists(timestamps, min_size=1, max_size=5)
)
@settings(max_examples=50, deadline=None)
def test_date_statistics_accuracy(num_files, timestamps):
    """Property 19: Date statistics accuracy
    
    For any date-based sort, the displayed counts per month should match 
    the actual files in each date folder
    
    **Validates: Requirements 4.6**
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
        
        # Sort files with date-based sorting
        stats = sort_files_with_date(source_path, use_creation=False, date_format="%Y-%m", dry_run=False)
        
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
