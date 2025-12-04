"""Property-based tests for size classifier module."""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.size_classifier import (
    classify_by_size,
    get_file_size,
    format_size,
    SizeCategory,
    SizeThresholds
)


# Feature: advanced-file-operations, Property 11: Size category folders created
@settings(max_examples=100, deadline=None)
@given(
    # Use default thresholds: small_max=1MB, medium_max=100MB
    small_size=st.integers(min_value=0, max_value=1_048_576),  # 0 to 1 MB
    medium_size=st.integers(min_value=1_048_577, max_value=104_857_600),  # 1 MB to 100 MB
    large_size=st.integers(min_value=104_857_601, max_value=209_715_200)  # 100 MB to 200 MB
)
def test_size_category_classification(small_size, medium_size, large_size):
    """
    Property 11: Size category folders created
    
    For any file sizes, files should be correctly categorized into small, medium, or large
    categories based on the default thresholds (small <= 1MB, medium <= 100MB, large > 100MB).
    
    Validates: Requirements 3.1
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test files with specific sizes
        small_file = tmppath / "small.txt"
        medium_file = tmppath / "medium.txt"
        large_file = tmppath / "large.txt"
        
        # Write files with specific sizes
        small_file.write_bytes(b'x' * small_size)
        medium_file.write_bytes(b'x' * medium_size)
        large_file.write_bytes(b'x' * large_size)
        
        # Classify files using default thresholds
        small_category = classify_by_size(small_file)
        medium_category = classify_by_size(medium_file)
        large_category = classify_by_size(large_file)
        
        # Assert correct categorization
        assert small_category == SizeCategory.SMALL, (
            f"File of size {small_size} bytes should be SMALL, got {small_category}"
        )
        assert medium_category == SizeCategory.MEDIUM, (
            f"File of size {medium_size} bytes should be MEDIUM, got {medium_category}"
        )
        assert large_category == SizeCategory.LARGE, (
            f"File of size {large_size} bytes should be LARGE, got {large_category}"
        )


# Feature: advanced-file-operations, Property 12: Custom size thresholds respected
@settings(max_examples=100, deadline=None)
@given(
    small_threshold=st.integers(min_value=1024, max_value=5_242_880),  # 1 KB to 5 MB
    medium_threshold=st.integers(min_value=5_242_881, max_value=52_428_800),  # 5 MB to 50 MB
    file_size=st.integers(min_value=0, max_value=104_857_600)  # 0 to 100 MB (reduced for speed)
)
def test_custom_size_thresholds(small_threshold, medium_threshold, file_size):
    """
    Property 12: Custom size thresholds respected
    
    For any custom size thresholds and file size, the file should be categorized
    according to those custom thresholds.
    
    Validates: Requirements 3.2
    """
    # Ensure medium threshold is greater than small threshold
    assume(medium_threshold > small_threshold)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test file with specific size
        test_file = tmppath / "test.txt"
        test_file.write_bytes(b'x' * file_size)
        
        # Create custom thresholds
        thresholds = SizeThresholds(
            small_max=small_threshold,
            medium_max=medium_threshold
        )
        
        # Classify file with custom thresholds
        category = classify_by_size(test_file, thresholds)
        
        # Determine expected category
        if file_size <= small_threshold:
            expected = SizeCategory.SMALL
        elif file_size <= medium_threshold:
            expected = SizeCategory.MEDIUM
        else:
            expected = SizeCategory.LARGE
        
        # Assert correct categorization
        assert category == expected, (
            f"File of size {file_size} bytes with thresholds "
            f"(small_max={small_threshold}, medium_max={medium_threshold}) "
            f"should be {expected}, got {category}"
        )


# Additional property test: get_file_size returns correct size
@settings(max_examples=100)
@given(
    file_size=st.integers(min_value=0, max_value=10_485_760)  # 0 to 10 MB
)
def test_get_file_size_accuracy(file_size):
    """
    Property: get_file_size returns accurate file size
    
    For any file, get_file_size should return the exact size in bytes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test file with specific size
        test_file = tmppath / "test.txt"
        test_file.write_bytes(b'x' * file_size)
        
        # Get file size
        actual_size = get_file_size(test_file)
        
        # Assert correct size
        assert actual_size == file_size, (
            f"Expected file size {file_size} bytes, got {actual_size} bytes"
        )


# Additional property test: format_size produces valid output
@settings(max_examples=100)
@given(
    size_bytes=st.integers(min_value=0, max_value=1_099_511_627_776)  # 0 to 1 TB
)
def test_format_size_validity(size_bytes):
    """
    Property: format_size produces valid human-readable output
    
    For any byte size, format_size should produce a valid string with a unit.
    """
    formatted = format_size(size_bytes)
    
    # Check that output contains a valid unit
    valid_units = ['B', 'KB', 'MB', 'GB', 'TB']
    assert any(unit in formatted for unit in valid_units), (
        f"Formatted size '{formatted}' does not contain a valid unit"
    )
    
    # Check that output is not empty
    assert len(formatted) > 0, "Formatted size should not be empty"
    
    # Check that output contains a number
    parts = formatted.split()
    assert len(parts) == 2, f"Formatted size should have format 'NUMBER UNIT', got '{formatted}'"
    
    # First part should be a valid number
    try:
        float(parts[0])
    except ValueError:
        assert False, f"First part of '{formatted}' should be a number"
    
    # Second part should be a valid unit
    assert parts[1] in valid_units, f"Unit '{parts[1]}' is not valid"


# Boundary test: Test exact threshold boundaries
@settings(max_examples=100)
@given(
    offset=st.integers(min_value=-10, max_value=10)
)
def test_threshold_boundaries(offset):
    """
    Property: Files at threshold boundaries are correctly categorized
    
    For any offset around threshold boundaries, files should be categorized correctly.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Test around small_max boundary (1 MB)
        small_max = 1_048_576
        boundary_size = max(0, small_max + offset)
        
        test_file = tmppath / "boundary.txt"
        test_file.write_bytes(b'x' * boundary_size)
        
        category = classify_by_size(test_file)
        
        # Determine expected category
        if boundary_size <= small_max:
            expected = SizeCategory.SMALL
        else:
            expected = SizeCategory.MEDIUM
        
        assert category == expected, (
            f"File of size {boundary_size} bytes (offset {offset} from {small_max}) "
            f"should be {expected}, got {category}"
        )
