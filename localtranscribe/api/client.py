"""
High-level SDK client for LocalTranscribe.

Provides a clean, Pythonic API for programmatic transcription.
"""

import os
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

from ..pipeline import PipelineOrchestrator
from ..config.loader import load_config
from .types import ProcessResult, BatchResult, Segment


class LocalTranscribe:
    """
    High-level client for LocalTranscribe.

    Provides a simple, intuitive API for audio transcription with speaker diarization.
    Automatically handles configuration, model selection, and error handling.

    Example:
        >>> lt = LocalTranscribe(model_size="base", num_speakers=2)
        >>> result = lt.process("meeting.mp3")
        >>> print(result.transcript)
        >>>
        >>> # Batch processing
        >>> results = lt.process_batch("./audio_files/")
        >>> print(f"Processed {results.successful}/{results.total} files")

    Args:
        model_size: Whisper model size (tiny, base, small, medium, large)
        num_speakers: Exact number of speakers (if known)
        min_speakers: Minimum number of speakers
        max_speakers: Maximum number of speakers
        language: Force specific language (e.g., 'en', 'es')
        implementation: Whisper implementation (auto, mlx, faster, original)
        output_dir: Default output directory for results
        hf_token: HuggingFace token (defaults to HUGGINGFACE_TOKEN env var)
        config_file: Path to custom configuration file
        verbose: Enable verbose logging
    """

    def __init__(
        self,
        model_size: str = "base",
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        language: Optional[str] = None,
        implementation: str = "auto",
        output_dir: Optional[Union[str, Path]] = None,
        hf_token: Optional[str] = None,
        config_file: Optional[Union[str, Path]] = None,
        verbose: bool = False,
    ):
        """Initialize LocalTranscribe client."""

        # Load configuration
        if config_file:
            self.config = load_config(Path(config_file))
        else:
            self.config = load_config()

        # Store settings (CLI args override config)
        self.model_size = model_size
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.language = language
        self.implementation = implementation
        self.verbose = verbose

        # Output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(self.config.get("paths", {}).get("output_dir", "./output"))

        # HuggingFace token
        self.hf_token = hf_token or os.getenv("HUGGINGFACE_TOKEN")
        if not self.hf_token and self.verbose:
            print("⚠️  No HuggingFace token found - diarization will fail")

    def process(
        self,
        audio_file: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        output_formats: Optional[List[str]] = None,
        skip_diarization: bool = False,
        **kwargs,
    ) -> ProcessResult:
        """
        Process a single audio file.

        Args:
            audio_file: Path to audio file
            output_dir: Override default output directory
            output_formats: Output formats (txt, json, srt, vtt, md)
            skip_diarization: Skip speaker diarization (transcription only)
            **kwargs: Override any initialization parameters for this call

        Returns:
            ProcessResult with transcription and metadata

        Raises:
            LocalTranscribeError: If processing fails

        Example:
            >>> result = lt.process("meeting.mp3", output_formats=["txt", "srt"])
            >>> print(f"Speakers: {result.num_speakers}")
            >>> print(f"Duration: {result.processing_time:.1f}s")
        """
        # Resolve paths
        audio_file = Path(audio_file)
        output_dir = Path(output_dir) if output_dir else self.output_dir

        # Merge kwargs with instance settings
        settings = {
            "model_size": kwargs.get("model_size", self.model_size),
            "num_speakers": kwargs.get("num_speakers", self.num_speakers),
            "min_speakers": kwargs.get("min_speakers", self.min_speakers),
            "max_speakers": kwargs.get("max_speakers", self.max_speakers),
            "language": kwargs.get("language", self.language),
            "implementation": kwargs.get("implementation", self.implementation),
            "hf_token": kwargs.get("hf_token", self.hf_token),
            "verbose": kwargs.get("verbose", self.verbose),
        }

        # Create orchestrator
        orchestrator = PipelineOrchestrator(
            audio_file=audio_file,
            output_dir=output_dir,
            output_formats=output_formats or ["txt", "json", "md"],
            skip_diarization=skip_diarization,
            **settings,
        )

        # Run pipeline
        pipeline_result = orchestrator.run()

        # Convert to SDK result type
        return self._convert_pipeline_result(pipeline_result)

    def process_batch(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        max_workers: int = 2,
        skip_existing: bool = False,
        recursive: bool = False,
        **kwargs,
    ) -> BatchResult:
        """
        Process multiple audio files in a directory.

        Args:
            input_dir: Directory containing audio files
            output_dir: Override default output directory
            max_workers: Maximum parallel workers
            skip_existing: Skip files that already have outputs
            recursive: Recursively search subdirectories
            **kwargs: Override any initialization parameters

        Returns:
            BatchResult with summary and individual results

        Example:
            >>> results = lt.process_batch("./audio_files/", max_workers=4)
            >>> print(f"Success rate: {results.successful}/{results.total}")
            >>> for result in results.get_failed():
            ...     print(f"Failed: {result.audio_file} - {result.error}")
        """
        from ..batch import BatchProcessor

        input_dir = Path(input_dir)
        output_dir = Path(output_dir) if output_dir else self.output_dir

        # Merge settings
        settings = {
            "model_size": kwargs.get("model_size", self.model_size),
            "num_speakers": kwargs.get("num_speakers", self.num_speakers),
            "min_speakers": kwargs.get("min_speakers", self.min_speakers),
            "max_speakers": kwargs.get("max_speakers", self.max_speakers),
            "language": kwargs.get("language", self.language),
            "implementation": kwargs.get("implementation", self.implementation),
            "hf_token": kwargs.get("hf_token", self.hf_token),
            "verbose": kwargs.get("verbose", self.verbose),
        }

        # Create batch processor
        processor = BatchProcessor(
            input_dir=input_dir,
            output_dir=output_dir,
            max_workers=max_workers,
            skip_existing=skip_existing,
            recursive=recursive,
            output_formats=kwargs.get("output_formats", ["txt", "json", "md"]),
            skip_diarization=kwargs.get("skip_diarization", False),
            **settings,
        )

        # Run batch processing
        batch_result = processor.process_batch()

        # Convert to SDK result type
        return self._convert_batch_result(batch_result)

    def _convert_pipeline_result(self, pipeline_result) -> ProcessResult:
        """Convert pipeline result to SDK result type."""
        if not pipeline_result.success:
            return ProcessResult(
                success=False,
                audio_file=pipeline_result.audio_file,
                processing_time=pipeline_result.processing_time,
                error=str(pipeline_result.error) if pipeline_result.error else "Unknown error",
            )

        # Extract segments
        segments = []
        if pipeline_result.combination_result:
            for seg in pipeline_result.combination_result.segments:
                segments.append(
                    Segment(
                        speaker=seg.get("speaker", "UNKNOWN"),
                        text=seg.get("text", ""),
                        start=seg.get("start", 0.0),
                        end=seg.get("end", 0.0),
                        confidence=seg.get("confidence"),
                    )
                )

        # Extract transcript
        transcript = ""
        if pipeline_result.transcription_result:
            transcript = pipeline_result.transcription_result.full_text

        return ProcessResult(
            success=True,
            audio_file=pipeline_result.audio_file,
            processing_time=pipeline_result.processing_time,
            transcript=transcript,
            segments=segments,
            num_speakers=(
                pipeline_result.diarization_result.num_speakers
                if pipeline_result.diarization_result
                else None
            ),
            speaker_durations=(
                pipeline_result.diarization_result.speaker_durations
                if pipeline_result.diarization_result
                else {}
            ),
            output_files=pipeline_result.output_files or {},
            model_size=self.model_size,
            language=self.language,
        )

    def _convert_batch_result(self, batch_result) -> BatchResult:
        """Convert batch processor result to SDK result type."""
        results = [self._convert_pipeline_result(r) for r in batch_result.results]

        return BatchResult(
            total=batch_result.total,
            successful=batch_result.successful,
            failed=batch_result.failed,
            processing_time=batch_result.processing_time,
            results=results,
        )
