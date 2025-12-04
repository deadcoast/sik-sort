"""Duplicate detector module for identifying files with identical content."""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class DuplicateStats:
    """Statistics for duplicate detection operations.
    
    Attributes:
        total_duplicates: Total number of duplicate files found
        unique_files: Number of unique files (first instance of each content)
        space_saved: Total bytes that could be saved by removing duplicates
        duplicate_groups: Number of groups of duplicate files
    """
    total_duplicates: int = 0
    unique_files: int = 0
    space_saved: int = 0
    duplicate_groups: int = 0


def find_duplicates(files: List[Path], algorithm: str = "md5") -> Dict[str, List[Path]]:
    """Identifies files with identical content using hash comparison.
    
    Args:
        files: List of file paths to check for duplicates
        algorithm: Hash algorithm to use ("md5" or "sha256")
        
    Returns:
        Dict mapping hash values to lists of file paths with that hash.
        Only includes hashes that have multiple files (duplicates).
    """
    hash_to_files: Dict[str, List[Path]] = {}
    
    for file_path in files:
        try:
            file_hash = compute_hash(file_path, algorithm)
            if file_hash not in hash_to_files:
                hash_to_files[file_hash] = []
            hash_to_files[file_hash].append(file_path)
        except (OSError, IOError) as e:
            # Skip files that cannot be read
            continue
    
    # Return only hashes with duplicates (more than one file)
    return {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}


def compute_hash(file_path: Path, algorithm: str = "md5") -> str:
    """Computes the hash of a file using streaming to handle large files.
    
    Args:
        file_path: Path to the file to hash
        algorithm: Hash algorithm to use ("md5" or "sha256")
        
    Returns:
        str: Hexadecimal hash string
        
    Raises:
        ValueError: If algorithm is not supported
        OSError: If file cannot be read
    """
    if algorithm.lower() == "md5":
        hasher = hashlib.md5()
    elif algorithm.lower() == "sha256":
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    # Use streaming to handle large files efficiently
    # Read in 64KB chunks
    chunk_size = 65536
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    
    return hasher.hexdigest()


def calculate_space_saved(duplicates: Dict[str, List[Path]]) -> int:
    """Calculates the total space that could be saved by removing duplicates.
    
    Args:
        duplicates: Dict mapping hashes to lists of duplicate file paths
        
    Returns:
        int: Total bytes that could be saved (size of all duplicates except first)
    """
    total_saved = 0
    
    for file_list in duplicates.values():
        if len(file_list) > 1:
            # Get size of first file (the one we keep)
            try:
                file_size = file_list[0].stat().st_size
                # Space saved is the size multiplied by number of duplicates (excluding the original)
                total_saved += file_size * (len(file_list) - 1)
            except OSError:
                # Skip if we can't get file size
                continue
    
    return total_saved
