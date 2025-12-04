# Requirements Document

## Introduction

Sik Sort is a command-line utility for Windows that organizes files from a specified directory into categorized folders based on file type. The system recursively processes all files in the source directory and its subdirectories, moving them into four predefined categories: images, videos, archives, and miscellaneous files. After sorting, the system provides statistics and offers to clean up empty directories left behind. The application is invoked using the `sik` command and uses Python's Rich library for an enhanced terminal interface.

## Glossary

- **Sik Sort**: The command-line application that organizes files into categorized folders, invoked via the `sik` command
- **Rich Library**: Python library used for creating rich text and beautiful formatting in the terminal interface
- **Source Path**: The directory path provided by the user containing files to be sorted
- **Target Categories**: Four predefined folders (img, vid, arc, msk) where files are organized
- **img**: Target folder for image files
- **vid**: Target folder for video files
- **arc**: Target folder for archive and compression files
- **msk**: Target folder for miscellaneous files that don't fit other categories
- **Recursive Processing**: Processing files in the source directory and all its subdirectories
- **Empty Folder Cleanup**: Removal of directories that contain no files after sorting
- **Dry Run**: A simulation mode where Sik Sort shows what operations would be performed without actually moving or modifying files
- **Operation Log**: Real-time display of file operations being performed during sorting
- **ASCII Progress Bar**: A text-based progress indicator using block characters (█ and ░) to show completion percentage

## Requirements

### Requirement 1

**User Story:** As a user, I want to specify a source directory path, so that the system knows which files to organize.

#### Acceptance Criteria

1. WHEN Sik Sort starts THEN Sik Sort SHALL prompt the user to enter a source path
2. WHEN the user provides a valid directory path THEN Sik Sort SHALL accept the path and proceed with sorting
3. WHEN the user provides an invalid directory path THEN Sik Sort SHALL display an error message and prompt again
4. WHEN the user provides a path that does not exist THEN Sik Sort SHALL display an error message and prompt again

### Requirement 2

**User Story:** As a user, I want files to be sorted into appropriate category folders, so that I can easily locate files by type.

#### Acceptance Criteria

1. WHEN Sik Sort processes files THEN Sik Sort SHALL create four target folders (img, vid, arc, msk) in the source path if they do not exist
2. WHEN Sik Sort encounters an image file THEN Sik Sort SHALL move the file to the img folder
3. WHEN Sik Sort encounters a video file THEN Sik Sort SHALL move the file to the vid folder
4. WHEN Sik Sort encounters an archive file THEN Sik Sort SHALL move the file to the arc folder
5. WHEN Sik Sort encounters any other file type THEN Sik Sort SHALL move the file to the msk folder

### Requirement 3

**User Story:** As a user, I want the system to process all subdirectories recursively, so that all files are organized regardless of their depth in the directory structure.

#### Acceptance Criteria

1. WHEN Sik Sort begins sorting THEN Sik Sort SHALL traverse all subdirectories within the source path recursively
2. WHEN Sik Sort encounters a file in any subdirectory THEN Sik Sort SHALL move the file to the appropriate target category folder
3. WHEN Sik Sort moves files from subdirectories THEN Sik Sort SHALL preserve the original filename

### Requirement 4

**User Story:** As a user, I want to see statistics about the sorting operation, so that I understand what changes were made to my file system.

#### Acceptance Criteria

1. WHEN Sik Sort completes sorting THEN Sik Sort SHALL display the total number of files moved
2. WHEN Sik Sort completes sorting THEN Sik Sort SHALL display the count of files moved to each category folder (img, vid, arc, msk)
3. WHEN Sik Sort displays statistics THEN Sik Sort SHALL present the information using Rich library formatting for enhanced readability

### Requirement 5

**User Story:** As a user, I want the option to remove empty folders after sorting, so that my directory structure remains clean.

#### Acceptance Criteria

1. WHEN Sik Sort completes sorting and displaying statistics THEN Sik Sort SHALL prompt the user whether to clean up empty folders
2. WHEN the user selects yes for cleanup THEN Sik Sort SHALL remove all empty directories from the source path
3. WHEN the user selects no for cleanup THEN Sik Sort SHALL exit without removing empty directories
4. WHEN Sik Sort removes empty folders THEN Sik Sort SHALL not remove the target category folders (img, vid, arc, msk)

### Requirement 6

**User Story:** As a user, I want the system to correctly identify file types by extension, so that files are sorted accurately.

#### Acceptance Criteria

1. WHEN Sik Sort evaluates a file with common image extensions (jpg, jpeg, png, gif, bmp, tiff, webp, svg) THEN Sik Sort SHALL classify the file as an image
2. WHEN Sik Sort evaluates a file with common video extensions (mp4, avi, mov, mkv, wmv, flv, webm, m4v, mpg, mpeg) THEN Sik Sort SHALL classify the file as a video
3. WHEN Sik Sort evaluates a file with archive extensions (zip, rar, 7z, tar, gz, bz2, xz, iso) THEN Sik Sort SHALL classify the file as an archive
4. WHEN Sik Sort evaluates file extensions THEN Sik Sort SHALL perform case-insensitive comparison

### Requirement 7

**User Story:** As a user, I want the system to handle file name conflicts gracefully, so that no files are lost during sorting.

#### Acceptance Criteria

1. WHEN Sik Sort attempts to move a file to a target folder where a file with the same name exists THEN Sik Sort SHALL rename the incoming file to avoid overwriting
2. WHEN Sik Sort renames a file due to conflict THEN Sik Sort SHALL append a unique identifier to the filename while preserving the extension
3. WHEN Sik Sort encounters multiple conflicts for the same filename THEN Sik Sort SHALL ensure each file receives a unique name

### Requirement 8

**User Story:** As a user, I want an enhanced terminal interface, so that the application is visually appealing and easy to use.

#### Acceptance Criteria

1. WHEN Sik Sort displays prompts THEN Sik Sort SHALL use Rich library components for formatted output
2. WHEN Sik Sort displays progress or status information THEN Sik Sort SHALL use Rich library features for visual feedback
3. WHEN Sik Sort displays errors THEN Sik Sort SHALL use Rich library styling to make errors clearly visible

### Requirement 9

**User Story:** As a user, I want to see real-time operation logs during sorting, so that I can monitor what the system is actively doing.

#### Acceptance Criteria

1. WHEN Sik Sort processes each file THEN Sik Sort SHALL display a stylized log message showing the file being moved and its destination category
2. WHEN Sik Sort displays operation logs THEN Sik Sort SHALL use consistent formatting with color coding for different categories
3. WHEN Sik Sort encounters an error during file operations THEN Sik Sort SHALL log the error with clear visual distinction
4. WHEN Sik Sort completes scanning THEN Sik Sort SHALL display the total number of files found before beginning the sorting operation

### Requirement 10

**User Story:** As a user, I want to see an ASCII progress bar during sorting operations, so that I can track completion status visually.

#### Acceptance Criteria

1. WHEN Sik Sort begins sorting files THEN Sik Sort SHALL display an ASCII progress bar using block characters (█ for completed, ░ for remaining)
2. WHEN Sik Sort processes files THEN Sik Sort SHALL update the progress bar in real-time to reflect current completion percentage
3. WHEN Sik Sort displays the progress bar THEN Sik Sort SHALL show the percentage value alongside the visual bar
4. WHEN Sik Sort completes sorting THEN Sik Sort SHALL show the progress bar at one hundred percent before displaying final statistics

### Requirement 11

**User Story:** As a user, I want to run the sort command with a dry-run option, so that I can preview what changes would be made without actually modifying files.

#### Acceptance Criteria

1. WHEN the user invokes Sik Sort with the dry run flag THEN Sik Sort SHALL simulate all operations without moving or modifying any files
2. WHEN Sik Sort runs in dry run mode THEN Sik Sort SHALL display all operation logs showing what would be done
3. WHEN Sik Sort runs in dry run mode THEN Sik Sort SHALL display statistics showing what would have been moved
4. WHEN Sik Sort runs in dry run mode THEN Sik Sort SHALL clearly indicate at the start and end that no actual changes were made
5. WHEN Sik Sort runs in dry run mode THEN Sik Sort SHALL skip the empty folder cleanup prompt

### Requirement 12

**User Story:** As a user, I want to invoke the sort command directly with a path argument, so that I can sort directories efficiently without interactive prompts.

#### Acceptance Criteria

1. WHEN the user invokes the sik command with a path argument THEN Sik Sort SHALL use the provided path as the source directory
2. WHEN the user invokes the sik command without a path argument THEN Sik Sort SHALL prompt for the path interactively
3. WHEN the user invokes the sik command with the dry run flag and a path THEN Sik Sort SHALL perform a dry run on the specified path
4. WHEN the user provides an invalid path as a command argument THEN Sik Sort SHALL display an error message and exit
