"""
Configuration loader for LocalTranscribe.

Handles loading configuration from files and environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .defaults import (
    get_default_config,
    get_config_search_paths,
    get_default_config_path,
)


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Dictionary with configuration values

    Raises:
        ImportError: If PyYAML is not installed
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for configuration files. "
            "Install with: pip install pyyaml"
        )

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config or {}


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries recursively.

    Override values take precedence over base values.

    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary

    Returns:
        Merged configuration dictionary
    """
    import copy

    result = copy.deepcopy(base)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_configs(result[key], value)
        else:
            # Override value
            result[key] = value

    return result


def load_env_overrides() -> Dict[str, Any]:
    """
    Load configuration overrides from environment variables.

    Environment variables follow the pattern:
    LOCALTRANSCRIBE_SECTION_KEY=value

    Example:
        LOCALTRANSCRIBE_MODEL_WHISPER_SIZE=small
        LOCALTRANSCRIBE_OUTPUT_DIRECTORY=./results

    Returns:
        Dictionary with configuration overrides from environment
    """
    overrides: Dict[str, Any] = {}
    prefix = "LOCALTRANSCRIBE_"

    for env_var, value in os.environ.items():
        if not env_var.startswith(prefix):
            continue

        # Parse environment variable name
        key_parts = env_var[len(prefix) :].lower().split("_")

        if len(key_parts) < 2:
            continue

        # Build nested dictionary
        current = overrides
        for part in key_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set value (try to parse as appropriate type)
        final_key = key_parts[-1]
        current[final_key] = _parse_env_value(value)

    return overrides


def _parse_env_value(value: str) -> Any:
    """
    Parse environment variable value to appropriate type.

    Args:
        value: String value from environment variable

    Returns:
        Parsed value (bool, int, float, list, or str)
    """
    # Boolean
    if value.lower() in ("true", "yes", "1", "on"):
        return True
    if value.lower() in ("false", "no", "0", "off"):
        return False

    # None
    if value.lower() in ("none", "null"):
        return None

    # List (comma-separated)
    if "," in value:
        return [item.strip() for item in value.split(",")]

    # Number
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass

    # String
    return value


def find_config_file() -> Optional[Path]:
    """
    Find configuration file by searching standard locations.

    Returns:
        Path to configuration file if found, None otherwise
    """
    for config_path in get_config_search_paths():
        if config_path.exists():
            return config_path

    return None


def get_config_path() -> Optional[Path]:
    """
    Get the path to the active configuration file.

    Returns:
        Path to configuration file if it exists, None otherwise
    """
    return find_config_file()


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load complete configuration from defaults, file, and environment.

    Priority order (highest to lowest):
    1. Environment variables (LOCALTRANSCRIBE_*)
    2. Specified config file
    3. Auto-discovered config file
    4. Default values

    Args:
        config_path: Optional explicit path to configuration file

    Returns:
        Complete merged configuration dictionary
    """
    # Start with defaults
    config = get_default_config()

    # Load from file if available
    if config_path:
        # Explicit path provided
        try:
            file_config = load_yaml_config(config_path)
            config = merge_configs(config, file_config)
        except Exception:
            # If explicit path fails, let it raise
            raise
    else:
        # Auto-discover config file
        discovered_path = find_config_file()
        if discovered_path:
            try:
                file_config = load_yaml_config(discovered_path)
                config = merge_configs(config, file_config)
            except Exception:
                # Ignore errors for auto-discovered configs
                pass

    # Apply environment variable overrides
    env_overrides = load_env_overrides()
    if env_overrides:
        config = merge_configs(config, env_overrides)

    return config


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> Path:
    """
    Save configuration to YAML file.

    Args:
        config: Configuration dictionary to save
        config_path: Optional path for config file (default: ~/.localtranscribe/config.yaml)

    Returns:
        Path where configuration was saved

    Raises:
        ImportError: If PyYAML is not installed
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for configuration files. "
            "Install with: pip install pyyaml"
        )

    if config_path is None:
        config_path = get_default_config_path()

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write configuration
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    return config_path
