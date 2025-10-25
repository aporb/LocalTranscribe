"""
Utility functions and classes for LocalTranscribe.

Includes error handling, progress tracking, file browsing, and common utilities.
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
]
