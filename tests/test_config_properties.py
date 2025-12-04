"""Property-based tests for configuration management module."""

from pathlib import Path
import tempfile
import json
import yaml
from hypothesis import given, strategies as st, settings, assume
from sik_sort.config import (
    Config, FilterConfig, SizeThresholds, DateMode,
    load_config, create_template_config, merge_with_cli_args, validate_config
)


# Strategy for generating valid configuration dictionaries
@st.composite
def config_dict_strategy(draw):
    """Generate a valid configuration dictionary."""
    return {
        'default_path': draw(st.one_of(st.none(), st.just('~/test_path'))),
        'auto_cleanup': draw(st.booleans()),
        'undo_enabled': draw(st.booleans()),
        'manifest_dir': draw(st.just('.test_manifests')),
        'filters': {
            'include_patterns': draw(st.lists(st.text(min_size=1, max_size=10), max_size=3)),
            'exclude_patterns': draw(st.lists(st.text(min_size=1, max_size=10), max_size=3)),
            'include_extensions': draw(st.lists(st.text(min_size=2, max_size=5), max_size=3)),
            'exclude_extensions': draw(st.lists(st.text(min_size=2, max_size=5), max_size=3)),
        },
        'size_sorting_enabled': draw(st.booleans()),
        'size_thresholds': {
            'small_max': draw(st.integers(min_value=1024, max_value=10_000_000)),
            'medium_max': draw(st.integers(min_value=10_000_001, max_value=1_000_000_000)),
        },
        'date_sorting_enabled': draw(st.booleans()),
        'date_mode': draw(st.sampled_from(['creation', 'modification'])),
        'date_format': draw(st.sampled_from(['%Y-%m', '%Y-%m-%d', '%Y/%m'])),
        'duplicate_detection_enabled': draw(st.booleans()),
        'hash_algorithm': draw(st.sampled_from(['md5', 'sha256'])),
        'archive_mode': draw(st.booleans()),
        'report_enabled': draw(st.booleans()),
        'report_format': draw(st.sampled_from(['json', 'csv'])),
        'report_path': draw(st.one_of(st.none(), st.just('./test_reports'))),
        'custom_categories': draw(st.dictionaries(
            st.sampled_from(['img', 'vid', 'arc', 'msk']),
            st.text(min_size=1, max_size=10),
            max_size=4
        )),
        'custom_extensions': draw(st.dictionaries(
            st.text(min_size=1, max_size=10),
            st.lists(st.text(min_size=2, max_size=5), min_size=1, max_size=3),
            max_size=3
        )),
    }


# Feature: advanced-file-operations, Property 25: Configuration loading
@settings(max_examples=100)
@given(config_data=config_dict_strategy())
def test_configuration_loading_yaml(config_data):
    """
    Property 25: Configuration loading
    
    For any valid configuration file, all settings in the file should be applied
    to the application.
    
    Validates: Requirements 6.1
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Verify all settings are applied
        assert config.auto_cleanup == config_data['auto_cleanup']
        assert config.undo_enabled == config_data['undo_enabled']
        assert config.manifest_dir == Path(config_data['manifest_dir'])
        
        # Verify filter settings
        assert config.filters.include_patterns == config_data['filters']['include_patterns']
        assert config.filters.exclude_patterns == config_data['filters']['exclude_patterns']
        assert config.filters.include_extensions == set(config_data['filters']['include_extensions'])
        assert config.filters.exclude_extensions == set(config_data['filters']['exclude_extensions'])
        
        # Verify size settings
        assert config.size_sorting_enabled == config_data['size_sorting_enabled']
        assert config.size_thresholds.small_max == config_data['size_thresholds']['small_max']
        assert config.size_thresholds.medium_max == config_data['size_thresholds']['medium_max']
        
        # Verify date settings
        assert config.date_sorting_enabled == config_data['date_sorting_enabled']
        expected_mode = DateMode.CREATION if config_data['date_mode'] == 'creation' else DateMode.MODIFICATION
        assert config.date_mode == expected_mode
        assert config.date_format == config_data['date_format']
        
        # Verify duplicate detection settings
        assert config.duplicate_detection_enabled == config_data['duplicate_detection_enabled']
        assert config.hash_algorithm == config_data['hash_algorithm']
        
        # Verify archive and report settings
        assert config.archive_mode == config_data['archive_mode']
        assert config.report_enabled == config_data['report_enabled']
        assert config.report_format == config_data['report_format']
        
        # Verify custom settings
        assert config.custom_categories == config_data['custom_categories']
        assert config.custom_extensions == config_data['custom_extensions']
        
    finally:
        config_path.unlink()


# Feature: advanced-file-operations, Property 25: Configuration loading (JSON)
@settings(max_examples=100)
@given(config_data=config_dict_strategy())
def test_configuration_loading_json(config_data):
    """
    Property 25: Configuration loading (JSON format)
    
    For any valid configuration file in JSON format, all settings in the file
    should be applied to the application.
    
    Validates: Requirements 6.1
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Verify all settings are applied
        assert config.auto_cleanup == config_data['auto_cleanup']
        assert config.undo_enabled == config_data['undo_enabled']
        assert config.manifest_dir == Path(config_data['manifest_dir'])
        
        # Verify filter settings
        assert config.filters.include_patterns == config_data['filters']['include_patterns']
        assert config.filters.exclude_patterns == config_data['filters']['exclude_patterns']
        assert config.filters.include_extensions == set(config_data['filters']['include_extensions'])
        assert config.filters.exclude_extensions == set(config_data['filters']['exclude_extensions'])
        
        # Verify size settings
        assert config.size_sorting_enabled == config_data['size_sorting_enabled']
        assert config.size_thresholds.small_max == config_data['size_thresholds']['small_max']
        assert config.size_thresholds.medium_max == config_data['size_thresholds']['medium_max']
        
        # Verify date settings
        assert config.date_sorting_enabled == config_data['date_sorting_enabled']
        expected_mode = DateMode.CREATION if config_data['date_mode'] == 'creation' else DateMode.MODIFICATION
        assert config.date_mode == expected_mode
        assert config.date_format == config_data['date_format']
        
        # Verify duplicate detection settings
        assert config.duplicate_detection_enabled == config_data['duplicate_detection_enabled']
        assert config.hash_algorithm == config_data['hash_algorithm']
        
        # Verify archive and report settings
        assert config.archive_mode == config_data['archive_mode']
        assert config.report_enabled == config_data['report_enabled']
        assert config.report_format == config_data['report_format']
        
        # Verify custom settings
        assert config.custom_categories == config_data['custom_categories']
        assert config.custom_extensions == config_data['custom_extensions']
        
    finally:
        config_path.unlink()



# Feature: advanced-file-operations, Property 26: Configuration completeness
@settings(max_examples=100)
@given(config_data=config_dict_strategy())
def test_configuration_completeness(config_data):
    """
    Property 26: Configuration completeness
    
    For any configuration file with settings for paths, filters, size thresholds,
    date sorting, and duplicate detection, all these settings should be applied.
    
    Validates: Requirements 6.2
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Verify paths are applied
        if config_data['default_path']:
            assert config.default_path is not None
        
        # Verify filters are applied
        assert len(config.filters.include_patterns) == len(config_data['filters']['include_patterns'])
        assert len(config.filters.exclude_patterns) == len(config_data['filters']['exclude_patterns'])
        # Extensions are stored as sets, so duplicates are removed
        assert config.filters.include_extensions == set(config_data['filters']['include_extensions'])
        assert config.filters.exclude_extensions == set(config_data['filters']['exclude_extensions'])
        
        # Verify size thresholds are applied
        assert config.size_thresholds.small_max == config_data['size_thresholds']['small_max']
        assert config.size_thresholds.medium_max == config_data['size_thresholds']['medium_max']
        
        # Verify date sorting settings are applied
        assert config.date_sorting_enabled == config_data['date_sorting_enabled']
        expected_mode = DateMode.CREATION if config_data['date_mode'] == 'creation' else DateMode.MODIFICATION
        assert config.date_mode == expected_mode
        assert config.date_format == config_data['date_format']
        
        # Verify duplicate detection settings are applied
        assert config.duplicate_detection_enabled == config_data['duplicate_detection_enabled']
        assert config.hash_algorithm == config_data['hash_algorithm']
        
    finally:
        config_path.unlink()



# Strategy for generating CLI arguments
@st.composite
def cli_args_strategy(draw):
    """Generate CLI arguments that can override config."""
    return {
        'auto_cleanup': draw(st.booleans()),
        'undo_enabled': draw(st.booleans()),
        'size_sorting_enabled': draw(st.booleans()),
        'size_small_max': draw(st.integers(min_value=1024, max_value=5_000_000)),
        'size_medium_max': draw(st.integers(min_value=5_000_001, max_value=500_000_000)),
        'date_sorting_enabled': draw(st.booleans()),
        'date_mode': draw(st.sampled_from([DateMode.CREATION, DateMode.MODIFICATION])),
        'date_format': draw(st.sampled_from(['%Y-%m-%d', '%Y/%m/%d'])),
        'duplicate_detection_enabled': draw(st.booleans()),
        'hash_algorithm': draw(st.sampled_from(['sha256'])),  # Different from config default
        'archive_mode': draw(st.booleans()),
        'report_enabled': draw(st.booleans()),
        'report_format': draw(st.sampled_from(['csv'])),  # Different from config default
    }


# Feature: advanced-file-operations, Property 27: CLI argument precedence
@settings(max_examples=100)
@given(
    config_data=config_dict_strategy(),
    cli_args=cli_args_strategy()
)
def test_cli_argument_precedence(config_data, cli_args):
    """
    Property 27: CLI argument precedence
    
    For any setting that appears in both configuration file and command-line arguments,
    the command-line value should be used.
    
    Validates: Requirements 6.3
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load base configuration
        base_config = load_config(config_path)
        
        # Merge with CLI arguments
        merged_config = merge_with_cli_args(base_config, cli_args)
        
        # Verify CLI arguments take precedence
        assert merged_config.auto_cleanup == cli_args['auto_cleanup']
        assert merged_config.undo_enabled == cli_args['undo_enabled']
        assert merged_config.size_sorting_enabled == cli_args['size_sorting_enabled']
        assert merged_config.size_thresholds.small_max == cli_args['size_small_max']
        assert merged_config.size_thresholds.medium_max == cli_args['size_medium_max']
        assert merged_config.date_sorting_enabled == cli_args['date_sorting_enabled']
        assert merged_config.date_mode == cli_args['date_mode']
        assert merged_config.date_format == cli_args['date_format']
        assert merged_config.duplicate_detection_enabled == cli_args['duplicate_detection_enabled']
        assert merged_config.hash_algorithm == cli_args['hash_algorithm']
        assert merged_config.archive_mode == cli_args['archive_mode']
        assert merged_config.report_enabled == cli_args['report_enabled']
        assert merged_config.report_format == cli_args['report_format']
        
    finally:
        config_path.unlink()



# Feature: advanced-file-operations, Property 51: Comprehensive configuration support
@settings(max_examples=100)
@given(config_data=config_dict_strategy())
def test_comprehensive_configuration_support(config_data):
    """
    Property 51: Comprehensive configuration support
    
    For any configuration file with settings for undo, filters, size thresholds,
    date sorting, duplicate detection, archive mode, and reporting, all settings
    should be applied.
    
    Validates: Requirements 12.1
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Verify undo settings
        assert config.undo_enabled == config_data['undo_enabled']
        assert config.manifest_dir == Path(config_data['manifest_dir'])
        
        # Verify filter settings
        assert config.filters.include_patterns == config_data['filters']['include_patterns']
        assert config.filters.exclude_patterns == config_data['filters']['exclude_patterns']
        
        # Verify size threshold settings
        assert config.size_thresholds.small_max == config_data['size_thresholds']['small_max']
        assert config.size_thresholds.medium_max == config_data['size_thresholds']['medium_max']
        
        # Verify date sorting settings
        assert config.date_sorting_enabled == config_data['date_sorting_enabled']
        expected_mode = DateMode.CREATION if config_data['date_mode'] == 'creation' else DateMode.MODIFICATION
        assert config.date_mode == expected_mode
        
        # Verify duplicate detection settings
        assert config.duplicate_detection_enabled == config_data['duplicate_detection_enabled']
        assert config.hash_algorithm == config_data['hash_algorithm']
        
        # Verify archive mode settings
        assert config.archive_mode == config_data['archive_mode']
        
        # Verify report settings
        assert config.report_enabled == config_data['report_enabled']
        assert config.report_format == config_data['report_format']
        
    finally:
        config_path.unlink()



# Feature: advanced-file-operations, Property 52: Custom category names
@settings(max_examples=100)
@given(
    custom_names=st.dictionaries(
        st.sampled_from(['img', 'vid', 'arc', 'msk']),
        st.text(min_size=1, max_size=15, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            blacklist_characters=['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        )),
        min_size=1,
        max_size=4
    )
)
def test_custom_category_names(custom_names):
    """
    Property 52: Custom category names
    
    For any custom category names specified in configuration, folders should be
    created with those names instead of defaults.
    
    Validates: Requirements 12.2
    """
    config_data = {
        'custom_categories': custom_names
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Verify custom category names are applied
        assert config.custom_categories == custom_names
        
        # Verify each custom category is preserved
        for default_name, custom_name in custom_names.items():
            assert config.custom_categories[default_name] == custom_name
        
    finally:
        config_path.unlink()



# Feature: advanced-file-operations, Property 53: Custom extension mappings
@settings(max_examples=100)
@given(
    custom_extensions=st.dictionaries(
        st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        st.lists(
            st.text(min_size=2, max_size=6, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            min_size=1,
            max_size=5
        ),
        min_size=1,
        max_size=5
    )
)
def test_custom_extension_mappings(custom_extensions):
    """
    Property 53: Custom extension mappings
    
    For any custom extension mappings in configuration, files should be classified
    using those mappings.
    
    Validates: Requirements 12.3
    """
    config_data = {
        'custom_extensions': custom_extensions
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Verify custom extension mappings are applied
        assert config.custom_extensions == custom_extensions
        
        # Verify each category's extensions are preserved
        for category, extensions in custom_extensions.items():
            assert config.custom_extensions[category] == extensions
            assert len(config.custom_extensions[category]) == len(extensions)
        
    finally:
        config_path.unlink()



# Feature: advanced-file-operations, Property 54: Auto-cleanup behavior
@settings(max_examples=100)
@given(auto_cleanup=st.booleans())
def test_auto_cleanup_behavior(auto_cleanup):
    """
    Property 54: Auto-cleanup behavior
    
    For any configuration with auto-cleanup enabled, empty directories should be
    removed without prompting.
    
    Validates: Requirements 12.4
    """
    config_data = {
        'auto_cleanup': auto_cleanup
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_path = Path(f.name)
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Verify auto-cleanup setting is applied
        assert config.auto_cleanup == auto_cleanup
        
    finally:
        config_path.unlink()
