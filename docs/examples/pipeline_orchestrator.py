"""
Pipeline Orchestrator - Complete Implementation Example

This module demonstrates how to orchestrate the full transcription pipeline:
1. Speaker Diarization (who spoke when)
2. Speech-to-Text Transcription (what was said)
3. Combine Results (merge diarization with transcription)

Features:
- Single command replaces manual 3-step process
- Automatic prerequisite validation
- Stage-by-stage progress tracking
- Error handling with recovery suggestions
- Intermediate file management
- Resume capability for partial completion
- Beautiful Rich UI with detailed feedback

Usage:
    from pipeline_orchestrator import PipelineOrchestrator

    orchestrator = PipelineOrchestrator(
        audio_file="meeting.mp3",
        output_dir="output",
        model_size="base",
        num_speakers=2
    )

    result = orchestrator.run()
"""

from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable
import time
import logging
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline stages in execution order."""
    VALIDATION = "validation"
    DIARIZATION = "diarization"
    TRANSCRIPTION = "transcription"
    COMBINATION = "combination"


@dataclass
class StageResult:
    """Result of a single pipeline stage."""
    stage: PipelineStage
    success: bool
    output_files: Optional[Dict[str, Path]] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PipelineOrchestrator:
    """
    Orchestrate the full transcription pipeline.

    This class manages the execution of all three pipeline stages,
    handling dependencies, error recovery, and progress tracking.
    """

    def __init__(
        self,
        audio_file: Path,
        output_dir: Path,
        model_size: str = "base",
        language: Optional[str] = None,
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        skip_diarization: bool = False,
        implementation: str = "auto",
        output_formats: Optional[list] = None,
        force_overwrite: bool = False,
    ):
        """
        Initialize pipeline orchestrator.

        Args:
            audio_file: Path to audio file to process
            output_dir: Directory for output files
            model_size: Whisper model size (tiny/base/small/medium/large)
            language: Force specific language (None = auto-detect)
            num_speakers: Exact number of speakers (optional)
            min_speakers: Minimum speakers to detect (optional)
            max_speakers: Maximum speakers to detect (optional)
            skip_diarization: Skip speaker diarization (transcription only)
            implementation: Whisper implementation (auto/mlx/faster/original)
            output_formats: Output formats to generate (default: [txt, md, json])
            force_overwrite: Overwrite existing files without confirmation
        """
        self.audio_file = Path(audio_file)
        self.output_dir = Path(output_dir)
        self.model_size = model_size
        self.language = language
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.skip_diarization = skip_diarization
        self.implementation = implementation
        self.output_formats = output_formats or ["txt", "md", "json"]
        self.force_overwrite = force_overwrite

        # State tracking
        self.stage_results: Dict[PipelineStage, StageResult] = {}
        self.intermediate_files: Dict[str, Path] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def validate_prerequisites(self) -> StageResult:
        """
        Validate environment and prerequisites before processing.

        Returns:
            StageResult with validation status
        """
        errors = []

        # Check audio file exists
        if not self.audio_file.exists():
            errors.append(f"Audio file not found: {self.audio_file}")

        # Check file is readable
        elif not self.audio_file.is_file():
            errors.append(f"Not a file: {self.audio_file}")

        # Check output directory is writable
        if not self.output_dir.exists():
            try:
                self.output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")

        # Check Hugging Face token (if diarization needed)
        if not self.skip_diarization:
            try:
                from dotenv import load_dotenv
                import os

                load_dotenv()
                token = os.getenv('HUGGINGFACE_TOKEN')

                if not token:
                    errors.append(
                        "HUGGINGFACE_TOKEN not found in environment. "
                        "Add to .env file or set as environment variable. "
                        "Get token from: https://huggingface.co/settings/tokens"
                    )

            except ImportError:
                errors.append("python-dotenv not installed (pip install python-dotenv)")

        # Check for existing output files
        if not self.force_overwrite:
            base_name = self.audio_file.stem
            existing = list(self.output_dir.glob(f"{base_name}*"))

            if existing:
                console.print(
                    f"\n[yellow]⚠️  Found {len(existing)} existing output file(s)[/yellow]"
                )
                # In real implementation, would prompt user
                # For now, just log
                logger.warning(f"Existing files will be overwritten: {existing}")

        # Return result
        if errors:
            error_msg = "\n".join(f"  - {e}" for e in errors)
            return StageResult(
                stage=PipelineStage.VALIDATION,
                success=False,
                error=f"Validation failed:\n{error_msg}"
            )

        return StageResult(
            stage=PipelineStage.VALIDATION,
            success=True,
            metadata={
                'audio_file': str(self.audio_file),
                'output_dir': str(self.output_dir),
                'model_size': self.model_size,
                'skip_diarization': self.skip_diarization,
            }
        )

    def run_diarization(self) -> StageResult:
        """
        Execute speaker diarization stage.

        Returns:
            StageResult with diarization outputs
        """
        console.print("\n[bold cyan]Stage 1/3: Speaker Diarization[/bold cyan]")

        try:
            start_time = time.time()

            # In real implementation, would import and call diarization module:
            # from localtranscribe.core.diarization import DiarizationPipeline
            #
            # diarizer = DiarizationPipeline(
            #     num_speakers=self.num_speakers,
            #     min_speakers=self.min_speakers,
            #     max_speakers=self.max_speakers,
            # )
            #
            # with console.status("[bold green]Identifying speakers..."):
            #     result = diarizer.process(self.audio_file)

            # Simulated processing with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task("Identifying speakers...", total=None)

                # Simulate work
                time.sleep(0.5)

                progress.update(task, completed=True)

            duration = time.time() - start_time

            # Generate output filename
            base_name = self.audio_file.stem
            diarization_output = self.output_dir / f"{base_name}_diarization_results.md"

            # Store for later stages
            self.intermediate_files['diarization'] = diarization_output

            console.print(
                f"✅ Diarization complete ({duration:.1f}s)",
                style="green"
            )
            console.print(f"   Output: {diarization_output.name}")

            return StageResult(
                stage=PipelineStage.DIARIZATION,
                success=True,
                output_files={'diarization': diarization_output},
                duration=duration,
                metadata={
                    'num_speakers_detected': self.num_speakers or 2,
                    'segments_count': 47,  # Example
                }
            )

        except Exception as e:
            logger.exception("Diarization failed")

            return StageResult(
                stage=PipelineStage.DIARIZATION,
                success=False,
                error=str(e)
            )

    def run_transcription(self) -> StageResult:
        """
        Execute speech-to-text transcription stage.

        Returns:
            StageResult with transcription outputs
        """
        stage_num = 2 if not self.skip_diarization else 1
        total_stages = 3 if not self.skip_diarization else 1

        console.print(
            f"\n[bold cyan]Stage {stage_num}/{total_stages}: "
            f"Speech-to-Text Transcription[/bold cyan]"
        )

        try:
            start_time = time.time()

            # In real implementation, would import and call transcription module:
            # from localtranscribe.core.transcription import TranscriptionPipeline
            #
            # transcriber = TranscriptionPipeline(
            #     model_size=self.model_size,
            #     language=self.language,
            #     implementation=self.implementation,
            # )
            #
            # with console.status(f"[bold green]Transcribing with {self.model_size} model..."):
            #     result = transcriber.process(self.audio_file)

            # Simulated processing
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task(
                    f"Transcribing with {self.model_size} model...",
                    total=None
                )

                # Simulate work
                time.sleep(0.5)

                progress.update(task, completed=True)

            duration = time.time() - start_time

            # Generate output filenames
            base_name = self.audio_file.stem
            output_files = {}

            for fmt in self.output_formats:
                output_file = self.output_dir / f"{base_name}_transcript.{fmt}"
                output_files[f'transcript_{fmt}'] = output_file

            # Store for later stages
            if 'json' in self.output_formats:
                self.intermediate_files['transcription_json'] = output_files['transcript_json']

            if 'txt' in self.output_formats:
                self.intermediate_files['transcription_txt'] = output_files['transcript_txt']

            console.print(
                f"✅ Transcription complete ({duration:.1f}s)",
                style="green"
            )

            for output_file in output_files.values():
                console.print(f"   Output: {output_file.name}")

            return StageResult(
                stage=PipelineStage.TRANSCRIPTION,
                success=True,
                output_files=output_files,
                duration=duration,
                metadata={
                    'model_size': self.model_size,
                    'implementation': self.implementation,
                    'language_detected': self.language or 'en',
                    'segments_count': 152,  # Example
                }
            )

        except Exception as e:
            logger.exception("Transcription failed")

            return StageResult(
                stage=PipelineStage.TRANSCRIPTION,
                success=False,
                error=str(e)
            )

    def run_combination(self) -> StageResult:
        """
        Execute combination stage (merge diarization + transcription).

        Returns:
            StageResult with combined outputs
        """
        console.print("\n[bold cyan]Stage 3/3: Combining Results[/bold cyan]")

        # Validate intermediate files exist
        required_files = ['diarization', 'transcription_json']
        missing = [f for f in required_files if f not in self.intermediate_files]

        if missing:
            error_msg = (
                f"Missing required intermediate files: {', '.join(missing)}. "
                f"Previous stages may have failed."
            )
            return StageResult(
                stage=PipelineStage.COMBINATION,
                success=False,
                error=error_msg
            )

        try:
            start_time = time.time()

            # In real implementation, would import and call combination module:
            # from localtranscribe.core.combination import CombinationPipeline
            #
            # combiner = CombinationPipeline()
            #
            # with console.status("[bold green]Mapping speakers to transcript..."):
            #     result = combiner.process(
            #         diarization_file=self.intermediate_files['diarization'],
            #         transcription_file=self.intermediate_files['transcription_json'],
            #         audio_file=self.audio_file,
            #     )

            # Simulated processing
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task(
                    "Mapping speakers to transcript...",
                    total=None
                )

                # Simulate work
                time.sleep(0.3)

                progress.update(task, completed=True)

            duration = time.time() - start_time

            # Generate output filename
            base_name = self.audio_file.stem
            combined_output = self.output_dir / f"{base_name}_combined_transcript.md"

            console.print(
                f"✅ Combining complete ({duration:.1f}s)",
                style="green"
            )
            console.print(f"   Output: {combined_output.name}")

            return StageResult(
                stage=PipelineStage.COMBINATION,
                success=True,
                output_files={'combined': combined_output},
                duration=duration,
                metadata={
                    'segments_mapped': 152,  # Example
                    'average_confidence': 0.87,  # Example
                }
            )

        except Exception as e:
            logger.exception("Combination failed")

            return StageResult(
                stage=PipelineStage.COMBINATION,
                success=False,
                error=str(e)
            )

    def run(self) -> Dict[str, Any]:
        """
        Execute the full pipeline.

        Returns:
            Dictionary with overall results and outputs
        """
        # Display header
        console.print(Panel.fit(
            "[bold blue]🎙️  LocalTranscribe Pipeline[/bold blue]",
            subtitle=f"Processing: {self.audio_file.name}"
        ))

        console.print(f"\n[bold]Configuration:[/bold]")
        console.print(f"  Audio: {self.audio_file.name}")
        console.print(f"  Model: {self.model_size}")
        console.print(f"  Output: {self.output_dir}")

        if not self.skip_diarization:
            if self.num_speakers:
                console.print(f"  Speakers: {self.num_speakers}")
            else:
                console.print(
                    f"  Speakers: {self.min_speakers or 1}-{self.max_speakers or 10} (auto-detect)"
                )

        self.start_time = time.time()

        try:
            # Stage 0: Validation
            validation_result = self.validate_prerequisites()
            self.stage_results[PipelineStage.VALIDATION] = validation_result

            if not validation_result.success:
                console.print(
                    f"\n[red]❌ Validation failed:[/red]\n{validation_result.error}"
                )
                return self._format_results(success=False)

            console.print("\n✅ Prerequisites validated")

            # Stage 1: Diarization (optional)
            if not self.skip_diarization:
                diarization_result = self.run_diarization()
                self.stage_results[PipelineStage.DIARIZATION] = diarization_result

                if not diarization_result.success:
                    console.print(
                        f"\n[red]❌ Diarization failed:[/red] {diarization_result.error}"
                    )
                    return self._format_results(success=False)

            # Stage 2: Transcription
            transcription_result = self.run_transcription()
            self.stage_results[PipelineStage.TRANSCRIPTION] = transcription_result

            if not transcription_result.success:
                console.print(
                    f"\n[red]❌ Transcription failed:[/red] {transcription_result.error}"
                )
                return self._format_results(success=False)

            # Stage 3: Combination (only if diarization was run)
            if not self.skip_diarization:
                combination_result = self.run_combination()
                self.stage_results[PipelineStage.COMBINATION] = combination_result

                if not combination_result.success:
                    console.print(
                        f"\n[red]❌ Combination failed:[/red] {combination_result.error}"
                    )
                    return self._format_results(success=False)

            # Success!
            self.end_time = time.time()
            return self._format_results(success=True)

        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Pipeline interrupted by user[/yellow]")
            return self._format_results(success=False, error="Interrupted by user")

        except Exception as e:
            logger.exception("Pipeline failed with unexpected error")
            console.print(f"\n[red]❌ Pipeline failed:[/red] {e}")
            return self._format_results(success=False, error=str(e))

    def _format_results(
        self,
        success: bool,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format and display pipeline results.

        Args:
            success: Whether pipeline completed successfully
            error: Optional error message if failed

        Returns:
            Dictionary with results summary
        """
        total_duration = (
            self.end_time - self.start_time
            if self.start_time and self.end_time
            else sum(
                r.duration for r in self.stage_results.values()
                if r.duration is not None
            )
        )

        # Collect all output files
        all_outputs = {}
        for stage, result in self.stage_results.items():
            if result.output_files:
                all_outputs.update(result.output_files)

        # Display results
        if success:
            console.print(f"\n[bold green]✅ Pipeline completed successfully![/bold green]")
            console.print(f"Total processing time: {total_duration:.1f}s\n")

            # Show output files
            if all_outputs:
                console.print("[bold]Output files:[/bold]")
                for name, path in all_outputs.items():
                    console.print(f"  📄 {path.name}")

                console.print(f"\nAll files saved to: {self.output_dir}")

            # Show stage breakdown
            table = Table(title="\nProcessing Breakdown", show_header=True)
            table.add_column("Stage", style="cyan")
            table.add_column("Duration", style="magenta")
            table.add_column("Status", style="green")

            for stage, result in self.stage_results.items():
                if stage == PipelineStage.VALIDATION:
                    continue  # Skip validation in breakdown

                duration_str = (
                    f"{result.duration:.1f}s"
                    if result.duration
                    else "N/A"
                )

                status_str = "✓" if result.success else "✗"

                table.add_row(
                    stage.value.title(),
                    duration_str,
                    status_str
                )

            console.print(table)

        else:
            console.print(f"\n[bold red]❌ Pipeline failed[/bold red]")

            if error:
                console.print(f"\n[red]Error:[/red] {error}")

            # Show which stages completed
            completed_stages = [
                stage.value
                for stage, result in self.stage_results.items()
                if result.success
            ]

            if completed_stages:
                console.print(
                    f"\n[yellow]Completed stages:[/yellow] "
                    f"{', '.join(completed_stages)}"
                )

        # Return structured results
        return {
            'success': success,
            'duration': total_duration,
            'audio_file': str(self.audio_file),
            'output_dir': str(self.output_dir),
            'stages': {
                stage.value: {
                    'success': result.success,
                    'duration': result.duration,
                    'outputs': {
                        name: str(path)
                        for name, path in (result.output_files or {}).items()
                    },
                    'error': result.error,
                    'metadata': result.metadata,
                }
                for stage, result in self.stage_results.items()
            },
            'outputs': {
                name: str(path)
                for name, path in all_outputs.items()
            },
            'error': error,
            'timestamp': datetime.now().isoformat(),
        }


# =============================================================================
# Helper Functions
# =============================================================================

def run_full_pipeline(
    audio_file: Path,
    output_dir: Path = Path("output"),
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to run full pipeline with default settings.

    Args:
        audio_file: Path to audio file
        output_dir: Output directory
        **kwargs: Additional arguments passed to PipelineOrchestrator

    Returns:
        Results dictionary

    Example:
        result = run_full_pipeline(
            audio_file="meeting.mp3",
            model_size="base",
            num_speakers=2
        )
    """
    orchestrator = PipelineOrchestrator(
        audio_file=audio_file,
        output_dir=output_dir,
        **kwargs
    )

    return orchestrator.run()


# =============================================================================
# CLI Integration Example
# =============================================================================

def main():
    """Example command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run LocalTranscribe pipeline"
    )

    parser.add_argument(
        "audio_file",
        type=Path,
        help="Audio file to process"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default="output",
        help="Output directory (default: output)"
    )

    parser.add_argument(
        "--model",
        "-m",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (default: base)"
    )

    parser.add_argument(
        "--speakers",
        "-s",
        type=int,
        help="Number of speakers"
    )

    parser.add_argument(
        "--skip-diarization",
        action="store_true",
        help="Skip speaker diarization (transcription only)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without confirmation"
    )

    args = parser.parse_args()

    # Run pipeline
    orchestrator = PipelineOrchestrator(
        audio_file=args.audio_file,
        output_dir=args.output,
        model_size=args.model,
        num_speakers=args.speakers,
        skip_diarization=args.skip_diarization,
        force_overwrite=args.force,
    )

    result = orchestrator.run()

    # Exit with appropriate code
    return 0 if result['success'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
