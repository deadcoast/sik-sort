"""File classifier module for determining file categories based on extensions."""

from enum import Enum
from pathlib import Path


class FileCategory(Enum):
    """File category enumeration."""
    IMAGE = "img"
    VIDEO = "vid"
    ARCHIVE = "arc"
    MISC = "msk"


def get_category_extensions() -> dict[FileCategory, set[str]]:
    """Returns extension mappings for each category.
    
    Returns:
        dict: Mapping of FileCategory to set of extensions
    """
    return {
        FileCategory.IMAGE: {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
        FileCategory.VIDEO: {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'},
        FileCategory.ARCHIVE: {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'},
    }


def classify_file(file_path: Path) -> FileCategory:
    """Returns category enum for a given file.
    
    Args:
        file_path: Path to the file to classify
        
    Returns:
        FileCategory: The category the file belongs to
    """
    extension = file_path.suffix.lower()
    extension_map = get_category_extensions()
    
    for category, extensions in extension_map.items():
        if extension in extensions:
            return category
    
    return FileCategory.MISC
