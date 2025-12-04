# Sik Sort

A command-line utility for Windows that organizes files from a specified directory into categorized folders based on file type. Sik Sort recursively processes all files and subdirectories, intelligently categorizing and moving files while handling conflicts gracefully.

## Features

- **Recursive Processing**: Automatically processes all files in a directory and its subdirectories
- **Smart Categorization**: Organizes files into four predefined categories:
  - `img` - Image files (jpg, jpeg, png, gif, bmp, tiff, webp, svg)
  - `vid` - Video files (mp4, avi, mov, mkv, wmv, flv, webm, m4v, mpg, mpeg)
  - `arc` - Archive files (zip, rar, 7z, tar, gz, bz2, xz, iso)
  - `msk` - Miscellaneous files (everything else)
- **Conflict Resolution**: Automatically handles file name conflicts by appending unique identifiers
- **Case-Insensitive**: File extensions are matched case-insensitively
- **Statistics Display**: Shows detailed statistics after sorting with beautiful formatting
- **Empty Directory Cleanup**: Optional removal of empty directories after sorting
- **Real-Time Operation Logs**: Color-coded logs showing each file operation as it happens
- **ASCII Progress Bar**: Visual progress indicator with percentage completion
- **Dry-Run Mode**: Preview what changes would be made without actually modifying files
- **Command-Line Arguments**: Direct path specification for efficient scripting
- **Safety Checks**: Built-in safety warnings for system directories and large operations
- **Enhanced UI**: Beautiful terminal interface powered by the Rich library

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install from Source

1. Clone or download this repository
2. Navigate to the project directory
3. Install the package:

```bash
pip install -e .
```

This installs Sik Sort in "editable" mode, making the `sik` command available system-wide.

### Install with Development Dependencies

If you want to run tests or contribute to development:

```bash
pip install -e ".[dev]"
```

This includes pytest and hypothesis for testing.

### Verify Installation

After installation, verify the `sik` command is available:

```bash
sik --help
```

## Usage

### Basic Usage

#### Interactive Mode

Simply run the `sik` command from your terminal:

```bash
sik
```

The application will guide you through the process:

1. **Enter Source Path**: You'll be prompted to enter the directory path you want to organize
2. **Safety Checks**: The system will check for potential issues (system directories, large file counts)
3. **Scanning**: Sik Sort scans the directory to find all files
4. **Sorting**: Files are moved to their appropriate category folders with real-time logs and progress bar
5. **Statistics**: A summary table shows how many files were moved to each category
6. **Cleanup**: You'll be asked if you want to remove empty directories

#### Direct Path Mode

Specify the directory path directly as a command-line argument:

```bash
sik sort <path>
```

Example:
```bash
sik sort C:\Users\YourName\Downloads
```

This skips the interactive prompt and immediately begins sorting the specified directory.

#### Dry-Run Mode

Preview what changes would be made without actually moving any files:

```bash
sik sort <path> --dry
```

Example:
```bash
sik sort C:\Users\YourName\Downloads --dry
```

In dry-run mode:
- No files are moved or modified
- All operation logs show what would happen
- Statistics display what would have been moved
- Clear banners indicate no actual changes were made
- Cleanup prompt is skipped

### Command-Line Options

```bash
sik sort [PATH] [OPTIONS]
```

**Arguments:**
- `PATH`: (Optional) Directory path to organize. If omitted, you'll be prompted interactively.

**Options:**
- `--dry`: Run in dry-run mode (simulation only, no files modified)
- `--force`: Bypass safety checks (USE WITH EXTREME CAUTION!)
- `--help`: Show help message and exit

### Example Sessions

#### Interactive Mode Example

```
Welcome to Sik Sort!

Enter the path to the directory you want to organize: C:\Users\YourName\Downloads

Setting up category folders...
Scanning directory...
Found 150 files to sort.

Sorting files...
[IMG] vacation_photo.jpg → img/
[IMG] screenshot.png → img/
[VID] movie_clip.mp4 → vid/
[ARC] backup.zip → arc/
[MSK] document.pdf → msk/
...
[████████████████████] 100%

Sorting complete!

┏━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Category     ┃ Count ┃
┡━━━━━━━━━━━━━━╇━━━━━━━┩
│ Images       │    45 │
│ Videos       │    12 │
│ Archives     │     8 │
│ Miscellaneous│    85 │
│ Total        │   150 │
└──────────────┴───────┘

Would you like to clean up empty directories? (y/n): y
Cleaning up empty directories...
Removed 3 empty directories.

Done!
```

#### Direct Path Mode Example

```bash
$ sik sort C:\Users\YourName\Downloads

Setting up category folders...
Scanning directory...
Found 150 files to sort.

Sorting files...
[IMG] vacation_photo.jpg → img/
[IMG] screenshot.png → img/
[VID] movie_clip.mp4 → vid/
...
[████████████████████] 100%

Sorting complete!
...
```

#### Dry-Run Mode Example

```bash
$ sik sort C:\Users\YourName\Downloads --dry

╔════════════════════════════════════════════════════════╗
║                    DRY RUN MODE                        ║
║            No files will be modified                   ║
╚════════════════════════════════════════════════════════╝

Setting up category folders... (simulated)
Scanning directory...
Found 150 files to sort.

Sorting files... (simulation)
[IMG] vacation_photo.jpg → img/ (would move)
[IMG] screenshot.png → img/ (would move)
[VID] movie_clip.mp4 → vid/ (would move)
[ARC] backup.zip → arc/ (would move)
[MSK] document.pdf → msk/ (would move)
...
[████████████████████] 100%

Sorting complete! (simulation)

┏━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Category     ┃ Count ┃
┡━━━━━━━━━━━━━━╇━━━━━━━┩
│ Images       │    45 │
│ Videos       │    12 │
│ Archives     │     8 │
│ Miscellaneous│    85 │
│ Total        │   150 │
└──────────────┴───────┘

╔════════════════════════════════════════════════════════╗
║                DRY RUN COMPLETE                        ║
║              No changes were made                      ║
╚════════════════════════════════════════════════════════╝
```

## How It Works

1. **Category Folder Creation**: Creates four folders (img, vid, arc, msk) in your source directory
2. **File Discovery**: Recursively scans all subdirectories, excluding the category folders themselves
3. **Classification**: Each file is classified based on its extension using case-insensitive matching
4. **File Moving**: Files are moved to their appropriate category folder with real-time operation logs
5. **Progress Tracking**: ASCII progress bar shows completion percentage as files are processed
6. **Conflict Handling**: If a file with the same name exists, a unique identifier is appended (e.g., `photo_1.jpg`, `photo_2.jpg`)
7. **Statistics**: Tracks and displays the number of files moved to each category
8. **Cleanup**: Optionally removes empty directories left behind after moving files

### Operation Logs

As files are processed, Sik Sort displays color-coded operation logs:

- **[IMG]** - Green: Image files being moved to img/
- **[VID]** - Blue: Video files being moved to vid/
- **[ARC]** - Yellow: Archive files being moved to arc/
- **[MSK]** - White: Miscellaneous files being moved to msk/
- **[ERROR]** - Red: Any errors encountered during processing

Each log entry shows the filename and destination, providing real-time feedback on the sorting process.

### Progress Bar

The ASCII progress bar uses block characters to show visual progress:

```
[████████████░░░░░░░░] 60%
```

- `█` (filled blocks) represent completed work
- `░` (light blocks) represent remaining work
- Percentage value shows exact completion status
- Updates in real-time as files are processed

## Supported File Types

### Images (img)
jpg, jpeg, png, gif, bmp, tiff, webp, svg

### Videos (vid)
mp4, avi, mov, mkv, wmv, flv, webm, m4v, mpg, mpeg

### Archives (arc)
zip, rar, 7z, tar, gz, bz2, xz, iso

### Miscellaneous (msk)
All other file types

## Use Cases

### Quick Cleanup
```bash
# Organize your Downloads folder quickly
sik sort C:\Users\YourName\Downloads
```

### Preview Before Sorting
```bash
# Check what would happen before making changes
sik sort C:\Users\YourName\Documents --dry
```

### Scripting and Automation
```bash
# Use in batch scripts or scheduled tasks
sik sort "D:\Project Files\Unsorted"
```

### Safe Exploration
```bash
# Explore a new directory structure safely with dry-run
sik sort "E:\External Drive\Files" --dry
```

## Safety Features

Sik Sort includes built-in safety checks to prevent accidental damage:

- **System Directory Protection**: Warns when operating on system directories
- **Large Operation Warning**: Alerts when processing a large number of files
- **Conflict Resolution**: Never overwrites existing files
- **Category Folder Preservation**: Never deletes category folders during cleanup

You can bypass safety checks with the `--force` flag, but this is not recommended.

## Development

### Project Structure

```
sik-sort/
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI interaction with Rich library
│   ├── classifier.py       # File type classification
│   ├── sorter.py           # File sorting logic
│   ├── scanner.py          # Directory traversal
│   ├── cleaner.py          # Empty folder cleanup
│   ├── safety.py           # Safety checks
│   ├── operation_logger.py # Operation logging
│   └── main.py             # Application entry point
├── tests/
│   ├── test_*_properties.py # Property-based tests
│   └── __init__.py
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Running Tests

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run specific test file:

```bash
pytest tests/test_classifier_properties.py
```

### Testing Strategy

Sik Sort uses both unit tests and property-based tests (using Hypothesis) to ensure correctness:

- **Unit Tests**: Verify specific examples and edge cases
- **Property Tests**: Verify universal properties across randomly generated inputs

Each property test runs a minimum of 100 iterations to ensure thorough coverage.

## Troubleshooting

### Command Not Found

If `sik` command is not found after installation:

1. Ensure pip's script directory is in your PATH
2. Try reinstalling: `pip uninstall sik-sort && pip install -e .`
3. Use the full path to the script (usually in `Scripts` folder of your Python installation)

### Permission Errors

If you encounter permission errors:

1. Run your terminal as Administrator (Windows)
2. Ensure you have write permissions to the target directory
3. Check that files aren't locked by other applications

### Files Not Moving

If files aren't being moved:

1. Check that the source path is correct
2. Verify files aren't in use by other applications
3. Ensure sufficient disk space is available

### Dry-Run Shows Different Results

If dry-run mode shows different results than expected:

1. Verify the path is correct
2. Check that no other processes are modifying files
3. Remember that dry-run doesn't create category folders, so it simulates the full operation

### Progress Bar Not Displaying Correctly

If the progress bar appears garbled or doesn't update smoothly:

1. Ensure your terminal supports Unicode characters (█ and ░)
2. Try using a modern terminal like Windows Terminal
3. Check that your terminal width is at least 40 characters

### Command-Line Arguments Not Working

If path arguments aren't being recognized:

1. Ensure you're using the correct syntax: `sik sort <path>`
2. Use quotes around paths with spaces: `sik sort "C:\My Files"`
3. Check that the path exists before running the command

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Author

Sik Sort Team

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Tested with [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing
