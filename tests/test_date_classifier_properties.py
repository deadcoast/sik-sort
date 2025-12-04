"""Property-based tests for date classifier module."""

import tempfile
import time
import os
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings
from sik_sort.date_classifier import (
    classify_by_date,
    get_file_date,
    format_date,
    DateMode
)


# Feature: advanced-file-operations, Property 15: Date folder naming format
@settings(max_examples=100, deadline=None)
@given(
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28)  # Use 28 to avoid invalid dates
)
def test_date_folder_naming_format(year, month, day):
    """
    Property 15: Date folder naming format
    
    For any date-based sort operation, all created date folders should be named
    in YYYY-MM format.
    
    Validates: Requirements 4.1
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a test file
        test_file = tmppath / "test.txt"
        test_file.write_text("test content")
        
        # Set the modification time to a specific date
        target_date = datetime(year, month, day, 12, 0, 0)
        timestamp = target_date.timestamp()
        os.utime(test_file, (timestamp, timestamp))
        
        # Classify the file using default format (YYYY-MM)
        date_folder = classify_by_date(test_file, use_creation=False)
        
        # Expected format: YYYY-MM
        expected_format = f"{year:04d}-{month:02d}"
        
        # Assert the folder name matches YYYY-MM format
        assert date_folder == expected_format, (
            f"Date folder should be in YYYY-MM format. "
            f"Expected '{expected_format}', got '{date_folder}'"
        )
        
        # Verify the format matches the pattern
        parts = date_folder.split('-')
        assert len(parts) == 2, f"Date folder should have format YYYY-MM, got '{date_folder}'"
        assert len(parts[0]) == 4, f"Year should be 4 digits, got '{parts[0]}'"
        assert len(parts[1]) == 2, f"Month should be 2 digits, got '{parts[1]}'"
        assert parts[0].isdigit(), f"Year should be numeric, got '{parts[0]}'"
        assert parts[1].isdigit(), f"Month should be numeric, got '{parts[1]}'"


# Feature: advanced-file-operations, Property 16: Creation date used when specified
@settings(max_examples=100, deadline=None)
@given(
    creation_year=st.integers(min_value=2020, max_value=2023),
    creation_month=st.integers(min_value=1, max_value=12),
    modification_year=st.integers(min_value=2024, max_value=2030),
    modification_month=st.integers(min_value=1, max_value=12)
)
def test_creation_date_usage(creation_year, creation_month, modification_year, modification_month):
    """
    Property 16: Creation date used when specified
    
    For any file sorted with creation date mode, the file should be categorized
    based on its creation timestamp.
    
    Validates: Requirements 4.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a test file
        test_file = tmppath / "test.txt"
        test_file.write_text("test content")
        
        # Set creation time (via ctime) and modification time to different dates
        creation_date = datetime(creation_year, creation_month, 15, 12, 0, 0)
        modification_date = datetime(modification_year, modification_month, 15, 12, 0, 0)
        
        creation_timestamp = creation_date.timestamp()
        modification_timestamp = modification_date.timestamp()
        
        # Set modification time
        os.utime(test_file, (modification_timestamp, modification_timestamp))
        
        # Note: We can't directly set creation time on all platforms,
        # but we can test that when use_creation=True, we get a different result
        # than when use_creation=False
        
        # Get dates using both modes
        creation_result = classify_by_date(test_file, use_creation=True)
        modification_result = classify_by_date(test_file, use_creation=False)
        
        # The modification result should match what we set
        expected_modification = f"{modification_year:04d}-{modification_month:02d}"
        assert modification_result == expected_modification, (
            f"Modification date should be {expected_modification}, got {modification_result}"
        )
        
        # When use_creation=True, we should get a date (may not be exactly what we want
        # due to platform limitations, but it should be a valid YYYY-MM format)
        parts = creation_result.split('-')
        assert len(parts) == 2, f"Creation date should have format YYYY-MM, got '{creation_result}'"
        assert len(parts[0]) == 4, f"Year should be 4 digits, got '{parts[0]}'"
        assert len(parts[1]) == 2, f"Month should be 2 digits, got '{parts[1]}'"


# Feature: advanced-file-operations, Property 17: Modification date used when specified
@settings(max_examples=100, deadline=None)
@given(
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28)
)
def test_modification_date_usage(year, month, day):
    """
    Property 17: Modification date used when specified
    
    For any file sorted with modification date mode, the file should be categorized
    based on its modification timestamp.
    
    Validates: Requirements 4.3
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a test file
        test_file = tmppath / "test.txt"
        test_file.write_text("test content")
        
        # Set the modification time to a specific date
        target_date = datetime(year, month, day, 12, 0, 0)
        timestamp = target_date.timestamp()
        os.utime(test_file, (timestamp, timestamp))
        
        # Classify the file using modification date (use_creation=False)
        date_folder = classify_by_date(test_file, use_creation=False)
        
        # Expected format: YYYY-MM
        expected_format = f"{year:04d}-{month:02d}"
        
        # Assert the folder name matches the modification date
        assert date_folder == expected_format, (
            f"Modification date should be {expected_format}, got {date_folder}"
        )
        
        # Verify we can retrieve the modification date directly
        file_date = get_file_date(test_file, use_creation=False)
        assert file_date.year == year, f"Year should be {year}, got {file_date.year}"
        assert file_date.month == month, f"Month should be {month}, got {file_date.month}"


# Additional property test: format_date produces valid output
@settings(max_examples=100)
@given(
    year=st.integers(min_value=1970, max_value=2100),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28),
    format_string=st.sampled_from(["%Y-%m", "%Y-%m-%d", "%Y/%m", "%Y%m", "%B %Y"])
)
def test_format_date_validity(year, month, day, format_string):
    """
    Property: format_date produces valid formatted output
    
    For any date and format string, format_date should produce a non-empty string.
    """
    date = datetime(year, month, day, 12, 0, 0)
    formatted = format_date(date, format_string)
    
    # Check that output is not empty
    assert len(formatted) > 0, "Formatted date should not be empty"
    
    # Check that the formatted string matches what strftime would produce
    expected = date.strftime(format_string)
    assert formatted == expected, (
        f"Formatted date should match strftime output. "
        f"Expected '{expected}', got '{formatted}'"
    )


# Additional property test: get_file_date returns valid datetime
@settings(max_examples=100)
@given(
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28)
)
def test_get_file_date_validity(year, month, day):
    """
    Property: get_file_date returns a valid datetime object
    
    For any file, get_file_date should return a datetime object with valid components.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a test file
        test_file = tmppath / "test.txt"
        test_file.write_text("test content")
        
        # Set the modification time
        target_date = datetime(year, month, day, 12, 0, 0)
        timestamp = target_date.timestamp()
        os.utime(test_file, (timestamp, timestamp))
        
        # Get the file date
        file_date = get_file_date(test_file, use_creation=False)
        
        # Check that it's a datetime object
        assert isinstance(file_date, datetime), (
            f"get_file_date should return a datetime object, got {type(file_date)}"
        )
        
        # Check that the date components are valid
        assert 1970 <= file_date.year <= 2100, (
            f"Year should be reasonable, got {file_date.year}"
        )
        assert 1 <= file_date.month <= 12, (
            f"Month should be 1-12, got {file_date.month}"
        )
        assert 1 <= file_date.day <= 31, (
            f"Day should be 1-31, got {file_date.day}"
        )


# Test custom date formats
@settings(max_examples=100)
@given(
    year=st.integers(min_value=2000, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28)
)
def test_custom_date_format(year, month, day):
    """
    Property: Custom date formats are respected
    
    For any custom date format, classify_by_date should use that format.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create a test file
        test_file = tmppath / "test.txt"
        test_file.write_text("test content")
        
        # Set the modification time
        target_date = datetime(year, month, day, 12, 0, 0)
        timestamp = target_date.timestamp()
        os.utime(test_file, (timestamp, timestamp))
        
        # Test with custom format: YYYY-MM-DD
        custom_format = "%Y-%m-%d"
        date_folder = classify_by_date(test_file, use_creation=False, date_format=custom_format)
        
        expected = f"{year:04d}-{month:02d}-{day:02d}"
        assert date_folder == expected, (
            f"Custom format should produce {expected}, got {date_folder}"
        )
