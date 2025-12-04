# Sik Sort

[![Tests](https://github.com/YOUR_USERNAME/sik-sort/workflows/Tests/badge.svg)](https://github.com/YOUR_USERNAME/sik-sort/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![UV](https://img.shields.io/badge/package%20manager-UV-orange.svg)](https://docs.astral.sh/uv/)

A command-line utility for Windows that organizes files from a specified directory into categorized folders based on file type. Sik Sort recursively processes all files and subdirectories, intelligently categorizing and moving files while handling conflicts gracefully.

## Quick Start

```bash
# Install UV (if not already installed)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clone and install Sik Sort
git clone <repository-url>
cd sik-sort
uv pip install -e .

# Run Sik Sort
sik sort C:\Users\YourName\Downloads
```

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
- [UV](https://docs.astral.sh/uv/) (recommended) or pip

### Installing UV

UV is a fast Python package manager that's significantly faster than pip. Install it using one of these methods:

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**With pip:**
```bash
pip install uv
```

For more installation options, see the [UV documentation](https://docs.astral.sh/uv/getting-started/installation/).

### Install from Source

#### Using UV (Recommended)

UV can automatically manage virtual environments for you, making installation even simpler.

**Option 1: Quick Install (UV manages everything)**

1. Clone or download this repository
2. Navigate to the project directory
3. Install and run:

```bash
# UV automatically creates a virtual environment and installs dependencies
uv pip install -e .

# Or run directly without explicit installation
uv run sik sort C:\Users\YourName\Downloads
```

**Option 2: Manual Virtual Environment**

```bash
# Create a virtual environment
uv venv

# Activate it (Windows)
.venv\Scripts\activate

# Install the package
uv pip install -e .
```

This installs Sik Sort in "editable" mode, making the `sik` command available.

#### Using pip

If you prefer to use pip:

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install the package
pip install -e .
```

### Install with Development Dependencies

If you want to run tests or contribute to development:

**With UV:**
```bash
uv pip install -e ".[dev]"
```

**With pip:**
```bash
pip install -e ".[dev]"
```

This includes pytest and hypothesis for testing.

> **Note**: UV automatically creates a `uv.lock` file that locks all dependency versions for reproducible installations. This file should be committed to version control to ensure all developers and CI systems use the same dependency versions.

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

For detailed information about contributing to Sik Sort, see [CONTRIBUTING.md](CONTRIBUTING.md).

### Quick Development Setup

**With UV:**
```bash
git clone <repository-url>
cd sik-sort
uv venv
.venv\Scripts\activate  # Windows
uv pip install -e ".[dev]"
uv run pytest
```

**With pip:**
```bash
git clone <repository-url>
cd sik-sort
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e ".[dev]"
pytest
```

### Project Structure

```
sik-sort/
├── sik_sort/
│   ├── __init__.py
│   ├── cli.py              # CLI interaction with Rich library
│   ├── classifier.py       # File type classification
│   ├── sorter.py           # File sorting logic
│   ├── scanner.py          # Directory traversal
│   ├── cleaner.py          # Empty folder cleanup
│   ├── safety.py           # Safety checks
│   ├── operation_logger.py # Operation logging
│   ├── config.py           # Configuration management
│   ├── date_classifier.py  # Date-based classification
│   ├── size_classifier.py  # Size-based classification
│   ├── duplicates.py       # Duplicate file detection
│   ├── filters.py          # File filtering
│   └── main.py             # Application entry point
├── tests/
│   ├── test_*_properties.py # Property-based tests
│   └── __init__.py
├── pyproject.toml          # Project configuration
├── uv.lock                 # UV lock file
└── README.md               # This file
```

### Running Tests

**With UV (Recommended):**

Run all tests:
```bash
uv run pytest
```

Run with verbose output:
```bash
uv run pytest -v
```

Run specific test file:
```bash
uv run pytest tests/test_classifier_properties.py
```

**With pytest directly:**

If you've already installed dependencies:
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

**With UV:**
1. Ensure UV's script directory is in your PATH
2. Try reinstalling: `uv pip uninstall sik-sort && uv pip install -e .`
3. Alternatively, run directly: `uv run sik`

**With pip:**
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

## Why UV?

UV is a modern Python package manager that offers several advantages:

- **Speed**: 10-100x faster than pip for package installation
  - Installing Sik Sort with dependencies: ~1-2 seconds with UV vs ~10-30 seconds with pip
  - Running tests with `uv run pytest`: Instant startup vs slower with traditional venv
- **Reliability**: Built-in dependency resolution and lock files (`uv.lock`)
  - Ensures consistent installations across different machines
  - Prevents dependency conflicts before installation
- **Compatibility**: Drop-in replacement for pip commands
  - `uv pip install` works exactly like `pip install`
  - No need to learn new commands
- **Modern**: Written in Rust with a focus on performance
  - Parallel downloads and installations
  - Efficient caching

### UV vs pip Comparison

| Task | UV | pip |
|------|-----|-----|
| Install dependencies | `uv pip install -e .` | `pip install -e .` |
| Install with dev deps | `uv pip install -e ".[dev]"` | `pip install -e ".[dev]"` |
| Run command | `uv run pytest` | `pytest` |
| Create venv | `uv venv` | `python -m venv .venv` |

While pip still works perfectly fine, UV provides a significantly better developer experience, especially for projects with many dependencies or when running tests frequently.

For a comprehensive list of UV commands, see [UV_QUICK_REFERENCE.md](UV_QUICK_REFERENCE.md).

> **Migrating from pip?** See [MIGRATION_TO_UV.md](MIGRATION_TO_UV.md) for a complete migration guide, or use our automated migration scripts in the `scripts/` directory.

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Tested with [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing
- Package management with [UV](https://docs.astral.sh/uv/) for fast, reliable installs
