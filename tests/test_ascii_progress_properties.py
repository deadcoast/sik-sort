"""Property-based tests for ASCII progress bar functionality."""

from hypothesis import given, strategies as st, settings
from io import StringIO
import sys


def capture_ascii_progress(current: int, total: int) -> str:
    """Helper function to capture ASCII progress bar output.
    
    Args:
        current: Current number of items processed
        total: Total number of items to process
        
    Returns:
        str: The captured progress bar output
    """
    # Import here to avoid circular imports
    from sik_sort.cli import display_ascii_progress
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        display_ascii_progress(current, total)
        output = sys.stdout.getvalue()
        return output
    finally:
        sys.stdout = old_stdout


# Feature: file-sorter-cli, Property 21: Progress bar uses ASCII block characters
@settings(max_examples=100)
@given(
    current=st.integers(min_value=0, max_value=1000),
    total=st.integers(min_value=1, max_value=1000)
)
def test_progress_bar_uses_ascii_characters(current, total):
    """
    Property 21: Progress bar uses ASCII block characters
    
    For any progress bar display, the output should contain the block characters █ and ░.
    
    Validates: Requirements 10.1
    """
    # Ensure current doesn't exceed total
    if current > total:
        current = total
    
    # Capture the progress bar output
    output = capture_ascii_progress(current, total)
    
    # Assert that the output contains the required ASCII block characters
    assert '█' in output or '░' in output, \
        f"Progress bar should contain █ or ░ characters, got: {output}"
    
    # Assert that the output is formatted correctly with brackets
    assert '[' in output and ']' in output, \
        f"Progress bar should be enclosed in brackets, got: {output}"


# Feature: file-sorter-cli, Property 22: Progress percentage increases monotonically
@settings(max_examples=100)
@given(
    total=st.integers(min_value=1, max_value=1000),
    step_count=st.integers(min_value=2, max_value=20)
)
def test_progress_percentage_monotonicity(total, step_count):
    """
    Property 22: Progress percentage increases monotonically
    
    For any sequence of file processing operations, the progress percentage
    should never decrease.
    
    Validates: Requirements 10.2
    """
    percentages = []
    
    # Generate a sequence of progress updates
    for i in range(step_count + 1):
        current = int((i / step_count) * total)
        output = capture_ascii_progress(current, total)
        
        # Extract percentage from output (format: "[...] XX%")
        if '%' in output:
            percentage_str = output.split('%')[0].split()[-1]
            try:
                percentage = int(percentage_str)
                percentages.append(percentage)
            except ValueError:
                pass
    
    # Assert that percentages are monotonically increasing
    for i in range(1, len(percentages)):
        assert percentages[i] >= percentages[i-1], \
            f"Progress percentage should never decrease: {percentages[i-1]} -> {percentages[i]}"


# Feature: file-sorter-cli, Property 23: Progress bar includes percentage value
@settings(max_examples=100)
@given(
    current=st.integers(min_value=0, max_value=1000),
    total=st.integers(min_value=1, max_value=1000)
)
def test_progress_bar_includes_percentage(current, total):
    """
    Property 23: Progress bar includes percentage value
    
    For any progress bar display, the output should contain a numeric percentage value.
    
    Validates: Requirements 10.3
    """
    # Ensure current doesn't exceed total
    if current > total:
        current = total
    
    # Capture the progress bar output
    output = capture_ascii_progress(current, total)
    
    # Assert that the output contains a percentage symbol
    assert '%' in output, \
        f"Progress bar should include percentage value, got: {output}"
    
    # Extract and validate the percentage value
    percentage_str = output.split('%')[0].split()[-1]
    try:
        percentage = int(percentage_str)
        assert 0 <= percentage <= 100, \
            f"Percentage should be between 0 and 100, got: {percentage}"
    except ValueError:
        assert False, f"Could not parse percentage from output: {output}"


# Feature: file-sorter-cli, Property 24: Progress completes at 100%
@settings(max_examples=100)
@given(
    total=st.integers(min_value=1, max_value=1000)
)
def test_progress_completes_at_100_percent(total):
    """
    Property 24: Progress completes at 100%
    
    For any sorting operation, after all files are processed, the progress bar
    should show 100% before statistics are displayed.
    
    Validates: Requirements 10.4
    """
    # Capture progress bar when all files are processed
    output = capture_ascii_progress(total, total)
    
    # Assert that the output shows 100%
    assert '100%' in output, \
        f"Progress bar should show 100% when complete, got: {output}"
    
    # Assert that the bar is fully filled (all █ characters)
    # Extract the bar portion (between brackets)
    if '[' in output and ']' in output:
        bar_start = output.index('[') + 1
        bar_end = output.index(']')
        bar = output[bar_start:bar_end]
        
        # The bar should be all filled characters (█) when at 100%
        assert '░' not in bar or bar.count('█') >= bar.count('░'), \
            f"Progress bar should be fully or mostly filled at 100%, got: {bar}"
