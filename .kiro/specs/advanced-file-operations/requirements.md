# Requirements Document

## Introduction

This specification extends the Sik Sort file organizer with advanced features including undo functionality, filtering options, size-based and date-based sorting, duplicate detection, configuration management, batch operations, archive mode, and report generation. These features integrate seamlessly with the existing modular architecture (CLI, classifier, sorter, scanner, cleaner, operation logger) to provide enterprise-grade file management capabilities while maintaining the application's simplicity and safety-first approach.

## Glossary

- **Sik Sort**: The command-line application that organizes files into categorized folders, invoked via the `sik` command
- **Undo Operation**: The ability to reverse the most recent sort operation by restoring files to their original locations
- **Operation History**: A persistent log of file movements that enables undo functionality
- **Filter Pattern**: A glob-style pattern or file extension used to include or exclude specific files from sorting
- **Size Threshold**: A file size boundary (in bytes, KB, MB, or GB) used to categorize files by size
- **Size Category**: A predefined size range (small, medium, large) for organizing files
- **Date-Based Sorting**: Organization of files based on creation date or modification date into time-period folders
- **Duplicate File**: Two or more files with identical content (determined by hash comparison)
- **Hash**: A cryptographic fingerprint (MD5 or SHA256) used to identify duplicate files
- **Configuration File**: A YAML or JSON file storing user preferences, custom rules, and default settings
- **Batch Operation**: Processing multiple directories in a single command invocation
- **Archive Mode**: A sorting mode that moves files into dated archive folders (e.g., "2024-12", "2024-11")
- **Report**: A structured export of sorting statistics and operations in CSV or JSON format
- **Manifest File**: A JSON file recording all file movements for undo functionality

## Requirements

### Requirement 1

**User Story:** As a user, I want to undo the last sort operation, so that I can recover from mistakes or unwanted changes.

#### Acceptance Criteria

1. WHEN Sik Sort completes a sort operation THEN Sik Sort SHALL create a manifest file recording all file movements with source and destination paths
2. WHEN the user invokes the undo command THEN Sik Sort SHALL read the most recent manifest file and restore all files to their original locations
3. WHEN Sik Sort performs an undo operation THEN Sik Sort SHALL display progress showing files being restored
4. WHEN Sik Sort completes an undo operation THEN Sik Sort SHALL display statistics showing the number of files restored
5. WHEN no manifest file exists THEN Sik Sort SHALL display an error message indicating no operation to undo
6. WHEN Sik Sort successfully completes an undo THEN Sik Sort SHALL delete the manifest file to prevent duplicate undo attempts

### Requirement 2

**User Story:** As a user, I want to filter files by type or pattern, so that I can sort only specific files and leave others untouched.

#### Acceptance Criteria

1. WHEN the user provides an include pattern THEN Sik Sort SHALL process only files matching the pattern
2. WHEN the user provides an exclude pattern THEN Sik Sort SHALL skip files matching the pattern
3. WHEN the user provides file extension filters THEN Sik Sort SHALL process only files with the specified extensions
4. WHEN both include and exclude patterns are provided THEN Sik Sort SHALL apply include first, then exclude from the included set
5. WHEN Sik Sort applies filters THEN Sik Sort SHALL display the number of files excluded by filters in the statistics

### Requirement 3

**User Story:** As a user, I want to organize files by size thresholds, so that I can separate large files from small ones.

#### Acceptance Criteria

1. WHEN the user enables size-based sorting THEN Sik Sort SHALL create size category folders (small, medium, large) in addition to type categories
2. WHEN the user specifies size thresholds THEN Sik Sort SHALL use those thresholds to categorize files
3. WHEN no size thresholds are specified THEN Sik Sort SHALL use default thresholds (small: less than 1MB, medium: 1MB to 100MB, large: greater than 100MB)
4. WHEN Sik Sort sorts by size THEN Sik Sort SHALL organize files into a hierarchy of size then type (e.g., small/img, medium/vid, large/arc)
5. WHEN Sik Sort displays statistics for size-based sorting THEN Sik Sort SHALL show counts and total sizes for each size category

### Requirement 4

**User Story:** As a user, I want to organize files by date, so that I can find files based on when they were created or modified.

#### Acceptance Criteria

1. WHEN the user enables date-based sorting THEN Sik Sort SHALL create date-based folders using YYYY-MM format
2. WHEN the user specifies creation date sorting THEN Sik Sort SHALL use file creation timestamps for categorization
3. WHEN the user specifies modification date sorting THEN Sik Sort SHALL use file modification timestamps for categorization
4. WHEN no date type is specified THEN Sik Sort SHALL default to modification date
5. WHEN Sik Sort sorts by date THEN Sik Sort SHALL organize files into a hierarchy of date then type (e.g., 2024-12/img, 2024-11/vid)
6. WHEN Sik Sort displays statistics for date-based sorting THEN Sik Sort SHALL show file counts grouped by month

### Requirement 5

**User Story:** As a user, I want to detect and handle duplicate files, so that I can save disk space and avoid redundancy.

#### Acceptance Criteria

1. WHEN the user enables duplicate detection THEN Sik Sort SHALL compute hash values for all files to identify duplicates
2. WHEN Sik Sort identifies duplicate files THEN Sik Sort SHALL create a duplicates folder and move all but the first instance there
3. WHEN Sik Sort moves duplicate files THEN Sik Sort SHALL preserve the original filename and add a suffix indicating it is a duplicate
4. WHEN Sik Sort completes duplicate detection THEN Sik Sort SHALL display statistics showing the number of duplicates found and space saved
5. WHEN the user specifies a hash algorithm THEN Sik Sort SHALL use that algorithm (MD5 or SHA256)
6. WHEN no hash algorithm is specified THEN Sik Sort SHALL default to MD5 for performance

### Requirement 6

**User Story:** As a user, I want to save my preferences in a configuration file, so that I don't have to specify the same options repeatedly.

#### Acceptance Criteria

1. WHEN the user creates a configuration file THEN Sik Sort SHALL read settings from the file on startup
2. WHEN Sik Sort reads a configuration file THEN Sik Sort SHALL support settings for default paths, filters, size thresholds, date sorting preferences, and duplicate detection options
3. WHEN command-line arguments conflict with configuration file settings THEN Sik Sort SHALL prioritize command-line arguments
4. WHEN no configuration file exists THEN Sik Sort SHALL use built-in default settings
5. WHEN the user invokes a config command THEN Sik Sort SHALL create a template configuration file with documented options
6. WHEN Sik Sort reads a configuration file with invalid syntax THEN Sik Sort SHALL display an error message and use default settings

### Requirement 7

**User Story:** As a user, I want to process multiple directories in one command, so that I can efficiently organize multiple locations.

#### Acceptance Criteria

1. WHEN the user provides multiple directory paths THEN Sik Sort SHALL process each directory sequentially
2. WHEN Sik Sort processes multiple directories THEN Sik Sort SHALL display progress for each directory separately
3. WHEN Sik Sort completes batch operations THEN Sik Sort SHALL display combined statistics for all directories
4. WHEN an error occurs in one directory THEN Sik Sort SHALL log the error and continue processing remaining directories
5. WHEN the user enables batch mode with undo THEN Sik Sort SHALL create separate manifest files for each directory

### Requirement 8

**User Story:** As a user, I want to use archive mode to organize files into dated folders, so that I can maintain a chronological archive.

#### Acceptance Criteria

1. WHEN the user enables archive mode THEN Sik Sort SHALL create folders named with YYYY-MM format based on file modification dates
2. WHEN Sik Sort runs in archive mode THEN Sik Sort SHALL move files into the appropriate dated folder without type categorization
3. WHEN the user combines archive mode with type categorization THEN Sik Sort SHALL create a hierarchy of date then type (e.g., 2024-12/img)
4. WHEN Sik Sort displays statistics in archive mode THEN Sik Sort SHALL show file counts grouped by month
5. WHEN the user specifies a custom date format THEN Sik Sort SHALL use that format for folder names

### Requirement 9

**User Story:** As a user, I want to export sorting statistics to a file, so that I can analyze operations and maintain records.

#### Acceptance Criteria

1. WHEN the user enables report generation THEN Sik Sort SHALL export statistics to a file after sorting completes
2. WHEN the user specifies CSV format THEN Sik Sort SHALL create a CSV file with columns for filename, category, size, date, and destination
3. WHEN the user specifies JSON format THEN Sik Sort SHALL create a JSON file with structured operation data
4. WHEN no format is specified THEN Sik Sort SHALL default to JSON format
5. WHEN Sik Sort generates a report THEN Sik Sort SHALL include timestamp, total files processed, category counts, and any errors encountered
6. WHEN the user specifies a report output path THEN Sik Sort SHALL save the report to that location

### Requirement 10

**User Story:** As a user, I want filtering to work with all sorting modes, so that I can combine filters with size, date, or archive sorting.

#### Acceptance Criteria

1. WHEN the user combines filters with size-based sorting THEN Sik Sort SHALL apply filters before size categorization
2. WHEN the user combines filters with date-based sorting THEN Sik Sort SHALL apply filters before date categorization
3. WHEN the user combines filters with archive mode THEN Sik Sort SHALL apply filters before archiving
4. WHEN the user combines filters with duplicate detection THEN Sik Sort SHALL only check for duplicates among filtered files

### Requirement 11

**User Story:** As a user, I want undo to work with all sorting modes, so that I can reverse any type of sort operation.

#### Acceptance Criteria

1. WHEN the user undoes a size-based sort THEN Sik Sort SHALL restore files from size category folders to their original locations
2. WHEN the user undoes a date-based sort THEN Sik Sort SHALL restore files from date folders to their original locations
3. WHEN the user undoes an archive mode sort THEN Sik Sort SHALL restore files from archive folders to their original locations
4. WHEN the user undoes a sort with duplicate detection THEN Sik Sort SHALL restore duplicate files to their original locations

### Requirement 12

**User Story:** As a user, I want configuration to support all advanced features, so that I can set defaults for all options.

#### Acceptance Criteria

1. WHEN Sik Sort reads configuration THEN Sik Sort SHALL support settings for undo enabled/disabled, filter patterns, size thresholds, date sorting mode, duplicate detection, archive mode, and report generation
2. WHEN the user specifies custom category names in configuration THEN Sik Sort SHALL use those names instead of default (img, vid, arc, msk)
3. WHEN the user specifies custom extension mappings in configuration THEN Sik Sort SHALL use those mappings for file classification
4. WHEN the user enables auto-cleanup in configuration THEN Sik Sort SHALL skip the cleanup prompt and automatically remove empty directories

### Requirement 13

**User Story:** As a developer, I want the new features to integrate with existing modules, so that the codebase remains maintainable and consistent.

#### Acceptance Criteria

1. WHEN implementing undo functionality THEN the implementation SHALL extend the operation_logger module to record movements
2. WHEN implementing filtering THEN the implementation SHALL extend the scanner module to apply filters during traversal
3. WHEN implementing size-based sorting THEN the implementation SHALL extend the classifier module to include size classification
4. WHEN implementing date-based sorting THEN the implementation SHALL extend the classifier module to include date classification
5. WHEN implementing duplicate detection THEN the implementation SHALL create a new duplicates module that integrates with the sorter
6. WHEN implementing configuration THEN the implementation SHALL create a new config module that provides settings to all other modules
7. WHEN implementing batch operations THEN the implementation SHALL extend the main module to iterate over multiple paths
8. WHEN implementing archive mode THEN the implementation SHALL extend the sorter module to support date-based folder creation
9. WHEN implementing report generation THEN the implementation SHALL create a new reporter module that consumes sorting statistics
