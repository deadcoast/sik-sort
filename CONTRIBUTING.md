# Contributing to Sik Sort

Thank you for your interest in contributing to Sik Sort! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- [UV](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Setting Up Your Development Environment

#### Using UV (Recommended)

UV makes development setup fast and simple:

```bash
# Clone the repository
git clone <repository-url>
cd sik-sort

# Create a virtual environment
uv venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install the package with development dependencies
uv pip install -e ".[dev]"
```

#### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd sik-sort

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install the package with development dependencies
pip install -e ".[dev]"
```

## Running Tests

### With UV

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_classifier_properties.py

# Run tests with coverage
uv run pytest --cov=sik_sort --cov-report=html
```

### With pytest directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_classifier_properties.py
```

## Testing Strategy

Sik Sort uses a comprehensive testing approach:

### Property-Based Testing

We use [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing. These tests verify that universal properties hold across randomly generated inputs.

- Each property test runs a minimum of 100 iterations
- Property tests are tagged with comments referencing the design document
- Tests validate correctness properties defined in the spec

### Unit Testing

Traditional unit tests verify specific examples and edge cases.

### Writing Tests

When adding new features:

1. **Write property tests** for universal behaviors that should hold across all inputs
2. **Write unit tests** for specific examples and edge cases
3. **Tag property tests** with references to the design document
4. **Ensure tests pass** before submitting a pull request

Example property test:

```python
from hypothesis import given, strategies as st

# Feature: file-sorter-cli, Property 1: Classification consistency
@given(st.text(min_size=1))
def test_classification_consistency(filename):
    """For any filename, classification should be deterministic."""
    result1 = classify_file(filename)
    result2 = classify_file(filename)
    assert result1 == result2
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Use type hints where appropriate

## Making Changes

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Write tests** for your changes

4. **Run tests** to ensure everything passes:
   ```bash
   uv run pytest
   ```

5. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

6. **Push your branch** and create a pull request

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update documentation if needed
- Keep pull requests focused on a single feature or fix

## Project Structure

```
sik-sort/
├── sik_sort/              # Main package
│   ├── cli.py            # CLI interface
│   ├── classifier.py     # File classification
│   ├── sorter.py         # File sorting logic
│   ├── scanner.py        # Directory scanning
│   ├── cleaner.py        # Empty directory cleanup
│   ├── safety.py         # Safety checks
│   ├── config.py         # Configuration
│   └── main.py           # Entry point
├── tests/                # Test suite
│   └── test_*.py         # Test files
├── .kiro/specs/          # Feature specifications
├── pyproject.toml        # Project configuration
└── README.md             # User documentation
```

## Reporting Issues

When reporting issues, please include:

- Your operating system and version
- Python version
- UV or pip version
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any error messages or logs

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.

## License

By contributing to Sik Sort, you agree that your contributions will be licensed under the MIT License.
