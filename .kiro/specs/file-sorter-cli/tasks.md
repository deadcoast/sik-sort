# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create Python package structure with modules: cli, classifier, sorter, scanner, cleaner, main
  - Set up pyproject.toml with dependencies: rich, pytest, hypothesis
  - Create entry point script for `sik` command
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 2. Implement file classifier module





  - Create FileCategory enum with values (IMAGE="img", VIDEO="vid", ARCHIVE="arc", MISC="msk")
  - Define extension mappings for each category
  - Implement classify_file() function with case-insensitive extension matching
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2.1 Write property test for case-insensitive classification


  - **Property 13: Case-insensitive classification**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 3. Implement directory scanner module





  - Create scan_directory() function to recursively traverse directories
  - Implement logic to skip category folders (img, vid, arc, msk) during scanning
  - Return list of all file paths found
  - _Requirements: 3.1_

- [x] 3.1 Write property test for recursive traversal


  - **Property 8: Recursive traversal finds all files**
  - **Validates: Requirements 3.1**

- [x] 4. Implement file sorter module with conflict resolution





  - Create SortingStats dataclass to track file counts
  - Implement move_file_with_conflict_resolution() to handle naming conflicts
  - Implement generate_unique_filename() to create unique names (filename_1.ext, filename_2.ext, etc.)
  - Implement sort_files() orchestrator function
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 3.3, 7.1, 7.2, 7.3_

- [x] 4.1 Write property test for filename preservation


  - **Property 9: Filename preservation**
  - **Validates: Requirements 3.3**

- [x] 4.2 Write property test for no file overwriting


  - **Property 14: No file overwriting**
  - **Validates: Requirements 7.1**

- [x] 4.3 Write property test for conflict resolution preserves extensions


  - **Property 15: Conflict resolution preserves extensions**
  - **Validates: Requirements 7.2**

- [x] 4.4 Write property test for unique names for all conflicts


  - **Property 16: Unique names for all conflicts**
  - **Validates: Requirements 7.3**

- [x] 5. Implement folder cleaner module





  - Create find_empty_directories() to identify empty folders
  - Implement logic to preserve category folders (img, vid, arc, msk)
  - Create remove_empty_directories() to delete empty folders
  - _Requirements: 5.2, 5.4_

- [x] 5.1 Write property test for empty directory removal


  - **Property 11: Empty directories are removed**
  - **Validates: Requirements 5.2**

- [x] 6. Implement CLI module with Rich library





  - Create prompt_for_path() with validation and error handling
  - Implement display_statistics() using Rich tables
  - Create confirm_cleanup() for yes/no prompts
  - Implement show_progress() using Rich progress bars
  - Create display_error() with Rich error styling
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.3, 5.1, 8.1, 8.2, 8.3_

- [x] 6.1 Write property test for valid paths acceptance


  - **Property 1: Valid paths are accepted**
  - **Validates: Requirements 1.2**

- [x] 6.2 Write property test for invalid paths rejection


  - **Property 2: Invalid paths are rejected**
  - **Validates: Requirements 1.3**

- [x] 7. Implement main application flow





  - Create setup_category_folders() to create img, vid, arc, msk folders
  - Implement main() function to orchestrate the complete workflow:
    - Prompt for path
    - Setup category folders
    - Scan directory
    - Sort files with progress display
    - Display statistics
    - Prompt for cleanup
    - Execute cleanup if confirmed
  - Add top-level error handling
  - _Requirements: 1.1, 1.2, 2.1, 4.1, 4.2, 5.1, 5.3_

- [x] 7.1 Write property test for category folders creation


  - **Property 3: Category folders are created**
  - **Validates: Requirements 2.1**

- [x] 7.2 Write property test for statistics accuracy


  - **Property 10: Statistics accuracy**
  - **Validates: Requirements 4.1, 4.2**

- [x] 7.3 Write property test for directory preservation when cleanup declined


  - **Property 12: Directory preservation when cleanup declined**
  - **Validates: Requirements 5.3**

- [x] 8. Implement property tests for file sorting by category





  - _Requirements: 2.2, 2.3, 2.4, 2.5_


- [x] 8.1 Write property test for image file sorting

  - **Property 4: Image files are sorted correctly**
  - **Validates: Requirements 2.2**

- [x] 8.2 Write property test for video file sorting


  - **Property 5: Video files are sorted correctly**
  - **Validates: Requirements 2.3**

- [x] 8.3 Write property test for archive file sorting


  - **Property 6: Archive files are sorted correctly**
  - **Validates: Requirements 2.4**

- [x] 8.4 Write property test for miscellaneous file sorting


  - **Property 7: Miscellaneous files are sorted correctly**
  - **Validates: Requirements 2.5**

- [x] 9. Create package entry point and installation setup




  - Configure pyproject.toml with console_scripts entry point for `sik` command
  - Add package metadata (name, version, description, author)
  - Create README with installation and usage instructions
  - Test installation with `pip install -e .`
  - _Requirements: All_

- [x] 10. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement operation logger module









  - Create operation_logger.py with color-coded logging functions
  - Implement log_file_operation() with category-specific colors (green for images, blue for videos, yellow for archives, white for misc)
  - Implement log_scan_complete() to display file count after scanning
  - Implement log_conflict_resolution() for filename conflicts
  - Implement log_error() with red/bold styling for errors
  - Use Rich Console for all log output
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 11.1 Write property test for operation log contains filename and category


  - **Property 17: Operation logs display file and category**
  - **Validates: Requirements 9.1**

- [x] 11.2 Write property test for consistent category formatting


  - **Property 18: Consistent category formatting**
  - **Validates: Requirements 9.2**

- [x] 11.3 Write property test for error log visual distinction


  - **Property 19: Error logs are visually distinct**
  - **Validates: Requirements 9.3**

- [x] 11.4 Write property test for scan completion displays count


  - **Property 20: Scan completion displays file count**
  - **Validates: Requirements 9.4**

- [x] 12. Implement ASCII progress bar functionality









  - Add display_ascii_progress() function to cli.py
  - Use █ (U+2588) for completed portions and ░ (U+2591) for remaining
  - Format as `[██████████░░░░░░░░░░] 50%` with fixed 20-character bar width
  - Update progress in-place using carriage return for smooth animation
  - Integrate progress bar updates into file sorting loop
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 12.1 Write property test for progress bar uses ASCII characters


  - **Property 21: Progress bar uses ASCII block characters**
  - **Validates: Requirements 10.1**

- [x] 12.2 Write property test for progress percentage monotonicity

  - **Property 22: Progress percentage increases monotonically**
  - **Validates: Requirements 10.2**

- [x] 12.3 Write property test for progress bar includes percentage

  - **Property 23: Progress bar includes percentage value**
  - **Validates: Requirements 10.3**

- [x] 12.4 Write property test for progress completes at 100%

  - **Property 24: Progress completes at 100%**
  - **Validates: Requirements 10.4**

- [x] 13. Implement dry-run mode









  - Add dry_run parameter to sort_files(), move_file_with_conflict_resolution(), and setup_category_folders()
  - Modify file operations to skip actual moves when dry_run=True
  - Create display_dry_run_banner() in cli.py to show prominent start/end banners
  - Update operation logger to indicate simulated operations in dry-run mode
  - Skip cleanup prompt when in dry-run mode
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 13.1 Write property test for dry-run preserves file system


  - **Property 25: Dry-run preserves file system**
  - **Validates: Requirements 11.1**

- [x] 13.2 Write property test for dry-run displays operation logs


  - **Property 26: Dry-run displays operation logs**
  - **Validates: Requirements 11.2**

- [x] 13.3 Write property test for dry-run statistics accuracy


  - **Property 27: Dry-run displays accurate statistics**
  - **Validates: Requirements 11.3**

- [x] 13.4 Write property test for dry-run mode indicators


  - **Property 28: Dry-run mode is clearly indicated**
  - **Validates: Requirements 11.4**

- [x] 13.5 Write property test for dry-run skips cleanup


  - **Property 29: Dry-run skips cleanup prompt**
  - **Validates: Requirements 11.5**

- [x] 14. Implement command-line argument parsing









  - Add parse_arguments() function to cli.py using argparse
  - Support positional path argument: `sik sort <path>`
  - Support `--dry` flag for dry-run mode
  - Add `--help` for usage information
  - Update main() to use parsed arguments instead of always prompting
  - Validate command-line path and show error if invalid
  - Fall back to interactive prompt if no path provided
  - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [x] 14.1 Write property test for command-line path is used


  - **Property 30: Command-line path argument is used**
  - **Validates: Requirements 12.1**

- [x] 14.2 Write property test for missing path triggers prompt

  - **Property 31: Missing path triggers interactive prompt**
  - **Validates: Requirements 12.2**

- [x] 14.3 Write property test for dry-run with path argument

  - **Property 32: Dry-run flag works with path argument**
  - **Validates: Requirements 12.3**

- [x] 14.4 Write property test for invalid command-line path error

  - **Property 33: Invalid command-line path shows error**
  - **Validates: Requirements 12.4**

- [x] 15. Integrate all new features into main workflow









  - Update main() to parse arguments and determine dry-run mode
  - Integrate operation logger calls throughout sorting process
  - Add ASCII progress bar updates during file processing
  - Display dry-run banners when appropriate
  - Update statistics display to indicate dry-run mode
  - Ensure all components work together seamlessly
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 11.1, 11.2, 11.3, 11.4, 11.5, 12.1, 12.2, 12.3, 12.4_

- [x] 16. Update README and documentation









  - Add documentation for new `sik sort <path>` command syntax
  - Document `--dry` flag usage and behavior
  - Add examples showing operation logs and progress bars
  - Update installation instructions if needed
  - _Requirements: All new requirements_

- [x] 17. Final checkpoint - Ensure all tests pass








  - Run all tests including new property tests
  - Verify dry-run mode works correctly
  - Test command-line argument parsing
  - Ensure operation logs and progress bars display correctly
  - Ensure all tests pass, ask the user if questions arise.
