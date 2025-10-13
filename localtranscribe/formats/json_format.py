"""
JSON formatter for LocalTranscribe.
"""

import json
from typing import List, Dict, Any

from .base import BaseFormatter, Segment


class JSONFormatter(BaseFormatter):
    """
    Format transcripts as JSON.

    Features:
    - Full metadata (duration, speakers, confidence)
    - Segment-level data
    - Speaker statistics
    - Schema versioning
    """

    SCHEMA_VERSION = "1.0"

    def format(
        self,
        segments: List[Segment],
        include_confidence: bool = True,
        include_stats: bool = True,
        **kwargs
    ) -> str:
        """
        Format segments as JSON.

        Args:
            segments: List of transcript segments
            include_confidence: Include confidence scores
            include_stats: Include speaker statistics

        Returns:
            JSON string
        """
        # Calculate metadata
        total_duration = max((seg.end for seg in segments), default=0)
        speakers = sorted(set(seg.speaker for seg in segments if seg.speaker))

        # Build JSON structure
        data: Dict[str, Any] = {
            "schema_version": self.SCHEMA_VERSION,
            "metadata": {
                "duration": total_duration,
                "num_segments": len(segments),
                "speakers": speakers,
                "num_speakers": len(speakers),
            },
            "segments": [],
        }

        # Add segments
        for i, segment in enumerate(segments):
            segment_data = {
                "id": i,
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "duration": round(segment.end - segment.start, 3),
                "text": segment.text.strip(),
            }

            if segment.speaker:
                segment_data["speaker"] = segment.speaker

            if include_confidence and segment.confidence is not None:
                segment_data["confidence"] = round(segment.confidence, 3)

            data["segments"].append(segment_data)

        # Add speaker statistics
        if include_stats and speakers:
            data["speaker_stats"] = self._calculate_speaker_stats(segments, speakers)

        return json.dumps(data, indent=2, ensure_ascii=False)

    def validate(self, content: str) -> bool:
        """
        Validate JSON content.

        Args:
            content: JSON content to validate

        Returns:
            True if valid JSON with required fields
        """
        try:
            data = json.loads(content)

            # Check required fields
            if "metadata" not in data:
                return False
            if "segments" not in data:
                return False
            if not isinstance(data["segments"], list):
                return False

            # Validate each segment
            for segment in data["segments"]:
                if not isinstance(segment, dict):
                    return False
                if "start" not in segment or "end" not in segment:
                    return False
                if "text" not in segment:
                    return False

            return True

        except (json.JSONDecodeError, KeyError, TypeError):
            return False

    def _calculate_speaker_stats(
        self, segments: List[Segment], speakers: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate speaking time statistics per speaker.

        Args:
            segments: List of segments
            speakers: List of speaker names

        Returns:
            Dictionary of speaker statistics
        """
        stats = {}

        for speaker in speakers:
            speaker_segments = [s for s in segments if s.speaker == speaker]
            total_time = sum(s.end - s.start for s in speaker_segments)
            word_count = sum(len(s.text.split()) for s in speaker_segments)

            stats[speaker] = {
                "total_time": round(total_time, 2),
                "num_segments": len(speaker_segments),
                "word_count": word_count,
                "avg_segment_duration": round(total_time / len(speaker_segments), 2)
                if speaker_segments
                else 0,
            }

        return stats
