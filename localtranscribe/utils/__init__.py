"""
Utility functions and classes for LocalTranscribe.

Includes error handling, progress tracking, and common utilities.
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
]
