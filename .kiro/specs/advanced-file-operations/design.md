# Design Document: Advanced File Operations for Sik Sort

## Overview

This design extends the Sik Sort file organizer with nine advanced features: undo functionality, filtering options, size-based sorting, date-based sorting, duplicate detection, configuration management, batch operations, archive mode, and report generation. The design maintains the existing modular architecture and integrates new capabilities through extension of existing modules and addition of new specialized modules. All features work independently and can be combined, with configuration file support for setting defaults.

## Architecture

The enhanced application extends the existing three-layer architecture with new modules that integrate at each layer:

```
┌─────────────────────────────────────────────────────────┐
│              CLI Layer (Rich)                           │
│  - Existing: Prompts, Statistics, Progress             │
│  - New: Undo command, Filter options, Config command   │
│  - New: Batch progress, Report confirmation            │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│           Business Logic Layer                          │
│  - Existing: Classifier, Sorter, Stats Tracker         │
│  - New: Config Manager, Duplicate Detector             │
│  - New: Size Classifier, Date Classifier               │
│  - New: Filter Engine, Report Generator                │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│           File System Layer                             │
│  - Existing: Scanner, Mover, Cleaner                   │
│  - New: Manifest Manager (undo), Hash Calculator       │
│  - New: Filtered Scanner, Batch Processor              │
└─────────────────────────────────────────────────────────┘
```

### Integration Strategy

Each new feature integrates with existing modules:

1. **Undo**: Extends `operation_logger` to write manifest files, adds new `undo` module
2. **Filtering**: Extends `scanner` with filter application logic
3. **Size Sorting**: Extends `classifier` with size-based classification
4. **Date Sorting**: Extends `classifier` with date-based classification
5. **Duplicates**: New `duplicates` module that works with `sorter`
6. **Configuration**: New `config` module that provides settings to all modules
7. **Batch**: Extends `main` to iterate over multiple directories
8. **Archive**: Extends `sorter` to support date-based folder structures
9. **Reports**: New `reporter` module that consumes `SortingStats`

## Components and Interfaces

### 1. Undo Module (`undo.py`)

**Responsibilities:**
- Create manifest files recording file movements
- Read manifest files and restore files to original locations
- Validate manifest integrity before undo
- Clean up manifest files after successful undo

**Key Functions:**
- `create_manifest(operations: list[FileOperation], manifest_path: Path) -> None`: Writes manifest file with all file movements
- `read_manifest(manifest_path: Path) -> list[FileOperation]`: Reads and parses manifest file
- `undo_sort(manifest_path: Path, progress_callback: Callable) -> UndoStats`: Restores files from manifest
- `get_latest_manifest(directory: Path) -> Path | None`: Finds most recent manifest file
- `validate_manifest(manifest: list[FileOperation]) -> bool`: Checks if all destination files exist

**Data Types:**
```python
@dataclass
class FileOperation:
    source: Path
    destination: Path
    timestamp: datetime
    category: str
    size: int

@dataclass
class UndoStats:
    files_restored: int
    errors: int
    duration: float
```

### 2. Filter Engine (`filters.py`)

**Responsibilities:**
- Apply include/exclude patterns to file lists
- Support glob patterns and extension filters
- Track filtered file counts for statistics

**Key Functions:**
- `apply_filters(files: list[Path], config: FilterConfig) -> tuple[list[Path], int]`: Returns filtered files and excluded count
- `matches_pattern(file_path: Path, pattern: str) -> bool`: Checks if file matches glob pattern
- `matches_extensions(file_path: Path, extensions: set[str]) -> bool`: Checks if file has specified extension

**Data Types:**
```python
@dataclass
class FilterConfig:
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    include_extensions: set[str] = field(default_factory=set)
    exclude_extensions: set[str] = field(default_factory=set)
```

### 3. Size Classifier (`size_classifier.py`)

**Responsibilities:**
- Categorize files by size thresholds
- Support custom size thresholds
- Provide default size categories (small, medium, large)

**Key Functions:**
- `classify_by_size(file_path: Path, thresholds: SizeThresholds) -> SizeCategory`: Returns size category for file
- `get_file_size(file_path: Path) -> int`: Returns file size in bytes
- `format_size(bytes: int) -> str`: Converts bytes to human-readable format

**Data Types:**
```python
class SizeCategory(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

@dataclass
class SizeThresholds:
    small_max: int = 1_048_576  # 1 MB
    medium_max: int = 104_857_600  # 100 MB
```

### 4. Date Classifier (`date_classifier.py`)

**Responsibilities:**
- Categorize files by creation or modification date
- Format dates for folder names
- Support custom date formats

**Key Functions:**
- `classify_by_date(file_path: Path, use_creation: bool = False) -> str`: Returns date string (YYYY-MM) for file
- `get_file_date(file_path: Path, use_creation: bool) -> datetime`: Returns file timestamp
- `format_date(date: datetime, format_string: str) -> str`: Formats date for folder name

**Data Types:**
```python
class DateMode(Enum):
    CREATION = "creation"
    MODIFICATION = "modification"
```

### 5. Duplicate Detector (`duplicates.py`)

**Responsibilities:**
- Compute file hashes for duplicate detection
- Identify duplicate files
- Track space savings from duplicate removal

**Key Functions:**
- `find_duplicates(files: list[Path], algorithm: str = "md5") -> dict[str, list[Path]]`: Returns hash-to-files mapping
- `compute_hash(file_path: Path, algorithm: str) -> str`: Computes file hash
- `calculate_space_saved(duplicates: dict[str, list[Path]]) -> int`: Returns bytes saved by removing duplicates

**Data Types:**
```python
@dataclass
class DuplicateStats:
    total_duplicates: int
    unique_files: int
    space_saved: int
    duplicate_groups: int
```

### 6. Configuration Manager (`config.py`)

**Responsibilities:**
- Load configuration from YAML/JSON files
- Provide default settings
- Merge command-line arguments with config file settings
- Validate configuration values

**Key Functions:**
- `load_config(config_path: Path | None) -> Config`: Loads and parses configuration file
- `create_template_config(output_path: Path) -> None`: Creates template configuration file
- `merge_with_cli_args(config: Config, cli_args: dict) -> Config`: Merges config with command-line arguments
- `validate_config(config: Config) -> list[str]`: Returns list of validation errors

**Data Types:**
```python
@dataclass
class Config:
    # General settings
    default_path: Path | None = None
    auto_cleanup: bool = False
    
    # Undo settings
    undo_enabled: bool = True
    manifest_dir: Path = Path(".sik_manifests")
    
    # Filter settings
    filters: FilterConfig = field(default_factory=FilterConfig)
    
    # Size sorting settings
    size_sorting_enabled: bool = False
    size_thresholds: SizeThresholds = field(default_factory=SizeThresholds)
    
    # Date sorting settings
    date_sorting_enabled: bool = False
    date_mode: DateMode = DateMode.MODIFICATION
    date_format: str = "%Y-%m"
    
    # Duplicate detection settings
    duplicate_detection_enabled: bool = False
    hash_algorithm: str = "md5"
    
    # Archive mode settings
    archive_mode: bool = False
    
    # Report settings
    report_enabled: bool = False
    report_format: str = "json"
    report_path: Path | None = None
    
    # Custom categories
    custom_categories: dict[str, str] = field(default_factory=dict)
    custom_extensions: dict[str, list[str]] = field(default_factory=dict)
```

### 7. Report Generator (`reporter.py`)

**Responsibilities:**
- Export sorting statistics to CSV or JSON
- Include operation metadata and errors
- Support custom report paths

**Key Functions:**
- `generate_report(stats: SortingStats, operations: list[FileOperation], format: str, output_path: Path) -> None`: Creates report file
- `generate_csv_report(data: dict, output_path: Path) -> None`: Writes CSV format report
- `generate_json_report(data: dict, output_path: Path) -> None`: Writes JSON format report

**Data Types:**
```python
@dataclass
class ReportData:
    timestamp: datetime
    source_path: Path
    total_files: int
    category_counts: dict[str, int]
    operations: list[FileOperation]
    errors: list[str]
    duration: float
    filters_applied: FilterConfig | None
    duplicates_found: int | None
```

### 8. Enhanced Scanner (`scanner.py` - extended)

**Responsibilities:**
- Existing: Recursive directory traversal
- New: Apply filters during scanning
- New: Support batch directory processing

**New Functions:**
- `scan_with_filters(path: Path, exclude_dirs: set[str], filters: FilterConfig) -> tuple[list[Path], int]`: Returns filtered files and excluded count
- `scan_multiple_directories(paths: list[Path], exclude_dirs: set[str], filters: FilterConfig) -> dict[Path, list[Path]]`: Returns files grouped by source directory

### 9. Enhanced Sorter (`sorter.py` - extended)

**Responsibilities:**
- Existing: Coordinate sorting, track statistics, handle conflicts
- New: Support size-based folder hierarchy
- New: Support date-based folder hierarchy
- New: Support archive mode
- New: Record operations for undo
- New: Handle duplicate detection

**New Functions:**
- `sort_files_with_size(source_path: Path, config: Config, ...) -> EnhancedSortingStats`: Sorts with size categorization
- `sort_files_with_date(source_path: Path, config: Config, ...) -> EnhancedSortingStats`: Sorts with date categorization
- `sort_files_archive_mode(source_path: Path, config: Config, ...) -> EnhancedSortingStats`: Sorts into dated archives
- `sort_files_with_duplicates(source_path: Path, config: Config, ...) -> EnhancedSortingStats`: Sorts with duplicate detection

**Enhanced Data Types:**
```python
@dataclass
class EnhancedSortingStats:
    # Existing fields
    total_files: int = 0
    img_count: int = 0
    vid_count: int = 0
    arc_count: int = 0
    msk_count: int = 0
    
    # New fields
    excluded_by_filters: int = 0
    duplicates_found: int = 0
    space_saved: int = 0
    size_categories: dict[str, int] = field(default_factory=dict)
    date_categories: dict[str, int] = field(default_factory=dict)
    operations: list[FileOperation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

### 10. Enhanced CLI (`cli.py` - extended)

**Responsibilities:**
- Existing: User interaction, statistics display, progress bars
- New: Undo command parsing
- New: Filter option parsing
- New: Config command
- New: Batch operation progress
- New: Enhanced statistics display

**New Functions:**
- `parse_undo_command() -> Path | None`: Parses undo command and returns directory
- `parse_filter_options() -> FilterConfig`: Parses filter command-line options
- `display_enhanced_statistics(stats: EnhancedSortingStats, config: Config) -> None`: Shows enhanced statistics with new features
- `display_batch_progress(current: int, total: int, directory: Path) -> None`: Shows progress for batch operations
- `confirm_undo() -> bool`: Prompts user to confirm undo operation

### 11. Enhanced Main (`main.py` - extended)

**Responsibilities:**
- Existing: Application entry point, workflow orchestration
- New: Load configuration
- New: Handle undo command
- New: Process batch operations
- New: Generate reports

**New Functions:**
- `main_with_config() -> None`: Main flow with configuration support
- `handle_undo_command(directory: Path) -> None`: Executes undo operation
- `process_batch(directories: list[Path], config: Config) -> None`: Processes multiple directories
- `generate_report_if_enabled(stats: EnhancedSortingStats, config: Config) -> None`: Creates report if configured

## Data Models

### FileOperation
```python
@dataclass
class FileOperation:
    source: Path
    destination: Path
    timestamp: datetime
    category: str
    size: int
    hash: str | None = None
```

### FilterConfig
```python
@dataclass
class FilterConfig:
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    include_extensions: set[str] = field(default_factory=set)
    exclude_extensions: set[str] = field(default_factory=set)
```

### SizeCategory and SizeThresholds
```python
class SizeCategory(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

@dataclass
class SizeThresholds:
    small_max: int = 1_048_576  # 1 MB
    medium_max: int = 104_857_600  # 100 MB
```

### Config
```python
@dataclass
class Config:
    default_path: Path | None = None
    auto_cleanup: bool = False
    undo_enabled: bool = True
    manifest_dir: Path = Path(".sik_manifests")
    filters: FilterConfig = field(default_factory=FilterConfig)
    size_sorting_enabled: bool = False
    size_thresholds: SizeThresholds = field(default_factory=SizeThresholds)
    date_sorting_enabled: bool = False
    date_mode: DateMode = DateMode.MODIFICATION
    date_format: str = "%Y-%m"
    duplicate_detection_enabled: bool = False
    hash_algorithm: str = "md5"
    archive_mode: bool = False
    report_enabled: bool = False
    report_format: str = "json"
    report_path: Path | None = None
    custom_categories: dict[str, str] = field(default_factory=dict)
    custom_extensions: dict[str, list[str]] = field(default_factory=dict)
```

### EnhancedSortingStats
```python
@dataclass
class EnhancedSortingStats:
    total_files: int = 0
    img_count: int = 0
    vid_count: int = 0
    arc_count: int = 0
    msk_count: int = 0
    excluded_by_filters: int = 0
    duplicates_found: int = 0
    space_saved: int = 0
    size_categories: dict[str, int] = field(default_factory=dict)
    date_categories: dict[str, int] = field(default_factory=dict)
    operations: list[FileOperation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Manifest creation after sort
*For any* sort operation that moves files, a manifest file should be created containing entries for all moved files with their source and destination paths
**Validates: Requirements 1.1**

### Property 2: Undo restores all files (round-trip)
*For any* set of file movements recorded in a manifest, performing an undo operation should restore all files to their original source locations
**Validates: Requirements 1.2**

### Property 3: Undo displays progress
*For any* undo operation, the progress callback should be invoked with monotonically increasing values from 0 to the total number of files
**Validates: Requirements 1.3**

### Property 4: Undo statistics accuracy
*For any* undo operation, the displayed count of restored files should equal the actual number of files moved back to their original locations
**Validates: Requirements 1.4**

### Property 5: Manifest cleanup after undo
*For any* successful undo operation, the manifest file should no longer exist after completion
**Validates: Requirements 1.6**

### Property 6: Include filter correctness
*For any* include pattern and set of files, only files matching the pattern should be included in the processing list
**Validates: Requirements 2.1**

### Property 7: Exclude filter correctness
*For any* exclude pattern and set of files, no files matching the pattern should be included in the processing list
**Validates: Requirements 2.2**

### Property 8: Extension filter correctness
*For any* set of allowed extensions and files, only files with those extensions should be included in the processing list
**Validates: Requirements 2.3**

### Property 9: Filter precedence
*For any* set of files with both include and exclude patterns, the result should equal applying include first, then excluding from that result
**Validates: Requirements 2.4**

### Property 10: Filter statistics accuracy
*For any* filtering operation, the excluded count should equal the total files scanned minus the files included
**Validates: Requirements 2.5**

### Property 11: Size category folders created
*For any* size-based sort operation, all size category folders (small, medium, large) should exist after sorting
**Validates: Requirements 3.1**

### Property 12: Custom size thresholds respected
*For any* file and custom size thresholds, the file should be categorized according to those thresholds
**Validates: Requirements 3.2**

### Property 13: Size hierarchy structure
*For any* file sorted by size, the file's destination path should match the pattern {size_category}/{type_category}
**Validates: Requirements 3.4**

### Property 14: Size statistics accuracy
*For any* size-based sort, the displayed counts and total sizes for each size category should match the actual files in those folders
**Validates: Requirements 3.5**

### Property 15: Date folder naming format
*For any* date-based sort operation, all created date folders should be named in YYYY-MM format
**Validates: Requirements 4.1**

### Property 16: Creation date used when specified
*For any* file sorted with creation date mode, the file should be categorized based on its creation timestamp
**Validates: Requirements 4.2**

### Property 17: Modification date used when specified
*For any* file sorted with modification date mode, the file should be categorized based on its modification timestamp
**Validates: Requirements 4.3**

### Property 18: Date hierarchy structure
*For any* file sorted by date, the file's destination path should match the pattern {date_folder}/{type_category}
**Validates: Requirements 4.5**

### Property 19: Date statistics accuracy
*For any* date-based sort, the displayed counts per month should match the actual files in each date folder
**Validates: Requirements 4.6**

### Property 20: Hash computation for all files
*For any* duplicate detection operation, every file should have a hash value computed
**Validates: Requirements 5.1**

### Property 21: Duplicate handling correctness
*For any* set of files with identical content, only one copy should remain in the original location and all others should be in the duplicates folder
**Validates: Requirements 5.2**

### Property 22: Duplicate filename preservation
*For any* duplicate file moved to the duplicates folder, the filename should contain the original name plus a duplicate suffix
**Validates: Requirements 5.3**

### Property 23: Duplicate statistics accuracy
*For any* duplicate detection operation, the displayed duplicate count and space saved should match the actual duplicates found and their total size
**Validates: Requirements 5.4**

### Property 24: Hash algorithm selection
*For any* specified hash algorithm (MD5 or SHA256), the computed hashes should match that algorithm's output format
**Validates: Requirements 5.5**

### Property 25: Configuration loading
*For any* valid configuration file, all settings in the file should be applied to the application
**Validates: Requirements 6.1**

### Property 26: Configuration completeness
*For any* configuration file with settings for paths, filters, size thresholds, date sorting, and duplicate detection, all these settings should be applied
**Validates: Requirements 6.2**

### Property 27: CLI argument precedence
*For any* setting that appears in both configuration file and command-line arguments, the command-line value should be used
**Validates: Requirements 6.3**

### Property 28: Batch processing order
*For any* list of directories, each directory should be processed in the order provided
**Validates: Requirements 7.1**

### Property 29: Batch progress reporting
*For any* batch operation, progress should be displayed separately for each directory
**Validates: Requirements 7.2**

### Property 30: Batch statistics aggregation
*For any* batch operation, the combined statistics should equal the sum of statistics from all individual directories
**Validates: Requirements 7.3**

### Property 31: Batch error resilience
*For any* batch operation where one directory fails, all remaining directories should still be processed
**Validates: Requirements 7.4**

### Property 32: Batch manifest separation
*For any* batch operation with undo enabled, each directory should have its own separate manifest file
**Validates: Requirements 7.5**

### Property 33: Archive folder naming
*For any* archive mode operation, all created folders should be named in YYYY-MM format based on file dates
**Validates: Requirements 8.1**

### Property 34: Archive mode flat structure
*For any* file sorted in archive mode without type categorization, the file should be directly in the date folder
**Validates: Requirements 8.2**

### Property 35: Archive mode with type hierarchy
*For any* file sorted in archive mode with type categorization, the file's path should match {date_folder}/{type_category}
**Validates: Requirements 8.3**

### Property 36: Archive statistics accuracy
*For any* archive mode operation, the displayed counts per month should match the actual files in each archive folder
**Validates: Requirements 8.4**

### Property 37: Custom date format support
*For any* custom date format specified, archive folders should be named using that format
**Validates: Requirements 8.5**

### Property 38: Report file creation
*For any* sort operation with reporting enabled, a report file should exist after completion
**Validates: Requirements 9.1**

### Property 39: CSV report structure
*For any* CSV report generated, the file should contain columns for filename, category, size, date, and destination with valid data
**Validates: Requirements 9.2**

### Property 40: JSON report structure
*For any* JSON report generated, the file should contain valid JSON with structured operation data
**Validates: Requirements 9.3**

### Property 41: Report completeness
*For any* generated report, it should include timestamp, total files processed, category counts, and any errors encountered
**Validates: Requirements 9.5**

### Property 42: Report custom path
*For any* specified report output path, the report file should be created at that location
**Validates: Requirements 9.6**

### Property 43: Filters applied before size sorting
*For any* operation combining filters and size sorting, only filtered files should be size-categorized
**Validates: Requirements 10.1**

### Property 44: Filters applied before date sorting
*For any* operation combining filters and date sorting, only filtered files should be date-categorized
**Validates: Requirements 10.2**

### Property 45: Filters applied before archiving
*For any* operation combining filters and archive mode, only filtered files should be archived
**Validates: Requirements 10.3**

### Property 46: Filters applied before duplicate detection
*For any* operation combining filters and duplicate detection, only filtered files should be checked for duplicates
**Validates: Requirements 10.4**

### Property 47: Undo size-based sort (round-trip)
*For any* size-based sort operation, performing an undo should restore all files to their original locations regardless of size categorization
**Validates: Requirements 11.1**

### Property 48: Undo date-based sort (round-trip)
*For any* date-based sort operation, performing an undo should restore all files to their original locations regardless of date categorization
**Validates: Requirements 11.2**

### Property 49: Undo archive mode (round-trip)
*For any* archive mode operation, performing an undo should restore all files from archive folders to their original locations
**Validates: Requirements 11.3**

### Property 50: Undo with duplicates (round-trip)
*For any* sort operation with duplicate detection, performing an undo should restore all files including duplicates to their original locations
**Validates: Requirements 11.4**

### Property 51: Comprehensive configuration support
*For any* configuration file with settings for undo, filters, size thresholds, date sorting, duplicate detection, archive mode, and reporting, all settings should be applied
**Validates: Requirements 12.1**

### Property 52: Custom category names
*For any* custom category names specified in configuration, folders should be created with those names instead of defaults
**Validates: Requirements 12.2**

### Property 53: Custom extension mappings
*For any* custom extension mappings in configuration, files should be classified using those mappings
**Validates: Requirements 12.3**

### Property 54: Auto-cleanup behavior
*For any* configuration with auto-cleanup enabled, empty directories should be removed without prompting
**Validates: Requirements 12.4**

## Error Handling

### Undo Operation Errors
- **Manifest file not found**: Display clear error message indicating no operation to undo
- **Manifest file corrupted**: Display error and offer to show manifest contents for manual recovery
- **Destination file missing**: Log warning, skip that file, continue with remaining files
- **Permission denied during restore**: Log error, skip file, continue with remaining files
- **Disk full during undo**: Display error and halt to prevent data loss

### Filter Errors
- **Invalid glob pattern**: Display error message and ignore invalid pattern
- **No files match filters**: Display warning and exit gracefully
- **Filter excludes all files**: Display warning and confirm with user before proceeding

### Size/Date Classification Errors
- **Cannot read file size**: Log warning, classify as miscellaneous
- **Cannot read file timestamp**: Log warning, use current date as fallback
- **Invalid size threshold values**: Display error and use default thresholds

### Duplicate Detection Errors
- **Cannot read file for hashing**: Log warning, skip file, continue with others
- **Hash computation fails**: Log error, treat file as unique
- **Insufficient memory for large files**: Use streaming hash computation

### Configuration Errors
- **Configuration file not found**: Use default settings, log info message
- **Invalid YAML/JSON syntax**: Display error with line number, use default settings
- **Invalid configuration values**: Display warnings for invalid values, use defaults for those settings
- **Missing required fields**: Use default values, log warnings

### Batch Operation Errors
- **One directory fails**: Log error, continue with remaining directories
- **Invalid directory in batch**: Skip invalid directory, log error, continue
- **Manifest creation fails for one directory**: Log error, continue without undo for that directory

### Report Generation Errors
- **Cannot write report file**: Display error with path and permissions info
- **Invalid report format specified**: Display error and use default JSON format
- **Report path is directory**: Display error and use default filename in that directory

## Testing Strategy

### Unit Testing
The application will use pytest as the testing framework. Unit tests will cover:

- **Undo functionality**: Test manifest creation, reading, and file restoration
- **Filter logic**: Test pattern matching, extension filtering, precedence
- **Size classification**: Test threshold boundaries, custom thresholds
- **Date classification**: Test date extraction, formatting, creation vs modification
- **Duplicate detection**: Test hash computation, duplicate identification
- **Configuration loading**: Test YAML/JSON parsing, validation, merging with CLI args
- **Report generation**: Test CSV and JSON formatting, data completeness

### Property-Based Testing
The application will use Hypothesis for property-based testing. Each property-based test will run a minimum of 100 iterations to ensure thorough coverage.

Property-based tests will verify:

- **Undo round-trip**: Generate random file movements, undo, verify restoration
- **Filter correctness**: Generate random file sets and patterns, verify filtering
- **Size categorization**: Generate files of random sizes, verify correct categorization
- **Date categorization**: Generate files with random dates, verify correct categorization
- **Duplicate detection**: Generate files with duplicate content, verify identification
- **Configuration merging**: Generate random configs and CLI args, verify precedence
- **Batch processing**: Generate random directory lists, verify sequential processing
- **Statistics accuracy**: Generate random operations, verify counts match reality

Each property-based test must be tagged with a comment explicitly referencing the correctness property from this design document using the format: `# Feature: advanced-file-operations, Property {number}: {property_text}`

### Integration Testing
Integration tests will verify end-to-end workflows:

- Complete sort with undo operation
- Filtering combined with various sorting modes
- Batch operations with multiple directories
- Configuration file loading and application
- Report generation with various formats

### Test Data Strategy
- Use temporary directories for all file system tests
- Generate test files with controlled sizes and dates
- Create test configuration files with various settings
- Use pytest fixtures for common test setup
- Clean up all test artifacts after test completion

## Implementation Notes

### Manifest File Format
Manifest files will be stored as JSON in a `.sik_manifests` directory:

```json
{
  "version": "1.0",
  "timestamp": "2024-12-03T10:30:00",
  "source_path": "/path/to/source",
  "operations": [
    {
      "source": "/path/to/source/file1.jpg",
      "destination": "/path/to/source/img/file1.jpg",
      "category": "img",
      "size": 1024,
      "hash": "abc123..."
    }
  ]
}
```

### Configuration File Format
Configuration files will support both YAML and JSON formats. Example YAML:

```yaml
# Sik Sort Configuration

# General settings
default_path: ~/Downloads
auto_cleanup: false

# Undo settings
undo_enabled: true
manifest_dir: .sik_manifests

# Filter settings
filters:
  include_patterns:
    - "*.jpg"
    - "*.png"
  exclude_patterns:
    - "*_backup*"
  include_extensions:
    - .pdf
    - .doc
  exclude_extensions:
    - .tmp

# Size sorting settings
size_sorting_enabled: false
size_thresholds:
  small_max: 1048576  # 1 MB
  medium_max: 104857600  # 100 MB

# Date sorting settings
date_sorting_enabled: false
date_mode: modification  # or creation
date_format: "%Y-%m"

# Duplicate detection settings
duplicate_detection_enabled: false
hash_algorithm: md5  # or sha256

# Archive mode settings
archive_mode: false

# Report settings
report_enabled: false
report_format: json  # or csv
report_path: ./reports

# Custom categories (optional)
custom_categories:
  img: images
  vid: videos
  arc: archives
  msk: misc

# Custom extension mappings (optional)
custom_extensions:
  images:
    - .heic
    - .raw
  videos:
    - .mts
```

### Command-Line Interface Extensions

New command-line options:

```bash
# Undo last operation
sik undo [PATH]

# Generate config template
sik config init

# Sort with filters
sik sort PATH --include "*.jpg" --exclude "*_backup*"
sik sort PATH --ext .pdf,.doc

# Sort by size
sik sort PATH --by-size --size-small 1MB --size-medium 100MB

# Sort by date
sik sort PATH --by-date --date-mode creation --date-format "%Y-%m-%d"

# Detect duplicates
sik sort PATH --find-duplicates --hash sha256

# Batch operations
sik sort PATH1 PATH2 PATH3

# Archive mode
sik sort PATH --archive --date-format "%Y-%m"

# Generate report
sik sort PATH --report --report-format csv --report-path ./report.csv

# Combine features
sik sort PATH --include "*.jpg" --by-size --find-duplicates --report

# Use configuration file
sik sort PATH --config ./my-config.yaml
```

### Performance Considerations

- **Duplicate detection**: Use streaming hash computation for large files to avoid memory issues
- **Batch operations**: Process directories sequentially to avoid overwhelming file system
- **Filtering**: Apply filters during scanning to avoid processing excluded files
- **Progress reporting**: Update progress efficiently without excessive terminal redraws
- **Manifest files**: Use JSON for fast parsing and writing
- **Configuration**: Cache parsed configuration to avoid repeated file reads

### Module Integration Strategy

1. **Undo**: Extend `operation_logger.py` to write manifest entries, create new `undo.py` module
2. **Filtering**: Extend `scanner.py` with filter application logic, create `filters.py` for pattern matching
3. **Size sorting**: Create `size_classifier.py`, integrate with `sorter.py` for hierarchy creation
4. **Date sorting**: Create `date_classifier.py`, integrate with `sorter.py` for hierarchy creation
5. **Duplicates**: Create `duplicates.py`, integrate with `sorter.py` for duplicate handling
6. **Configuration**: Create `config.py`, integrate with `main.py` for startup loading
7. **Batch**: Extend `main.py` with batch processing loop
8. **Archive**: Extend `sorter.py` with archive mode logic
9. **Reports**: Create `reporter.py`, integrate with `main.py` for post-sort reporting

### Backward Compatibility

All new features are opt-in and do not affect existing functionality:

- Default behavior remains unchanged (basic type-based sorting)
- Existing command-line syntax continues to work
- No breaking changes to existing modules
- New features can be enabled individually or in combination
- Configuration file is optional

### Safety Considerations

- **Undo safety**: Validate manifest before undo, check destination files exist
- **Filter safety**: Warn if filters exclude all files
- **Duplicate safety**: Never delete original file, only move duplicates
- **Batch safety**: Continue processing even if one directory fails
- **Configuration safety**: Validate all config values, use defaults for invalid values
- **Manifest safety**: Store manifests in hidden directory to avoid accidental deletion

