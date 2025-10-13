"""
Combine speaker diarization and transcription results.

Maps speakers to transcription segments and creates speaker-labeled transcripts.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import datetime

from ..utils.errors import CombinationError
from .transcription import TranscriptionSegment
from .diarization import DiarizationResult
from .transcription import TranscriptionResult


@dataclass
class EnhancedSegment:
    """Transcription segment enhanced with speaker information."""

    start: float
    end: float
    text: str
    speaker: str
    speaker_confidence: float
    transcription_quality: float
    combined_confidence: float
    avg_logprob: float = 0.0
    no_speech_prob: float = 0.0
    compression_ratio: float = 1.0


@dataclass
class CombinationResult:
    """Result of combining diarization and transcription."""

    success: bool
    audio_file: Path
    segments: List[EnhancedSegment]
    num_speakers: int
    speaker_durations: Dict[str, float]
    output_file: Optional[Path] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def map_speakers_to_segments(
    diarization_segments: List[Dict[str, Any]], transcription_segments: List[TranscriptionSegment]
) -> List[EnhancedSegment]:
    """
    Map speakers to transcription segments based on time overlap.

    Uses confidence scoring based on overlap percentage and transcription quality.

    Args:
        diarization_segments: List of diarization segments with speaker labels
        transcription_segments: List of transcription segments

    Returns:
        List of enhanced segments with speaker labels and confidence scores
    """
    enhanced_segments = []

    for trans_seg in transcription_segments:
        trans_start = trans_seg.start
        trans_end = trans_seg.end
        trans_duration = trans_end - trans_start

        # Find speaker with most overlap
        best_overlap = 0
        best_speaker = 'UNKNOWN'
        best_confidence = 0.0

        for dia_seg in diarization_segments:
            dia_start = dia_seg['start']
            dia_end = dia_seg['end']

            # Calculate overlap
            overlap_start = max(trans_start, dia_start)
            overlap_end = min(trans_end, dia_end)
            overlap_duration = max(0, overlap_end - overlap_start)

            if overlap_duration > best_overlap:
                best_overlap = overlap_duration
                best_speaker = dia_seg['speaker']
                best_confidence = overlap_duration / trans_duration if trans_duration > 0 else 0.0

        # If no overlap, use nearest speaker with low confidence
        if best_overlap == 0:
            min_distance = float('inf')
            for dia_seg in diarization_segments:
                dia_start = dia_seg['start']
                dia_end = dia_seg['end']

                # Calculate distance to nearest boundary
                distance = min(
                    abs(trans_start - dia_end),
                    abs(trans_end - dia_start),
                    abs(trans_start - dia_start),
                    abs(trans_end - dia_end),
                )

                if distance < min_distance:
                    min_distance = distance
                    best_speaker = dia_seg['speaker']
                    best_confidence = 0.1  # Low confidence for distance-based

        # Calculate transcription quality metrics
        avg_logprob = trans_seg.avg_logprob
        no_speech_prob = trans_seg.no_speech_prob
        compression_ratio = trans_seg.compression_ratio

        # Transcription quality score (0-1)
        transcription_quality = max(0.0, min(1.0, (1.0 - no_speech_prob) * (1.0 - abs(avg_logprob) / 10.0)))

        # Combined confidence
        combined_confidence = best_confidence * transcription_quality

        enhanced_segments.append(
            EnhancedSegment(
                start=trans_start,
                end=trans_end,
                text=trans_seg.text,
                speaker=best_speaker,
                speaker_confidence=best_confidence,
                transcription_quality=transcription_quality,
                combined_confidence=combined_confidence,
                avg_logprob=avg_logprob,
                no_speech_prob=no_speech_prob,
                compression_ratio=compression_ratio,
            )
        )

    return enhanced_segments


def create_combined_transcript(
    enhanced_segments: List[EnhancedSegment], audio_file: Path, include_confidence: bool = True
) -> str:
    """
    Create formatted transcript with speaker labels.

    Args:
        enhanced_segments: List of segments with speaker labels
        audio_file: Original audio file path
        include_confidence: Whether to include confidence scores in output

    Returns:
        Formatted markdown transcript
    """
    lines = []

    # Header
    lines.append(f"# Combined Speaker Diarization and Transcription\n")
    lines.append(f"**Audio File:** {audio_file.name}\n")
    lines.append(f"**Processing Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"\n## Full Transcript with Speaker Labels\n")

    # Group consecutive segments by speaker
    current_speaker = None
    current_segments = []

    for seg in enhanced_segments:
        if seg.speaker != current_speaker:
            # Process previous group
            if current_segments:
                combined_text = " ".join([s.text.strip() for s in current_segments])
                first_start = f"{current_segments[0].start:.3f}s"
                last_end = f"{current_segments[-1].end:.3f}s"

                lines.append(f"### {current_speaker}\n")
                lines.append(f"**Time:** [{first_start} - {last_end}]\n")
                lines.append(f"\n{combined_text}\n")

            current_speaker = seg.speaker
            current_segments = [seg]
        else:
            current_segments.append(seg)

    # Process last group
    if current_segments:
        combined_text = " ".join([s.text.strip() for s in current_segments])
        first_start = f"{current_segments[0].start:.3f}s"
        last_end = f"{current_segments[-1].end:.3f}s"

        lines.append(f"### {current_speaker}\n")
        lines.append(f"**Time:** [{first_start} - {last_end}]\n")
        lines.append(f"\n{combined_text}\n")

    # Detailed breakdown
    lines.append(f"\n## Detailed Breakdown by Segments\n")

    for seg in enhanced_segments:
        line = f"**[{seg.speaker}] [{seg.start:.3f}s - {seg.end:.3f}s]** {seg.text.strip()}\n"
        if include_confidence:
            confidence_pct = seg.combined_confidence * 100
            line += f"**Confidence:** {confidence_pct:.1f}% | Quality: {seg.transcription_quality:.2f}\n"
        lines.append(line)

    # Speaking time distribution
    lines.append(f"\n## Speaking Time Distribution\n")

    speaker_durations = {}
    speaker_segments_count = {}
    speaker_confidence_sums = {}

    for seg in enhanced_segments:
        speaker = seg.speaker
        duration = seg.end - seg.start

        if speaker not in speaker_durations:
            speaker_durations[speaker] = 0
            speaker_segments_count[speaker] = 0
            speaker_confidence_sums[speaker] = 0

        speaker_durations[speaker] += duration
        speaker_segments_count[speaker] += 1
        speaker_confidence_sums[speaker] += seg.combined_confidence

    total_duration = sum(speaker_durations.values())

    for speaker in sorted(speaker_durations.keys()):
        duration = speaker_durations[speaker]
        percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
        avg_confidence = (
            speaker_confidence_sums[speaker] / speaker_segments_count[speaker]
            if speaker_segments_count[speaker] > 0
            else 0
        )

        lines.append(f"### {speaker}\n")
        lines.append(f"- **Speaking time:** {duration:.2f}s ({percentage:.1f}% of total)\n")
        lines.append(f"- **Segments:** {speaker_segments_count[speaker]}\n")
        lines.append(f"- **Average confidence:** {avg_confidence:.3f}\n")

    # Overall statistics
    lines.append(f"\n## General Statistics\n")
    speakers = set(seg.speaker for seg in enhanced_segments)
    lines.append(f"- **Total speakers:** {len(speakers)}\n")
    lines.append(f"- **Total duration:** {total_duration:.2f}s\n")
    lines.append(f"- **Total segments:** {len(enhanced_segments)}\n")
    lines.append(f"- **Speakers:** {', '.join(sorted(speakers))}\n")

    return "\n".join(lines)


def combine_results(
    diarization_result: DiarizationResult,
    transcription_result: TranscriptionResult,
    output_dir: Path,
    save_markdown: bool = True,
    include_confidence: bool = True,
) -> CombinationResult:
    """
    Combine diarization and transcription results into speaker-labeled transcript.

    Args:
        diarization_result: Result from speaker diarization
        transcription_result: Result from transcription
        output_dir: Directory for output files
        save_markdown: Whether to save combined result as markdown
        include_confidence: Whether to include confidence scores in output

    Returns:
        CombinationResult with combined transcript

    Raises:
        CombinationError: If combination fails
    """
    try:
        # Map speakers to transcription segments
        enhanced_segments = map_speakers_to_segments(diarization_result.segments, transcription_result.segments)

        # Calculate speaker durations from enhanced segments
        speaker_durations = {}
        for seg in enhanced_segments:
            if seg.speaker not in speaker_durations:
                speaker_durations[seg.speaker] = 0
            speaker_durations[seg.speaker] += seg.end - seg.start

        # Create combined transcript
        transcript_text = create_combined_transcript(
            enhanced_segments, transcription_result.audio_file, include_confidence
        )

        # Save to file if requested
        output_file = None
        if save_markdown:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{transcription_result.audio_file.stem}_combined.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

        return CombinationResult(
            success=True,
            audio_file=transcription_result.audio_file,
            segments=enhanced_segments,
            num_speakers=len(set(seg.speaker for seg in enhanced_segments)),
            speaker_durations=speaker_durations,
            output_file=output_file,
            metadata={
                'diarization_model': diarization_result.metadata.get('model'),
                'transcription_model': transcription_result.metadata.get('model_size'),
                'transcription_implementation': transcription_result.implementation,
            },
        )

    except Exception as e:
        raise CombinationError(
            f"Failed to combine results: {str(e)}",
            suggestions=[
                "Check that both diarization and transcription completed successfully",
                "Verify segment timestamps are valid",
                "Ensure output directory is writable",
            ],
            context={'audio_file': str(transcription_result.audio_file), 'error': str(e)},
        )


def combine_from_files(
    diarization_file: Path,
    transcription_file: Path,
    audio_file: Path,
    output_dir: Path,
    save_markdown: bool = True,
) -> CombinationResult:
    """
    Combine results from diarization and transcription output files.

    This is a convenience function for when you have saved files instead of
    DiarizationResult and TranscriptionResult objects.

    Args:
        diarization_file: Path to diarization markdown file
        transcription_file: Path to transcription JSON file
        audio_file: Original audio file
        output_dir: Directory for output files
        save_markdown: Whether to save combined result

    Returns:
        CombinationResult with combined transcript

    Raises:
        CombinationError: If loading or combination fails
    """
    try:
        # Load diarization results from markdown
        diarization_segments = _load_diarization_from_markdown(diarization_file)

        # Load transcription results from JSON
        with open(transcription_file, 'r', encoding='utf-8') as f:
            trans_data = json.load(f)

        # Convert to TranscriptionSegment objects
        from .transcription import TranscriptionSegment

        transcription_segments = [
            TranscriptionSegment(
                id=seg.get('id', i),
                start=seg['start'],
                end=seg['end'],
                text=seg['text'],
                temperature=seg.get('temperature', 0),
                avg_logprob=seg.get('avg_logprob', 0),
                compression_ratio=seg.get('compression_ratio', 0),
                no_speech_prob=seg.get('no_speech_prob', 0),
            )
            for i, seg in enumerate(trans_data.get('segments', []))
        ]

        # Map speakers to segments
        enhanced_segments = map_speakers_to_segments(diarization_segments, transcription_segments)

        # Create combined transcript
        transcript_text = create_combined_transcript(enhanced_segments, Path(audio_file), include_confidence=True)

        # Save to file
        output_file = None
        if save_markdown:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{Path(audio_file).stem}_combined.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

        # Calculate speaker durations
        speaker_durations = {}
        for seg in enhanced_segments:
            if seg.speaker not in speaker_durations:
                speaker_durations[seg.speaker] = 0
            speaker_durations[seg.speaker] += seg.end - seg.start

        return CombinationResult(
            success=True,
            audio_file=Path(audio_file),
            segments=enhanced_segments,
            num_speakers=len(set(seg.speaker for seg in enhanced_segments)),
            speaker_durations=speaker_durations,
            output_file=output_file,
        )

    except Exception as e:
        raise CombinationError(
            f"Failed to combine from files: {str(e)}",
            suggestions=[
                f"Check that diarization file exists: {diarization_file}",
                f"Check that transcription file exists: {transcription_file}",
                "Verify files are in correct format",
            ],
            context={'diarization_file': str(diarization_file), 'transcription_file': str(transcription_file), 'error': str(e)},
        )


def _load_diarization_from_markdown(diarization_file: Path) -> List[Dict[str, Any]]:
    """Load diarization segments from markdown file."""
    with open(diarization_file, 'r', encoding='utf-8') as f:
        content = f.read()

    segments = []
    lines = content.split('\n')
    in_table = False
    header_found = False

    for line in lines:
        if 'Speaker Segments' in line or 'Regular Speaker Diarization' in line:
            in_table = True
            header_found = False
            continue

        if in_table:
            if line.strip() == '':
                continue

            if line.startswith('|---'):
                header_found = True
                continue

            if line.startswith('|') and header_found:
                parts = [part.strip() for part in line.split('|')]
                parts = [part for part in parts if part != '']

                if len(parts) >= 4:
                    try:
                        segments.append({
                            'speaker': parts[0],
                            'start': float(parts[1]),
                            'end': float(parts[2]),
                            'duration': float(parts[3]),
                        })
                    except ValueError:
                        continue
            elif not line.startswith('|'):
                in_table = False

    return segments
