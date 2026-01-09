"""
Custom exception classes for LocalTranscribe.

Provides helpful error messages with context and suggestions for common issues.
Based on CLI error message best practices from:
- https://clig.dev/
- https://blog.logrocket.com/ux-design/writing-clear-error-messages-ux-guidelines-examples/
"""

from typing import List, Dict, Any, Optional
from pathlib import Path


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

    def __init__(self, file_path: str, searched_paths: Optional[List[str]] = None):
        """Initialize with file path and search locations."""
        searched = searched_paths or [file_path]
        super().__init__(
            message=f"Audio file not found: {file_path}",
            suggestions=[
                "Check the file path for typos",
                "Verify the file exists: ls -l " + file_path if "/" in file_path else f"dir {file_path}",
                "Use an absolute path instead of relative path",
                "Ensure you have read permissions for the file",
            ],
            context={
                "requested_path": file_path,
                "searched_locations": searched,
                "current_directory": str(Path.cwd()),
            }
        )


class ModelDownloadError(LocalTranscribeError):
    """Failed to download model from HuggingFace."""

    pass


class HuggingFaceTokenError(LocalTranscribeError):
    """HuggingFace token missing or invalid."""

    def __init__(self, reason: str = "Token not found or invalid"):
        """Initialize with specific reason."""
        super().__init__(
            message=f"HuggingFace authentication failed: {reason}",
            suggestions=[
                "Run interactive setup: localtranscribe init",
                "Get a free token at: https://huggingface.co/settings/tokens",
                "Accept required model licenses:",
                "  • https://huggingface.co/pyannote/speaker-diarization-3.1",
                "  • https://huggingface.co/pyannote/segmentation-3.0",
                "Create .env file with: HUGGINGFACE_TOKEN=\"your_token_here\"",
                "Or skip diarization: localtranscribe process audio.mp3 --skip-diarization",
            ],
            context={
                "env_file_exists": Path(".env").exists(),
                "env_file_location": str(Path(".env").absolute()) if Path(".env").exists() else "Not found",
                "reason": reason,
            }
        )


class InvalidAudioFormatError(LocalTranscribeError):
    """Audio file format not supported or corrupted."""

    def __init__(self, file_path: str, reason: str = "Unsupported or corrupted audio"):
        """Initialize with file path and reason."""
        super().__init__(
            message=f"Cannot process audio file: {reason}",
            suggestions=[
                "Verify the file is a valid audio file (not corrupted)",
                "Supported formats: MP3, WAV, M4A, FLAC, OGG, AAC, OPUS",
                "Video formats supported: MP4, MOV, AVI, MKV, WEBM (audio extracted)",
                "Try converting with ffmpeg: ffmpeg -i input.xxx output.mp3",
                "Check file size - file may be empty or truncated",
                "Install FFmpeg if not available: https://ffmpeg.org/download.html",
            ],
            context={
                "file_path": file_path,
                "file_exists": Path(file_path).exists() if file_path else False,
                "file_size": f"{Path(file_path).stat().st_size} bytes" if file_path and Path(file_path).exists() else "N/A",
                "file_extension": Path(file_path).suffix if file_path else "N/A",
            }
        )


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

    def __init__(self, dependency: str, reason: str = "Not found or incompatible"):
        """Initialize with dependency name and reason."""
        install_hints = {
            "ffmpeg": [
                "macOS: brew install ffmpeg",
                "Linux: sudo apt install ffmpeg  (or yum/dnf install ffmpeg)",
                "Windows: choco install ffmpeg  (or download from https://ffmpeg.org)",
            ],
            "torch": [
                "pip install torch torchaudio",
                "For GPU support: https://pytorch.org/get-started/locally/",
            ],
            "pyannote.audio": [
                "pip install pyannote-audio",
                "Requires HuggingFace token - run: localtranscribe init",
            ],
        }

        suggestions = install_hints.get(dependency, [
            f"pip install {dependency}",
            "Run health check: localtranscribe doctor --verbose",
        ])

        suggestions.insert(0, f"Install {dependency}:")
        suggestions.append("Run system check to verify: localtranscribe doctor")

        super().__init__(
            message=f"Missing or incompatible dependency: {dependency} ({reason})",
            suggestions=suggestions,
            context={
                "dependency": dependency,
                "reason": reason,
            }
        )


class PipelineError(LocalTranscribeError):
    """Error during pipeline orchestration."""

    pass
