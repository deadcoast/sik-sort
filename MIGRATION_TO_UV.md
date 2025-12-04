# Migration to UV - Summary of Changes

This document summarizes the changes made to migrate Sik Sort from pip to UV as the recommended package manager.

## What Changed?

### 1. Documentation Updates

#### README.md
- Added UV installation instructions with multiple methods (PowerShell, curl, pip)
- Updated all installation commands to show both UV and pip options
- Added "Quick Start" section highlighting UV usage
- Added "Why UV?" section explaining benefits with concrete examples
- Added UV vs pip comparison table
- Updated development setup instructions
- Updated testing commands to use `uv run pytest`
- Updated troubleshooting section with UV-specific guidance
- Added badges for CI, Python version, and UV
- Added note about `uv.lock` file and reproducibility
- Updated project structure to reflect actual directory layout

#### New Files Created
- **CONTRIBUTING.md**: Comprehensive guide for contributors with UV-focused workflows
- **UV_QUICK_REFERENCE.md**: Quick reference card for common UV commands
- **MIGRATION_TO_UV.md**: This file, documenting the migration
- **.python-version**: Specifies Python 3.8 as the project's Python version
- **.gitignore**: Proper Python and UV-aware gitignore file
- **.github/workflows/test.yml**: CI/CD workflow using UV

### 2. Configuration Updates

#### pyproject.toml
- Changed build backend from `setuptools` to `hatchling` (more modern, UV-friendly)
- Simplified dependency version constraints (removed upper bounds for flexibility)
- Added `[tool.hatch.build.targets.wheel]` section
- Added `[tool.uv]` section with dev-dependencies
- Kept backward compatibility with pip

### 3. Key Benefits of the Migration

#### For Users
- **Faster installation**: 10-100x faster than pip
- **Better reliability**: Lock file ensures consistent installations
- **Simpler commands**: `uv run sik` works without activation
- **No breaking changes**: pip still works perfectly fine

#### For Developers
- **Faster test runs**: `uv run pytest` starts instantly
- **Better dependency management**: Automatic lock file generation
- **Parallel downloads**: Multiple packages installed simultaneously
- **Better caching**: Faster subsequent installations

### 4. Backward Compatibility

All changes maintain full backward compatibility:
- pip commands still work exactly as before
- No changes to the actual application code
- Users can choose to use pip or UV
- Both package managers are documented

## Migration Guide for Existing Users

### If You're Currently Using pip

You don't need to change anything! The project still works perfectly with pip.

### If You Want to Switch to UV

#### Automated Migration (Recommended)

We provide migration scripts to automate the process:

**Windows (PowerShell):**
```powershell
.\scripts\migrate_to_uv.ps1
```

**macOS/Linux:**
```bash
chmod +x scripts/migrate_to_uv.sh
./scripts/migrate_to_uv.sh
```

These scripts will:
- Install UV if not already installed
- Remove old virtual environment (with confirmation)
- Create new virtual environment with UV
- Install all dependencies
- Verify the installation

#### Manual Migration

1. **Install UV:**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Reinstall Sik Sort with UV:**
   ```bash
   # Uninstall old version
   pip uninstall sik-sort
   
   # Install with UV
   cd sik-sort
   uv pip install -e .
   ```

3. **Verify it works:**
   ```bash
   sik --help
   ```

## Migration Guide for Contributors

### If You're Currently Using pip

1. **Install UV:**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Recreate your virtual environment:**
   ```bash
   # Remove old venv
   deactivate  # if currently activated
   rmdir /s .venv  # Windows
   
   # Create new venv with UV
   uv venv
   .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -e ".[dev]"
   ```

3. **Update your workflow:**
   - Replace `pytest` with `uv run pytest`
   - Replace `pip install` with `uv pip install`
   - Commit the `uv.lock` file when it changes

## Files Modified

### Updated
- `README.md` - Comprehensive UV documentation
- `pyproject.toml` - Modern build system and UV configuration

### Created
- `CONTRIBUTING.md` - Contributor guide with UV workflows
- `UV_QUICK_REFERENCE.md` - UV command reference
- `MIGRATION_TO_UV.md` - This migration guide
- `.python-version` - Python version specification
- `.gitignore` - Proper ignore patterns
- `.github/workflows/test.yml` - CI/CD with UV

### Not Changed
- All source code in `sik_sort/`
- All test files in `tests/`
- Application functionality
- Command-line interface
- User experience

## Testing the Migration

To verify everything works correctly:

### With UV
```bash
# Install
uv pip install -e ".[dev]"

# Run tests
uv run pytest -v

# Run the application
uv run sik --help
sik sort C:\Users\YourName\Downloads --dry
```

### With pip (verify backward compatibility)
```bash
# Install
pip install -e ".[dev]"

# Run tests
pytest -v

# Run the application
sik --help
sik sort C:\Users\YourName\Downloads --dry
```

## Rollback Plan

If you need to rollback to pip-only:

1. The project still works with pip - no rollback needed
2. Simply use pip commands instead of UV commands
3. Ignore UV-specific files (`.python-version`, `uv.lock`)

## Questions?

If you have questions about the migration:
- Check [UV_QUICK_REFERENCE.md](UV_QUICK_REFERENCE.md) for command help
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development workflows
- Open an issue on GitHub

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)
