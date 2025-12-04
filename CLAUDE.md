# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies (pytest, hypothesis)
pip install -e ".[dev]"

# Run tests
pytest

# Run a single test file
pytest tests/test_classifier_properties.py

# Run a specific test
pytest tests/test_classifier_properties.py::test_case_insensitive_classification

# Run the application
sik
```

## Architecture

Sik Sort is a Windows CLI utility that organizes files into categorized folders (img, vid, arc, msk) based on file extensions. It uses the Rich library for terminal UI.

### Three-Layer Architecture

1. **CLI Layer** (`cli.py`) - User interaction using Rich components (prompts, progress bars, tables)
2. **Business Logic Layer** (`classifier.py`, `sorter.py`) - File classification by extension and sorting coordination
3. **File System Layer** (`scanner.py`, `cleaner.py`) - Directory traversal and empty folder cleanup

### Key Data Types

- `FileCategory` enum in `classifier.py` - Maps to folder names: IMAGE→"img", VIDEO→"vid", ARCHIVE→"arc", MISC→"msk"
- `SortingStats` dataclass in `sorter.py` - Tracks file counts per category
- `EnhancedSortingStats` dataclass in `sorter.py` - Extended stats with size tracking and largest file info

### Entry Point Flow

`main.py:main()` orchestrates: prompt for path → safety checks → create category folders → scan directory → sort files with progress → display statistics → optional cleanup

### Safety Module

`safety.py` detects development directories (git repos, Python packages, node_modules, etc.) and warns before sorting to prevent accidentally reorganizing project files.

## Testing

Tests use property-based testing with Hypothesis (minimum 100 iterations per test). Test files follow the pattern `test_*_properties.py` and reference correctness properties from `.kiro/specs/file-sorter-cli/design.md`.

Property test format:
```python
# Feature: file-sorter-cli, Property {number}: {property_text}
@settings(max_examples=100)
@given(...)
def test_property_name(...):
    ...
```
