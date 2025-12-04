# Design Document: Sik Sort

## Overview

Sik Sort is a Python-based command-line utility for Windows that recursively organizes files into categorized folders. The application uses a simple architecture with clear separation between CLI interaction, file classification logic, and file system operations. The Rich library provides an enhanced terminal experience with formatted output, progress indicators, and styled prompts.

## Architecture

The application follows a modular architecture with three main layers:

1. **CLI Layer**: Handles user interaction using Rich library components
2. **Business Logic Layer**: Contains file classification and sorting logic
3. **File System Layer**: Manages file operations and directory traversal

```
┌─────────────────────────────────────┐
│         CLI Layer (Rich)            │
│  - Prompts & Input Validation       │
│  - Statistics Display               │
│  - Progress Indicators              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Business Logic Layer           │
│  - File Classifier                  │
│  - Sorting Coordinator              │
│  - Statistics Tracker               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      File System Layer              │
│  - Directory Scanner                │
│  - File Mover                       │
│  - Empty Folder Cleaner             │
└─────────────────────────────────────┘
```

## Components and Interfaces

### 1. CLI Module (`cli.py`)

**Responsibilities:**
- Display prompts and collect user input
- Show progress during file operations with ASCII progress bars
- Display statistics in formatted tables
- Handle yes/no confirmations
- Parse command-line arguments for path and flags

**Key Functions:**
- `parse_arguments() -> tuple[Path | None, bool]`: Parses command-line arguments for path and dry-run flag
- `prompt_for_path() -> Path`: Prompts user for source directory path with validation
- `display_statistics(stats: SortingStats, dry_run: bool) -> None`: Shows sorting results using Rich tables
- `confirm_cleanup() -> bool`: Prompts user for empty folder cleanup confirmation
- `display_ascii_progress(current: int, total: int) -> None`: Shows ASCII progress bar with █ and ░ characters
- `display_error(message: str) -> None`: Shows formatted error messages
- `display_dry_run_banner() -> None`: Shows prominent banner indicating dry-run mode

### 2. File Classifier (`classifier.py`)

**Responsibilities:**
- Determine file category based on extension
- Maintain mappings of extensions to categories

**Key Functions:**
- `classify_file(file_path: Path) -> FileCategory`: Returns category enum for a given file
- `get_category_extensions() -> dict[FileCategory, set[str]]`: Returns extension mappings

**Data Types:**
```python
class FileCategory(Enum):
    IMAGE = "img"
    VIDEO = "vid"
    ARCHIVE = "arc"
    MISC = "msk"
```

### 3. File Sorter (`sorter.py`)

**Responsibilities:**
- Coordinate the sorting process
- Track statistics
- Handle file name conflicts
- Log operations in real-time

**Key Functions:**
- `sort_files(source_path: Path, dry_run: bool, progress_callback: Callable, log_callback: Callable) -> SortingStats`: Main sorting orchestrator
- `move_file_with_conflict_resolution(src: Path, dest: Path, dry_run: bool) -> None`: Moves file and handles naming conflicts (or simulates in dry-run)
- `generate_unique_filename(dest_path: Path, filename: str) -> str`: Creates unique filename when conflicts occur

**Data Types:**
```python
@dataclass
class SortingStats:
    total_files: int
    img_count: int
    vid_count: int
    arc_count: int
    msk_count: int
```

### 4. Directory Scanner (`scanner.py`)

**Responsibilities:**
- Recursively traverse directory structure
- Identify all files to be processed
- Skip target category folders during scanning

**Key Functions:**
- `scan_directory(path: Path, exclude_dirs: set[str]) -> list[Path]`: Returns list of all files to process
- `is_excluded_directory(path: Path, exclude_dirs: set[str]) -> bool`: Checks if directory should be skipped

### 5. Folder Cleaner (`cleaner.py`)

**Responsibilities:**
- Identify empty directories
- Remove empty folders while preserving category folders

**Key Functions:**
- `find_empty_directories(root_path: Path, preserve_dirs: set[str]) -> list[Path]`: Finds all empty directories
- `remove_empty_directories(directories: list[Path]) -> int`: Removes empty folders and returns count

### 6. Operation Logger (`operation_logger.py`)

**Responsibilities:**
- Display real-time operation logs during sorting
- Provide color-coded, stylized output for different operations
- Show file movements with source and destination

**Key Functions:**
- `log_file_operation(filename: str, category: FileCategory, dry_run: bool) -> None`: Logs a file being moved to a category
- `log_scan_complete(file_count: int) -> None`: Logs completion of directory scan
- `log_conflict_resolution(original_name: str, new_name: str) -> None`: Logs when a filename conflict is resolved
- `log_error(filename: str, error_message: str) -> None`: Logs errors during file operations

### 7. Main Entry Point (`main.py`)

**Responsibilities:**
- Application entry point
- Orchestrate the overall workflow
- Handle top-level error handling
- Coordinate dry-run vs normal execution modes

**Key Functions:**
- `main() -> None`: Main application flow with argument parsing and mode selection
- `setup_category_folders(source_path: Path, dry_run: bool) -> None`: Creates target category folders (or simulates in dry-run)

## Data Models

### FileCategory Enum
```python
class FileCategory(Enum):
    IMAGE = "img"
    VIDEO = "vid"
    ARCHIVE = "arc"
    MISC = "msk"
```

### SortingStats Dataclass
```python
@dataclass
class SortingStats:
    total_files: int = 0
    img_count: int = 0
    vid_count: int = 0
    arc_count: int = 0
    msk_count: int = 0
    
    def increment(self, category: FileCategory) -> None:
        """Increment counter for given category"""
        pass
```

### Extension Mappings
```python
EXTENSION_MAP = {
    FileCategory.IMAGE: {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
    FileCategory.VIDEO: {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'},
    FileCategory.ARCHIVE: {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'},
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Valid paths are accepted
*For any* valid directory path format, the path validation function should accept the path and return success
**Validates: Requirements 1.2**

### Property 2: Invalid paths are rejected
*For any* invalid directory path format (malformed, contains illegal characters, etc.), the path validation function should reject the path and return an error
**Validates: Requirements 1.3**

### Property 3: Category folders are created
*For any* source directory, after initialization, all four category folders (img, vid, arc, msk) should exist in the source directory
**Validates: Requirements 2.1**

### Property 4: Image files are sorted correctly
*For any* file with an image extension (jpg, jpeg, png, gif, bmp, tiff, webp, svg), the file should be moved to the img folder
**Validates: Requirements 2.2**

### Property 5: Video files are sorted correctly
*For any* file with a video extension (mp4, avi, mov, mkv, wmv, flv, webm, m4v, mpg, mpeg), the file should be moved to the vid folder
**Validates: Requirements 2.3**

### Property 6: Archive files are sorted correctly
*For any* file with an archive extension (zip, rar, 7z, tar, gz, bz2, xz, iso), the file should be moved to the arc folder
**Validates: Requirements 2.4**

### Property 7: Miscellaneous files are sorted correctly
*For any* file with a non-standard extension (not image, video, or archive), the file should be moved to the msk folder
**Validates: Requirements 2.5**

### Property 8: Recursive traversal finds all files
*For any* directory structure with files at various depths, the scanner should find all files regardless of their nesting level
**Validates: Requirements 3.1**

### Property 9: Filename preservation
*For any* file being moved (excluding conflict resolution cases), the basename of the file should remain unchanged after the move operation
**Validates: Requirements 3.3**

### Property 10: Statistics accuracy
*For any* sorting operation, the sum of displayed category counts should equal the total number of files moved, and each category count should match the actual number of files in that category folder
**Validates: Requirements 4.1, 4.2**

### Property 11: Empty directories are removed
*For any* directory structure after sorting, when cleanup is selected, all empty directories (except category folders) should be removed
**Validates: Requirements 5.2**

### Property 12: Directory preservation when cleanup declined
*For any* directory structure after sorting, when cleanup is declined, the directory structure should remain unchanged
**Validates: Requirements 5.3**

### Property 13: Case-insensitive classification
*For any* file extension in any case combination (uppercase, lowercase, mixed), the classification should be the same as the lowercase version
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 14: No file overwriting
*For any* file being moved to a destination where a file with the same name exists, the original file at the destination should remain unchanged and the incoming file should be renamed
**Validates: Requirements 7.1**

### Property 15: Conflict resolution preserves extensions
*For any* file renamed due to conflict, the file extension should remain unchanged from the original
**Validates: Requirements 7.2**

### Property 16: Unique names for all conflicts
*For any* set of files with identical names being moved to the same destination, each file should receive a unique final name
**Validates: Requirements 7.3**

### Property 17: Operation logs display file and category
*For any* file being processed, the operation log should contain both the filename and the destination category
**Validates: Requirements 9.1**

### Property 18: Consistent category formatting
*For any* two files of the same category, their operation log messages should have consistent formatting and color coding
**Validates: Requirements 9.2**

### Property 19: Error logs are visually distinct
*For any* error during file operations, the error log should have different styling than normal operation logs
**Validates: Requirements 9.3**

### Property 20: Scan completion displays file count
*For any* directory scan operation, after completion, the displayed message should contain the total number of files found
**Validates: Requirements 9.4**

### Property 21: Progress bar uses ASCII block characters
*For any* progress bar display, the output should contain the block characters █ and ░
**Validates: Requirements 10.1**

### Property 22: Progress percentage increases monotonically
*For any* sequence of file processing operations, the progress percentage should never decrease
**Validates: Requirements 10.2**

### Property 23: Progress bar includes percentage value
*For any* progress bar display, the output should contain a numeric percentage value
**Validates: Requirements 10.3**

### Property 24: Progress completes at 100%
*For any* sorting operation, after all files are processed, the progress bar should show 100% before statistics are displayed
**Validates: Requirements 10.4**

### Property 25: Dry-run preserves file system
*For any* directory, running in dry-run mode should result in no files being moved or modified
**Validates: Requirements 11.1**

### Property 26: Dry-run displays operation logs
*For any* file that would be moved in normal mode, dry-run mode should display an operation log for that file
**Validates: Requirements 11.2**

### Property 27: Dry-run displays accurate statistics
*For any* directory, the statistics displayed in dry-run mode should match what would have been moved in normal mode
**Validates: Requirements 11.3**

### Property 28: Dry-run mode is clearly indicated
*For any* dry-run execution, the output should contain clear indicators at the start and end that no changes were made
**Validates: Requirements 11.4**

### Property 29: Dry-run skips cleanup prompt
*For any* dry-run execution, the cleanup prompt should not be displayed
**Validates: Requirements 11.5**

### Property 30: Command-line path argument is used
*For any* valid path provided as a command-line argument, that path should be used as the source directory without prompting
**Validates: Requirements 12.1**

### Property 31: Missing path triggers interactive prompt
*For any* invocation without a path argument, an interactive prompt should be displayed
**Validates: Requirements 12.2**

### Property 32: Dry-run flag works with path argument
*For any* valid path, invoking with both the path and dry-run flag should perform a dry-run on that path
**Validates: Requirements 12.3**

### Property 33: Invalid command-line path shows error
*For any* invalid path provided as a command-line argument, an error message should be displayed and the program should exit
**Validates: Requirements 12.4**

## Error Handling

### Path Validation Errors
- **Invalid path format**: Display error message with Rich styling and re-prompt
- **Non-existent path**: Display error message indicating path doesn't exist and re-prompt
- **Permission denied**: Display error message about insufficient permissions and exit gracefully

### File Operation Errors
- **Permission denied during move**: Log error, skip file, continue with remaining files
- **Disk full**: Display error message and halt operation to prevent data loss
- **File locked by another process**: Log warning, skip file, continue with remaining files

### Unexpected Errors
- **Unhandled exceptions**: Catch at top level, display user-friendly error message, log full stack trace for debugging

### Error Display Strategy
All errors should be displayed using Rich's error styling (typically red/bold) to ensure visibility. Critical errors that halt execution should be clearly distinguished from warnings that allow continuation.

## Testing Strategy

### Unit Testing
The application will use pytest as the testing framework. Unit tests will cover:

- **Path validation logic**: Test valid and invalid path formats
- **File classification**: Test extension mapping for all supported types
- **Conflict resolution**: Test unique filename generation
- **Statistics tracking**: Test counter increments and totals
- **Empty directory detection**: Test identification of empty vs non-empty directories

### Property-Based Testing
The application will use Hypothesis for property-based testing. Each property-based test will run a minimum of 100 iterations to ensure thorough coverage.

Property-based tests will verify:

- **Classification properties**: Generate random filenames with various extensions and verify correct categorization
- **Filename preservation**: Generate random file structures and verify basenames remain unchanged
- **Statistics accuracy**: Generate random file sets and verify counts match actual results
- **Conflict resolution**: Generate files with duplicate names and verify uniqueness
- **Case insensitivity**: Generate extensions in random cases and verify consistent classification
- **Recursive traversal**: Generate directory trees of random depth and verify all files are found

Each property-based test must be tagged with a comment explicitly referencing the correctness property from this design document using the format: `# Feature: file-sorter-cli, Property {number}: {property_text}`

### Integration Testing
Integration tests will verify end-to-end workflows:

- Complete sorting operation from path input to statistics display
- Cleanup operation with various directory structures
- Error recovery scenarios

### Test Data Strategy
- Use temporary directories for all file system tests
- Generate test files with appropriate extensions but minimal content
- Clean up all test artifacts after test completion
- Use pytest fixtures for common test setup

## Implementation Notes

### Windows-Specific Considerations
- Use `pathlib.Path` for cross-platform path handling
- Handle Windows path length limitations (MAX_PATH)
- Respect Windows file system case-insensitivity
- Handle Windows-specific path formats (UNC paths, drive letters)

### Performance Considerations
- Use batch operations where possible to minimize file system calls
- Display progress for large directories to provide user feedback
- Consider memory usage when scanning very large directory structures
- Update progress bar efficiently without excessive terminal redraws

### Rich Library Integration
- Use `rich.prompt.Prompt` for user input
- Use `rich.console.Console` for all output with appropriate styling
- Use `rich.table.Table` for statistics display
- Use `rich.panel.Panel` for dry-run mode banners
- Use color coding: green for images, blue for videos, yellow for archives, white for misc
- Use red/bold styling for errors

### ASCII Progress Bar Implementation
- Format: `[██████████░░░░░░░░░░] 50%`
- Use █ (U+2588) for completed portions
- Use ░ (U+2591) for remaining portions
- Update in-place using carriage return (`\r`) for smooth animation
- Bar width should be fixed (e.g., 20 characters) with percentage displayed after

### Command-Line Interface
- Use `argparse` or `click` for argument parsing
- Support positional path argument: `sik sort <path>`
- Support `--dry` or `--dry-run` flag for simulation mode
- Provide `--help` for usage information

### Dry-Run Mode Implementation
- Set a global or passed flag to indicate dry-run mode
- Skip all file system modification operations (move, delete)
- Log all operations that would be performed
- Display prominent banner at start: "DRY RUN MODE - No files will be modified"
- Display confirmation at end: "DRY RUN COMPLETE - No changes were made"
- Skip cleanup prompt entirely in dry-run mode

### Operation Logging Strategy
- Log each file operation as it happens (not batched)
- Format: `[CATEGORY] filename.ext → /path/to/category/folder`
- Use category-specific colors for visual distinction
- Log conflicts: `[CONFLICT] filename.ext → filename_1.ext`
- Log errors with red styling and error icon
- Display scan summary before sorting begins

### File Conflict Resolution Strategy
Append a numeric suffix before the extension: `filename_1.ext`, `filename_2.ext`, etc.
Continue incrementing until a unique name is found.

