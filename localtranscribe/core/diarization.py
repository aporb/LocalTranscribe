"""
Speaker diarization using pyannote.audio.

Identifies and timestamps different speakers in audio files.
"""

import torch
import torchaudio
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pydub import AudioSegment
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
import warnings
import time
import os

from ..utils.errors import DiarizationError, HuggingFaceTokenError, InvalidAudioFormatError
from ..utils.download import wrap_model_download, check_model_cached, loading_spinner

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pyannote.audio")


@dataclass
class DiarizationResult:
    """Structured result from speaker diarization."""

    success: bool
    audio_file: Path
    processing_time: float
    num_speakers: int
    segments: list = field(default_factory=list)
    speaker_durations: Dict[str, float] = field(default_factory=dict)
    output_file: Optional[Path] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def setup_device() -> torch.device:
    """
    Configure optimal device for speaker diarization.

    Returns:
        torch.device: Best available device (MPS > CUDA > CPU)
    """
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        # Optimize for Apple Silicon
        torch.set_num_threads(10)  # Good for M4 Pro with 10 cores
        return device
    elif torch.cuda.is_available():
        device = torch.device('cuda')
        return device
    else:
        device = torch.device('cpu')
        torch.set_num_threads(8)  # Optimize for CPU
        return device


def preprocess_audio(input_file: Path, output_dir: Path) -> Path:
    """
    Preprocess audio file to optimal format for pyannote (mono, 16kHz WAV).

    Args:
        input_file: Path to input audio file
        output_dir: Directory for temporary processed file

    Returns:
        Path to processed audio file

    Raises:
        InvalidAudioFormatError: If audio format is invalid or cannot be processed
    """
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        base_name = input_file.stem
        ext = input_file.suffix.lower()

        # Load audio with pydub
        if ext == '.ogg':
            audio = AudioSegment.from_ogg(str(input_file))
        elif ext == '.mp3':
            audio = AudioSegment.from_mp3(str(input_file))
        elif ext == '.m4a':
            audio = AudioSegment.from_file(str(input_file), format='m4a')
        elif ext == '.wav':
            audio = AudioSegment.from_wav(str(input_file))
        elif ext == '.flac':
            audio = AudioSegment.from_file(str(input_file), format='flac')
        else:
            audio = AudioSegment.from_file(str(input_file))

        # Check if conversion needed
        if audio.frame_rate == 16000 and audio.channels == 1 and ext == '.wav':
            # Already in correct format
            return input_file

        # Convert to mono and 16kHz
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Export as WAV
        wav_file = output_dir / f"{base_name}_processed.wav"
        audio.export(str(wav_file), format='wav')

        return wav_file

    except Exception as e:
        raise InvalidAudioFormatError(
            f"Failed to preprocess audio file: {str(e)}",
            suggestions=[
                "Check that FFmpeg is installed: brew install ffmpeg",
                "Verify audio file is not corrupted",
                "Try converting to MP3 or WAV first",
            ],
            context={
                'input_file': str(input_file),
                'error': str(e),
            },
        )


def load_diarization_pipeline(
    hf_token: str,
    model_name: str = "pyannote/speaker-diarization-3.1",
    device: Optional[torch.device] = None,
) -> Pipeline:
    """
    Load pyannote speaker diarization pipeline.

    Args:
        hf_token: HuggingFace access token
        model_name: Model identifier on HuggingFace
        device: Device to load model on (default: auto-detect)

    Returns:
        Loaded pipeline ready for diarization

    Raises:
        HuggingFaceTokenError: If token is invalid or model cannot be loaded
    """
    try:
        # Load pipeline with progress indicator
        def _load_pipeline():
            return Pipeline.from_pretrained(model_name, token=hf_token)

        pipeline = wrap_model_download(
            _load_pipeline,
            model_name=model_name,
            model_type="diarization model",
            check_cache=True,
        )

        # Move to device if specified
        if device is not None:
            if device.type in ['mps', 'cuda']:
                pipeline.to(device)

        return pipeline

    except Exception as e:
        error_msg = str(e).lower()
        if 'token' in error_msg or 'auth' in error_msg or '401' in error_msg:
            raise HuggingFaceTokenError(
                "HuggingFace token is invalid or expired",
                suggestions=[
                    "Get a token from: https://huggingface.co/settings/tokens",
                    "Add token to .env file: HUGGINGFACE_TOKEN=your_token",
                    f"Accept model license at: https://huggingface.co/{model_name}",
                    "Ensure token has read access to models",
                ],
                context={
                    'model': model_name,
                    'error': str(e),
                },
            )
        else:
            raise DiarizationError(
                f"Failed to load diarization model: {str(e)}",
                suggestions=[
                    "Check internet connection for first-time model download",
                    "Verify HuggingFace token is valid",
                    f"Check model exists: https://huggingface.co/{model_name}",
                ],
                context={
                    'model': model_name,
                    'error': str(e),
                },
            )


def run_diarization(
    audio_file: Path,
    hf_token: str,
    output_dir: Path,
    num_speakers: Optional[int] = None,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
    model_name: str = "pyannote/speaker-diarization-3.1",
    device: Optional[torch.device] = None,
    save_markdown: bool = True,
) -> DiarizationResult:
    """
    Run speaker diarization on audio file.

    Args:
        audio_file: Path to audio file
        hf_token: HuggingFace access token
        output_dir: Directory for output files
        num_speakers: Exact number of speakers (if known)
        min_speakers: Minimum number of speakers
        max_speakers: Maximum number of speakers
        model_name: HuggingFace model identifier
        device: Device to run on (auto-detect if None)
        save_markdown: Whether to save results as markdown file

    Returns:
        DiarizationResult with all diarization information

    Raises:
        DiarizationError: If diarization fails
    """
    start_time = time.time()

    try:
        # Setup device
        if device is None:
            device = setup_device()

        # Preprocess audio
        processed_audio = preprocess_audio(audio_file, output_dir)
        cleanup_processed = processed_audio != audio_file

        # Load pipeline
        pipeline = load_diarization_pipeline(hf_token, model_name, device)

        # Prepare diarization arguments
        diarization_args = {}
        if num_speakers:
            diarization_args['num_speakers'] = num_speakers
        if min_speakers:
            diarization_args['min_speakers'] = min_speakers
        if max_speakers:
            diarization_args['max_speakers'] = max_speakers

        # Run diarization with progress monitoring
        try:
            waveform, sample_rate = torchaudio.load(str(processed_audio))
            with ProgressHook() as hook:
                diarization_output = pipeline(
                    {"waveform": waveform, "sample_rate": sample_rate},
                    hook=hook,
                    **diarization_args
                )
        except Exception:
            # Fallback to file path method
            with ProgressHook() as hook:
                diarization_output = pipeline(str(processed_audio), hook=hook, **diarization_args)

        # Process results
        segments = []
        speaker_durations = {}
        speakers = set()

        for turn, speaker in diarization_output.speaker_diarization:
            speaker_label = speaker
            segments.append({
                'speaker': speaker_label,
                'start': turn.start,
                'end': turn.end,
                'duration': turn.end - turn.start,
            })

            speakers.add(speaker_label)
            if speaker_label not in speaker_durations:
                speaker_durations[speaker_label] = 0
            speaker_durations[speaker_label] += turn.end - turn.start

        # Clean up processed file if needed
        if cleanup_processed and processed_audio.exists():
            try:
                processed_audio.unlink()
            except Exception:
                pass  # Ignore cleanup errors

        # Calculate total time
        processing_time = time.time() - start_time

        # Save markdown if requested
        output_file = None
        if save_markdown:
            output_file = _write_markdown_results(
                segments=segments,
                speaker_durations=speaker_durations,
                audio_file=audio_file,
                output_dir=output_dir,
                processing_time=processing_time,
            )

        return DiarizationResult(
            success=True,
            audio_file=audio_file,
            processing_time=processing_time,
            num_speakers=len(speakers),
            segments=segments,
            speaker_durations=speaker_durations,
            output_file=output_file,
            metadata={
                'device': str(device),
                'model': model_name,
                'num_speakers_specified': num_speakers,
                'min_speakers': min_speakers,
                'max_speakers': max_speakers,
            },
        )

    except (HuggingFaceTokenError, InvalidAudioFormatError):
        # Re-raise our custom errors
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        raise DiarizationError(
            f"Diarization failed: {str(e)}",
            suggestions=[
                "Check that audio file is valid",
                "Verify HuggingFace token is correct",
                "Ensure enough memory available",
                "Try with different speaker count parameters",
            ],
            context={
                'audio_file': str(audio_file),
                'processing_time': f"{processing_time:.1f}s",
                'error': str(e),
            },
        )


def _write_markdown_results(
    segments: list,
    speaker_durations: Dict[str, float],
    audio_file: Path,
    output_dir: Path,
    processing_time: float,
) -> Path:
    """Write diarization results to markdown file."""
    import datetime

    output_file = output_dir / f"{audio_file.stem}_diarization.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write(f"# Speaker Diarization Results\n\n")
        f.write(f"**Audio File:** {audio_file.name}\n\n")
        f.write(f"**Processing Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Processing Time:** {processing_time:.2f}s\n\n")

        # Speaker segments table
        f.write("## Speaker Segments\n\n")
        f.write("| Speaker | Start Time (s) | End Time (s) | Duration (s) |\n")
        f.write("|---------|----------------|--------------|-------------|\n")

        for seg in segments:
            f.write(
                f"| {seg['speaker']} | {seg['start']:.3f} | {seg['end']:.3f} | {seg['duration']:.3f} |\n"
            )

        f.write("\n")

        # Summary statistics
        speakers = set(seg['speaker'] for seg in segments)
        total_duration = sum(seg['duration'] for seg in segments)

        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total speakers detected:** {len(speakers)}\n")
        f.write(f"- **Total speech duration:** {total_duration:.2f}s\n")
        f.write(f"- **Total segments:** {len(segments)}\n")
        f.write(f"- **Speakers:** {', '.join(sorted(speakers))}\n\n")

        # Speaker time distribution
        f.write("### Speaker Time Distribution\n\n")
        for speaker in sorted(speaker_durations.keys()):
            duration = speaker_durations[speaker]
            percentage = (duration / total_duration) * 100 if total_duration > 0 else 0
            f.write(f"- **{speaker}:** {duration:.2f}s ({percentage:.1f}% of total speech)\n")

    return output_file
