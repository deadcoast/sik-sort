# UV Quick Reference for Sik Sort

This document provides a quick reference for common UV commands used in the Sik Sort project.

## Installation

### Install UV

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

## Virtual Environment Management

### Create a virtual environment
```bash
uv venv
```

### Create with specific Python version
```bash
uv venv --python 3.11
```

### Activate virtual environment

**Windows:**
```powershell
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

## Package Management

### Install project in editable mode
```bash
uv pip install -e .
```

### Install with development dependencies
```bash
uv pip install -e ".[dev]"
```

### Install from requirements file
```bash
uv pip install -r requirements.txt
```

### Sync dependencies from lock file
```bash
uv pip sync
```

### Update dependencies
```bash
uv pip install --upgrade -e ".[dev]"
```

### Uninstall package
```bash
uv pip uninstall sik-sort
```

## Running Commands

### Run without activating venv
```bash
uv run sik sort C:\Users\YourName\Downloads
```

### Run tests
```bash
uv run pytest
```

### Run tests with verbose output
```bash
uv run pytest -v
```

### Run specific test file
```bash
uv run pytest tests/test_classifier_properties.py
```

### Run with coverage
```bash
uv run pytest --cov=sik_sort --cov-report=html
```

## Lock File Management

### Generate lock file
UV automatically generates `uv.lock` when you install dependencies.

### Update lock file
```bash
uv pip install --upgrade -e ".[dev]"
```

### Install from lock file (reproducible)
```bash
uv pip sync
```

## Useful Commands

### List installed packages
```bash
uv pip list
```

### Show package information
```bash
uv pip show sik-sort
```

### Check for outdated packages
```bash
uv pip list --outdated
```

### Freeze dependencies
```bash
uv pip freeze
```

## Comparison with pip

| Task | UV | pip |
|------|-----|-----|
| Create venv | `uv venv` | `python -m venv .venv` |
| Install package | `uv pip install package` | `pip install package` |
| Install editable | `uv pip install -e .` | `pip install -e .` |
| Run command | `uv run command` | `command` (after activation) |
| List packages | `uv pip list` | `pip list` |
| Freeze deps | `uv pip freeze` | `pip freeze` |

## Tips and Tricks

### Speed up installations
UV is already fast, but you can make it even faster by:
- Using the lock file for reproducible installs
- Leveraging UV's cache (automatic)
- Installing from local wheels when available

### Debugging
```bash
# Verbose output
uv pip install -v -e .

# Very verbose output
uv pip install -vv -e .
```

### Clean cache
```bash
uv cache clean
```

### Check UV version
```bash
uv --version
```

### Update UV
**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Common Workflows

### First-time setup
```bash
# Clone repository
git clone <repository-url>
cd sik-sort

# Create virtual environment
uv venv

# Activate it
.venv\Scripts\activate  # Windows

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests to verify
uv run pytest
```

### Daily development
```bash
# Activate venv (if not already active)
.venv\Scripts\activate  # Windows

# Make changes to code...

# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_classifier_properties.py -v
```

### Before committing
```bash
# Run all tests
uv run pytest -v

# Check if lock file needs updating
git status uv.lock

# Commit changes including lock file
git add .
git commit -m "Your commit message"
```

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub Repository](https://github.com/astral-sh/uv)
- [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
