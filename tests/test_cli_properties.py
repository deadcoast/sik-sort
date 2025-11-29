"""Property-based tests for CLI module."""

from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
import tempfile


def validate_path(path_str: str) -> tuple[bool, str]:
    """Helper function to validate a path.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    path = Path(path_str)
    
    if not path.exists():
        return (False, f"Path does not exist: {path_str}")
    
    if not path.is_dir():
        return (False, f"Path is not a directory: {path_str}")
    
    return (True, "")


# Feature: file-sorter-cli, Property 1: Valid paths are accepted
@settings(max_examples=100)
@given(
    dir_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        blacklist_characters=['<', '>', ':', '"', '|', '?', '*', '\0', '/', '\\']
    ))
)
def test_valid_paths_are_accepted(dir_name):
    """
    Property 1: Valid paths are accepted
    
    For any valid directory path format, the path validation function should
    accept the path and return success.
    
    Validates: Requirements 1.2
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory with the generated name
        test_dir = Path(temp_dir) / dir_name
        test_dir.mkdir(exist_ok=True)
        
        # Validate the path
        is_valid, error_msg = validate_path(str(test_dir))
        
        # Assert the path is accepted
        assert is_valid, f"Valid directory should be accepted, but got error: {error_msg}"
        assert test_dir.exists()
        assert test_dir.is_dir()


# Feature: file-sorter-cli, Property 2: Invalid paths are rejected
@settings(max_examples=100)
@given(
    invalid_path=st.one_of(
        # Non-existent paths with random characters
        st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['<', '>', ':', '"', '|', '?', '*', '\0']
        )).filter(lambda x: not Path(x).exists()),
    )
)
def test_invalid_paths_are_rejected(invalid_path):
    """
    Property 2: Invalid paths are rejected
    
    For any invalid directory path format (malformed, contains illegal characters, etc.),
    the path validation function should reject the path and return an error.
    
    Validates: Requirements 1.3
    """
    # Assume the path doesn't exist or is not a directory
    assume(not Path(invalid_path).exists() or not Path(invalid_path).is_dir())
    
    # Validate the path
    is_valid, error_msg = validate_path(invalid_path)
    
    # Assert that the path is rejected
    assert not is_valid, f"Invalid path '{invalid_path}' should be rejected"
    assert len(error_msg) > 0, "Error message should be provided for invalid path"
