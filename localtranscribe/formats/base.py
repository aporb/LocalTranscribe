"""
Base formatter interface for LocalTranscribe output formats.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Segment:
    """
    Represents a transcript segment with timing and speaker information.
    """

    start: float  # Start time in seconds
    end: float  # End time in seconds
    text: str  # Transcript text
    speaker: Optional[str] = None  # Speaker label
    confidence: Optional[float] = None  # Confidence score (0-1)


class BaseFormatter(ABC):
    """
    Abstract base class for output formatters.

    All formatters must implement format() and validate() methods.
    """

    @abstractmethod
    def format(self, segments: List[Segment], **kwargs) -> str:
        """
        Format segments to output string.

        Args:
            segments: List of transcript segments
            **kwargs: Additional format-specific options

        Returns:
            Formatted output string
        """
        pass

    @abstractmethod
    def validate(self, content: str) -> bool:
        """
        Validate formatted content.

        Args:
            content: Formatted content to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def get_extension(self) -> str:
        """
        Get file extension for this format (without dot).

        Returns:
            File extension (e.g., 'txt', 'json', 'srt')
        """
        return self.__class__.__name__.replace("Formatter", "").lower()
