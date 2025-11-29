"""Property-based tests for file classifier module."""

from pathlib import Path
from hypothesis import given, strategies as st, settings
from sik_sort.classifier import classify_file, FileCategory, get_category_extensions


# Feature: file-sorter-cli, Property 13: Case-insensitive classification
@settings(max_examples=100)
@given(
    base_name=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_characters=['.', '/', '\\', '\0'])),
    extension=st.sampled_from([
        # Image extensions
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg',
        # Video extensions
        'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm', 'm4v', 'mpg', 'mpeg',
        # Archive extensions
        'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'iso',
    ]),
    case_transform=st.sampled_from(['lower', 'upper', 'title', 'mixed'])
)
def test_case_insensitive_classification(base_name, extension, case_transform):
    """
    Property 13: Case-insensitive classification
    
    For any file extension in any case combination (uppercase, lowercase, mixed),
    the classification should be the same as the lowercase version.
    
    Validates: Requirements 6.1, 6.2, 6.3, 6.4
    """
    # Apply case transformation
    if case_transform == 'lower':
        transformed_ext = extension.lower()
    elif case_transform == 'upper':
        transformed_ext = extension.upper()
    elif case_transform == 'title':
        transformed_ext = extension.title()
    else:  # mixed - alternate case for each character
        transformed_ext = ''.join(
            c.upper() if i % 2 == 0 else c.lower() 
            for i, c in enumerate(extension)
        )
    
    # Create file paths with different case extensions
    file_lower = Path(f"{base_name}.{extension.lower()}")
    file_transformed = Path(f"{base_name}.{transformed_ext}")
    
    # Classify both files
    category_lower = classify_file(file_lower)
    category_transformed = classify_file(file_transformed)
    
    # Assert they have the same classification
    assert category_lower == category_transformed, (
        f"File with extension '.{extension.lower()}' classified as {category_lower}, "
        f"but '.{transformed_ext}' classified as {category_transformed}"
    )
