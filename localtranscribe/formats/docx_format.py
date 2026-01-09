"""
DOCX (Microsoft Word) formatter for LocalTranscribe.

Generates professional Word documents with proper formatting, speaker labels,
and optional styling.
"""

from typing import List, Optional
from pathlib import Path

from .base import BaseFormatter, Segment


class DOCXFormatter(BaseFormatter):
    """
    Format transcripts as Microsoft Word (.docx) documents.

    Features:
    - Professional document styling
    - Speaker-specific text formatting
    - Optional timestamps
    - Table of contents support
    - Metadata (duration, speaker count)

    Requires: python-docx library
    """

    def format(
        self,
        segments: List[Segment],
        include_timestamps: bool = True,
        include_speakers: bool = True,
        title: Optional[str] = None,
        add_metadata: bool = True,
        **kwargs
    ) -> bytes:
        """
        Format segments as a Word document.

        Args:
            segments: List of transcript segments
            include_timestamps: Include timestamps for each segment
            include_speakers: Include speaker labels
            title: Document title (defaults to "Transcript")
            add_metadata: Include metadata section at top

        Returns:
            DOCX file content as bytes
        """
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor, Inches
            from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
        except ImportError:
            raise ImportError(
                "python-docx is required for DOCX export. "
                "Install with: pip install python-docx"
            )

        # Create document
        doc = Document()

        # Add title
        title_text = title or "Transcript"
        heading = doc.add_heading(title_text, level=1)
        heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Add metadata
        if add_metadata and segments:
            self._add_metadata(doc, segments)

        # Add transcript content
        current_speaker = None

        for segment in segments:
            # Add speaker heading when speaker changes
            if include_speakers and segment.speaker != current_speaker:
                if current_speaker is not None:
                    # Add spacing between speakers
                    doc.add_paragraph()

                current_speaker = segment.speaker

                # Add speaker heading
                if segment.speaker:
                    speaker_heading = doc.add_heading(segment.speaker, level=2)
                    # Style speaker heading
                    for run in speaker_heading.runs:
                        run.font.color.rgb = self._get_speaker_color(segment.speaker)
                        run.font.size = Pt(14)

            # Add segment text
            text = segment.text.strip()

            if include_timestamps:
                # Add timestamp with text
                p = doc.add_paragraph()

                # Timestamp in gray
                timestamp_run = p.add_run(
                    f"[{self._format_timestamp(segment.start, segment.end)}] "
                )
                timestamp_run.font.color.rgb = RGBColor(128, 128, 128)
                timestamp_run.font.size = Pt(10)

                # Text in normal color
                text_run = p.add_run(text)
                text_run.font.size = Pt(11)

                # Add confidence indicator if available
                if segment.confidence is not None:
                    confidence_pct = int(segment.confidence * 100)
                    conf_run = p.add_run(f" ({confidence_pct}%)")
                    conf_run.font.size = Pt(9)
                    conf_run.font.color.rgb = self._get_confidence_color(segment.confidence)
            else:
                # Just text
                p = doc.add_paragraph(text)
                p.style = 'Body Text'

        # Return document as bytes
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_metadata(self, doc, segments: List[Segment]):
        """Add metadata section to document."""
        from docx.shared import Pt, RGBColor

        # Calculate metadata
        total_duration = segments[-1].end if segments else 0
        unique_speakers = set(s.speaker for s in segments if s.speaker)
        speaker_count = len(unique_speakers)
        segment_count = len(segments)

        # Average confidence
        confidences = [s.confidence for s in segments if s.confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        # Add metadata paragraph
        p = doc.add_paragraph()
        p.alignment = 1  # Center

        # Duration
        duration_run = p.add_run(f"Duration: {self._format_duration(total_duration)} | ")
        duration_run.font.size = Pt(10)
        duration_run.font.color.rgb = RGBColor(100, 100, 100)

        # Speakers
        speakers_run = p.add_run(f"Speakers: {speaker_count} | ")
        speakers_run.font.size = Pt(10)
        speakers_run.font.color.rgb = RGBColor(100, 100, 100)

        # Segments
        segments_run = p.add_run(f"Segments: {segment_count}")
        segments_run.font.size = Pt(10)
        segments_run.font.color.rgb = RGBColor(100, 100, 100)

        # Confidence if available
        if avg_confidence is not None:
            conf_run = p.add_run(f" | Avg. Confidence: {avg_confidence:.1%}")
            conf_run.font.size = Pt(10)
            conf_run.font.color.rgb = RGBColor(100, 100, 100)

        # Add separator
        doc.add_paragraph()

        # List speakers if present
        if unique_speakers:
            speakers_p = doc.add_paragraph()
            speakers_p.add_run("Speakers: ").bold = True
            for speaker in sorted(unique_speakers):
                speaker_run = speakers_p.add_run(f"{speaker}, ")
                speaker_run.font.color.rgb = self._get_speaker_color(speaker)

            doc.add_paragraph()  # Spacing

    def _get_speaker_color(self, speaker: str) -> 'RGBColor':
        """Get consistent color for a speaker based on their name."""
        from docx.shared import RGBColor

        # Color palette for speakers
        colors = [
            RGBColor(37, 99, 235),    # Blue
            RGBColor(220, 38, 38),    # Red
            RGBColor(22, 163, 74),    # Green
            RGBColor(234, 88, 12),    # Orange
            RGBColor(147, 51, 234),   # Purple
            RGBColor(6, 182, 212),    # Cyan
            RGBColor(234, 179, 8),    # Yellow
            RGBColor(219, 39, 119),   # Pink
        ]

        # Use hash of speaker name to deterministically assign color
        if speaker:
            index = hash(speaker) % len(colors)
            return colors[index]

        return RGBColor(0, 0, 0)  # Black default

    def _get_confidence_color(self, confidence: float) -> 'RGBColor':
        """Get color based on confidence level."""
        from docx.shared import RGBColor

        if confidence >= 0.9:
            return RGBColor(22, 163, 74)  # Green - high confidence
        elif confidence >= 0.7:
            return RGBColor(234, 179, 8)  # Yellow - medium confidence
        else:
            return RGBColor(220, 38, 38)  # Red - low confidence

    def _format_timestamp(self, start: float, end: float) -> str:
        """Format timestamp for display."""
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)

            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"

        return f"{format_time(start)} - {format_time(end)}"

    def _format_duration(self, seconds: float) -> str:
        """Format total duration."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

    def validate(self, content: bytes) -> bool:
        """
        Validate DOCX content.

        Args:
            content: DOCX file content as bytes

        Returns:
            True if valid DOCX file
        """
        try:
            from docx import Document
            from io import BytesIO

            # Try to load as Document
            doc = Document(BytesIO(content))

            # Check has paragraphs
            return len(doc.paragraphs) > 0
        except Exception:
            return False

    def get_extension(self) -> str:
        """Get file extension for DOCX format."""
        return "docx"

    def save_to_file(self, segments: List[Segment], filepath: Path, **kwargs):
        """
        Save formatted document directly to file.

        Args:
            segments: List of transcript segments
            filepath: Output file path
            **kwargs: Additional formatting options
        """
        content = self.format(segments, **kwargs)

        with open(filepath, 'wb') as f:
            f.write(content)
