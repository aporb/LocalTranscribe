"""
Output format support for LocalTranscribe.

Provides formatters for different output types: TXT, JSON, SRT, VTT, MD.
"""

from .base import BaseFormatter, Segment
from .txt import TXTFormatter
from .json_format import JSONFormatter
from .srt import SRTFormatter
from .vtt import VTTFormatter

__all__ = [
    "BaseFormatter",
    "Segment",
    "TXTFormatter",
    "JSONFormatter",
    "SRTFormatter",
    "VTTFormatter",
]


def get_formatter(format_name: str) -> BaseFormatter:
    """
    Get formatter instance for the specified format.

    Args:
        format_name: Format name (txt, json, srt, vtt, md)

    Returns:
        Formatter instance

    Raises:
        ValueError: If format is not supported
    """
    formatters = {
        "txt": TXTFormatter(),
        "json": JSONFormatter(),
        "srt": SRTFormatter(),
        "vtt": VTTFormatter(),
        "md": None,  # Markdown uses existing implementation
    }

    formatter = formatters.get(format_name.lower())
    if formatter is None and format_name.lower() != "md":
        raise ValueError(
            f"Unsupported format: {format_name}. "
            f"Supported formats: {', '.join(formatters.keys())}"
        )

    return formatter
