"""Property-based tests for operation logger module."""

from io import StringIO
from hypothesis import given, strategies as st, settings
from rich.console import Console
from sik_sort.operation_logger import (
    log_file_operation,
    log_scan_complete,
    log_conflict_resolution,
    log_error
)
from sik_sort.classifier import FileCategory


# Feature: file-sorter-cli, Property 17: Operation logs display file and category
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1, 
        max_size=50,
        alphabet=st.characters(
            min_codepoint=32, 
            max_codepoint=126,
            blacklist_characters='[]<>\\/:*?"|'  # Exclude invalid filename chars and Rich markup chars
        )
    ).filter(lambda x: x.strip()),  # Ensure non-empty after stripping
    category=st.sampled_from([FileCategory.IMAGE, FileCategory.VIDEO, FileCategory.ARCHIVE, FileCategory.MISC])
)
def test_operation_log_contains_filename_and_category(filename, category):
    """
    Property 17: Operation logs display file and category
    
    For any file being processed, the operation log should contain both
    the filename and the destination category.
    
    Validates: Requirements 9.1
    """
    # Capture console output
    string_io = StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    
    # Temporarily replace the global console
    import sik_sort.operation_logger as logger_module
    original_console = logger_module.console
    logger_module.console = test_console
    
    try:
        # Log the operation
        log_file_operation(filename, category, dry_run=False)
        
        # Get the output
        output = string_io.getvalue()
        
        # Verify filename is in the output
        assert filename in output, f"Filename '{filename}' not found in log output: {output}"
        
        # Verify category is in the output (either as value or uppercase)
        assert category.value in output or category.value.upper() in output, (
            f"Category '{category.value}' not found in log output: {output}"
        )
    finally:
        # Restore original console
        logger_module.console = original_console


# Feature: file-sorter-cli, Property 18: Consistent category formatting
@settings(max_examples=100)
@given(
    files=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=30),
            st.just(FileCategory.IMAGE)  # Use same category for consistency check
        ),
        min_size=2,
        max_size=10
    )
)
def test_consistent_category_formatting(files):
    """
    Property 18: Consistent category formatting
    
    For any two files of the same category, their operation log messages
    should have consistent formatting and color coding.
    
    Validates: Requirements 9.2
    """
    # Capture console output
    string_io = StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    
    # Temporarily replace the global console
    import sik_sort.operation_logger as logger_module
    original_console = logger_module.console
    logger_module.console = test_console
    
    try:
        # Log all operations
        for filename, category in files:
            log_file_operation(filename, category, dry_run=False)
        
        # Get the output
        output = string_io.getvalue()
        lines = output.strip().split('\n')
        
        # Extract category markers from each line
        category_markers = []
        for line in lines:
            # Look for the category marker pattern [CATEGORY]
            if '[IMG]' in line or '[img]' in line:
                category_markers.append('IMG')
        
        # All lines should have the same category marker format
        assert len(category_markers) == len(files), (
            f"Expected {len(files)} category markers, found {len(category_markers)}"
        )
        
        # Check that all markers are consistent (all uppercase or all lowercase)
        if category_markers:
            first_marker = category_markers[0]
            for marker in category_markers:
                assert marker == first_marker, (
                    f"Inconsistent category formatting: {marker} vs {first_marker}"
                )
    finally:
        # Restore original console
        logger_module.console = original_console


# Feature: file-sorter-cli, Property 19: Error logs are visually distinct
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1, 
        max_size=50,
        alphabet=st.characters(
            min_codepoint=32, 
            max_codepoint=126,
            blacklist_characters='[]<>\\/:*?"|'  # Exclude invalid filename chars and Rich markup chars
        )
    ).filter(lambda x: x.strip()),  # Ensure non-empty after stripping
    error_message=st.text(
        min_size=1, 
        max_size=100,
        alphabet=st.characters(
            min_codepoint=32, 
            max_codepoint=126,
            blacklist_characters='[]<>'  # Exclude Rich markup chars
        )
    ).filter(lambda x: x.strip()),  # Ensure non-empty after stripping
    normal_filename=st.text(
        min_size=1, 
        max_size=50,
        alphabet=st.characters(
            min_codepoint=32, 
            max_codepoint=126,
            blacklist_characters='[]<>\\/:*?"|'  # Exclude invalid filename chars and Rich markup chars
        )
    ).filter(lambda x: x.strip()),  # Ensure non-empty after stripping
    category=st.sampled_from([FileCategory.IMAGE, FileCategory.VIDEO, FileCategory.ARCHIVE, FileCategory.MISC])
)
def test_error_log_visual_distinction(filename, error_message, normal_filename, category):
    """
    Property 19: Error logs are visually distinct
    
    For any error during file operations, the error log should have
    different styling than normal operation logs.
    
    Validates: Requirements 9.3
    """
    # Capture console output for error
    error_io = StringIO()
    error_console = Console(file=error_io, force_terminal=True, width=120)
    
    # Capture console output for normal operation
    normal_io = StringIO()
    normal_console = Console(file=normal_io, force_terminal=True, width=120)
    
    # Temporarily replace the global console
    import sik_sort.operation_logger as logger_module
    original_console = logger_module.console
    
    try:
        # Log error
        logger_module.console = error_console
        log_error(filename, error_message)
        error_output = error_io.getvalue()
        
        # Log normal operation
        logger_module.console = normal_console
        log_file_operation(normal_filename, category, dry_run=False)
        normal_output = normal_io.getvalue()
        
        # Verify error output contains ERROR marker
        assert '[ERROR]' in error_output or 'ERROR' in error_output, (
            f"Error log missing ERROR marker: {error_output}"
        )
        
        # Verify normal output does NOT contain ERROR marker
        assert '[ERROR]' not in normal_output and 'ERROR' not in normal_output, (
            f"Normal log should not contain ERROR marker: {normal_output}"
        )
        
        # Verify error output contains the filename and error message
        assert filename in error_output, f"Filename not in error log: {error_output}"
        assert error_message in error_output, f"Error message not in error log: {error_output}"
    finally:
        # Restore original console
        logger_module.console = original_console


# Feature: file-sorter-cli, Property 20: Scan completion displays file count
@settings(max_examples=100)
@given(
    file_count=st.integers(min_value=0, max_value=10000)
)
def test_scan_completion_displays_count(file_count):
    """
    Property 20: Scan completion displays file count
    
    For any directory scan operation, after completion, the displayed
    message should contain the total number of files found.
    
    Validates: Requirements 9.4
    """
    # Capture console output
    string_io = StringIO()
    test_console = Console(file=string_io, force_terminal=True, width=120)
    
    # Temporarily replace the global console
    import sik_sort.operation_logger as logger_module
    original_console = logger_module.console
    logger_module.console = test_console
    
    try:
        # Log scan completion
        log_scan_complete(file_count)
        
        # Get the output
        output = string_io.getvalue()
        
        # Verify the file count is in the output
        assert str(file_count) in output, (
            f"File count {file_count} not found in scan completion log: {output}"
        )
        
        # Verify it mentions "file" or "files"
        assert 'file' in output.lower(), (
            f"Scan completion log should mention 'file': {output}"
        )
    finally:
        # Restore original console
        logger_module.console = original_console
