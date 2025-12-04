"""Property-based tests for size-based sorting functionality.

Feature: advanced-file-operations
"""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
from sik_sort.sorter import sort_files_with_size, EnhancedSortingStats
from sik_sort.size_classifier import SizeThresholds, SizeCategory, classify_by_size
from sik_sort.classifier import FileCategory


# Strategy for generating file sizes (smaller for faster tests)
file_sizes = st.integers(min_value=0, max_value=200_000_000)  # 0 to 200MB

# Strategy for generating filenames
filenames = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
    min_size=1,
    max_size=20
).map(lambda s: s + ".txt")


@given(
    file_size=file_sizes,
    filename=filenames
)
@settings(max_examples=100, deadline=None)
def test_size_hierarchy_structure(file_size, filename):
    """Property 13: Size hierarchy structure
    
    For any file sorted by size, the file's destination path should match 
    the pattern {size_category}/{type_category}
    
    **Validates: Requirements 3.4**
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Create a test file with specific size
        test_file = source_path / filename
        test_file.write_bytes(b'x' * file_size)
        
        # Determine expected size category before moving
        thresholds = SizeThresholds()
        expected_size_category = classify_by_size(test_file, thresholds)
        
        # Sort files with size-based sorting
        stats = sort_files_with_size(source_path, dry_run=False)
        
        # Verify the file was moved
        assert stats.total_files == 1
        assert len(stats.operations) == 1
        
        operation = stats.operations[0]
        dest_path = operation.destination
        
        # Verify the destination path matches {size_category}/{type_category} pattern
        # The path should be: source_path / size_category / type_category / filename
        relative_path = dest_path.relative_to(source_path)
        parts = relative_path.parts
        
        # Should have at least 3 parts: size_category, type_category, filename
        assert len(parts) >= 3, f"Expected at least 3 path parts, got {len(parts)}: {parts}"
        
        # First part should be size category
        size_part = parts[0]
        assert size_part in ['small', 'medium', 'large'], f"Expected size category, got {size_part}"
        
        # Second part should be type category
        type_part = parts[1]
        assert type_part in ['img', 'vid', 'arc', 'msk'], f"Expected type category, got {type_part}"
        
        # Verify the size category matches the file size
        assert size_part == expected_size_category.value


@given(
    num_files=st.integers(min_value=1, max_value=10),
    file_sizes=st.lists(file_sizes, min_size=1, max_size=10)
)
@settings(max_examples=100, deadline=None)
def test_size_statistics_accuracy(num_files, file_sizes):
    """Property 14: Size statistics accuracy
    
    For any size-based sort, the displayed counts and total sizes for each 
    size category should match the actual files in those folders
    
    **Validates: Requirements 3.5**
    """
    # Ensure we have enough sizes
    if len(file_sizes) < num_files:
        file_sizes = file_sizes * ((num_files // len(file_sizes)) + 1)
    file_sizes = file_sizes[:num_files]
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = Path(tmpdir)
        
        # Count expected categories before creating files
        thresholds = SizeThresholds()
        expected_counts = {'small': 0, 'medium': 0, 'large': 0}
        
        for size in file_sizes:
            if size <= thresholds.small_max:
                expected_counts['small'] += 1
            elif size <= thresholds.medium_max:
                expected_counts['medium'] += 1
            else:
                expected_counts['large'] += 1
        
        # Create test files with specific sizes
        for i, size in enumerate(file_sizes):
            test_file = source_path / f"file_{i}.txt"
            test_file.write_bytes(b'x' * size)
        
        # Sort files with size-based sorting
        stats = sort_files_with_size(source_path, dry_run=False)
        
        # Verify total files count
        assert stats.total_files == num_files
        
        # Verify size category counts match
        for category, expected_count in expected_counts.items():
            actual_count = stats.size_categories.get(category, 0)
            assert actual_count == expected_count, \
                f"Size category {category}: expected {expected_count}, got {actual_count}"
        
        # Verify all files are accounted for
        total_in_categories = sum(stats.size_categories.values())
        assert total_in_categories == num_files
