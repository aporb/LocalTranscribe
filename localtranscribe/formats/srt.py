"""
SRT (SubRip) subtitle formatter for LocalTranscribe.
"""

from typing import List

from .base import BaseFormatter, Segment


class SRTFormatter(BaseFormatter):
    """
    Format transcripts as SRT subtitles.

    Features:
    - Sequential numbering
    - Timecode format (00:00:00,000)
    - Speaker labels in text
    - Max line length enforcement
    """

    MAX_LINE_LENGTH = 42  # Standard subtitle line length
    MAX_LINES = 2  # Maximum lines per subtitle

    def format(
        self,
        segments: List[Segment],
        include_speakers: bool = True,
        max_line_length: int = None,
        **kwargs
    ) -> str:
        """
        Format segments as SRT subtitles.

        Args:
            segments: List of transcript segments
            include_speakers: Include speaker labels in subtitle text
            max_line_length: Maximum characters per line

        Returns:
            SRT formatted string
        """
        if max_line_length is None:
            max_line_length = self.MAX_LINE_LENGTH

        srt_blocks = []

        for i, segment in enumerate(segments, start=1):
            # Format timestamps
            start_time = self._format_timecode(segment.start)
            end_time = self._format_timecode(segment.end)

            # Format text
            text = segment.text.strip()

            if include_speakers and segment.speaker:
                text = f"{segment.speaker}: {text}"

            # Wrap text if too long
            wrapped_text = self._wrap_text(text, max_line_length)

            # Build SRT block
            srt_block = f"{i}\n{start_time} --> {end_time}\n{wrapped_text}\n"
            srt_blocks.append(srt_block)

        return "\n".join(srt_blocks)

    def validate(self, content: str) -> bool:
        """
        Validate SRT content.

        Args:
            content: SRT content to validate

        Returns:
            True if valid SRT format
        """
        if not content.strip():
            return False

        # Split into blocks
        blocks = content.strip().split("\n\n")

        for block in blocks:
            lines = block.split("\n")

            # Each block should have at least 3 lines: number, timecode, text
            if len(lines) < 3:
                return False

            # First line should be a number
            try:
                int(lines[0])
            except ValueError:
                return False

            # Second line should be timecode
            if " --> " not in lines[1]:
                return False

        return True

    def _format_timecode(self, seconds: float) -> str:
        """
        Format seconds to SRT timecode (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            SRT timecode string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _wrap_text(self, text: str, max_length: int) -> str:
        """
        Wrap text to fit subtitle line length requirements.

        Args:
            text: Text to wrap
            max_length: Maximum characters per line

        Returns:
            Wrapped text with newlines
        """
        if len(text) <= max_length:
            return text

        # Simple word-based wrapping
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word) + (1 if current_line else 0)  # +1 for space

            if current_length + word_length <= max_length:
                current_line.append(word)
                current_length += word_length
            else:
                # Start new line
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        # Add remaining words
        if current_line:
            lines.append(" ".join(current_line))

        # Limit to MAX_LINES
        if len(lines) > self.MAX_LINES:
            lines = lines[: self.MAX_LINES]
            # Add ellipsis to last line
            lines[-1] += "..."

        return "\n".join(lines)
