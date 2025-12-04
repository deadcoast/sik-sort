"""Configuration management module for Sik Sort."""

from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from typing import Any
import json
import yaml


class DateMode(Enum):
    """Date mode enumeration for date-based sorting."""
    CREATION = "creation"
    MODIFICATION = "modification"


@dataclass
class FilterConfig:
    """Configuration for file filtering."""
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    include_extensions: set[str] = field(default_factory=set)
    exclude_extensions: set[str] = field(default_factory=set)


@dataclass
class SizeThresholds:
    """Size thresholds for size-based sorting."""
    small_max: int = 1_048_576  # 1 MB
    medium_max: int = 104_857_600  # 100 MB


@dataclass
class Config:
    """Main configuration dataclass for Sik Sort."""
    # General settings
    default_path: Path | None = None
    auto_cleanup: bool = False
    
    # Undo settings
    undo_enabled: bool = True
    manifest_dir: Path = field(default_factory=lambda: Path(".sik_manifests"))
    
    # Filter settings
    filters: FilterConfig = field(default_factory=FilterConfig)
    
    # Size sorting settings
    size_sorting_enabled: bool = False
    size_thresholds: SizeThresholds = field(default_factory=SizeThresholds)
    
    # Date sorting settings
    date_sorting_enabled: bool = False
    date_mode: DateMode = DateMode.MODIFICATION
    date_format: str = "%Y-%m"
    
    # Duplicate detection settings
    duplicate_detection_enabled: bool = False
    hash_algorithm: str = "md5"
    
    # Archive mode settings
    archive_mode: bool = False
    
    # Report settings
    report_enabled: bool = False
    report_format: str = "json"
    report_path: Path | None = None
    
    # Custom categories
    custom_categories: dict[str, str] = field(default_factory=dict)
    custom_extensions: dict[str, list[str]] = field(default_factory=dict)


def load_config(config_path: Path | None) -> Config:
    """Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file (YAML or JSON), or None for defaults
        
    Returns:
        Config: Loaded configuration object
        
    Raises:
        FileNotFoundError: If config_path is provided but file doesn't exist
        ValueError: If file format is invalid or unsupported
    """
    if config_path is None:
        return Config()
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    # Read file content
    content = config_path.read_text()
    
    # Parse based on file extension
    suffix = config_path.suffix.lower()
    if suffix in ['.yaml', '.yml']:
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax: {e}")
    elif suffix == '.json':
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON syntax: {e}")
    else:
        raise ValueError(f"Unsupported configuration file format: {suffix}")
    
    if data is None:
        data = {}
    
    # Build Config object from parsed data
    return _dict_to_config(data)


def _dict_to_config(data: dict[str, Any]) -> Config:
    """Convert dictionary to Config object.
    
    Args:
        data: Dictionary with configuration values
        
    Returns:
        Config: Configuration object
    """
    config = Config()
    
    # General settings
    if 'default_path' in data and data['default_path']:
        config.default_path = Path(data['default_path']).expanduser()
    if 'auto_cleanup' in data:
        config.auto_cleanup = bool(data['auto_cleanup'])
    
    # Undo settings
    if 'undo_enabled' in data:
        config.undo_enabled = bool(data['undo_enabled'])
    if 'manifest_dir' in data:
        config.manifest_dir = Path(data['manifest_dir'])
    
    # Filter settings
    if 'filters' in data:
        filters_data = data['filters']
        config.filters = FilterConfig(
            include_patterns=filters_data.get('include_patterns', []),
            exclude_patterns=filters_data.get('exclude_patterns', []),
            include_extensions=set(filters_data.get('include_extensions', [])),
            exclude_extensions=set(filters_data.get('exclude_extensions', []))
        )
    
    # Size sorting settings
    if 'size_sorting_enabled' in data:
        config.size_sorting_enabled = bool(data['size_sorting_enabled'])
    if 'size_thresholds' in data:
        thresholds_data = data['size_thresholds']
        config.size_thresholds = SizeThresholds(
            small_max=thresholds_data.get('small_max', 1_048_576),
            medium_max=thresholds_data.get('medium_max', 104_857_600)
        )
    
    # Date sorting settings
    if 'date_sorting_enabled' in data:
        config.date_sorting_enabled = bool(data['date_sorting_enabled'])
    if 'date_mode' in data:
        mode_str = data['date_mode']
        config.date_mode = DateMode.CREATION if mode_str == 'creation' else DateMode.MODIFICATION
    if 'date_format' in data:
        config.date_format = str(data['date_format'])
    
    # Duplicate detection settings
    if 'duplicate_detection_enabled' in data:
        config.duplicate_detection_enabled = bool(data['duplicate_detection_enabled'])
    if 'hash_algorithm' in data:
        config.hash_algorithm = str(data['hash_algorithm'])
    
    # Archive mode settings
    if 'archive_mode' in data:
        config.archive_mode = bool(data['archive_mode'])
    
    # Report settings
    if 'report_enabled' in data:
        config.report_enabled = bool(data['report_enabled'])
    if 'report_format' in data:
        config.report_format = str(data['report_format'])
    if 'report_path' in data and data['report_path']:
        config.report_path = Path(data['report_path'])
    
    # Custom categories
    if 'custom_categories' in data:
        config.custom_categories = dict(data['custom_categories'])
    if 'custom_extensions' in data:
        config.custom_extensions = dict(data['custom_extensions'])
    
    return config


def create_template_config(output_path: Path) -> None:
    """Create a template configuration file with documented options.
    
    Args:
        output_path: Path where template configuration will be written
    """
    template = """# Sik Sort Configuration

# General settings
default_path: ~/Downloads
auto_cleanup: false

# Undo settings
undo_enabled: true
manifest_dir: .sik_manifests

# Filter settings
filters:
  include_patterns:
    - "*.jpg"
    - "*.png"
  exclude_patterns:
    - "*_backup*"
  include_extensions:
    - .pdf
    - .doc
  exclude_extensions:
    - .tmp

# Size sorting settings
size_sorting_enabled: false
size_thresholds:
  small_max: 1048576  # 1 MB
  medium_max: 104857600  # 100 MB

# Date sorting settings
date_sorting_enabled: false
date_mode: modification  # or creation
date_format: "%Y-%m"

# Duplicate detection settings
duplicate_detection_enabled: false
hash_algorithm: md5  # or sha256

# Archive mode settings
archive_mode: false

# Report settings
report_enabled: false
report_format: json  # or csv
report_path: ./reports

# Custom categories (optional)
custom_categories:
  img: images
  vid: videos
  arc: archives
  msk: misc

# Custom extension mappings (optional)
custom_extensions:
  images:
    - .heic
    - .raw
  videos:
    - .mts
"""
    output_path.write_text(template)


def merge_with_cli_args(config: Config, cli_args: dict[str, Any]) -> Config:
    """Merge configuration with command-line arguments.
    
    Command-line arguments take precedence over configuration file settings.
    
    Args:
        config: Base configuration object
        cli_args: Dictionary of command-line arguments
        
    Returns:
        Config: Merged configuration object
    """
    # Create a copy to avoid modifying the original
    merged = Config(
        default_path=config.default_path,
        auto_cleanup=config.auto_cleanup,
        undo_enabled=config.undo_enabled,
        manifest_dir=config.manifest_dir,
        filters=FilterConfig(
            include_patterns=config.filters.include_patterns.copy(),
            exclude_patterns=config.filters.exclude_patterns.copy(),
            include_extensions=config.filters.include_extensions.copy(),
            exclude_extensions=config.filters.exclude_extensions.copy()
        ),
        size_sorting_enabled=config.size_sorting_enabled,
        size_thresholds=SizeThresholds(
            small_max=config.size_thresholds.small_max,
            medium_max=config.size_thresholds.medium_max
        ),
        date_sorting_enabled=config.date_sorting_enabled,
        date_mode=config.date_mode,
        date_format=config.date_format,
        duplicate_detection_enabled=config.duplicate_detection_enabled,
        hash_algorithm=config.hash_algorithm,
        archive_mode=config.archive_mode,
        report_enabled=config.report_enabled,
        report_format=config.report_format,
        report_path=config.report_path,
        custom_categories=config.custom_categories.copy(),
        custom_extensions=config.custom_extensions.copy()
    )
    
    # Override with CLI arguments
    if 'default_path' in cli_args and cli_args['default_path'] is not None:
        merged.default_path = Path(cli_args['default_path'])
    if 'auto_cleanup' in cli_args:
        merged.auto_cleanup = cli_args['auto_cleanup']
    if 'undo_enabled' in cli_args:
        merged.undo_enabled = cli_args['undo_enabled']
    if 'manifest_dir' in cli_args and cli_args['manifest_dir'] is not None:
        merged.manifest_dir = Path(cli_args['manifest_dir'])
    
    # Filter settings
    if 'include_patterns' in cli_args and cli_args['include_patterns']:
        merged.filters.include_patterns = cli_args['include_patterns']
    if 'exclude_patterns' in cli_args and cli_args['exclude_patterns']:
        merged.filters.exclude_patterns = cli_args['exclude_patterns']
    if 'include_extensions' in cli_args and cli_args['include_extensions']:
        merged.filters.include_extensions = set(cli_args['include_extensions'])
    if 'exclude_extensions' in cli_args and cli_args['exclude_extensions']:
        merged.filters.exclude_extensions = set(cli_args['exclude_extensions'])
    
    # Size sorting settings
    if 'size_sorting_enabled' in cli_args:
        merged.size_sorting_enabled = cli_args['size_sorting_enabled']
    if 'size_small_max' in cli_args and cli_args['size_small_max'] is not None:
        merged.size_thresholds.small_max = cli_args['size_small_max']
    if 'size_medium_max' in cli_args and cli_args['size_medium_max'] is not None:
        merged.size_thresholds.medium_max = cli_args['size_medium_max']
    
    # Date sorting settings
    if 'date_sorting_enabled' in cli_args:
        merged.date_sorting_enabled = cli_args['date_sorting_enabled']
    if 'date_mode' in cli_args and cli_args['date_mode'] is not None:
        merged.date_mode = cli_args['date_mode']
    if 'date_format' in cli_args and cli_args['date_format'] is not None:
        merged.date_format = cli_args['date_format']
    
    # Duplicate detection settings
    if 'duplicate_detection_enabled' in cli_args:
        merged.duplicate_detection_enabled = cli_args['duplicate_detection_enabled']
    if 'hash_algorithm' in cli_args and cli_args['hash_algorithm'] is not None:
        merged.hash_algorithm = cli_args['hash_algorithm']
    
    # Archive mode settings
    if 'archive_mode' in cli_args:
        merged.archive_mode = cli_args['archive_mode']
    
    # Report settings
    if 'report_enabled' in cli_args:
        merged.report_enabled = cli_args['report_enabled']
    if 'report_format' in cli_args and cli_args['report_format'] is not None:
        merged.report_format = cli_args['report_format']
    if 'report_path' in cli_args and cli_args['report_path'] is not None:
        merged.report_path = Path(cli_args['report_path'])
    
    # Custom categories and extensions
    if 'custom_categories' in cli_args and cli_args['custom_categories']:
        merged.custom_categories = cli_args['custom_categories']
    if 'custom_extensions' in cli_args and cli_args['custom_extensions']:
        merged.custom_extensions = cli_args['custom_extensions']
    
    return merged


def validate_config(config: Config) -> list[str]:
    """Validate configuration values.
    
    Args:
        config: Configuration object to validate
        
    Returns:
        list[str]: List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate size thresholds
    if config.size_thresholds.small_max <= 0:
        errors.append("size_thresholds.small_max must be positive")
    if config.size_thresholds.medium_max <= 0:
        errors.append("size_thresholds.medium_max must be positive")
    if config.size_thresholds.small_max >= config.size_thresholds.medium_max:
        errors.append("size_thresholds.small_max must be less than medium_max")
    
    # Validate hash algorithm
    if config.hash_algorithm not in ['md5', 'sha256']:
        errors.append(f"hash_algorithm must be 'md5' or 'sha256', got '{config.hash_algorithm}'")
    
    # Validate report format
    if config.report_format not in ['json', 'csv']:
        errors.append(f"report_format must be 'json' or 'csv', got '{config.report_format}'")
    
    # Validate date format (basic check)
    if not config.date_format:
        errors.append("date_format cannot be empty")
    
    # Validate paths exist if specified
    if config.default_path is not None and not config.default_path.exists():
        errors.append(f"default_path does not exist: {config.default_path}")
    
    return errors
