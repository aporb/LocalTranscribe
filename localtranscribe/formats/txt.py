"""
Plain text formatter for LocalTranscribe.
"""

from typing import List

from .base import BaseFormatter, Segment


class TXTFormatter(BaseFormatter):
    """
    Format transcripts as plain text.

    Features:
    - Speaker labels
    - Optional timestamps
    - Clean paragraph formatting
    """

    def format(
        self,
        segments: List[Segment],
        include_timestamps: bool = False,
        include_speakers: bool = True,
        **kwargs
    ) -> str:
        """
        Format segments as plain text.

        Args:
            segments: List of transcript segments
            include_timestamps: Include timestamp for each segment
            include_speakers: Include speaker labels

        Returns:
            Plain text transcript
        """
        lines = []
        current_speaker = None

        for segment in segments:
            # Group by speaker
            if include_speakers and segment.speaker != current_speaker:
                if current_speaker is not None:
                    lines.append("")  # Blank line between speakers

                current_speaker = segment.speaker

                # Add speaker label
                if segment.speaker:
                    lines.append(f"{segment.speaker}:")

            # Format segment
            text = segment.text.strip()

            if include_timestamps:
                timestamp = self._format_timestamp(segment.start, segment.end)
                lines.append(f"[{timestamp}] {text}")
            else:
                lines.append(text)

        return "\n".join(lines)

    def validate(self, content: str) -> bool:
        """
        Validate plain text content.

        Args:
            content: Content to validate

        Returns:
            True if valid
        """
        # Plain text is always valid if non-empty
        return bool(content.strip())

    def _format_timestamp(self, start: float, end: float) -> str:
        """
        Format timestamp for display.

        Args:
            start: Start time in seconds
            end: End time in seconds

        Returns:
            Formatted timestamp string
        """
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)

            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"

        return f"{format_time(start)} - {format_time(end)}"
