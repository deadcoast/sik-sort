"""Property-based tests for CLI argument parsing."""

from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
import tempfile
import sys
from unittest.mock import patch
from sik_sort.cli import parse_arguments


# Windows reserved names that should be filtered out
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}


# Feature: file-sorter-cli, Property 30: Command-line path argument is used
@settings(max_examples=100)
@given(
    dir_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        blacklist_characters=['<', '>', ':', '"', '|', '?', '*', '\0', '/', '\\']
    ))
)
def test_command_line_path_is_used(dir_name):
    """
    Property 30: Command-line path argument is used
    
    For any valid path provided as a command-line argument, that path should be
    used as the source directory without prompting.
    
    Validates: Requirements 12.1
    """
    # Filter out Windows reserved names
    assume(dir_name.upper() not in WINDOWS_RESERVED_NAMES)
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory with the generated name
        test_dir = Path(temp_dir) / dir_name
        test_dir.mkdir(exist_ok=True)
        
        # Verify it's actually a directory (not a device file)
        assume(test_dir.is_dir())
        
        # Mock sys.argv to simulate command-line arguments
        with patch.object(sys, 'argv', ['sik', str(test_dir)]):
            path, dry_run = parse_arguments()
            
            # Assert the path is used
            assert path is not None, "Path should not be None when provided via command line"
            assert path == test_dir, f"Expected path {test_dir}, got {path}"
            assert not dry_run, "Dry-run should be False by default"


# Feature: file-sorter-cli, Property 31: Missing path triggers interactive prompt
@settings(max_examples=100)
@given(
    dry_flag=st.booleans()
)
def test_missing_path_triggers_prompt(dry_flag):
    """
    Property 31: Missing path triggers interactive prompt
    
    For any invocation without a path argument, an interactive prompt should be
    displayed (indicated by returning None for the path).
    
    Validates: Requirements 12.2
    """
    # Mock sys.argv to simulate command-line arguments without path
    args = ['sik']
    if dry_flag:
        args.append('--dry')
    
    with patch.object(sys, 'argv', args):
        path, dry_run = parse_arguments()
        
        # Assert that path is None (indicating prompt is needed)
        assert path is None, "Path should be None when not provided via command line"
        assert dry_run == dry_flag, f"Dry-run flag should be {dry_flag}"


# Feature: file-sorter-cli, Property 32: Dry-run flag works with path argument
@settings(max_examples=100)
@given(
    dir_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        blacklist_characters=['<', '>', ':', '"', '|', '?', '*', '\0', '/', '\\']
    )),
    dry_flag_variant=st.sampled_from(['--dry', '--dry-run'])
)
def test_dry_run_with_path_argument(dir_name, dry_flag_variant):
    """
    Property 32: Dry-run flag works with path argument
    
    For any valid path, invoking with both the path and dry-run flag should
    perform a dry-run on that path.
    
    Validates: Requirements 12.3
    """
    # Filter out Windows reserved names
    assume(dir_name.upper() not in WINDOWS_RESERVED_NAMES)
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory with the generated name
        test_dir = Path(temp_dir) / dir_name
        test_dir.mkdir(exist_ok=True)
        
        # Verify it's actually a directory (not a device file)
        assume(test_dir.is_dir())
        
        # Mock sys.argv to simulate command-line arguments with dry-run flag
        with patch.object(sys, 'argv', ['sik', str(test_dir), dry_flag_variant]):
            path, dry_run = parse_arguments()
            
            # Assert the path is used and dry-run is enabled
            assert path is not None, "Path should not be None when provided via command line"
            assert path == test_dir, f"Expected path {test_dir}, got {path}"
            assert dry_run, "Dry-run should be True when flag is provided"


# Feature: file-sorter-cli, Property 33: Invalid command-line path shows error
@settings(max_examples=100)
@given(
    invalid_path=st.text(min_size=1, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        blacklist_characters=['<', '>', ':', '"', '|', '?', '*', '\0']
    )).filter(lambda x: not Path(x).exists())
)
def test_invalid_command_line_path_error(invalid_path):
    """
    Property 33: Invalid command-line path shows error
    
    For any invalid path provided as a command-line argument, an error message
    should be displayed and the program should exit.
    
    Validates: Requirements 12.4
    """
    # Assume the path doesn't exist
    assume(not Path(invalid_path).exists())
    
    # Mock sys.argv to simulate command-line arguments with invalid path
    with patch.object(sys, 'argv', ['sik', invalid_path]):
        try:
            path, dry_run = parse_arguments()
            # If we get here, the test should fail
            assert False, f"Expected SystemExit for invalid path '{invalid_path}', but got path={path}"
        except SystemExit as e:
            # Assert that the program exits with error code
            assert e.code == 1, f"Expected exit code 1, got {e.code}"
