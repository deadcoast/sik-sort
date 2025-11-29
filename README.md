# Sik Sort

A command-line utility for Windows that organizes files from a specified directory into categorized folders based on file type.

## Features

- Recursively processes all files in a directory and subdirectories
- Organizes files into four categories:
  - `img` - Image files (jpg, png, gif, etc.)
  - `vid` - Video files (mp4, avi, mov, etc.)
  - `arc` - Archive files (zip, rar, 7z, etc.)
  - `msk` - Miscellaneous files (everything else)
- Handles file name conflicts automatically
- Displays statistics after sorting
- Optional cleanup of empty directories
- Enhanced terminal interface using Rich library

## Installation

Install the package in development mode:

```bash
pip install -e .
```

For development with testing dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

Run the `sik` command from your terminal:

```bash
sik
```

The application will:
1. Prompt you for a source directory path
2. Scan and organize all files into category folders
3. Display statistics about the sorting operation
4. Ask if you want to clean up empty directories

## Requirements

- Python 3.8 or higher
- Rich library (for enhanced terminal UI)

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
sik_sort/
├── __init__.py
├── cli.py          # CLI interaction with Rich library
├── classifier.py   # File type classification
├── sorter.py       # File sorting logic
├── scanner.py      # Directory traversal
├── cleaner.py      # Empty folder cleanup
└── main.py         # Application entry point
```

## License

MIT
