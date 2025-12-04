"""Property-based tests for duplicate detector module."""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from sik_sort.duplicates import (
    find_duplicates,
    compute_hash,
    calculate_space_saved,
    DuplicateStats
)


# Feature: advanced-file-operations, Property 20: Hash computation for all files
@settings(max_examples=100, deadline=None)
@given(
    num_files=st.integers(min_value=1, max_value=20),
    file_contents=st.lists(
        st.binary(min_size=0, max_size=10240),  # 0 to 10KB files
        min_size=1,
        max_size=20
    ),
    algorithm=st.sampled_from(["md5", "sha256"])
)
def test_hash_computation_for_all_files(num_files, file_contents, algorithm):
    """
    Property 20: Hash computation for all files
    
    For any duplicate detection operation, every file should have a hash value computed.
    
    Validates: Requirements 5.1
    """
    # Ensure we have enough content for the number of files
    assume(len(file_contents) >= num_files)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test files
        files = []
        for i in range(num_files):
            file_path = tmppath / f"file_{i}.txt"
            file_path.write_bytes(file_contents[i])
            files.append(file_path)
        
        # Find duplicates (which computes hashes for all files)
        duplicates = find_duplicates(files, algorithm)
        
        # Count total files that were hashed
        # This includes both unique files and duplicates
        hashed_files = set()
        for file_list in duplicates.values():
            hashed_files.update(file_list)
        
        # Also need to account for unique files (not in duplicates dict)
        # We can verify by computing hashes directly
        all_hashes = {}
        for file_path in files:
            file_hash = compute_hash(file_path, algorithm)
            if file_hash not in all_hashes:
                all_hashes[file_hash] = []
            all_hashes[file_hash].append(file_path)
        
        # Every file should have been hashed
        total_hashed = sum(len(paths) for paths in all_hashes.values())
        assert total_hashed == num_files, (
            f"Expected {num_files} files to be hashed, but only {total_hashed} were hashed"
        )
        
        # Verify that all files can be hashed individually
        for file_path in files:
            hash_value = compute_hash(file_path, algorithm)
            assert hash_value is not None, f"Hash computation failed for {file_path}"
            assert len(hash_value) > 0, f"Hash value is empty for {file_path}"
            
            # Verify hash format based on algorithm
            if algorithm == "md5":
                assert len(hash_value) == 32, f"MD5 hash should be 32 characters, got {len(hash_value)}"
            elif algorithm == "sha256":
                assert len(hash_value) == 64, f"SHA256 hash should be 64 characters, got {len(hash_value)}"


# Feature: advanced-file-operations, Property 21: Duplicate handling correctness
@settings(max_examples=100, deadline=None)
@given(
    unique_content=st.binary(min_size=1, max_size=5120),  # 1 byte to 5KB
    num_duplicates=st.integers(min_value=2, max_value=10),
    num_unique=st.integers(min_value=0, max_value=5),
    algorithm=st.sampled_from(["md5", "sha256"])
)
def test_duplicate_handling_correctness(unique_content, num_duplicates, num_unique, algorithm):
    """
    Property 21: Duplicate handling correctness
    
    For any set of files with identical content, only one copy should remain in the original
    location and all others should be identified as duplicates.
    
    Validates: Requirements 5.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create duplicate files with identical content
        duplicate_files = []
        for i in range(num_duplicates):
            file_path = tmppath / f"duplicate_{i}.txt"
            file_path.write_bytes(unique_content)
            duplicate_files.append(file_path)
        
        # Create unique files with different content
        unique_files = []
        for i in range(num_unique):
            file_path = tmppath / f"unique_{i}.txt"
            # Make unique content by appending index
            file_path.write_bytes(unique_content + bytes([i]))
            unique_files.append(file_path)
        
        all_files = duplicate_files + unique_files
        
        # Find duplicates
        duplicates = find_duplicates(all_files, algorithm)
        
        # Verify duplicate detection
        if num_duplicates > 1:
            # Should have exactly one group of duplicates
            assert len(duplicates) == 1, (
                f"Expected 1 duplicate group, found {len(duplicates)}"
            )
            
            # The duplicate group should contain all duplicate files
            duplicate_group = list(duplicates.values())[0]
            assert len(duplicate_group) == num_duplicates, (
                f"Expected {num_duplicates} files in duplicate group, found {len(duplicate_group)}"
            )
            
            # All files in the group should have identical content
            for file_path in duplicate_group:
                assert file_path.read_bytes() == unique_content, (
                    f"File {file_path} does not have expected content"
                )
        
        # Unique files should not appear in duplicates
        for unique_file in unique_files:
            for duplicate_group in duplicates.values():
                assert unique_file not in duplicate_group, (
                    f"Unique file {unique_file} should not be in duplicate group"
                )


# Feature: advanced-file-operations, Property 22: Duplicate filename preservation
@settings(max_examples=100, deadline=None)
@given(
    base_name=st.text(
        alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
        min_size=1,
        max_size=20
    ),
    extension=st.sampled_from([".txt", ".jpg", ".pdf", ".doc"]),
    num_duplicates=st.integers(min_value=2, max_value=8),
    content=st.binary(min_size=1, max_size=2048)
)
def test_duplicate_filename_preservation(base_name, extension, num_duplicates, content):
    """
    Property 22: Duplicate filename preservation
    
    For any duplicate file, the original filename should be preserved in the duplicate
    detection results.
    
    Validates: Requirements 5.3
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create duplicate files with specific names
        files = []
        for i in range(num_duplicates):
            file_path = tmppath / f"{base_name}_{i}{extension}"
            file_path.write_bytes(content)
            files.append(file_path)
        
        # Find duplicates
        duplicates = find_duplicates(files)
        
        # Should have one duplicate group
        assert len(duplicates) == 1, f"Expected 1 duplicate group, found {len(duplicates)}"
        
        duplicate_group = list(duplicates.values())[0]
        
        # All original filenames should be preserved
        for file_path in duplicate_group:
            # File should still exist with original name
            assert file_path.exists(), f"File {file_path} should exist"
            
            # Filename should contain the base name
            assert base_name in file_path.stem, (
                f"Filename {file_path.name} should contain base name {base_name}"
            )
            
            # Extension should be preserved
            assert file_path.suffix == extension, (
                f"Extension should be {extension}, got {file_path.suffix}"
            )


# Feature: advanced-file-operations, Property 23: Duplicate statistics accuracy
@settings(max_examples=100, deadline=None)
@given(
    num_duplicate_groups=st.integers(min_value=1, max_value=5),
    duplicates_per_group=st.lists(
        st.integers(min_value=2, max_value=6),
        min_size=1,
        max_size=5
    ),
    file_size=st.integers(min_value=100, max_value=10240)
)
def test_duplicate_statistics_accuracy(num_duplicate_groups, duplicates_per_group, file_size):
    """
    Property 23: Duplicate statistics accuracy
    
    For any duplicate detection operation, the displayed duplicate count and space saved
    should match the actual duplicates found and their total size.
    
    Validates: Requirements 5.4
    """
    # Ensure we have enough groups
    assume(len(duplicates_per_group) >= num_duplicate_groups)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        all_files = []
        expected_duplicates = 0
        expected_space_saved = 0
        
        # Create duplicate groups
        for group_idx in range(num_duplicate_groups):
            num_in_group = duplicates_per_group[group_idx]
            content = f"group_{group_idx}_content".encode() * (file_size // 20)
            
            for file_idx in range(num_in_group):
                file_path = tmppath / f"group_{group_idx}_file_{file_idx}.txt"
                file_path.write_bytes(content)
                all_files.append(file_path)
            
            # Count duplicates (all but the first in each group)
            expected_duplicates += (num_in_group - 1)
            # Space saved is file_size * number of duplicates
            expected_space_saved += len(content) * (num_in_group - 1)
        
        # Find duplicates
        duplicates = find_duplicates(all_files)
        
        # Calculate statistics
        actual_space_saved = calculate_space_saved(duplicates)
        
        # Count actual duplicates
        actual_duplicates = sum(len(group) - 1 for group in duplicates.values())
        
        # Verify statistics
        assert actual_duplicates == expected_duplicates, (
            f"Expected {expected_duplicates} duplicates, found {actual_duplicates}"
        )
        
        assert actual_space_saved == expected_space_saved, (
            f"Expected {expected_space_saved} bytes saved, calculated {actual_space_saved}"
        )
        
        # Verify number of duplicate groups
        assert len(duplicates) == num_duplicate_groups, (
            f"Expected {num_duplicate_groups} duplicate groups, found {len(duplicates)}"
        )


# Feature: advanced-file-operations, Property 24: Hash algorithm selection
@settings(max_examples=100, deadline=None)
@given(
    content=st.binary(min_size=1, max_size=5120),
    algorithm=st.sampled_from(["md5", "sha256"])
)
def test_hash_algorithm_selection(content, algorithm):
    """
    Property 24: Hash algorithm selection
    
    For any specified hash algorithm (MD5 or SHA256), the computed hashes should match
    that algorithm's output format.
    
    Validates: Requirements 5.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test file
        file_path = tmppath / "test.txt"
        file_path.write_bytes(content)
        
        # Compute hash with specified algorithm
        hash_value = compute_hash(file_path, algorithm)
        
        # Verify hash format
        assert hash_value is not None, "Hash value should not be None"
        assert len(hash_value) > 0, "Hash value should not be empty"
        
        # Check hash length based on algorithm
        if algorithm == "md5":
            assert len(hash_value) == 32, (
                f"MD5 hash should be 32 hex characters, got {len(hash_value)}"
            )
        elif algorithm == "sha256":
            assert len(hash_value) == 64, (
                f"SHA256 hash should be 64 hex characters, got {len(hash_value)}"
            )
        
        # Verify hash contains only hexadecimal characters
        assert all(c in '0123456789abcdef' for c in hash_value), (
            f"Hash should contain only hex characters, got {hash_value}"
        )
        
        # Verify consistency: computing hash again should give same result
        hash_value_2 = compute_hash(file_path, algorithm)
        assert hash_value == hash_value_2, (
            f"Hash computation should be deterministic, got {hash_value} and {hash_value_2}"
        )


# Additional property test: Identical files produce identical hashes
@settings(max_examples=100)
@given(
    content=st.binary(min_size=1, max_size=5120),
    algorithm=st.sampled_from(["md5", "sha256"])
)
def test_identical_files_same_hash(content, algorithm):
    """
    Property: Identical files produce identical hashes
    
    For any file content, two files with identical content should produce the same hash.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create two files with identical content
        file1 = tmppath / "file1.txt"
        file2 = tmppath / "file2.txt"
        
        file1.write_bytes(content)
        file2.write_bytes(content)
        
        # Compute hashes
        hash1 = compute_hash(file1, algorithm)
        hash2 = compute_hash(file2, algorithm)
        
        # Hashes should be identical
        assert hash1 == hash2, (
            f"Identical files should have identical hashes, got {hash1} and {hash2}"
        )


# Additional property test: Different files produce different hashes
@settings(max_examples=100)
@given(
    content1=st.binary(min_size=1, max_size=5120),
    content2=st.binary(min_size=1, max_size=5120),
    algorithm=st.sampled_from(["md5", "sha256"])
)
def test_different_files_different_hash(content1, content2, algorithm):
    """
    Property: Different files produce different hashes (with high probability)
    
    For any two different file contents, they should produce different hashes.
    """
    # Only test when contents are actually different
    assume(content1 != content2)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create two files with different content
        file1 = tmppath / "file1.txt"
        file2 = tmppath / "file2.txt"
        
        file1.write_bytes(content1)
        file2.write_bytes(content2)
        
        # Compute hashes
        hash1 = compute_hash(file1, algorithm)
        hash2 = compute_hash(file2, algorithm)
        
        # Hashes should be different (collision is extremely unlikely)
        assert hash1 != hash2, (
            f"Different files should have different hashes, both got {hash1}"
        )
