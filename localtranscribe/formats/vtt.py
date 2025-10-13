"""
VTT (WebVTT) subtitle formatter for LocalTranscribe.
"""

from typing import List

from .base import BaseFormatter, Segment


class VTTFormatter(BaseFormatter):
    """
    Format transcripts as WebVTT subtitles.

    Features:
    - WebVTT header
    - Cue identifiers
    - Speaker tags (<v>)
    - Style support
    """

    MAX_LINE_LENGTH = 42  # Standard subtitle line length

    def format(
        self,
        segments: List[Segment],
        include_speakers: bool = True,
        use_voice_tags: bool = True,
        max_line_length: int = None,
        **kwargs
    ) -> str:
        """
        Format segments as WebVTT subtitles.

        Args:
            segments: List of transcript segments
            include_speakers: Include speaker information
            use_voice_tags: Use <v> tags for speakers
            max_line_length: Maximum characters per line

        Returns:
            WebVTT formatted string
        """
        if max_line_length is None:
            max_line_length = self.MAX_LINE_LENGTH

        # Start with WebVTT header
        lines = ["WEBVTT", ""]

        for i, segment in enumerate(segments, start=1):
            # Cue identifier
            lines.append(f"cue-{i}")

            # Format timestamps
            start_time = self._format_timecode(segment.start)
            end_time = self._format_timecode(segment.end)
            lines.append(f"{start_time} --> {end_time}")

            # Format text with speaker
            text = segment.text.strip()

            if include_speakers and segment.speaker:
                if use_voice_tags:
                    text = f"<v {segment.speaker}>{text}</v>"
                else:
                    text = f"{segment.speaker}: {text}"

            # Wrap text if needed
            wrapped_text = self._wrap_text(text, max_line_length)
            lines.append(wrapped_text)

            # Blank line between cues
            lines.append("")

        return "\n".join(lines)

    def validate(self, content: str) -> bool:
        """
        Validate WebVTT content.

        Args:
            content: WebVTT content to validate

        Returns:
            True if valid WebVTT format
        """
        if not content.strip():
            return False

        lines = content.strip().split("\n")

        # Must start with WEBVTT header
        if not lines[0].startswith("WEBVTT"):
            return False

        # Check for timecode patterns
        has_timecodes = any(" --> " in line for line in lines)
        if not has_timecodes:
            return False

        return True

    def _format_timecode(self, seconds: float) -> str:
        """
        Format seconds to WebVTT timecode (HH:MM:SS.mmm).

        Args:
            seconds: Time in seconds

        Returns:
            WebVTT timecode string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def _wrap_text(self, text: str, max_length: int) -> str:
        """
        Wrap text to fit subtitle line length requirements.

        Args:
            text: Text to wrap
            max_length: Maximum characters per line

        Returns:
            Wrapped text with newlines
        """
        # Handle voice tags separately
        if text.startswith("<v "):
            # Extract speaker and content
            tag_end = text.index(">")
            voice_tag = text[: tag_end + 1]
            content = text[tag_end + 1 : -4]  # Remove </v>

            if len(content) <= max_length:
                return text

            # Wrap content only
            wrapped = self._simple_wrap(content, max_length)
            return f"{voice_tag}{wrapped}</v>"
        else:
            return self._simple_wrap(text, max_length)

    def _simple_wrap(self, text: str, max_length: int) -> str:
        """
        Simple word-based text wrapping.

        Args:
            text: Text to wrap
            max_length: Maximum line length

        Returns:
            Wrapped text
        """
        if len(text) <= max_length:
            return text

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word) + (1 if current_line else 0)

            if current_length + word_length <= max_length:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)
