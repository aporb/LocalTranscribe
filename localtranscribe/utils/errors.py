"""
Custom exception classes for LocalTranscribe.

Provides helpful error messages with context and suggestions for common issues.
"""

from typing import List, Dict, Any, Optional


class LocalTranscribeError(Exception):
    """Base exception for LocalTranscribe with helpful context."""

    def __init__(
        self,
        message: str,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize error with message, suggestions, and context.

        Args:
            message: Human-readable error message
            suggestions: List of actionable suggestions to fix the error
            context: Dict of contextual information (paths, settings, etc.)
        """
        self.message = message
        self.suggestions = suggestions or []
        self.context = context or {}
        super().__init__(self.format_error())

    def format_error(self) -> str:
        """Format error message with suggestions and context."""
        lines = [f"❌ {self.message}", ""]

        if self.suggestions:
            lines.append("💡 Suggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
            lines.append("")

        if self.context:
            lines.append("📋 Context:")
            for key, value in self.context.items():
                # Handle list values
                if isinstance(value, list):
                    lines.append(f"  {key}:")
                    if value:
                        for item in value[:5]:  # Limit to first 5 items
                            lines.append(f"    - {item}")
                        if len(value) > 5:
                            lines.append(f"    ... and {len(value) - 5} more")
                    else:
                        lines.append("    (empty)")
                else:
                    lines.append(f"  {key}: {value}")

        return "\n".join(lines)


class AudioFileNotFoundError(LocalTranscribeError):
    """Audio file not found in expected locations."""

    pass


class ModelDownloadError(LocalTranscribeError):
    """Failed to download model from HuggingFace."""

    pass


class HuggingFaceTokenError(LocalTranscribeError):
    """HuggingFace token missing or invalid."""

    pass


class InvalidAudioFormatError(LocalTranscribeError):
    """Audio file format not supported or corrupted."""

    pass


class DiarizationError(LocalTranscribeError):
    """Error during speaker diarization process."""

    pass


class TranscriptionError(LocalTranscribeError):
    """Error during speech-to-text transcription."""

    pass


class CombinationError(LocalTranscribeError):
    """Error while combining diarization and transcription results."""

    pass


class ConfigurationError(LocalTranscribeError):
    """Invalid configuration or missing required settings."""

    pass


class DependencyError(LocalTranscribeError):
    """Required dependency not found or incompatible version."""

    pass


class PipelineError(LocalTranscribeError):
    """Error during pipeline orchestration."""

    pass
