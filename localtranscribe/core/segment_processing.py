"""
Segment post-processing for improved diarization quality.

This module provides functionality to clean and optimize diarization segments
by filtering micro-segments, merging consecutive same-speaker segments, and
applying temporal smoothing to reduce false speaker switches.

Based on research and best practices from pyannote.audio and the IMPROVEMENT_PLAN.md.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SegmentProcessingConfig:
    """Configuration for segment post-processing.

    Attributes:
        min_segment_duration: Minimum duration (seconds) for a segment to be kept.
            Segments shorter than this are filtered out.
        merge_gap_threshold: Maximum gap (seconds) between consecutive same-speaker
            segments to merge them together.
        min_speaker_turn: Minimum duration (seconds) for a speaker turn after merging.
        smoothing_window: Time window (seconds) for temporal smoothing of speaker transitions.
        enabled: Whether segment processing is enabled.
    """
    min_segment_duration: float = 0.3
    merge_gap_threshold: float = 1.0
    min_speaker_turn: float = 2.0
    smoothing_window: float = 2.0
    enabled: bool = True


@dataclass
class SegmentProcessingStats:
    """Statistics about segment processing operations.

    Tracks what changes were made during post-processing for analysis and debugging.
    """
    original_segment_count: int = 0
    filtered_segment_count: int = 0
    merged_segment_count: int = 0
    smoothed_segment_count: int = 0
    final_segment_count: int = 0
    micro_segments_removed: int = 0
    speaker_switches_before: int = 0
    speaker_switches_after: int = 0
    avg_segment_duration_before: float = 0.0
    avg_segment_duration_after: float = 0.0


class SegmentProcessor:
    """Post-process diarization segments for improved quality.

    This class implements various segment cleaning and optimization algorithms
    to reduce common diarization issues like over-segmentation and false
    speaker switches.

    Example:
        >>> config = SegmentProcessingConfig(min_segment_duration=0.3)
        >>> processor = SegmentProcessor(config)
        >>> cleaned_result = processor.process(diarization_result)
        >>> print(f"Reduced segments from {cleaned_result.metadata['processing_stats']['original_segment_count']} "
        ...       f"to {cleaned_result.metadata['processing_stats']['final_segment_count']}")
    """

    def __init__(self, config: Optional[SegmentProcessingConfig] = None):
        """Initialize segment processor with configuration.

        Args:
            config: Configuration for processing. If None, uses default values.
        """
        self.config = config or SegmentProcessingConfig()
        logger.info(f"Initialized SegmentProcessor with config: {self.config}")

    def process(self, diarization_result):
        """Process diarization result to improve segment quality.

        Applies a series of post-processing steps:
        1. Filter micro-segments (< min_segment_duration)
        2. Merge consecutive same-speaker segments
        3. Smooth speaker transitions to reduce ping-pong effects

        Args:
            diarization_result: DiarizationResult object with segments to process

        Returns:
            Modified DiarizationResult with cleaned segments and processing statistics
        """
        if not self.config.enabled:
            logger.info("Segment processing is disabled, returning original result")
            return diarization_result

        if not diarization_result.success:
            logger.warning("Diarization was not successful, skipping segment processing")
            return diarization_result

        segments = diarization_result.segments
        if not segments:
            logger.warning("No segments to process")
            return diarization_result

        # Initialize statistics
        stats = SegmentProcessingStats()
        stats.original_segment_count = len(segments)
        stats.speaker_switches_before = self._count_speaker_switches(segments)
        stats.avg_segment_duration_before = self._calculate_avg_duration(segments)

        logger.info(f"Processing {len(segments)} segments...")
        logger.info(f"Original stats: {stats.speaker_switches_before} speaker switches, "
                   f"avg duration {stats.avg_segment_duration_before:.2f}s")

        # Step 1: Filter micro-segments
        segments = self._filter_micro_segments(segments, stats)
        logger.info(f"After filtering: {len(segments)} segments "
                   f"({stats.micro_segments_removed} micro-segments removed)")

        # Step 2: Merge consecutive same-speaker segments
        segments = self._merge_consecutive_segments(segments, stats)
        logger.info(f"After merging: {len(segments)} segments")

        # Step 3: Smooth speaker transitions
        segments = self._smooth_speaker_transitions(segments, stats)
        logger.info(f"After smoothing: {len(segments)} segments "
                   f"({stats.smoothed_segment_count} transitions smoothed)")

        # Update final statistics
        stats.final_segment_count = len(segments)
        stats.speaker_switches_after = self._count_speaker_switches(segments)
        stats.avg_segment_duration_after = self._calculate_avg_duration(segments)

        # Recalculate speaker durations
        speaker_durations = self._calculate_speaker_durations(segments)

        # Update the result
        diarization_result.segments = segments
        diarization_result.speaker_durations = speaker_durations

        # Add processing stats to metadata
        if 'segment_processing' not in diarization_result.metadata:
            diarization_result.metadata['segment_processing'] = {}

        diarization_result.metadata['segment_processing']['stats'] = {
            'original_segment_count': stats.original_segment_count,
            'final_segment_count': stats.final_segment_count,
            'micro_segments_removed': stats.micro_segments_removed,
            'merged_segment_count': stats.merged_segment_count,
            'smoothed_segment_count': stats.smoothed_segment_count,
            'speaker_switches_before': stats.speaker_switches_before,
            'speaker_switches_after': stats.speaker_switches_after,
            'switch_reduction_pct': (
                100 * (stats.speaker_switches_before - stats.speaker_switches_after) /
                stats.speaker_switches_before if stats.speaker_switches_before > 0 else 0
            ),
            'avg_segment_duration_before': stats.avg_segment_duration_before,
            'avg_segment_duration_after': stats.avg_segment_duration_after,
            'duration_improvement_pct': (
                100 * (stats.avg_segment_duration_after - stats.avg_segment_duration_before) /
                stats.avg_segment_duration_before if stats.avg_segment_duration_before > 0 else 0
            )
        }
        diarization_result.metadata['segment_processing']['config'] = {
            'min_segment_duration': self.config.min_segment_duration,
            'merge_gap_threshold': self.config.merge_gap_threshold,
            'smoothing_window': self.config.smoothing_window
        }

        logger.info(f"Segment processing complete: {stats.original_segment_count} → "
                   f"{stats.final_segment_count} segments "
                   f"({100 * (stats.original_segment_count - stats.final_segment_count) / stats.original_segment_count:.1f}% reduction)")
        logger.info(f"Speaker switches: {stats.speaker_switches_before} → {stats.speaker_switches_after} "
                   f"({100 * (stats.speaker_switches_before - stats.speaker_switches_after) / stats.speaker_switches_before:.1f}% reduction)")
        logger.info(f"Avg segment duration: {stats.avg_segment_duration_before:.2f}s → "
                   f"{stats.avg_segment_duration_after:.2f}s")

        return diarization_result

    def _filter_micro_segments(self, segments: List[Dict[str, Any]], stats: SegmentProcessingStats) -> List[Dict[str, Any]]:
        """Filter out micro-segments below minimum duration threshold.

        Args:
            segments: List of segment dicts with 'start', 'end', 'duration', 'speaker'
            stats: Statistics object to update

        Returns:
            Filtered list of segments
        """
        filtered = []
        for seg in segments:
            if seg['duration'] >= self.config.min_segment_duration:
                filtered.append(seg)
            else:
                stats.micro_segments_removed += 1

        stats.filtered_segment_count = len(filtered)
        return filtered

    def _merge_consecutive_segments(self, segments: List[Dict[str, Any]], stats: SegmentProcessingStats) -> List[Dict[str, Any]]:
        """Merge consecutive segments from the same speaker within gap threshold.

        Args:
            segments: List of segment dicts
            stats: Statistics object to update

        Returns:
            Merged list of segments
        """
        if not segments:
            return segments

        merged = []
        current = segments[0].copy()

        for next_seg in segments[1:]:
            # Check if same speaker and within gap threshold
            gap = next_seg['start'] - current['end']

            if (next_seg['speaker'] == current['speaker'] and
                gap <= self.config.merge_gap_threshold):
                # Merge: extend current segment to include next
                current['end'] = next_seg['end']
                current['duration'] = current['end'] - current['start']
                stats.merged_segment_count += 1
            else:
                # Different speaker or gap too large, save current and start new
                merged.append(current)
                current = next_seg.copy()

        # Don't forget the last segment
        merged.append(current)

        return merged

    def _smooth_speaker_transitions(self, segments: List[Dict[str, Any]], stats: SegmentProcessingStats) -> List[Dict[str, Any]]:
        """Apply temporal smoothing to reduce ping-pong speaker switches.

        If a speaker segment is very short and surrounded by the same different speaker,
        it's likely a misclassification and should be reassigned.

        Args:
            segments: List of segment dicts
            stats: Statistics object to update

        Returns:
            Smoothed list of segments
        """
        if len(segments) < 3:
            return segments

        smoothed = segments.copy()

        # Look for short segments surrounded by the same speaker
        for i in range(1, len(smoothed) - 1):
            prev = smoothed[i - 1]
            curr = smoothed[i]
            next_seg = smoothed[i + 1]

            # If current is short and surrounded by same speaker (but not current speaker)
            if (curr['duration'] < self.config.smoothing_window and
                prev['speaker'] == next_seg['speaker'] and
                prev['speaker'] != curr['speaker']):

                # Reassign current to surrounding speaker
                logger.debug(f"Smoothing transition: reassigning segment at {curr['start']:.2f}s "
                           f"from {curr['speaker']} to {prev['speaker']}")
                curr['speaker'] = prev['speaker']
                stats.smoothed_segment_count += 1

        # After reassignment, we might have created new consecutive same-speaker segments
        # So merge again
        merged = []
        if smoothed:
            current = smoothed[0].copy()

            for next_seg in smoothed[1:]:
                if next_seg['speaker'] == current['speaker']:
                    # Merge adjacent same-speaker segments
                    current['end'] = next_seg['end']
                    current['duration'] = current['end'] - current['start']
                else:
                    merged.append(current)
                    current = next_seg.copy()

            merged.append(current)

        return merged

    def _count_speaker_switches(self, segments: List[Dict[str, Any]]) -> int:
        """Count the number of speaker switches in segments.

        Args:
            segments: List of segment dicts

        Returns:
            Number of speaker switches
        """
        if len(segments) < 2:
            return 0

        switches = 0
        for i in range(1, len(segments)):
            if segments[i]['speaker'] != segments[i - 1]['speaker']:
                switches += 1

        return switches

    def _calculate_avg_duration(self, segments: List[Dict[str, Any]]) -> float:
        """Calculate average segment duration.

        Args:
            segments: List of segment dicts

        Returns:
            Average duration in seconds
        """
        if not segments:
            return 0.0

        total_duration = sum(seg['duration'] for seg in segments)
        return total_duration / len(segments)

    def _calculate_speaker_durations(self, segments: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate total speaking time per speaker.

        Args:
            segments: List of segment dicts

        Returns:
            Dict mapping speaker ID to total duration
        """
        durations = {}
        for seg in segments:
            speaker = seg['speaker']
            if speaker not in durations:
                durations[speaker] = 0.0
            durations[speaker] += seg['duration']

        return durations


def process_segments(diarization_result, config: Optional[SegmentProcessingConfig] = None):
    """Convenience function to process diarization segments.

    Args:
        diarization_result: DiarizationResult to process
        config: Optional configuration. If None, uses defaults.

    Returns:
        Processed DiarizationResult
    """
    processor = SegmentProcessor(config)
    return processor.process(diarization_result)
