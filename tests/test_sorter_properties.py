"""Property-based tests for file sorter module."""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.sorter import (
    move_file_with_conflict_resolution,
    generate_unique_filename,
    sort_files,
    SortingStats
)
from sik_sort.classifier import FileCategory, get_category_extensions


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


# Feature: file-sorter-cli, Property 9: Filename preservation
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf'])
)
def test_filename_preservation(filename, extension):
    """
    Property 9: Filename preservation
    
    For any file being moved (excluding conflict resolution cases),
    the basename of the file should remain unchanged after the move operation.
    
    Validates: Requirements 3.3
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directories for source and destination
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        dest_dir = root / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()
        
        # Create source file
        full_filename = f"{filename}.{extension}"
        src_file = src_dir / full_filename
        src_file.write_text("test content")
        
        # Move file (no conflict case)
        dest_file = dest_dir / full_filename
        move_file_with_conflict_resolution(src_file, dest_file)
        
        # Assert the file exists at destination with same name
        assert dest_file.exists(), f"File {full_filename} was not moved to destination"
        assert dest_file.name == full_filename, (
            f"Filename changed from {full_filename} to {dest_file.name}"
        )
        
        # Assert source file no longer exists
        assert not src_file.exists(), f"Source file {src_file} still exists after move"



# Feature: file-sorter-cli, Property 14: No file overwriting
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf']),
    original_content=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(min_codepoint=32, max_codepoint=126)  # ASCII printable
    ),
    new_content=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(min_codepoint=32, max_codepoint=126)  # ASCII printable
    )
)
def test_no_file_overwriting(filename, extension, original_content, new_content):
    """
    Property 14: No file overwriting
    
    For any file being moved to a destination where a file with the same name exists,
    the original file at the destination should remain unchanged and the incoming file
    should be renamed.
    
    Validates: Requirements 7.1
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    # Ensure contents are different so we can verify no overwriting
    assume(original_content != new_content)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        dest_dir = root / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()
        
        # Create destination file with original content
        full_filename = f"{filename}.{extension}"
        dest_file = dest_dir / full_filename
        dest_file.write_text(original_content)
        
        # Create source file with new content
        src_file = src_dir / full_filename
        src_file.write_text(new_content)
        
        # Move file (conflict case)
        move_file_with_conflict_resolution(src_file, dest_file)
        
        # Assert original file still exists with original content
        assert dest_file.exists(), f"Original file {dest_file} was removed"
        assert dest_file.read_text() == original_content, (
            f"Original file content was changed"
        )
        
        # Assert source file was moved (doesn't exist at source)
        assert not src_file.exists(), f"Source file {src_file} still exists"
        
        # Assert a renamed file exists in destination with new content
        renamed_files = [f for f in dest_dir.iterdir() if f.name != full_filename]
        assert len(renamed_files) == 1, (
            f"Expected 1 renamed file, found {len(renamed_files)}"
        )
        assert renamed_files[0].read_text() == new_content, (
            f"Renamed file doesn't have the expected content"
        )


# Feature: file-sorter-cli, Property 15: Conflict resolution preserves extensions
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf'])
)
def test_conflict_resolution_preserves_extensions(filename, extension):
    """
    Property 15: Conflict resolution preserves extensions
    
    For any file renamed due to conflict, the file extension should remain
    unchanged from the original.
    
    Validates: Requirements 7.2
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_dir = Path(temp_dir)
        
        # Create existing file
        full_filename = f"{filename}.{extension}"
        existing_file = dest_dir / full_filename
        existing_file.write_text("existing")
        
        # Generate unique filename
        unique_filename = generate_unique_filename(dest_dir, full_filename)
        
        # Assert extension is preserved
        unique_path = Path(unique_filename)
        assert unique_path.suffix == f".{extension}", (
            f"Extension changed from .{extension} to {unique_path.suffix}"
        )


# Feature: file-sorter-cli, Property 16: Unique names for all conflicts
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'jpg', 'mp4', 'zip', 'doc', 'pdf']),
    num_conflicts=st.integers(min_value=2, max_value=10)
)
def test_unique_names_for_all_conflicts(filename, extension, num_conflicts):
    """
    Property 16: Unique names for all conflicts
    
    For any set of files with identical names being moved to the same destination,
    each file should receive a unique final name.
    
    Validates: Requirements 7.3
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        dest_dir = root / "dest"
        src_dir.mkdir()
        dest_dir.mkdir()
        
        full_filename = f"{filename}.{extension}"
        
        # Create multiple source files with same name in different subdirectories
        src_files = []
        for i in range(num_conflicts):
            subdir = src_dir / f"sub{i}"
            subdir.mkdir()
            src_file = subdir / full_filename
            src_file.write_text(f"content_{i}")
            src_files.append(src_file)
        
        # Move all files to destination
        dest_file = dest_dir / full_filename
        for src_file in src_files:
            move_file_with_conflict_resolution(src_file, dest_file)
        
        # Get all files in destination
        dest_files = list(dest_dir.iterdir())
        
        # Assert we have the correct number of files
        assert len(dest_files) == num_conflicts, (
            f"Expected {num_conflicts} files in destination, found {len(dest_files)}"
        )
        
        # Assert all filenames are unique
        filenames = [f.name for f in dest_files]
        assert len(filenames) == len(set(filenames)), (
            f"Duplicate filenames found: {filenames}"
        )
        
        # Assert all files have the correct extension
        for dest_file in dest_files:
            assert dest_file.suffix == f".{extension}", (
                f"File {dest_file.name} has wrong extension {dest_file.suffix}"
            )


# Feature: file-sorter-cli, Property 4: Image files are sorted correctly
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'])
)
def test_image_files_sorted_correctly(filename, extension):
    """
    Property 4: Image files are sorted correctly
    
    For any file with an image extension (jpg, jpeg, png, gif, bmp, tiff, webp, svg),
    the file should be moved to the img folder.
    
    Validates: Requirements 2.2
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        
        # Create source file in a subdirectory
        src_subdir = root / "source_folder"
        src_subdir.mkdir()
        full_filename = f"{filename}.{extension}"
        src_file = src_subdir / full_filename
        src_file.write_text("test image content")
        
        # Run sort_files
        stats = sort_files(root, progress_callback=None)
        
        # Assert file was moved to img folder
        img_folder = root / "img"
        assert img_folder.exists(), "img folder was not created"
        
        # Check if file exists in img folder (either with original name or renamed due to conflict)
        img_files = list(img_folder.iterdir())
        assert len(img_files) >= 1, f"No files found in img folder"
        
        # Find our file (it might have been renamed)
        found = False
        for img_file in img_files:
            # Check if this is our file by extension
            if img_file.suffix == f".{extension}":
                found = True
                break
        
        assert found, f"File with extension .{extension} not found in img folder"
        
        # Assert source file no longer exists
        assert not src_file.exists(), "Source file still exists after sorting"
        
        # Assert statistics are correct
        assert stats.img_count >= 1, f"Image count in stats is {stats.img_count}, expected >= 1"


# Feature: file-sorter-cli, Property 5: Video files are sorted correctly
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', 'mpg', 'mpeg'])
)
def test_video_files_sorted_correctly(filename, extension):
    """
    Property 5: Video files are sorted correctly
    
    For any file with a video extension (mp4, avi, mov, mkv, wmv, flv, webm, m4v, mpg, mpeg),
    the file should be moved to the vid folder.
    
    Validates: Requirements 2.3
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        
        # Create source file in a subdirectory
        src_subdir = root / "source_folder"
        src_subdir.mkdir()
        full_filename = f"{filename}.{extension}"
        src_file = src_subdir / full_filename
        src_file.write_text("test video content")
        
        # Run sort_files
        stats = sort_files(root, progress_callback=None)
        
        # Assert file was moved to vid folder
        vid_folder = root / "vid"
        assert vid_folder.exists(), "vid folder was not created"
        
        # Check if file exists in vid folder
        vid_files = list(vid_folder.iterdir())
        assert len(vid_files) >= 1, f"No files found in vid folder"
        
        # Find our file (it might have been renamed)
        found = False
        for vid_file in vid_files:
            # Check if this is our file by extension
            if vid_file.suffix == f".{extension}":
                found = True
                break
        
        assert found, f"File with extension .{extension} not found in vid folder"
        
        # Assert source file no longer exists
        assert not src_file.exists(), "Source file still exists after sorting"
        
        # Assert statistics are correct
        assert stats.vid_count >= 1, f"Video count in stats is {stats.vid_count}, expected >= 1"


# Feature: file-sorter-cli, Property 6: Archive files are sorted correctly
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'iso'])
)
def test_archive_files_sorted_correctly(filename, extension):
    """
    Property 6: Archive files are sorted correctly
    
    For any file with an archive extension (zip, rar, 7z, tar, gz, bz2, xz, iso),
    the file should be moved to the arc folder.
    
    Validates: Requirements 2.4
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        
        # Create source file in a subdirectory
        src_subdir = root / "source_folder"
        src_subdir.mkdir()
        full_filename = f"{filename}.{extension}"
        src_file = src_subdir / full_filename
        src_file.write_text("test archive content")
        
        # Run sort_files
        stats = sort_files(root, progress_callback=None)
        
        # Assert file was moved to arc folder
        arc_folder = root / "arc"
        assert arc_folder.exists(), "arc folder was not created"
        
        # Check if file exists in arc folder
        arc_files = list(arc_folder.iterdir())
        assert len(arc_files) >= 1, f"No files found in arc folder"
        
        # Find our file (it might have been renamed)
        found = False
        for arc_file in arc_files:
            # Check if this is our file by extension
            if arc_file.suffix == f".{extension}":
                found = True
                break
        
        assert found, f"File with extension .{extension} not found in arc folder"
        
        # Assert source file no longer exists
        assert not src_file.exists(), "Source file still exists after sorting"
        
        # Assert statistics are correct
        assert stats.arc_count >= 1, f"Archive count in stats is {stats.arc_count}, expected >= 1"


# Feature: file-sorter-cli, Property 7: Miscellaneous files are sorted correctly
@settings(max_examples=100)
@given(
    filename=st.text(
        min_size=1,
        max_size=20,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', '\0', ':', '*', '?', '"', '<', '>', '|', '.']
        )
    ),
    extension=st.sampled_from(['txt', 'doc', 'docx', 'pdf', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'json'])
)
def test_miscellaneous_files_sorted_correctly(filename, extension):
    """
    Property 7: Miscellaneous files are sorted correctly
    
    For any file with a non-standard extension (not image, video, or archive),
    the file should be moved to the msk folder.
    
    Validates: Requirements 2.5
    """
    # Skip invalid filenames
    assume(is_valid_windows_name(filename))
    
    # Verify the extension is not in any of the known categories
    extensions_map = get_category_extensions()
    ext_with_dot = f".{extension}"
    for category, exts in extensions_map.items():
        assume(ext_with_dot not in exts)
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        
        # Create source file in a subdirectory
        src_subdir = root / "source_folder"
        src_subdir.mkdir()
        full_filename = f"{filename}.{extension}"
        src_file = src_subdir / full_filename
        src_file.write_text("test misc content")
        
        # Run sort_files
        stats = sort_files(root, progress_callback=None)
        
        # Assert file was moved to msk folder
        msk_folder = root / "msk"
        assert msk_folder.exists(), "msk folder was not created"
        
        # Check if file exists in msk folder
        msk_files = list(msk_folder.iterdir())
        assert len(msk_files) >= 1, f"No files found in msk folder"
        
        # Find our file (it might have been renamed)
        found = False
        for msk_file in msk_files:
            # Check if this is our file by extension
            if msk_file.suffix == f".{extension}":
                found = True
                break
        
        assert found, f"File with extension .{extension} not found in msk folder"
        
        # Assert source file no longer exists
        assert not src_file.exists(), "Source file still exists after sorting"
        
        # Assert statistics are correct
        assert stats.msk_count >= 1, f"Miscellaneous count in stats is {stats.msk_count}, expected >= 1"


# Feature: file-sorter-enhancements, Property 7: Statistics size accuracy
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
            st.sampled_from(['jpg', 'mp4', 'zip', 'txt']),
            st.integers(min_value=0, max_value=1000000)  # file size in bytes
        ),
        min_size=1,
        max_size=20
    )
)
def test_statistics_size_accuracy(files_data):
    """
    Property 7: Statistics size accuracy
    
    For any sorting operation, the total size for each category should equal
    the sum of all file sizes in that category.
    
    Validates: Requirements 4.1
    """
    from sik_sort.sorter import EnhancedSortingStats
    from sik_sort.classifier import classify_file
    
    # Skip if any filename is invalid
    for filename, _, _ in files_data:
        assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        src_dir.mkdir()
        
        # Track expected sizes per category
        expected_sizes = {
            'img': 0,
            'vid': 0,
            'arc': 0,
            'msk': 0
        }
        
        # Create files with specific sizes
        for filename, extension, size in files_data:
            full_filename = f"{filename}.{extension}"
            src_file = src_dir / full_filename
            
            # Create file with specific size
            content = 'x' * size
            src_file.write_text(content)
            
            # Determine category and track expected size
            category = classify_file(src_file)
            expected_sizes[category.value] += size
        
        # Create EnhancedSortingStats and simulate processing
        stats = EnhancedSortingStats()
        
        for filename, extension, size in files_data:
            full_filename = f"{filename}.{extension}"
            src_file = src_dir / full_filename
            
            if src_file.exists():  # File might have been processed already
                category = classify_file(src_file)
                stats.increment(category, size, full_filename, conflict=False)
        
        # Verify size accuracy for each category
        assert stats.img_size == expected_sizes['img'], (
            f"Image size mismatch: expected {expected_sizes['img']}, got {stats.img_size}"
        )
        assert stats.vid_size == expected_sizes['vid'], (
            f"Video size mismatch: expected {expected_sizes['vid']}, got {stats.vid_size}"
        )
        assert stats.arc_size == expected_sizes['arc'], (
            f"Archive size mismatch: expected {expected_sizes['arc']}, got {stats.arc_size}"
        )
        assert stats.msk_size == expected_sizes['msk'], (
            f"Miscellaneous size mismatch: expected {expected_sizes['msk']}, got {stats.msk_size}"
        )


# Feature: file-sorter-enhancements, Property 9: Largest file correctness
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
            st.sampled_from(['jpg', 'mp4', 'zip', 'txt']),
            st.integers(min_value=1, max_value=1000000)  # file size in bytes
        ),
        min_size=1,
        max_size=20
    )
)
def test_largest_file_correctness(files_data):
    """
    Property 9: Largest file correctness
    
    For any category with files, the reported largest file should actually be
    the largest file in that category.
    
    Validates: Requirements 4.4
    """
    from sik_sort.sorter import EnhancedSortingStats
    from sik_sort.classifier import classify_file
    
    # Skip if any filename is invalid
    for filename, _, _ in files_data:
        assume(is_valid_windows_name(filename))
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        src_dir = root / "source"
        src_dir.mkdir()
        
        # Track largest file per category
        largest_per_category = {
            'img': (None, 0),
            'vid': (None, 0),
            'arc': (None, 0),
            'msk': (None, 0)
        }
        
        # Create files
        for filename, extension, size in files_data:
            full_filename = f"{filename}.{extension}"
            src_file = src_dir / full_filename
            
            # Create file with specific size
            content = 'x' * size
            src_file.write_text(content)
            
            # Determine category and track largest
            category = classify_file(src_file)
            cat_value = category.value
            if size > largest_per_category[cat_value][1]:
                largest_per_category[cat_value] = (full_filename, size)
        
        # Create EnhancedSortingStats and simulate processing
        stats = EnhancedSortingStats()
        
        for filename, extension, size in files_data:
            full_filename = f"{filename}.{extension}"
            src_file = src_dir / full_filename
            
            if src_file.exists():
                category = classify_file(src_file)
                stats.increment(category, size, full_filename, conflict=False)
        
        # Verify largest file for each category
        if largest_per_category['img'][0] is not None:
            assert stats.largest_img is not None, "Expected largest_img to be set"
            assert stats.largest_img[1] == largest_per_category['img'][1], (
                f"Largest image size mismatch: expected {largest_per_category['img'][1]}, "
                f"got {stats.largest_img[1]}"
            )
        
        if largest_per_category['vid'][0] is not None:
            assert stats.largest_vid is not None, "Expected largest_vid to be set"
            assert stats.largest_vid[1] == largest_per_category['vid'][1], (
                f"Largest video size mismatch: expected {largest_per_category['vid'][1]}, "
                f"got {stats.largest_vid[1]}"
            )
        
        if largest_per_category['arc'][0] is not None:
            assert stats.largest_arc is not None, "Expected largest_arc to be set"
            assert stats.largest_arc[1] == largest_per_category['arc'][1], (
                f"Largest archive size mismatch: expected {largest_per_category['arc'][1]}, "
                f"got {stats.largest_arc[1]}"
            )
        
        if largest_per_category['msk'][0] is not None:
            assert stats.largest_msk is not None, "Expected largest_msk to be set"
            assert stats.largest_msk[1] == largest_per_category['msk'][1], (
                f"Largest misc size mismatch: expected {largest_per_category['msk'][1]}, "
                f"got {stats.largest_msk[1]}"
            )


# Feature: file-sorter-enhancements, Property 10: Size formatting correctness
@settings(max_examples=100)
@given(
    size_bytes=st.integers(min_value=0, max_value=10**15)  # Up to petabytes
)
def test_size_formatting_correctness(size_bytes):
    """
    Property 10: Size formatting correctness
    
    For any file size in bytes, the formatted string should correctly represent
    the size in appropriate units (KB, MB, GB, TB).
    
    Validates: Requirements 4.5
    """
    from sik_sort.sorter import EnhancedSortingStats
    
    formatted = EnhancedSortingStats.format_size(size_bytes)
    
    # Verify format is a string
    assert isinstance(formatted, str), f"Expected string, got {type(formatted)}"
    
    # Verify format contains a number and a unit
    parts = formatted.split()
    assert len(parts) == 2, f"Expected 'number unit' format, got '{formatted}'"
    
    number_str, unit = parts
    
    # Verify unit is valid
    valid_units = ['B', 'KB', 'MB', 'GB', 'TB']
    assert unit in valid_units, f"Invalid unit '{unit}', expected one of {valid_units}"
    
    # Verify number is valid
    try:
        number = float(number_str)
    except ValueError:
        assert False, f"Invalid number '{number_str}' in formatted string '{formatted}'"
    
    # Verify number is non-negative
    assert number >= 0, f"Number should be non-negative, got {number}"
    
    # Verify the conversion is correct
    if unit == 'B':
        # For bytes, should be exact integer
        assert number == size_bytes, f"Expected {size_bytes} B, got {formatted}"
    elif unit == 'KB':
        # Should be in range [1, 1024)
        expected = size_bytes / 1024.0
        assert 1 <= number < 1024, f"KB value {number} out of range [1, 1024)"
        assert abs(number - expected) < 0.01, f"Expected ~{expected:.2f} KB, got {number} KB"
    elif unit == 'MB':
        # Should be in range [1, 1024)
        expected = size_bytes / (1024.0 ** 2)
        assert 1 <= number < 1024, f"MB value {number} out of range [1, 1024)"
        assert abs(number - expected) < 0.01, f"Expected ~{expected:.2f} MB, got {number} MB"
    elif unit == 'GB':
        # Should be in range [1, 1024)
        expected = size_bytes / (1024.0 ** 3)
        assert 1 <= number < 1024, f"GB value {number} out of range [1, 1024)"
        assert abs(number - expected) < 0.01, f"Expected ~{expected:.2f} GB, got {number} GB"
    elif unit == 'TB':
        # Should be >= 1
        expected = size_bytes / (1024.0 ** 4)
        assert number >= 1, f"TB value {number} should be >= 1"
        assert abs(number - expected) < 0.01, f"Expected ~{expected:.2f} TB, got {number} TB"
    
    # Verify decimal places for non-byte units
    if unit != 'B':
        decimal_part = number_str.split('.')
        if len(decimal_part) == 2:
            assert len(decimal_part[1]) <= 2, (
                f"Expected at most 2 decimal places, got {len(decimal_part[1])} in '{formatted}'"
            )
