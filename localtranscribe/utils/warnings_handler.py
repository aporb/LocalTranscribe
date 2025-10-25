"""
Custom warning handler for clean user experience.

Filters technical dependency warnings that users cannot action,
while showing actionable warnings in a clean, readable format.
"""

import warnings
import sys
from typing import Optional


def setup_warning_filters(silent: bool = False):
    """
    Configure warning filters for clean CLI output.

    This function suppresses known non-critical dependency warnings
    (like torchcodec) that users cannot action, while allowing
    important warnings to show in a clean format.

    Args:
        silent: If True, suppress all warnings completely (for production)
    """

    if silent:
        warnings.filterwarnings("ignore")
        return

    # Suppress known non-critical dependency warnings
    # These are technical warnings that users cannot action

    # TorchCodec warnings from pyannote.audio
    # (LocalTranscribe uses pydub/FFmpeg for audio processing instead)
    warnings.filterwarnings("ignore", message=".*torchcodec.*")
    warnings.filterwarnings("ignore", message=".*libtorchcodec.*")
    warnings.filterwarnings("ignore", module="pyannote.audio.core.io")

    # FFmpeg library loading warnings (handled by pydub)
    warnings.filterwarnings("ignore", message=".*Library not loaded.*")
    warnings.filterwarnings("ignore", message=".*@rpath.*")
    warnings.filterwarnings("ignore", message=".*libavutil.*")
    warnings.filterwarnings("ignore", message=".*libavcodec.*")
    warnings.filterwarnings("ignore", message=".*libavformat.*")

    # Custom warning handler for remaining warnings
    original_showwarning = warnings.showwarning

    def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
        """
        Show clean, actionable warnings only.

        Filters out technical dependency warnings and displays
        remaining warnings in a user-friendly format.
        """
        msg_str = str(message).lower()

        # Additional runtime filtering for noise we've already addressed
        skip_patterns = [
            'torchcodec',
            'libtorchcodec',
            'ffmpeg version',
            'library not loaded',
            '@rpath',
            'libavutil',
            'libavcodec',
            'libavformat',
            'dylib',
        ]

        # Check if this warning should be filtered
        if any(skip in msg_str for skip in skip_patterns):
            return  # Silently ignore

        # Show other warnings in clean format
        try:
            from rich.console import Console
            console = Console(stderr=True)

            # Format warning nicely
            warning_type = category.__name__ if category else "Warning"
            console.print(
                f"[yellow]⚠️  {warning_type}:[/yellow] {message}",
                style="dim"
            )

            # Show location if verbose
            if filename and lineno:
                console.print(
                    f"[dim]   Location: {filename}:{lineno}[/dim]",
                    style="dim"
                )

        except ImportError:
            # Fallback to standard output if Rich not available
            warning_type = category.__name__ if category else "Warning"
            print(f"⚠️  {warning_type}: {message}", file=sys.stderr)

    warnings.showwarning = custom_warning_handler


def suppress_all_warnings():
    """
    Completely suppress all warnings.

    Useful for production/SDK use where you want absolutely
    no warning output. Use with caution.
    """
    warnings.filterwarnings("ignore")


def reset_warning_filters():
    """
    Reset warning filters to default Python behavior.

    Useful for debugging or when you want to see all warnings.
    """
    warnings.resetwarnings()
