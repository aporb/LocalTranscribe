"""
Speech-to-text transcription using Whisper implementations.

Supports multiple Whisper implementations: MLX, Faster-Whisper, and Original.
"""

import os
import json
import time
import warnings
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from pydub import AudioSegment

from ..utils.errors import TranscriptionError, DependencyError, InvalidAudioFormatError
from ..utils.download import loading_spinner, show_first_run_message, check_model_cached

warnings.filterwarnings("ignore", category=UserWarning)

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


@dataclass
class TranscriptionSegment:
    """Single segment of transcribed audio."""

    id: int
    start: float
    end: float
    text: str
    temperature: float = 0.0
    avg_logprob: float = 0.0
    compression_ratio: float = 0.0
    no_speech_prob: float = 0.0


@dataclass
class TranscriptionResult:
    """Structured result from speech-to-text transcription."""

    success: bool
    audio_file: Path
    text: str
    segments: List[TranscriptionSegment]
    language: str
    duration: float
    processing_time: float
    implementation: str
    output_files: Dict[str, Path] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def check_implementations() -> Optional[str]:
    """
    Check available Whisper implementations and return the best one.

    Priority: MLX > Faster > Original

    Returns:
        Name of best available implementation, or None if none found
    """
    implementations = []

    # Check for MLX-Whisper (Apple Silicon optimized)
    try:
        import mlx_whisper
        import mlx.core as mx

        if mx.metal.is_available():
            implementations.append("mlx")
    except ImportError:
        pass
    except Exception:
        pass

    # Check for faster-whisper
    try:
        import faster_whisper

        implementations.append("faster")
    except ImportError:
        pass

    # Check for original whisper with MPS
    try:
        import torch

        if torch.backends.mps.is_available():
            import whisper

            implementations.append("original")
    except ImportError:
        pass

    return implementations[0] if implementations else None


def preprocess_audio(input_file: Path, output_dir: Path) -> Path:
    """
    Preprocess audio file to optimal format for Whisper (mono, 16kHz).

    Args:
        input_file: Path to input audio file
        output_dir: Directory for temporary processed file

    Returns:
        Path to processed audio file

    Raises:
        InvalidAudioFormatError: If audio cannot be processed
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        base_name = input_file.stem
        ext = input_file.suffix.lower()

        # Load audio
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
            return input_file

        # Convert to mono and 16kHz
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Export as WAV
        wav_file = output_dir / f"{base_name}_processed.wav"
        audio.export(str(wav_file), format='wav')

        return wav_file

    except Exception as e:
        raise InvalidAudioFormatError(
            f"Failed to preprocess audio: {str(e)}",
            suggestions=[
                "Check that FFmpeg is installed: brew install ffmpeg",
                "Verify audio file is not corrupted",
                "Try converting to MP3 or WAV format first",
            ],
            context={'input_file': str(input_file), 'error': str(e)},
        )


def _get_audio_duration(audio_file: Path) -> float:
    """
    Get the duration of an audio file in seconds.

    Args:
        audio_file: Path to audio file

    Returns:
        Duration in seconds

    Raises:
        Exception: If unable to determine duration
    """
    ext = audio_file.suffix.lower()

    # Load audio based on format
    if ext == '.ogg':
        audio = AudioSegment.from_ogg(str(audio_file))
    elif ext == '.mp3':
        audio = AudioSegment.from_mp3(str(audio_file))
    elif ext == '.m4a':
        audio = AudioSegment.from_file(str(audio_file), format='m4a')
    elif ext == '.wav':
        audio = AudioSegment.from_wav(str(audio_file))
    elif ext == '.flac':
        audio = AudioSegment.from_file(str(audio_file), format='flac')
    else:
        audio = AudioSegment.from_file(str(audio_file))

    # Duration in seconds
    return len(audio) / 1000.0


def transcribe_with_mlx(
    audio_file: Path, model_size: str = "base", language: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]], str, float]:
    """Transcribe using MLX-Whisper (Apple Silicon optimized)."""
    try:
        import mlx_whisper
        import mlx.core as mx
    except ImportError:
        raise DependencyError(
            "MLX-Whisper not installed",
            suggestions=["Install with: pip install mlx-whisper mlx"],
        )

    # Set memory limit
    mx.set_cache_limit(1024 * 1024 * 1024)  # 1GB

    # Model mapping for community models
    model_map = {
        "tiny": "mlx-community/whisper-tiny-mlx",
        "base": "mlx-community/whisper-base-mlx",
        "small": "mlx-community/whisper-small-mlx",
        "medium": "mlx-community/whisper-medium-mlx",
        "large": "mlx-community/whisper-large-v3-mlx",
    }

    model_repo = model_map.get(model_size, f"mlx-community/whisper-{model_size}")

    # Show progress for model download
    with loading_spinner(
        f"Loading MLX-Whisper {model_size} model...",
        f"MLX-Whisper loaded"
    ):
        pass  # Model loading happens in transcribe call

    # Get audio duration for progress estimation
    try:
        audio_duration = _get_audio_duration(audio_file)
    except:
        audio_duration = None

    # Transcribe with progress tracking
    print(f"⏳ Transcribing audio{f' ({audio_duration:.1f}s)' if audio_duration else ''}...")

    if audio_duration:
        # Show estimated progress based on benchmarks
        # MLX-Whisper benchmarks: ~0.12x realtime for large model on M-series
        model_speeds = {
            "tiny": 0.02,    # 2% of audio duration
            "base": 0.04,    # 4% of audio duration
            "small": 0.06,   # 6% of audio duration
            "medium": 0.08,  # 8% of audio duration
            "large": 0.12,   # 12% of audio duration
        }
        estimated_time = audio_duration * model_speeds.get(model_size, 0.1)
        print(f"⏱️  Estimated time: {estimated_time:.1f}s (this may vary)")

    result = mlx_whisper.transcribe(str(audio_file), path_or_hf_repo=model_repo, language=language)
    print("✓ Transcription complete")

    # Extract data
    text = result.get("text", "")
    language_detected = result.get("language", language or "unknown")
    segments = []

    for i, seg in enumerate(result.get("segments", [])):
        segments.append({
            'id': seg.get("id", i),
            'start': seg.get("start", 0),
            'end': seg.get("end", 0),
            'text': seg.get("text", ""),
            'temperature': seg.get("temperature", 0),
            'avg_logprob': seg.get("avg_logprob", 0),
            'compression_ratio': seg.get("compression_ratio", 0),
            'no_speech_prob': seg.get("no_speech_prob", 0),
        })

    duration = max([s['end'] for s in segments]) if segments else 0

    return text, segments, language_detected, duration


def transcribe_with_faster_whisper(
    audio_file: Path, model_size: str = "base", language: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]], str, float]:
    """Transcribe using Faster-Whisper."""
    try:
        import torch
        from faster_whisper import WhisperModel
    except ImportError:
        raise DependencyError(
            "Faster-Whisper not installed",
            suggestions=["Install with: pip install faster-whisper"],
        )

    # Setup device
    torch_device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch_device == "cpu" else "float32"

    # Optimize for Apple Silicon CPU
    if torch_device == "cpu":
        torch.set_num_threads(8)

    # Load model with progress indicator
    with loading_spinner(
        f"Loading Faster-Whisper {model_size} model...",
        f"Faster-Whisper loaded"
    ):
        model = WhisperModel(model_size, device="cpu", compute_type=compute_type)

    # Run transcription
    segments_iter, info = model.transcribe(str(audio_file), beam_size=5, language=language)

    # Collect segments with progress bar
    segments = []
    full_text = ""

    # Get audio duration for progress bar
    audio_duration = getattr(info, 'duration', 0)

    if audio_duration > 0 and TQDM_AVAILABLE:
        # Show progress bar based on segment timestamps
        print(f"⏳ Transcribing {audio_duration:.1f}s of audio...")

        timestamp = 0.0
        with tqdm(total=audio_duration, unit="s", desc="Transcription",
                  bar_format="{l_bar}{bar}| {n:.1f}/{total:.1f}s [{elapsed}<{remaining}]") as pbar:
            for segment in segments_iter:
                segments.append({
                    'id': len(segments),
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text,
                    'temperature': 0,
                    'avg_logprob': 0,
                    'compression_ratio': 0,
                    'no_speech_prob': 0,
                })
                full_text += segment.text + " "

                # Update progress bar
                progress_delta = segment.end - timestamp
                pbar.update(progress_delta)
                timestamp = segment.end

        print("✓ Transcription complete")
    else:
        # Fallback without progress bar if duration unavailable or tqdm not installed
        if audio_duration > 0:
            print(f"⏳ Transcribing {audio_duration:.1f}s of audio...")
        else:
            print("⏳ Transcribing audio...")

        segment_count = 0
        for segment in segments_iter:
            segments.append({
                'id': len(segments),
                'start': segment.start,
                'end': segment.end,
                'text': segment.text,
                'temperature': 0,
                'avg_logprob': 0,
                'compression_ratio': 0,
                'no_speech_prob': 0,
            })
            full_text += segment.text + " "

            # Show periodic updates
            segment_count += 1
            if segment_count % 10 == 0:
                print(f"  ... processed {segment_count} segments (at {segment.end:.1f}s)")

        print("✓ Transcription complete")

    language_detected = getattr(info, 'language', language or 'unknown')
    duration = max([s['end'] for s in segments]) if segments else 0

    return full_text.strip(), segments, language_detected, duration


def transcribe_with_original_whisper(
    audio_file: Path, model_size: str = "base", language: Optional[str] = None
) -> Tuple[str, List[Dict[str, Any]], str, float]:
    """Transcribe using Original OpenAI Whisper."""
    try:
        import whisper
        import torch
    except ImportError:
        raise DependencyError(
            "OpenAI Whisper not installed",
            suggestions=["Install with: pip install openai-whisper"],
        )

    # Setup device
    device = torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')

    # Load model with progress indicator
    with loading_spinner(
        f"Loading Whisper {model_size} model...",
        f"Whisper loaded"
    ):
        model = whisper.load_model(model_size, device=device)

    # Run transcription
    result = model.transcribe(
        str(audio_file), language=language, task="transcribe", fp16=False if device.type == 'cpu' else True
    )

    # Extract data
    text = result['text']
    language_detected = result.get('language', language or 'unknown')
    segments = []

    for seg in result.get('segments', []):
        segments.append({
            'id': seg.get('id', len(segments)),
            'start': seg['start'],
            'end': seg['end'],
            'text': seg['text'],
            'temperature': seg.get('temperature', 0),
            'avg_logprob': seg.get('avg_logprob', 0),
            'compression_ratio': seg.get('compression_ratio', 0),
            'no_speech_prob': seg.get('no_speech_prob', 0),
        })

    duration = max([s['end'] for s in segments]) if segments else 0

    return text, segments, language_detected, duration


def run_transcription(
    audio_file: Path,
    output_dir: Path,
    model_size: str = "base",
    language: Optional[str] = None,
    implementation: str = "auto",
    output_formats: List[str] = ["txt", "json"],
) -> TranscriptionResult:
    """
    Run speech-to-text transcription on audio file.

    Args:
        audio_file: Path to audio file
        output_dir: Directory for output files
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Force specific language (None for auto-detect)
        implementation: Whisper implementation (auto, mlx, faster, original)
        output_formats: List of output formats (txt, json, srt, md)

    Returns:
        TranscriptionResult with all transcription data

    Raises:
        TranscriptionError: If transcription fails
    """
    start_time = time.time()

    try:
        # Detect implementation if auto
        if implementation == "auto":
            implementation = check_implementations()
            if not implementation:
                raise DependencyError(
                    "No Whisper implementation available",
                    suggestions=[
                        "Install MLX-Whisper: pip install mlx-whisper mlx",
                        "Install Faster-Whisper: pip install faster-whisper",
                        "Install Original Whisper: pip install openai-whisper",
                    ],
                )

        # Preprocess audio
        processed_audio = preprocess_audio(audio_file, output_dir)
        cleanup_processed = processed_audio != audio_file

        # Run transcription based on implementation
        if implementation == "mlx":
            text, segments_raw, language_detected, duration = transcribe_with_mlx(
                processed_audio, model_size, language
            )
        elif implementation == "faster":
            text, segments_raw, language_detected, duration = transcribe_with_faster_whisper(
                processed_audio, model_size, language
            )
        elif implementation == "original":
            text, segments_raw, language_detected, duration = transcribe_with_original_whisper(
                processed_audio, model_size, language
            )
        else:
            raise TranscriptionError(
                f"Unknown implementation: {implementation}",
                suggestions=["Use: auto, mlx, faster, or original"],
            )

        # Convert segments to dataclass
        segments = [
            TranscriptionSegment(
                id=s['id'],
                start=s['start'],
                end=s['end'],
                text=s['text'],
                temperature=s.get('temperature', 0),
                avg_logprob=s.get('avg_logprob', 0),
                compression_ratio=s.get('compression_ratio', 0),
                no_speech_prob=s.get('no_speech_prob', 0),
            )
            for s in segments_raw
        ]

        # Clean up processed file
        if cleanup_processed and processed_audio.exists():
            try:
                processed_audio.unlink()
            except Exception:
                pass

        # Calculate processing time
        processing_time = time.time() - start_time

        # Write output files
        output_files = _write_output_files(
            text=text,
            segments=segments,
            audio_file=audio_file,
            output_dir=output_dir,
            language=language_detected,
            duration=duration,
            formats=output_formats,
        )

        return TranscriptionResult(
            success=True,
            audio_file=audio_file,
            text=text,
            segments=segments,
            language=language_detected,
            duration=duration,
            processing_time=processing_time,
            implementation=implementation,
            output_files=output_files,
            metadata={'model_size': model_size, 'language_forced': language is not None},
        )

    except (DependencyError, InvalidAudioFormatError):
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        raise TranscriptionError(
            f"Transcription failed: {str(e)}",
            suggestions=[
                "Check that audio file is valid",
                "Try a different model size",
                "Verify Whisper implementation is installed correctly",
            ],
            context={'audio_file': str(audio_file), 'processing_time': f"{processing_time:.1f}s", 'error': str(e)},
        )


def _write_output_files(
    text: str,
    segments: List[TranscriptionSegment],
    audio_file: Path,
    output_dir: Path,
    language: str,
    duration: float,
    formats: List[str],
) -> Dict[str, Path]:
    """Write transcription results to various output formats."""
    import datetime

    output_files = {}
    base_name = audio_file.stem

    # Text format
    if 'txt' in formats:
        txt_file = output_dir / f"{base_name}_transcript.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text)
        output_files['txt'] = txt_file

    # JSON format
    if 'json' in formats:
        json_file = output_dir / f"{base_name}_transcript.json"
        json_data = {
            'transcript': text,
            'segments': [
                {
                    'id': seg.id,
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text.strip(),
                    'temperature': seg.temperature,
                    'avg_logprob': seg.avg_logprob,
                    'compression_ratio': seg.compression_ratio,
                    'no_speech_prob': seg.no_speech_prob,
                }
                for seg in segments
            ],
            'processing_info': {
                'audio_file': str(audio_file),
                'processing_date': datetime.datetime.now().isoformat(),
                'language': language,
                'duration': duration,
            },
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        output_files['json'] = json_file

    # SRT subtitle format
    if 'srt' in formats:
        srt_file = output_dir / f"{base_name}_transcript.srt"
        with open(srt_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start = datetime.timedelta(seconds=segment.start)
                end = datetime.timedelta(seconds=segment.end)
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment.text.strip()}\n\n")
        output_files['srt'] = srt_file

    # Markdown format
    if 'md' in formats:
        md_file = output_dir / f"{base_name}_transcript.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Audio Transcript\n\n")
            f.write(f"**Audio File:** {audio_file.name}\n\n")
            f.write(f"**Processing Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Detected Language:** {language}\n\n")
            f.write(f"**Total Duration:** {duration:.2f}s\n\n")
            f.write("## Transcript\n\n")

            for segment in segments:
                f.write(f"**[{segment.start:.3f}s - {segment.end:.3f}s]** {segment.text.strip()}\n\n")

        output_files['md'] = md_file

    return output_files
