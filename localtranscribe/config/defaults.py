"""
Default configuration values for LocalTranscribe.

These defaults can be overridden by user configuration files.
"""

from pathlib import Path
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    # Model settings
    "model": {
        "whisper_size": "base",  # tiny, base, small, medium, large
        "whisper_implementation": "auto",  # auto, mlx, faster, original
        "diarization_model": "pyannote/speaker-diarization-3.1",
    },
    # Processing settings
    "processing": {
        "skip_diarization": False,
        "language": None,  # None for auto-detect
        "num_speakers": None,  # None for auto-detect
        "min_speakers": None,
        "max_speakers": None,
    },
    # Output settings
    "output": {
        "directory": "./output",
        "formats": ["txt", "json", "md"],  # Available: txt, json, srt, md
        "include_confidence": True,
        "save_markdown": True,
    },
    # Path settings
    "paths": {
        "input_dir": "./input",
        "output_dir": "./output",
        "temp_dir": None,  # None = system temp
    },
    # Performance settings
    "performance": {
        "device": "auto",  # auto, mps, cuda, cpu
        "num_threads": None,  # None = auto-detect
        "cache_limit_mb": 1024,  # MLX cache limit in MB
    },
    # Logging settings
    "logging": {
        "verbose": False,
        "log_file": None,  # None = no log file
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    },
}


def get_default_config() -> Dict[str, Any]:
    """
    Get a copy of the default configuration.

    Returns:
        Dictionary with default configuration values
    """
    import copy

    return copy.deepcopy(DEFAULT_CONFIG)


def get_config_search_paths() -> list[Path]:
    """
    Get list of paths to search for configuration files.

    Priority order:
    1. Current directory: ./localtranscribe.yaml
    2. Current directory: ./.localtranscribe/config.yaml
    3. User home: ~/.localtranscribe/config.yaml
    4. User config dir: ~/.config/localtranscribe/config.yaml

    Returns:
        List of Path objects to search for config files
    """
    paths = [
        Path.cwd() / "localtranscribe.yaml",
        Path.cwd() / ".localtranscribe" / "config.yaml",
        Path.home() / ".localtranscribe" / "config.yaml",
        Path.home() / ".config" / "localtranscribe" / "config.yaml",
    ]

    return paths


def get_default_config_path() -> Path:
    """
    Get the default path for creating a new configuration file.

    Returns:
        Path to default config location (~/.localtranscribe/config.yaml)
    """
    return Path.home() / ".localtranscribe" / "config.yaml"
