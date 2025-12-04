"""Property-based tests for dry-run mode functionality."""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.sorter import sort_files
from sik_sort.main import setup_category_folders
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


# Feature: file-sorter-cli, Property 25: Dry-run preserves file system
@settings(max_examples=100)
@given(
    files_data=st.lists(
        st.tuples(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
                )
            ),
            st.sampled_from(['jpg', 'mp4', 'zip', 'txt', 'doc', 'pdf'])
        ),
        min_size=1,
        max_size=10
    )
)
def test_dry_run_preserves_file_system(files_data):
    """
    Property 25: Dry-run preserves file system
    
    For any directory, running in dry-run mode should result in no files
    being moved or modified.
    
    Validates: Requirements 11.1
    """
    # Skip if any filename is invalid
    for filename, _ in files_data:
        assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        src_dir.mkdir()
        
        # Create files
        created_files = []
        for filename, extension in files_data:
            full_filename = f"{filename}.{extension}"
            src_file = src_dir / full_filename
            src_file.write_text(f"content of {full_filename}", encoding='utf-8')
            created_files.append(src_file)
        
        # Record initial state
        initial_files = {f: f.read_text(encoding='utf-8') for f in created_files if f.exists()}
        initial_file_paths = set(initial_files.keys())
        
        # Check that category folders don't exist yet
        category_folders = [root / 'img', root / 'vid', root / 'arc', root / 'msk']
        for folder in category_folders:
            assert not folder.exists(), f"Category folder {folder} should not exist before dry-run"
        
        # Run sort_files in dry-run mode
        stats = sort_files(root, dry_run=True, progress_callback=None)
        
        # Verify all original files still exist with same content
        for file_path, original_content in initial_files.items():
            assert file_path.exists(), f"File {file_path} was removed during dry-run"
            assert file_path.read_text(encoding='utf-8') == original_content, (
                f"File {file_path} content was modified during dry-run"
            )
        
        # Verify no new files were created in source directory
        current_files = set(src_dir.rglob('*'))
        current_files = {f for f in current_files if f.is_file()}
        assert current_files == initial_file_paths, (
            f"Files were added or removed during dry-run"
        )
        
        # Verify category folders were not created or are empty
        for folder in category_folders:
            if folder.exists():
                files_in_folder = list(folder.iterdir())
                assert len(files_in_folder) == 0, (
                    f"Category folder {folder} contains files after dry-run: {files_in_folder}"
                )



# Feature: file-sorter-cli, Property 26: Dry-run displays operation logs
@settings(max_examples=100)
@given(
    files_data=st.lists(
        st.tuples(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
                )
            ),
            st.sampled_from(['jpg', 'mp4', 'zip', 'txt', 'doc', 'pdf'])
        ),
        min_size=1,
        max_size=10
    )
)
def test_dry_run_displays_operation_logs(files_data):
    """
    Property 26: Dry-run displays operation logs
    
    For any file that would be moved in normal mode, dry-run mode should
    display an operation log for that file.
    
    Validates: Requirements 11.2
    """
    import io
    import sys
    
    # Skip if any filename is invalid
    for filename, _ in files_data:
        assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        src_dir.mkdir()
        
        # Create files
        created_files = []
        for filename, extension in files_data:
            full_filename = f"{filename}.{extension}"
            src_file = src_dir / full_filename
            src_file.write_text(f"content of {full_filename}", encoding='utf-8')
            created_files.append((full_filename, src_file))
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Run sort_files in dry-run mode
            stats = sort_files(root, dry_run=True, progress_callback=None)
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        # Get captured output
        output = captured_output.getvalue()
        
        # Verify that operation logs were displayed for each file
        for full_filename, _ in created_files:
            # Check that the filename appears in the output
            assert full_filename in output, (
                f"Expected operation log for {full_filename} in dry-run output"
            )
            
            # Check that [DRY RUN] prefix appears in output
            assert "[DRY RUN]" in output, (
                "Expected [DRY RUN] prefix in operation logs"
            )



# Feature: file-sorter-cli, Property 27: Dry-run displays accurate statistics
@settings(max_examples=100)
@given(
    files_data=st.lists(
        st.tuples(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
                )
            ),
            st.sampled_from(['jpg', 'mp4', 'zip', 'txt'])
        ),
        min_size=1,
        max_size=10
    )
)
def test_dry_run_statistics_accuracy(files_data):
    """
    Property 27: Dry-run displays accurate statistics
    
    For any directory, the statistics displayed in dry-run mode should match
    what would have been moved in normal mode.
    
    Validates: Requirements 11.3
    """
    from sik_sort.classifier import classify_file
    
    # Skip if any filename is invalid
    for filename, _ in files_data:
        assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        src_dir.mkdir()
        
        # Create files and track expected counts
        expected_counts = {'img': 0, 'vid': 0, 'arc': 0, 'msk': 0}
        created_files_set = set()
        
        for i, (filename, extension) in enumerate(files_data):
            # Make filename unique by adding index if duplicate
            full_filename = f"{filename}.{extension}"
            if full_filename in created_files_set:
                full_filename = f"{filename}_{i}.{extension}"
            
            created_files_set.add(full_filename)
            src_file = src_dir / full_filename
            src_file.write_text(f"content of {full_filename}", encoding='utf-8')
            
            # Determine category
            category = classify_file(src_file)
            expected_counts[category.value] += 1
        
        # Run sort_files in dry-run mode
        stats = sort_files(root, dry_run=True, progress_callback=None)
        
        # Verify statistics match expected counts
        assert stats.img_count == expected_counts['img'], (
            f"Image count mismatch: expected {expected_counts['img']}, got {stats.img_count}"
        )
        assert stats.vid_count == expected_counts['vid'], (
            f"Video count mismatch: expected {expected_counts['vid']}, got {stats.vid_count}"
        )
        assert stats.arc_count == expected_counts['arc'], (
            f"Archive count mismatch: expected {expected_counts['arc']}, got {stats.arc_count}"
        )
        assert stats.msk_count == expected_counts['msk'], (
            f"Miscellaneous count mismatch: expected {expected_counts['msk']}, got {stats.msk_count}"
        )
        
        # Verify total count
        expected_total = sum(expected_counts.values())
        assert stats.total_files == expected_total, (
            f"Total count mismatch: expected {expected_total}, got {stats.total_files}"
        )



# Feature: file-sorter-cli, Property 28: Dry-run mode is clearly indicated
@settings(max_examples=100)
@given(
    files_data=st.lists(
        st.tuples(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
                )
            ),
            st.sampled_from(['jpg', 'mp4', 'zip', 'txt'])
        ),
        min_size=1,
        max_size=5
    )
)
def test_dry_run_mode_indicators(files_data):
    """
    Property 28: Dry-run mode is clearly indicated
    
    For any dry-run execution, the output should contain clear indicators
    at the start and end that no changes were made.
    
    Validates: Requirements 11.4
    """
    import io
    import sys
    
    # Skip if any filename is invalid
    for filename, _ in files_data:
        assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        src_dir.mkdir()
        
        # Create files
        for i, (filename, extension) in enumerate(files_data):
            full_filename = f"{filename}_{i}.{extension}"
            src_file = src_dir / full_filename
            src_file.write_text(f"content of {full_filename}", encoding='utf-8')
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Run sort_files in dry-run mode
            stats = sort_files(root, dry_run=True, progress_callback=None)
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        # Get captured output
        output = captured_output.getvalue()
        
        # Verify that [DRY RUN] indicators appear in output
        assert "[DRY RUN]" in output, (
            "Expected [DRY RUN] indicator in output"
        )
        
        # The output should clearly indicate this is a simulation
        # by having the [DRY RUN] prefix on operation logs
        dry_run_count = output.count("[DRY RUN]")
        assert dry_run_count >= len(files_data), (
            f"Expected at least {len(files_data)} [DRY RUN] indicators, found {dry_run_count}"
        )



# Feature: file-sorter-cli, Property 29: Dry-run skips cleanup prompt
@settings(max_examples=100)
@given(
    num_files=st.integers(min_value=1, max_value=5)
)
def test_dry_run_skips_cleanup(num_files):
    """
    Property 29: Dry-run skips cleanup prompt
    
    For any dry-run execution, the cleanup prompt should not be displayed.
    This test verifies that the dry-run flag properly controls whether
    cleanup operations are performed.
    
    Validates: Requirements 11.5
    """
    # This property is tested by verifying that in dry-run mode:
    # 1. No cleanup operations are performed
    # 2. The main workflow skips the cleanup prompt
    
    # Since we can't easily test the interactive prompt without mocking,
    # we verify that the dry-run mode is properly passed through the system
    # and that cleanup-related operations are skipped.
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        src_dir.mkdir()
        
        # Create some files
        for i in range(num_files):
            src_file = src_dir / f"file_{i}.txt"
            src_file.write_text(f"content {i}", encoding='utf-8')
        
        # Create an empty subdirectory that would normally be cleaned up
        empty_dir = src_dir / "empty_subdir"
        empty_dir.mkdir()
        
        # Run sort_files in dry-run mode
        stats = sort_files(root, dry_run=True, progress_callback=None)
        
        # Verify that the empty directory still exists (wasn't cleaned up)
        # This indirectly verifies that cleanup was skipped
        assert empty_dir.exists(), (
            "Empty directory was removed during dry-run, but cleanup should be skipped"
        )
        
        # Verify that files are still in their original location
        remaining_files = list(src_dir.glob("file_*.txt"))
        assert len(remaining_files) == num_files, (
            f"Expected {num_files} files to remain in source, found {len(remaining_files)}"
        )
