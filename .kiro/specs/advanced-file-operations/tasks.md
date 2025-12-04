# Implementation Plan

## Overview

This implementation plan extends Sik Sort with nine advanced features: undo functionality, filtering options, size-based sorting, date-based sorting, duplicate detection, configuration management, batch operations, archive mode, and report generation. Tasks are organized to build features incrementally, with each feature integrated into the existing modular architecture.

## Tasks

- [x] 1. Create configuration management module





  - Create config.py with Config dataclass and all configuration fields
  - Implement load_config() to read YAML/JSON configuration files
  - Implement create_template_config() to generate template configuration
  - Implement merge_with_cli_args() to merge config with command-line arguments
  - Implement validate_config() to check configuration values
  - Add PyYAML dependency to pyproject.toml
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 12.1, 12.2, 12.3, 12.4_

- [x] 1.1 Write property test for configuration loading


  - **Property 25: Configuration loading**
  - **Validates: Requirements 6.1**

- [x] 1.2 Write property test for configuration completeness


  - **Property 26: Configuration completeness**
  - **Validates: Requirements 6.2**

- [x] 1.3 Write property test for CLI argument precedence


  - **Property 27: CLI argument precedence**
  - **Validates: Requirements 6.3**

- [x] 1.4 Write property test for comprehensive configuration support


  - **Property 51: Comprehensive configuration support**
  - **Validates: Requirements 12.1**

- [x] 1.5 Write property test for custom category names


  - **Property 52: Custom category names**
  - **Validates: Requirements 12.2**

- [x] 1.6 Write property test for custom extension mappings


  - **Property 53: Custom extension mappings**
  - **Validates: Requirements 12.3**

- [x] 1.7 Write property test for auto-cleanup behavior


  - **Property 54: Auto-cleanup behavior**
  - **Validates: Requirements 12.4**

- [x] 2. Implement filter engine module





  - Create filters.py with FilterConfig dataclass
  - Implement apply_filters() to filter file lists based on patterns and extensions
  - Implement matches_pattern() for glob pattern matching
  - Implement matches_extensions() for extension filtering
  - Add support for both include and exclude patterns with correct precedence
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2.1 Write property test for include filter correctness


  - **Property 6: Include filter correctness**
  - **Validates: Requirements 2.1**

- [x] 2.2 Write property test for exclude filter correctness



  - **Property 7: Exclude filter correctness**
  - **Validates: Requirements 2.2**



- [x] 2.3 Write property test for extension filter correctness

  - **Property 8: Extension filter correctness**
  - **Validates: Requirements 2.3**



- [x] 2.4 Write property test for filter precedence

  - **Property 9: Filter precedence**
  - **Validates: Requirements 2.4**

- [x] 2.5 Write property test for filter statistics accuracy



  - **Property 10: Filter statistics accuracy**
  - **Validates: Requirements 2.5**

- [x] 3. Extend scanner module with filtering support





  - Add scan_with_filters() function to scanner.py
  - Integrate FilterConfig into scanning process
  - Return both filtered files and excluded count
  - Update scan_multiple_directories() for batch operations
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 7.1_

- [x] 4. Implement size classifier module





  - Create size_classifier.py with SizeCategory enum and SizeThresholds dataclass
  - Implement classify_by_size() to categorize files by size
  - Implement get_file_size() to retrieve file size in bytes
  - Implement format_size() to convert bytes to human-readable format
  - Support custom size thresholds with defaults (1MB, 100MB)
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 4.1 Write property test for size category folders created


  - **Property 11: Size category folders created**
  - **Validates: Requirements 3.1**

- [x] 4.2 Write property test for custom size thresholds

  - **Property 12: Custom size thresholds respected**
  - **Validates: Requirements 3.2**

- [x] 5. Implement date classifier module





  - Create date_classifier.py with DateMode enum
  - Implement classify_by_date() to categorize files by date
  - Implement get_file_date() to retrieve creation or modification timestamp
  - Implement format_date() to format dates for folder names
  - Support custom date formats with default YYYY-MM
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5.1 Write property test for date folder naming format


  - **Property 15: Date folder naming format**
  - **Validates: Requirements 4.1**

- [x] 5.2 Write property test for creation date usage

  - **Property 16: Creation date used when specified**
  - **Validates: Requirements 4.2**

- [x] 5.3 Write property test for modification date usage

  - **Property 17: Modification date used when specified**
  - **Validates: Requirements 4.3**

- [x] 6. Implement duplicate detector module





  - Create duplicates.py with DuplicateStats dataclass
  - Implement find_duplicates() to identify files with identical content
  - Implement compute_hash() supporting MD5 and SHA256 algorithms
  - Implement calculate_space_saved() to compute space savings
  - Use streaming hash computation for large files
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 6.1 Write property test for hash computation


  - **Property 20: Hash computation for all files**
  - **Validates: Requirements 5.1**

- [x] 6.2 Write property test for duplicate handling


  - **Property 21: Duplicate handling correctness**
  - **Validates: Requirements 5.2**

- [x] 6.3 Write property test for duplicate filename preservation


  - **Property 22: Duplicate filename preservation**
  - **Validates: Requirements 5.3**

- [x] 6.4 Write property test for duplicate statistics


  - **Property 23: Duplicate statistics accuracy**
  - **Validates: Requirements 5.4**

- [x] 6.5 Write property test for hash algorithm selection


  - **Property 24: Hash algorithm selection**
  - **Validates: Requirements 5.5**

- [x] 7. Extend sorter module with new sorting modes





  - Add EnhancedSortingStats dataclass to sorter.py
  - Implement sort_files_with_size() for size-based sorting with hierarchy
  - Implement sort_files_with_date() for date-based sorting with hierarchy
  - Implement sort_files_archive_mode() for archive mode
  - Implement sort_files_with_duplicates() for duplicate detection
  - Update existing sort_files() to record FileOperation objects
  - _Requirements: 3.4, 3.5, 4.5, 4.6, 5.2, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7.1 Write property test for size hierarchy structure


  - **Property 13: Size hierarchy structure**
  - **Validates: Requirements 3.4**


- [ ] 7.2 Write property test for size statistics accuracy
  - **Property 14: Size statistics accuracy**
  - **Validates: Requirements 3.5**



- [x] 7.3 Write property test for date hierarchy structure

  - **Property 18: Date hierarchy structure**
  - **Validates: Requirements 4.5**



- [ ] 7.4 Write property test for date statistics accuracy
  - **Property 19: Date statistics accuracy**

  - **Validates: Requirements 4.6**

- [x] 7.5 Write property test for archive folder naming

  - **Property 33: Archive folder naming**
  - **Validates: Requirements 8.1**


- [ ] 7.6 Write property test for archive flat structure
  - **Property 34: Archive mode flat structure**
  - **Validates: Requirements 8.2**


- [ ] 7.7 Write property test for archive with type hierarchy
  - **Property 35: Archive mode with type hierarchy**
  - **Validates: Requirements 8.3**

- [ ] 7.8 Write property test for archive statistics
  - **Property 36: Archive statistics accuracy**
  - **Validates: Requirements 8.4**

- [ ] 7.9 Write property test for custom date format
  - **Property 37: Custom date format support**
  - **Validates: Requirements 8.5**

- [ ] 8. Implement undo functionality
  - Create undo.py with FileOperation and UndoStats dataclasses
  - Implement create_manifest() to write manifest files as JSON
  - Implement read_manifest() to parse manifest files
  - Implement undo_sort() to restore files from manifest
  - Implement get_latest_manifest() to find most recent manifest
  - Implement validate_manifest() to check manifest integrity
  - Extend operation_logger.py to record operations for manifest
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ] 8.1 Write property test for manifest creation
  - **Property 1: Manifest creation after sort**
  - **Validates: Requirements 1.1**

- [ ] 8.2 Write property test for undo round-trip
  - **Property 2: Undo restores all files (round-trip)**
  - **Validates: Requirements 1.2**

- [ ] 8.3 Write property test for undo progress
  - **Property 3: Undo displays progress**
  - **Validates: Requirements 1.3**

- [ ] 8.4 Write property test for undo statistics
  - **Property 4: Undo statistics accuracy**
  - **Validates: Requirements 1.4**

- [ ] 8.5 Write property test for manifest cleanup
  - **Property 5: Manifest cleanup after undo**
  - **Validates: Requirements 1.6**

- [ ] 9. Implement report generator module
  - Create reporter.py with ReportData dataclass
  - Implement generate_report() to create CSV or JSON reports
  - Implement generate_csv_report() for CSV format
  - Implement generate_json_report() for JSON format
  - Include all required fields: timestamp, counts, operations, errors
  - Support custom report output paths
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [ ] 9.1 Write property test for report file creation
  - **Property 38: Report file creation**
  - **Validates: Requirements 9.1**

- [ ] 9.2 Write property test for CSV report structure
  - **Property 39: CSV report structure**
  - **Validates: Requirements 9.2**

- [ ] 9.3 Write property test for JSON report structure
  - **Property 40: JSON report structure**
  - **Validates: Requirements 9.3**

- [ ] 9.4 Write property test for report completeness
  - **Property 41: Report completeness**
  - **Validates: Requirements 9.5**

- [ ] 9.5 Write property test for report custom path
  - **Property 42: Report custom path**
  - **Validates: Requirements 9.6**

- [ ] 10. Extend CLI module with new commands and options
  - Add parse_undo_command() to cli.py for undo command parsing
  - Add parse_filter_options() for filter command-line options
  - Add display_enhanced_statistics() for enhanced statistics display
  - Add display_batch_progress() for batch operation progress
  - Add confirm_undo() for undo confirmation prompt
  - Update parse_arguments() to support all new command-line options
  - Add config init command support
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 3.5, 4.6, 5.4, 6.5, 7.2, 7.3, 8.4, 9.1_

- [ ] 11. Extend main module with new workflows
  - Update main() to load configuration on startup
  - Add handle_undo_command() for undo workflow
  - Add process_batch() for batch directory processing
  - Add generate_report_if_enabled() for conditional report generation
  - Integrate all new sorting modes with configuration
  - Add config init command handler
  - _Requirements: 6.1, 6.3, 7.1, 7.2, 7.3, 7.4, 7.5, 9.1_

- [ ] 11.1 Write property test for batch processing order
  - **Property 28: Batch processing order**
  - **Validates: Requirements 7.1**

- [ ] 11.2 Write property test for batch progress reporting
  - **Property 29: Batch progress reporting**
  - **Validates: Requirements 7.2**

- [ ] 11.3 Write property test for batch statistics aggregation
  - **Property 30: Batch statistics aggregation**
  - **Validates: Requirements 7.3**

- [ ] 11.4 Write property test for batch error resilience
  - **Property 31: Batch error resilience**
  - **Validates: Requirements 7.4**

- [ ] 11.5 Write property test for batch manifest separation
  - **Property 32: Batch manifest separation**
  - **Validates: Requirements 7.5**

- [ ] 12. Implement feature combination tests
  - Test filters with size-based sorting
  - Test filters with date-based sorting
  - Test filters with archive mode
  - Test filters with duplicate detection
  - Test undo with size-based sorting
  - Test undo with date-based sorting
  - Test undo with archive mode
  - Test undo with duplicate detection
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 11.1, 11.2, 11.3, 11.4_

- [ ] 12.1 Write property test for filters with size sorting
  - **Property 43: Filters applied before size sorting**
  - **Validates: Requirements 10.1**

- [ ] 12.2 Write property test for filters with date sorting
  - **Property 44: Filters applied before date sorting**
  - **Validates: Requirements 10.2**

- [ ] 12.3 Write property test for filters with archive mode
  - **Property 45: Filters applied before archiving**
  - **Validates: Requirements 10.3**

- [ ] 12.4 Write property test for filters with duplicate detection
  - **Property 46: Filters applied before duplicate detection**
  - **Validates: Requirements 10.4**

- [ ] 12.5 Write property test for undo size-based sort
  - **Property 47: Undo size-based sort (round-trip)**
  - **Validates: Requirements 11.1**

- [ ] 12.6 Write property test for undo date-based sort
  - **Property 48: Undo date-based sort (round-trip)**
  - **Validates: Requirements 11.2**

- [ ] 12.7 Write property test for undo archive mode
  - **Property 49: Undo archive mode (round-trip)**
  - **Validates: Requirements 11.3**

- [ ] 12.8 Write property test for undo with duplicates
  - **Property 50: Undo with duplicates (round-trip)**
  - **Validates: Requirements 11.4**

- [ ] 13. Update documentation
  - Update README.md with all new features and command-line options
  - Add configuration file documentation with examples
  - Add undo command documentation
  - Add filtering examples
  - Add size-based and date-based sorting examples
  - Add duplicate detection examples
  - Add batch operation examples
  - Add archive mode examples
  - Add report generation examples
  - Document feature combinations
  - _Requirements: All_

- [ ] 14. Create example configuration files
  - Create example-config.yaml with all options documented
  - Create example-config.json with all options documented
  - Create minimal-config.yaml with common settings
  - Create advanced-config.yaml with all features enabled
  - Place examples in a configs/ directory
  - _Requirements: 6.1, 6.2, 6.5_

- [ ] 15. Final checkpoint - Ensure all tests pass
  - Run all unit tests
  - Run all property-based tests
  - Test all feature combinations
  - Test configuration loading and merging
  - Test undo with all sorting modes
  - Test batch operations
  - Test report generation
  - Ensure all tests pass, ask the user if questions arise.

