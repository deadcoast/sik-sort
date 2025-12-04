"""Safety checks module to prevent sorting development directories."""

from pathlib import Path
from typing import List, Tuple


def check_python_package(path: Path) -> Tuple[bool, str]:
    """Check if directory contains Python package files.
    
    Args:
        path: Directory to check
        
    Returns:
        Tuple of (is_package, warning_message)
    """
    package_indicators = ['setup.py', 'pyproject.toml']
    
    # Check for package files in root
    for indicator in package_indicators:
        if (path / indicator).exists():
            return True, f"Directory contains {indicator} - appears to be a Python package"
    
    # Check for __init__.py in subdirectories (indicates package structure)
    try:
        for subdir in path.iterdir():
            if subdir.is_dir() and (subdir / '__init__.py').exists():
                return True, f"Directory contains Python package structure (found {subdir.name}/__init__.py)"
    except PermissionError:
        pass
    
    return False, ""


def check_git_repository(path: Path) -> Tuple[bool, str]:
    """Check if directory is a git repository with uncommitted changes.
    
    Args:
        path: Directory to check
        
    Returns:
        Tuple of (has_uncommitted_changes, warning_message)
    """
    git_dir = path / '.git'
    
    if not git_dir.exists():
        return False, ""
    
    # If .git exists, it's a repository
    # We'll warn about any git repo, as checking for uncommitted changes
    # requires running git commands which may not be available
    return True, "Directory is a Git repository - sorting may affect version control"


def check_dev_folders(path: Path) -> Tuple[bool, str]:
    """Check if directory contains common development folders.
    
    Args:
        path: Directory to check
        
    Returns:
        Tuple of (has_dev_folders, warning_message)
    """
    dev_folders = {'.git', '.venv', 'venv', 'node_modules', '.env', '__pycache__', 
                   '.pytest_cache', '.hypothesis', 'dist', 'build', '.tox'}
    
    found_folders = []
    try:
        for item in path.iterdir():
            if item.is_dir() and item.name in dev_folders:
                found_folders.append(item.name)
    except PermissionError:
        pass
    
    if found_folders:
        folders_str = ", ".join(found_folders)
        return True, f"Directory contains development folders: {folders_str}"
    
    return False, ""


def run_safety_checks(path: Path) -> List[str]:
    """Run all safety checks on a directory.
    
    Args:
        path: Directory to check
        
    Returns:
        List of warning messages (empty if all checks pass)
    """
    warnings = []
    
    # Check for Python package
    is_package, msg = check_python_package(path)
    if is_package:
        warnings.append(msg)
    
    # Check for Git repository
    is_git, msg = check_git_repository(path)
    if is_git:
        warnings.append(msg)
    
    # Check for dev folders
    has_dev, msg = check_dev_folders(path)
    if has_dev:
        warnings.append(msg)
    
    return warnings
