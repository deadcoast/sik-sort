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

- [ ] 3. Implement directory scanner module
  - Create scan_directory() function to recursively traverse directories
  - Implement logic to skip category folders (img, vid, arc, msk) during scanning
  - Return list of all file paths found
  - _Requirements: 3.1_

- [ ] 3.1 Write property test for recursive traversal
  - **Property 8: Recursive traversal finds all files**
  - **Validates: Requirements 3.1**

- [ ] 4. Implement file sorter module with conflict resolution
  - Create SortingStats dataclass to track file counts
  - Implement move_file_with_conflict_resolution() to handle naming conflicts
  - Implement generate_unique_filename() to create unique names (filename_1.ext, filename_2.ext, etc.)
  - Implement sort_files() orchestrator function
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 3.3, 7.1, 7.2, 7.3_

- [ ] 4.1 Write property test for filename preservation
  - **Property 9: Filename preservation**
  - **Validates: Requirements 3.3**

- [ ] 4.2 Write property test for no file overwriting
  - **Property 14: No file overwriting**
  - **Validates: Requirements 7.1**

- [ ] 4.3 Write property test for conflict resolution preserves extensions
  - **Property 15: Conflict resolution preserves extensions**
  - **Validates: Requirements 7.2**

- [ ] 4.4 Write property test for unique names for all conflicts
  - **Property 16: Unique names for all conflicts**
  - **Validates: Requirements 7.3**

- [ ] 5. Implement folder cleaner module
  - Create find_empty_directories() to identify empty folders
  - Implement logic to preserve category folders (img, vid, arc, msk)
  - Create remove_empty_directories() to delete empty folders
  - _Requirements: 5.2, 5.4_

- [ ] 5.1 Write property test for empty directory removal
  - **Property 11: Empty directories are removed**
  - **Validates: Requirements 5.2**

- [ ] 6. Implement CLI module with Rich library
  - Create prompt_for_path() with validation and error handling
  - Implement display_statistics() using Rich tables
  - Create confirm_cleanup() for yes/no prompts
  - Implement show_progress() using Rich progress bars
  - Create display_error() with Rich error styling
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.3, 5.1, 8.1, 8.2, 8.3_

- [ ] 6.1 Write property test for valid paths acceptance
  - **Property 1: Valid paths are accepted**
  - **Validates: Requirements 1.2**

- [ ] 6.2 Write property test for invalid paths rejection
  - **Property 2: Invalid paths are rejected**
  - **Validates: Requirements 1.3**

- [ ] 7. Implement main application flow
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

- [ ] 7.1 Write property test for category folders creation
  - **Property 3: Category folders are created**
  - **Validates: Requirements 2.1**

- [ ] 7.2 Write property test for statistics accuracy
  - **Property 10: Statistics accuracy**
  - **Validates: Requirements 4.1, 4.2**

- [ ] 7.3 Write property test for directory preservation when cleanup declined
  - **Property 12: Directory preservation when cleanup declined**
  - **Validates: Requirements 5.3**

- [ ] 8. Implement property tests for file sorting by category
  - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [ ] 8.1 Write property test for image file sorting
  - **Property 4: Image files are sorted correctly**
  - **Validates: Requirements 2.2**

- [ ] 8.2 Write property test for video file sorting
  - **Property 5: Video files are sorted correctly**
  - **Validates: Requirements 2.3**

- [ ] 8.3 Write property test for archive file sorting
  - **Property 6: Archive files are sorted correctly**
  - **Validates: Requirements 2.4**

- [ ] 8.4 Write property test for miscellaneous file sorting
  - **Property 7: Miscellaneous files are sorted correctly**
  - **Validates: Requirements 2.5**

- [ ] 9. Create package entry point and installation setup
  - Configure pyproject.toml with console_scripts entry point for `sik` command
  - Add package metadata (name, version, description, author)
  - Create README with installation and usage instructions
  - Test installation with `pip install -e .`
  - _Requirements: All_

- [ ] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
