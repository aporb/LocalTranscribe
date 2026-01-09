"""
HTML formatter for LocalTranscribe with speaker color coding.

Generates modern, responsive HTML transcripts with CSS styling and
speaker-specific colors for improved readability.
"""

from typing import List, Optional, Dict
from .base import BaseFormatter, Segment


class HTMLFormatter(BaseFormatter):
    """
    Format transcripts as styled HTML documents.

    Features:
    - Responsive design
    - Speaker-specific color coding
    - WCAG AA accessible color contrast
    - Timestamps with tooltips
    - Confidence indicators
    - Search-friendly semantic markup
    - Print-optimized styling
    """

    # Speaker color palette (WCAG AA compliant)
    SPEAKER_COLORS = [
        "#2563eb",  # Blue
        "#dc2626",  # Red
        "#059669",  # Green (darker for better contrast)
        "#ea580c",  # Orange
        "#7c3aed",  # Purple
        "#0891b2",  # Cyan
        "#ca8a04",  # Yellow (darker for better contrast)
        "#db2777",  # Pink
    ]

    def format(
        self,
        segments: List[Segment],
        include_timestamps: bool = True,
        include_speakers: bool = True,
        title: Optional[str] = None,
        add_metadata: bool = True,
        dark_mode: bool = False,
        **kwargs
    ) -> str:
        """
        Format segments as styled HTML.

        Args:
            segments: List of transcript segments
            include_timestamps: Include timestamps for each segment
            include_speakers: Include speaker labels
            title: Document title (defaults to "Transcript")
            add_metadata: Include metadata section at top
            dark_mode: Use dark mode color scheme

        Returns:
            Complete HTML document string
        """
        title_text = title or "Transcript"

        # Build speaker color map
        speaker_colors = self._build_speaker_colors(segments)

        # Generate CSS
        css = self._generate_css(speaker_colors, dark_mode)

        # Generate HTML body
        body_html = self._generate_body(
            segments,
            include_timestamps,
            include_speakers,
            add_metadata,
            speaker_colors
        )

        # Complete HTML document
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(title_text)}</title>
    <style>{css}</style>
</head>
<body class="{'dark-mode' if dark_mode else ''}">
    <div class="container">
        <header>
            <h1>{self._escape_html(title_text)}</h1>
        </header>
        {body_html}
    </div>
</body>
</html>"""

        return html

    def _build_speaker_colors(self, segments: List[Segment]) -> Dict[str, str]:
        """Build mapping of speakers to colors."""
        unique_speakers = []
        seen = set()

        for segment in segments:
            if segment.speaker and segment.speaker not in seen:
                unique_speakers.append(segment.speaker)
                seen.add(segment.speaker)

        # Assign colors
        speaker_colors = {}
        for i, speaker in enumerate(unique_speakers):
            color_index = i % len(self.SPEAKER_COLORS)
            speaker_colors[speaker] = self.SPEAKER_COLORS[color_index]

        return speaker_colors

    def _generate_css(self, speaker_colors: Dict[str, str], dark_mode: bool) -> str:
        """Generate CSS including speaker-specific styles."""
        # Base colors
        if dark_mode:
            bg_color = "#1a1a1a"
            text_color = "#e5e5e5"
            meta_color = "#a3a3a3"
            border_color = "#404040"
        else:
            bg_color = "#ffffff"
            text_color = "#1f2937"
            meta_color = "#6b7280"
            border_color = "#e5e7eb"

        # Base CSS
        css = f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: {text_color};
            background-color: {bg_color};
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background-color: {bg_color};
        }}

        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid {border_color};
            margin-bottom: 30px;
        }}

        h1 {{
            font-size: 2.5em;
            font-weight: 700;
            color: {text_color};
        }}

        .metadata {{
            background-color: {'#2a2a2a' if dark_mode else '#f9fafb'};
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
            color: {meta_color};
            font-size: 0.95em;
        }}

        .metadata-item {{
            display: inline-block;
            margin: 0 15px;
        }}

        .metadata-label {{
            font-weight: 600;
        }}

        .speakers-list {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid {border_color};
        }}

        .speaker-badge {{
            display: inline-block;
            padding: 4px 12px;
            margin: 4px;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: 600;
            color: white;
        }}

        .transcript {{
            margin-top: 30px;
        }}

        .speaker-section {{
            margin-bottom: 30px;
        }}

        .speaker-heading {{
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid currentColor;
        }}

        .segment {{
            margin-bottom: 12px;
            padding: 10px 0;
        }}

        .timestamp {{
            display: inline-block;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: {meta_color};
            margin-right: 10px;
            min-width: 100px;
        }}

        .text {{
            display: inline;
            font-size: 1.05em;
        }}

        .confidence {{
            display: inline-block;
            margin-left: 8px;
            font-size: 0.8em;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
        }}

        .confidence-high {{
            background-color: #d1fae5;
            color: #065f46;
        }}

        .dark-mode .confidence-high {{
            background-color: #064e3b;
            color: #6ee7b7;
        }}

        .confidence-medium {{
            background-color: #fef3c7;
            color: #92400e;
        }}

        .dark-mode .confidence-medium {{
            background-color: #78350f;
            color: #fde68a;
        }}

        .confidence-low {{
            background-color: #fee2e2;
            color: #991b1b;
        }}

        .dark-mode .confidence-low {{
            background-color: #7f1d1d;
            color: #fca5a5;
        }}

        /* Print styles */
        @media print {{
            body {{
                background-color: white;
                color: black;
            }}

            .container {{
                max-width: 100%;
            }}

            .segment {{
                page-break-inside: avoid;
            }}

            .speaker-section {{
                page-break-inside: avoid;
            }}
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}

            h1 {{
                font-size: 2em;
            }}

            .timestamp {{
                display: block;
                margin-bottom: 5px;
            }}
        }}
"""

        # Add speaker-specific colors
        for speaker, color in speaker_colors.items():
            safe_speaker = self._css_safe_name(speaker)
            css += f"""
        .speaker-{safe_speaker} .speaker-heading {{
            color: {color};
        }}

        .speaker-badge-{safe_speaker} {{
            background-color: {color};
        }}
"""

        return css

    def _generate_body(
        self,
        segments: List[Segment],
        include_timestamps: bool,
        include_speakers: bool,
        add_metadata: bool,
        speaker_colors: Dict[str, str]
    ) -> str:
        """Generate HTML body content."""
        html_parts = []

        # Add metadata
        if add_metadata and segments:
            html_parts.append(self._generate_metadata(segments, speaker_colors))

        # Add transcript
        html_parts.append('<div class="transcript">')

        current_speaker = None
        current_section = []

        for segment in segments:
            # Start new speaker section if speaker changed
            if include_speakers and segment.speaker != current_speaker:
                # Close previous section
                if current_section:
                    html_parts.append(self._close_speaker_section(current_section))
                    current_section = []

                # Start new section
                current_speaker = segment.speaker
                if segment.speaker:
                    safe_speaker = self._css_safe_name(segment.speaker)
                    current_section.append(
                        f'<div class="speaker-section speaker-{safe_speaker}">'
                    )
                    current_section.append(
                        f'<h2 class="speaker-heading">{self._escape_html(segment.speaker)}</h2>'
                    )

            # Add segment
            segment_html = self._generate_segment(segment, include_timestamps)
            current_section.append(segment_html)

        # Close final section
        if current_section:
            html_parts.append(self._close_speaker_section(current_section))

        html_parts.append('</div>')  # Close transcript

        return '\n'.join(html_parts)

    def _generate_metadata(self, segments: List[Segment], speaker_colors: Dict[str, str]) -> str:
        """Generate metadata section HTML."""
        # Calculate metadata
        total_duration = segments[-1].end if segments else 0
        speaker_count = len(speaker_colors)
        segment_count = len(segments)

        # Average confidence
        confidences = [s.confidence for s in segments if s.confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        html = '<div class="metadata">'
        html += '<div class="metadata-items">'

        # Duration
        html += f'<span class="metadata-item"><span class="metadata-label">Duration:</span> {self._format_duration(total_duration)}</span>'

        # Speakers
        html += f'<span class="metadata-item"><span class="metadata-label">Speakers:</span> {speaker_count}</span>'

        # Segments
        html += f'<span class="metadata-item"><span class="metadata-label">Segments:</span> {segment_count}</span>'

        # Confidence
        if avg_confidence is not None:
            html += f'<span class="metadata-item"><span class="metadata-label">Avg. Confidence:</span> {avg_confidence:.1%}</span>'

        html += '</div>'  # Close metadata-items

        # Speaker list
        if speaker_colors:
            html += '<div class="speakers-list">'
            html += '<span class="metadata-label">Speakers: </span>'
            for speaker in sorted(speaker_colors.keys()):
                safe_speaker = self._css_safe_name(speaker)
                html += f'<span class="speaker-badge speaker-badge-{safe_speaker}">{self._escape_html(speaker)}</span>'
            html += '</div>'

        html += '</div>'  # Close metadata

        return html

    def _generate_segment(self, segment: Segment, include_timestamps: bool) -> str:
        """Generate HTML for a single segment."""
        html = '<div class="segment">'

        # Timestamp
        if include_timestamps:
            timestamp = self._format_timestamp(segment.start, segment.end)
            html += f'<span class="timestamp">{timestamp}</span>'

        # Text
        html += f'<span class="text">{self._escape_html(segment.text.strip())}</span>'

        # Confidence
        if segment.confidence is not None:
            conf_pct = int(segment.confidence * 100)
            conf_class = self._get_confidence_class(segment.confidence)
            html += f'<span class="confidence {conf_class}">{conf_pct}%</span>'

        html += '</div>'

        return html

    def _close_speaker_section(self, section_parts: List[str]) -> str:
        """Close a speaker section."""
        section_parts.append('</div>')  # Close speaker-section
        return '\n'.join(section_parts)

    def _get_confidence_class(self, confidence: float) -> str:
        """Get CSS class for confidence level."""
        if confidence >= 0.9:
            return "confidence-high"
        elif confidence >= 0.7:
            return "confidence-medium"
        else:
            return "confidence-low"

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

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _css_safe_name(self, name: str) -> str:
        """Convert speaker name to CSS-safe class name."""
        # Replace non-alphanumeric with hyphens
        import re
        safe = re.sub(r'[^a-zA-Z0-9]+', '-', name)
        # Remove leading/trailing hyphens
        safe = safe.strip('-')
        # Ensure it doesn't start with a number
        if safe and safe[0].isdigit():
            safe = 'speaker-' + safe
        return safe.lower()

    def validate(self, content: str) -> bool:
        """
        Validate HTML content.

        Args:
            content: HTML content to validate

        Returns:
            True if valid HTML
        """
        # Basic validation: check for required tags
        required_tags = ['<!DOCTYPE html>', '<html', '</html>', '<body', '</body>']
        return all(tag in content for tag in required_tags)

    def get_extension(self) -> str:
        """Get file extension for HTML format."""
        return "html"
