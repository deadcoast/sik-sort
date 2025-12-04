"""Property-based tests for operation logger module."""

import tempfile
import json
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.operation_logger import (
    create_operation_log,
    log_file_movement,
    finalize_log,
    read_latest_log,
    get_log_path,
    FileOperation,
    OperationLog
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


# Feature: file-sorter-enhancements, Property 4: Operation log completeness
@settings(max_examples=100)
@given(
    operations_data=st.lists(
        st.tuples(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
                )
            ),
            st.sampled_from(['jpg', 'mp4', 'zip', 'txt']),
            st.sampled_from([FileCategory.IMAGE, FileCategory.VIDEO, FileCategory.ARCHIVE, FileCategory.MISC]),
            st.booleans()  # conflict_resolved
        ),
        min_size=1,
        max_size=50
    )
)
def test_operation_log_completeness(operations_data):
    """
    Property 4: Operation log completeness
    
    For any sorting operation, the operation log should contain an entry
    for every file that was moved.
    
    Validates: Requirements 2.1
    """
    # Skip if any filename is invalid
    for filename, _, _, _ in operations_data:
        assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        dest_dir = root / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()
        
        # Create operation log
        log = create_operation_log(src_dir)
        
        # Track all operations we perform
        performed_operations = []
        
        # Simulate file movements and log them
        for filename, extension, category, conflict_resolved in operations_data:
            full_filename = f"{filename}.{extension}"
            src_file = src_dir / full_filename
            dest_file = dest_dir / category.value / full_filename
            
            # Create the source file
            src_file.write_text("test content")
            
            # Log the operation
            log_file_movement(log, src_file, dest_file, category, conflict_resolved)
            
            # Track what we logged
            performed_operations.append({
                'source': str(src_file),
                'dest': str(dest_file),
                'category': category.value,
                'conflict': conflict_resolved
            })
        
        # Finalize the log
        finalize_log(log)
        
        # Verify the log file was created
        assert log.log_path.exists(), f"Log file {log.log_path} was not created"
        
        # Read the log file
        with open(log.log_path, 'r') as f:
            log_data = json.load(f)
        
        # Verify all operations are in the log
        assert len(log_data['operations']) == len(performed_operations), (
            f"Expected {len(performed_operations)} operations in log, "
            f"found {len(log_data['operations'])}"
        )
        
        # Verify each operation is correctly recorded
        for i, (expected, actual) in enumerate(zip(performed_operations, log_data['operations'])):
            assert actual['source'] == expected['source'], (
                f"Operation {i}: source mismatch - expected {expected['source']}, "
                f"got {actual['source']}"
            )
            assert actual['destination'] == expected['dest'], (
                f"Operation {i}: destination mismatch - expected {expected['dest']}, "
                f"got {actual['destination']}"
            )
            assert actual['category'] == expected['category'], (
                f"Operation {i}: category mismatch - expected {expected['category']}, "
                f"got {actual['category']}"
            )
            assert actual['conflict_resolved'] == expected['conflict'], (
                f"Operation {i}: conflict_resolved mismatch - expected {expected['conflict']}, "
                f"got {actual['conflict_resolved']}"
            )
        
        # Verify timestamps are present
        assert 'start_time' in log_data, "start_time missing from log"
        assert 'end_time' in log_data, "end_time missing from log"
        
        # Verify all operations have timestamps
        for i, op in enumerate(log_data['operations']):
            assert 'timestamp' in op, f"Operation {i} missing timestamp"
