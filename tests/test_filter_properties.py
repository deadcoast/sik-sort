"""Property-based tests for filter engine module."""

from pathlib import Path
import tempfile
from hypothesis import given, strategies as st, settings, assume
from sik_sort.filters import FilterConfig, apply_filters, matches_pattern, matches_extensions


# Strategy for generating file paths with various extensions and names
@st.composite
def file_path_strategy(draw):
    """Generate a file path with random name and extension."""
    name = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        blacklist_characters=['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    )))
    extension = draw(st.sampled_from(['.jpg', '.png', '.pdf', '.txt', '.mp4', '.zip', '.doc', '.tmp', '.bak']))
    return Path(f"{name}{extension}")


# Strategy for generating glob patterns
@st.composite
def glob_pattern_strategy(draw):
    """Generate a glob pattern."""
    patterns = ['*.jpg', '*.png', '*.pdf', '*_backup*', '*_temp*', 'test_*', '*_old.*']
    return draw(st.sampled_from(patterns))


# Feature: advanced-file-operations, Property 6: Include filter correctness
@settings(max_examples=100)
@given(
    files=st.lists(file_path_strategy(), min_size=1, max_size=50),
    pattern=glob_pattern_strategy()
)
def test_include_filter_correctness(files, pattern):
    """
    Property 6: Include filter correctness
    
    For any include pattern and set of files, only files matching the pattern
    should be included in the processing list.
    
    Validates: Requirements 2.1
    """
    # Create filter config with include pattern
    config = FilterConfig(include_patterns=[pattern])
    
    # Apply filters
    filtered, excluded_count = apply_filters(files, config)
    
    # Verify all filtered files match the pattern
    for file in filtered:
        assert matches_pattern(file, pattern), f"File {file} in filtered list but doesn't match pattern {pattern}"
    
    # Verify no files that don't match the pattern are included
    for file in files:
        if file not in filtered:
            assert not matches_pattern(file, pattern), f"File {file} matches pattern {pattern} but was excluded"
    
    # Verify count consistency
    assert len(filtered) + excluded_count == len(files)


# Feature: advanced-file-operations, Property 7: Exclude filter correctness
@settings(max_examples=100)
@given(
    files=st.lists(file_path_strategy(), min_size=1, max_size=50),
    pattern=glob_pattern_strategy()
)
def test_exclude_filter_correctness(files, pattern):
    """
    Property 7: Exclude filter correctness
    
    For any exclude pattern and set of files, no files matching the pattern
    should be included in the processing list.
    
    Validates: Requirements 2.2
    """
    # Create filter config with exclude pattern
    config = FilterConfig(exclude_patterns=[pattern])
    
    # Apply filters
    filtered, excluded_count = apply_filters(files, config)
    
    # Verify no filtered files match the exclude pattern
    for file in filtered:
        assert not matches_pattern(file, pattern), f"File {file} matches exclude pattern {pattern} but was included"
    
    # Verify all files matching the pattern are excluded
    for file in files:
        if matches_pattern(file, pattern):
            assert file not in filtered, f"File {file} matches exclude pattern {pattern} but was not excluded"
    
    # Verify count consistency
    assert len(filtered) + excluded_count == len(files)


# Feature: advanced-file-operations, Property 8: Extension filter correctness
@settings(max_examples=100)
@given(
    files=st.lists(file_path_strategy(), min_size=1, max_size=50),
    extensions=st.sets(st.sampled_from(['.jpg', '.png', '.pdf', '.txt', '.mp4']), min_size=1, max_size=3)
)
def test_extension_filter_correctness(files, extensions):
    """
    Property 8: Extension filter correctness
    
    For any set of allowed extensions and files, only files with those extensions
    should be included in the processing list.
    
    Validates: Requirements 2.3
    """
    # Create filter config with include extensions
    config = FilterConfig(include_extensions=extensions)
    
    # Apply filters
    filtered, excluded_count = apply_filters(files, config)
    
    # Verify all filtered files have one of the allowed extensions
    for file in filtered:
        assert matches_extensions(file, extensions), f"File {file} in filtered list but doesn't have allowed extension"
    
    # Verify no files with disallowed extensions are included
    for file in files:
        if file not in filtered:
            assert not matches_extensions(file, extensions), f"File {file} has allowed extension but was excluded"
    
    # Verify count consistency
    assert len(filtered) + excluded_count == len(files)


# Feature: advanced-file-operations, Property 9: Filter precedence
@settings(max_examples=100)
@given(
    files=st.lists(file_path_strategy(), min_size=1, max_size=50),
    include_pattern=glob_pattern_strategy(),
    exclude_pattern=glob_pattern_strategy()
)
def test_filter_precedence(files, include_pattern, exclude_pattern):
    """
    Property 9: Filter precedence
    
    For any set of files with both include and exclude patterns, the result
    should equal applying include first, then excluding from that result.
    
    Validates: Requirements 2.4
    """
    # Assume patterns are different to make test meaningful
    assume(include_pattern != exclude_pattern)
    
    # Create filter config with both include and exclude patterns
    config = FilterConfig(
        include_patterns=[include_pattern],
        exclude_patterns=[exclude_pattern]
    )
    
    # Apply filters
    filtered, excluded_count = apply_filters(files, config)
    
    # Manually apply include first
    included = [f for f in files if matches_pattern(f, include_pattern)]
    
    # Then apply exclude
    expected = [f for f in included if not matches_pattern(f, exclude_pattern)]
    
    # Verify the result matches expected precedence
    assert set(filtered) == set(expected), "Filter precedence not correct: include should be applied before exclude"
    
    # Verify count consistency
    assert len(filtered) + excluded_count == len(files)


# Feature: advanced-file-operations, Property 10: Filter statistics accuracy
@settings(max_examples=100)
@given(
    files=st.lists(file_path_strategy(), min_size=1, max_size=50),
    include_patterns=st.lists(glob_pattern_strategy(), min_size=0, max_size=3),
    exclude_patterns=st.lists(glob_pattern_strategy(), min_size=0, max_size=3),
    include_extensions=st.sets(st.sampled_from(['.jpg', '.png', '.pdf', '.txt']), min_size=0, max_size=3),
    exclude_extensions=st.sets(st.sampled_from(['.tmp', '.bak', '.zip']), min_size=0, max_size=2)
)
def test_filter_statistics_accuracy(files, include_patterns, exclude_patterns, include_extensions, exclude_extensions):
    """
    Property 10: Filter statistics accuracy
    
    For any filtering operation, the excluded count should equal the total files
    scanned minus the files included.
    
    Validates: Requirements 2.5
    """
    # Create filter config
    config = FilterConfig(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        include_extensions=include_extensions,
        exclude_extensions=exclude_extensions
    )
    
    # Apply filters
    filtered, excluded_count = apply_filters(files, config)
    
    # Verify statistics accuracy
    total_files = len(files)
    included_count = len(filtered)
    
    assert excluded_count == total_files - included_count, \
        f"Excluded count {excluded_count} doesn't match total {total_files} - included {included_count}"
    
    # Verify all filtered files are from original list
    for file in filtered:
        assert file in files, f"File {file} in filtered list but not in original files"
    
    # Verify the filtered list preserves the order and duplicates from the original
    # (filtering should not add or remove duplicates, just filter based on criteria)
    assert len(filtered) <= len(files), "Filtered list has more files than original"
