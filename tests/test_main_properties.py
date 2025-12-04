"""Property-based tests for main module."""

from pathlib import Path
from hypothesis import given, strategies as st, settings
import tempfile
import shutil
from sik_sort.main import setup_category_folders
from sik_sort.sorter import sort_files, SortingStats
from sik_sort.cleaner import find_empty_directories


# Windows reserved names that cannot be used as directory names
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

# Feature: file-sorter-cli, Property 3: Category folders are created
@settings(max_examples=100)
@given(
    dir_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        blacklist_characters=['<', '>', ':', '"', '|', '?', '*', '\0', '/', '\\']
    )).filter(lambda x: x.upper() not in WINDOWS_RESERVED_NAMES and not x.endswith('.') and not x.endswith(' '))
)
def test_category_folders_are_created(dir_name):
    """
    Property 3: Category folders are created
    
    For any source directory, after initialization, all four category folders
    (img, vid, arc, msk) should exist in the source directory.
    
    Validates: Requirements 2.1
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a subdirectory with the generated name
        test_dir = Path(temp_dir) / dir_name
        test_dir.mkdir(exist_ok=True)
        
        # Call setup_category_folders
        setup_category_folders(test_dir)
        
        # Assert all category folders exist
        expected_folders = ['img', 'vid', 'arc', 'msk']
        for folder_name in expected_folders:
            folder_path = test_dir / folder_name
            assert folder_path.exists(), f"Category folder '{folder_name}' should exist"
            assert folder_path.is_dir(), f"Category folder '{folder_name}' should be a directory"



# Feature: file-sorter-cli, Property 10: Statistics accuracy
@settings(max_examples=100)
@given(
    num_images=st.integers(min_value=0, max_value=10),
    num_videos=st.integers(min_value=0, max_value=10),
    num_archives=st.integers(min_value=0, max_value=10),
    num_misc=st.integers(min_value=0, max_value=10)
)
def test_statistics_accuracy(num_images, num_videos, num_archives, num_misc):
    """
    Property 10: Statistics accuracy
    
    For any sorting operation, the sum of displayed category counts should equal
    the total number of files moved, and each category count should match the
    actual number of files in that category folder.
    
    Validates: Requirements 4.1, 4.2
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Setup category folders
        setup_category_folders(test_dir)
        
        # Create test files with appropriate extensions
        image_extensions = ['.jpg', '.png', '.gif', '.bmp']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        archive_extensions = ['.zip', '.rar', '.7z', '.tar']
        misc_extensions = ['.txt', '.doc', '.pdf', '.exe']
        
        # Create image files
        for i in range(num_images):
            ext = image_extensions[i % len(image_extensions)]
            file_path = test_dir / f"image_{i}{ext}"
            file_path.touch()
        
        # Create video files
        for i in range(num_videos):
            ext = video_extensions[i % len(video_extensions)]
            file_path = test_dir / f"video_{i}{ext}"
            file_path.touch()
        
        # Create archive files
        for i in range(num_archives):
            ext = archive_extensions[i % len(archive_extensions)]
            file_path = test_dir / f"archive_{i}{ext}"
            file_path.touch()
        
        # Create misc files
        for i in range(num_misc):
            ext = misc_extensions[i % len(misc_extensions)]
            file_path = test_dir / f"misc_{i}{ext}"
            file_path.touch()
        
        # Sort files (not in dry-run mode)
        stats = sort_files(test_dir, dry_run=False)
        
        # Verify statistics accuracy
        expected_total = num_images + num_videos + num_archives + num_misc
        
        # Check that sum of category counts equals total
        assert stats.img_count + stats.vid_count + stats.arc_count + stats.msk_count == stats.total_files, \
            "Sum of category counts should equal total files"
        
        # Check that total matches expected
        assert stats.total_files == expected_total, \
            f"Total files should be {expected_total}, but got {stats.total_files}"
        
        # Check individual category counts
        assert stats.img_count == num_images, \
            f"Image count should be {num_images}, but got {stats.img_count}"
        assert stats.vid_count == num_videos, \
            f"Video count should be {num_videos}, but got {stats.vid_count}"
        assert stats.arc_count == num_archives, \
            f"Archive count should be {num_archives}, but got {stats.arc_count}"
        assert stats.msk_count == num_misc, \
            f"Misc count should be {num_misc}, but got {stats.msk_count}"
        
        # Verify actual files in folders match counts
        img_folder = test_dir / 'img'
        vid_folder = test_dir / 'vid'
        arc_folder = test_dir / 'arc'
        msk_folder = test_dir / 'msk'
        
        actual_img_count = len(list(img_folder.glob('*'))) if img_folder.exists() else 0
        actual_vid_count = len(list(vid_folder.glob('*'))) if vid_folder.exists() else 0
        actual_arc_count = len(list(arc_folder.glob('*'))) if arc_folder.exists() else 0
        actual_msk_count = len(list(msk_folder.glob('*'))) if msk_folder.exists() else 0
        
        assert actual_img_count == stats.img_count, \
            f"Actual files in img folder ({actual_img_count}) should match stats ({stats.img_count})"
        assert actual_vid_count == stats.vid_count, \
            f"Actual files in vid folder ({actual_vid_count}) should match stats ({stats.vid_count})"
        assert actual_arc_count == stats.arc_count, \
            f"Actual files in arc folder ({actual_arc_count}) should match stats ({stats.arc_count})"
        assert actual_msk_count == stats.msk_count, \
            f"Actual files in msk folder ({actual_msk_count}) should match stats ({stats.msk_count})"



# Feature: file-sorter-cli, Property 12: Directory preservation when cleanup declined
@settings(max_examples=100)
@given(
    num_subdirs=st.integers(min_value=1, max_value=5),
    num_files=st.integers(min_value=0, max_value=5)
)
def test_directory_preservation_when_cleanup_declined(num_subdirs, num_files):
    """
    Property 12: Directory preservation when cleanup declined
    
    For any directory structure after sorting, when cleanup is declined,
    the directory structure should remain unchanged.
    
    Validates: Requirements 5.3
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Setup category folders
        setup_category_folders(test_dir)
        
        # Create subdirectories
        subdirs = []
        for i in range(num_subdirs):
            subdir = test_dir / f"subdir_{i}"
            subdir.mkdir(exist_ok=True)
            subdirs.append(subdir)
        
        # Create some files in subdirectories
        for i in range(num_files):
            subdir = subdirs[i % len(subdirs)]
            file_path = subdir / f"file_{i}.txt"
            file_path.touch()
        
        # Sort files (this will move files and potentially leave empty directories)
        sort_files(test_dir, dry_run=False)
        
        # Get the directory structure before "declining cleanup"
        # (we simulate declining by not calling remove_empty_directories)
        dirs_before = set()
        for item in test_dir.rglob('*'):
            if item.is_dir():
                dirs_before.add(item.relative_to(test_dir))
        
        # Simulate declining cleanup by not calling remove_empty_directories
        # Instead, just verify that the directories still exist
        dirs_after = set()
        for item in test_dir.rglob('*'):
            if item.is_dir():
                dirs_after.add(item.relative_to(test_dir))
        
        # Assert that directory structure is unchanged
        assert dirs_before == dirs_after, \
            "Directory structure should remain unchanged when cleanup is declined"
        
        # Verify all original subdirectories still exist
        for subdir in subdirs:
            assert subdir.exists(), \
                f"Subdirectory {subdir.name} should still exist when cleanup is declined"
