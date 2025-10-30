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
    # Segment post-processing settings (Phase 1 enhancement)
    "segment_processing": {
        "enabled": True,  # Enable segment post-processing
        "min_segment_duration": 0.3,  # Min duration (seconds) for a segment
        "merge_gap_threshold": 1.0,  # Max gap (seconds) to merge same-speaker segments
        "min_speaker_turn": 2.0,  # Min duration (seconds) for speaker turn
        "smoothing_window": 2.0,  # Time window (seconds) for temporal smoothing
    },
    # Speaker mapping settings (Phase 1 enhancement)
    "speaker_mapping": {
        "use_regions": True,  # Use speaker regions for better context
        "temporal_consistency_weight": 0.3,  # Weight for temporal consistency
        "duration_weight": 0.4,  # Weight for region duration
        "overlap_weight": 0.3,  # Weight for overlap score
    },
    # Audio analysis settings (Phase 2 enhancement)
    "audio_analysis": {
        "enabled": True,  # Enable audio quality analysis
        "calculate_snr": True,  # Calculate Signal-to-Noise Ratio
        "estimate_speakers": True,  # Estimate speaker count
        "recommend_parameters": True,  # Recommend optimal parameters
        "verbose": False,  # Verbose analysis output
    },
    # Quality gates settings (Phase 2 enhancement)
    "quality_gates": {
        "enabled": True,  # Enable quality assessment gates
        "thresholds": {
            # Diarization thresholds
            "max_micro_segment_ratio": 0.15,  # Max 15% micro-segments
            "min_avg_segment_duration": 2.0,  # Min 2s average
            "max_speaker_switches_per_minute": 8.0,  # Max switches per minute
            # Transcription thresholds
            "min_avg_confidence": 0.7,  # Min average confidence
            "max_no_speech_prob": 0.3,  # Max no-speech probability
            "max_compression_ratio": 2.5,  # Max compression ratio
            # Combination thresholds
            "min_speaker_mapping_confidence": 0.6,  # Min mapping confidence
            "max_ambiguous_segments_ratio": 0.1,  # Max 10% ambiguous
        },
        "generate_report": True,  # Generate quality report
        "save_report": True,  # Save report to file
    },
    # Enhanced proofreading settings (Phase 2 enhancement)
    "proofreading": {
        "enable_domain_dictionaries": False,  # Enable domain-specific corrections
        "domains": ["common"],  # Domains to enable: military, technical, business, medical, common
        "enable_acronym_expansion": False,  # Enable acronym expansion
        "acronym_format": "parenthetical",  # Format: parenthetical, replacement, footnote
    },
    # Output settings
    "output": {
        "directory": "./output",
        "formats": ["txt", "json", "md"],  # Available: txt, json, srt, md
        "include_confidence": True,
        "save_markdown": True,
        "include_quality_report": False,  # Include quality report in output (Phase 2)
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
