"""
Utility functions and classes for LocalTranscribe.

Includes error handling, progress tracking, file browsing, warning management, and common utilities.
"""

from .errors import (
    LocalTranscribeError,
    AudioFileNotFoundError,
    ModelDownloadError,
    HuggingFaceTokenError,
    InvalidAudioFormatError,
    DiarizationError,
    TranscriptionError,
    CombinationError,
    ConfigurationError,
    DependencyError,
    PipelineError,
)
from .file_browser import browse_files, prompt_for_file
from .warnings_handler import (
    setup_warning_filters,
    suppress_all_warnings,
    reset_warning_filters,
)

__all__ = [
    "LocalTranscribeError",
    "AudioFileNotFoundError",
    "ModelDownloadError",
    "HuggingFaceTokenError",
    "InvalidAudioFormatError",
    "DiarizationError",
    "TranscriptionError",
    "CombinationError",
    "ConfigurationError",
    "DependencyError",
    "PipelineError",
    "browse_files",
    "prompt_for_file",
    "setup_warning_filters",
    "suppress_all_warnings",
    "reset_warning_filters",
]
