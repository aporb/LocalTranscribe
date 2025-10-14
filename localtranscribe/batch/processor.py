"""
Batch processing implementation for LocalTranscribe.

Handles processing of multiple audio files with parallel execution,
progress tracking, and error recovery.
"""

import logging
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)
from rich.table import Table
from rich.panel import Panel

from ..pipeline import PipelineOrchestrator, PipelineResult
from ..utils.errors import LocalTranscribeError

console = Console()
logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """Result of processing a single file."""

    file_name: str
    success: bool
    duration: float = 0.0
    output_files: List[Path] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class BatchResult:
    """Result of batch processing operation."""

    total: int
    successful: int
    failed: int
    skipped: int
    results: List[ProcessResult]
    total_duration: float
    failed_files: List[str] = field(default_factory=list)


class BatchProcessor:
    """
    Process multiple audio files through the LocalTranscribe pipeline.

    Features:
    - Automatic file discovery in directories
    - Parallel processing with configurable workers
    - Progress tracking with Rich UI
    - Error handling and recovery
    - Resume capability (skip existing outputs)
    """

    # Supported audio file extensions
    AUDIO_EXTENSIONS = {
        # Audio formats
        ".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma", ".opus",
        # Video formats (audio extraction)
        ".mp4", ".mov", ".avi", ".mkv", ".webm"
    }

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        model_size: str = "base",
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        language: Optional[str] = None,
        implementation: str = "auto",
        skip_diarization: bool = False,
        output_formats: Optional[List[str]] = None,
        max_workers: int = 2,
        skip_existing: bool = False,
        recursive: bool = False,
        hf_token: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        Initialize batch processor.

        Args:
            input_dir: Directory containing audio files
            output_dir: Directory for output files
            model_size: Whisper model size
            num_speakers: Exact number of speakers (if known)
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
            language: Force specific language
            implementation: Whisper implementation to use
            skip_diarization: Skip speaker diarization
            output_formats: List of output formats
            max_workers: Maximum parallel workers (default: 2 for GPU memory)
            skip_existing: Skip files that already have outputs
            recursive: Recursively search subdirectories
            hf_token: HuggingFace token
            verbose: Enable verbose output
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.model_size = model_size
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.language = language
        self.implementation = implementation
        self.skip_diarization = skip_diarization
        self.output_formats = output_formats or ["txt", "json", "md"]
        self.max_workers = max_workers
        self.skip_existing = skip_existing
        self.recursive = recursive
        self.hf_token = hf_token
        self.verbose = verbose

        # Validate directories
        if not self.input_dir.exists():
            raise LocalTranscribeError(
                f"Input directory not found: {self.input_dir}",
                suggestions=[
                    "Check the directory path",
                    "Ensure the directory exists",
                    "Use an absolute path if relative path isn't working",
                ],
            )

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def find_audio_files(self) -> List[Path]:
        """
        Discover audio files in input directory.

        Returns:
            List of audio file paths
        """
        files: List[Path] = []

        if self.recursive:
            # Recursive search
            for ext in self.AUDIO_EXTENSIONS:
                files.extend(self.input_dir.rglob(f"*{ext}"))
        else:
            # Non-recursive search
            for ext in self.AUDIO_EXTENSIONS:
                files.extend(self.input_dir.glob(f"*{ext}"))

        # Sort by name for consistent ordering
        return sorted(files)

    def should_skip_file(self, audio_file: Path) -> bool:
        """
        Check if file should be skipped (output already exists).

        Args:
            audio_file: Audio file path

        Returns:
            True if file should be skipped
        """
        if not self.skip_existing:
            return False

        # Check if any output files exist
        base_name = audio_file.stem
        for fmt in self.output_formats:
            output_file = self.output_dir / f"{base_name}_combined.{fmt}"
            if output_file.exists():
                return True

        return False

    def process_single_file(self, audio_file: Path) -> ProcessResult:
        """
        Process a single audio file through the pipeline.

        Args:
            audio_file: Path to audio file

        Returns:
            ProcessResult with outcome
        """
        file_name = audio_file.name
        start_time = time.time()

        try:
            # Check if should skip
            if self.should_skip_file(audio_file):
                return ProcessResult(
                    file_name=file_name,
                    success=True,
                    duration=0.0,
                    output_files=[],
                    error="Skipped (output exists)",
                )

            # Initialize orchestrator
            orchestrator = PipelineOrchestrator(
                audio_file=audio_file,
                output_dir=self.output_dir,
                model_size=self.model_size,
                num_speakers=self.num_speakers,
                min_speakers=self.min_speakers,
                max_speakers=self.max_speakers,
                language=self.language,
                implementation=self.implementation,
                skip_diarization=self.skip_diarization,
                output_formats=self.output_formats,
                hf_token=self.hf_token,
                verbose=False,  # Disable verbose for batch to avoid clutter
            )

            # Run pipeline
            result: PipelineResult = orchestrator.run()

            duration = time.time() - start_time

            if result.success:
                return ProcessResult(
                    file_name=file_name,
                    success=True,
                    duration=duration,
                    output_files=list(result.outputs.values()) if result.outputs else [],
                )
            else:
                return ProcessResult(
                    file_name=file_name,
                    success=False,
                    duration=duration,
                    error=result.error or "Unknown error",
                )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to process {file_name}: {e}")
            return ProcessResult(
                file_name=file_name,
                success=False,
                duration=duration,
                error=str(e),
            )

    def process_batch(self) -> BatchResult:
        """
        Process all audio files in the input directory.

        Returns:
            BatchResult with aggregated results
        """
        # Find audio files
        console.print("\n[cyan]🔍 Discovering audio files...[/cyan]")
        audio_files = self.find_audio_files()

        if not audio_files:
            console.print(
                f"\n[yellow]⚠️  No audio files found in {self.input_dir}[/yellow]\n"
                f"Supported formats: {', '.join(sorted(self.AUDIO_EXTENSIONS))}"
            )
            return BatchResult(
                total=0,
                successful=0,
                failed=0,
                skipped=0,
                results=[],
                total_duration=0.0,
            )

        console.print(f"[green]✓[/green] Found {len(audio_files)} audio files\n")

        # Show configuration
        if self.verbose:
            config_table = Table(title="Batch Configuration", show_header=False, box=None)
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")

            config_table.add_row("Input Directory", str(self.input_dir))
            config_table.add_row("Output Directory", str(self.output_dir))
            config_table.add_row("Model Size", self.model_size)
            config_table.add_row("Max Workers", str(self.max_workers))
            config_table.add_row("Skip Existing", "Yes" if self.skip_existing else "No")
            config_table.add_row("Output Formats", ", ".join(self.output_formats))

            console.print(config_table)
            console.print()

        # Initialize results
        results: List[ProcessResult] = []
        start_time = time.time()

        # Process files
        if self.max_workers == 1:
            # Sequential processing
            results = self._process_sequential(audio_files)
        else:
            # Parallel processing
            results = self._process_parallel(audio_files)

        total_duration = time.time() - start_time

        # Aggregate results
        successful = sum(1 for r in results if r.success and not r.error)
        failed = sum(1 for r in results if not r.success)
        skipped = sum(1 for r in results if r.success and r.error == "Skipped (output exists)")
        failed_files = [r.file_name for r in results if not r.success]

        batch_result = BatchResult(
            total=len(audio_files),
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=results,
            total_duration=total_duration,
            failed_files=failed_files,
        )

        # Display summary
        self._display_summary(batch_result)

        return batch_result

    def _process_sequential(self, audio_files: List[Path]) -> List[ProcessResult]:
        """Process files sequentially with progress bar."""
        results: List[ProcessResult] = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:

            task = progress.add_task(
                "[cyan]Processing files...", total=len(audio_files)
            )

            for audio_file in audio_files:
                progress.update(
                    task,
                    description=f"[cyan]Processing: {audio_file.name}",
                )
                result = self.process_single_file(audio_file)
                results.append(result)
                progress.advance(task)

        return results

    def _process_parallel(self, audio_files: List[Path]) -> List[ProcessResult]:
        """Process files in parallel with progress bar."""
        results: List[ProcessResult] = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:

            task = progress.add_task(
                f"[cyan]Processing {len(audio_files)} files...",
                total=len(audio_files),
            )

            # Submit all tasks
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Map futures to file names
                future_to_file = {
                    executor.submit(self.process_single_file, audio_file): audio_file
                    for audio_file in audio_files
                }

                # Process completed tasks
                for future in as_completed(future_to_file):
                    audio_file = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)

                        # Update progress
                        status = "✓" if result.success else "✗"
                        progress.update(
                            task,
                            description=f"[cyan]{status} Processed: {audio_file.name}",
                        )
                        progress.advance(task)

                    except Exception as e:
                        # Handle future exception
                        logger.error(f"Worker failed for {audio_file.name}: {e}")
                        results.append(
                            ProcessResult(
                                file_name=audio_file.name,
                                success=False,
                                error=f"Worker error: {e}",
                            )
                        )
                        progress.advance(task)

        return results

    def _display_summary(self, result: BatchResult) -> None:
        """Display batch processing summary."""
        console.print()
        console.print(Panel.fit(
            "[bold cyan]Batch Processing Complete[/bold cyan]",
            border_style="cyan",
        ))
        console.print()

        # Summary table
        summary = Table(show_header=False, box=None)
        summary.add_column("Metric", style="cyan")
        summary.add_column("Count", style="white", justify="right")

        summary.add_row("Total Files", str(result.total))
        summary.add_row(
            "Successful",
            f"[green]{result.successful}[/green]",
        )
        if result.skipped > 0:
            summary.add_row(
                "Skipped",
                f"[yellow]{result.skipped}[/yellow]",
            )
        if result.failed > 0:
            summary.add_row(
                "Failed",
                f"[red]{result.failed}[/red]",
            )
        summary.add_row(
            "Total Time",
            f"{result.total_duration:.1f}s",
        )
        summary.add_row(
            "Average Time",
            f"{result.total_duration / result.total:.1f}s/file" if result.total > 0 else "N/A",
        )

        console.print(summary)
        console.print()

        # Show failed files if any
        if result.failed > 0:
            console.print("[bold red]Failed Files:[/bold red]")
            for file_result in result.results:
                if not file_result.success:
                    console.print(
                        f"  [red]✗[/red] {file_result.file_name}: {file_result.error}"
                    )
            console.print()

        # Success message
        if result.failed == 0:
            console.print("[bold green]✓ All files processed successfully![/bold green]\n")
        elif result.successful > 0:
            console.print(
                f"[yellow]⚠️  {result.successful} files succeeded, {result.failed} failed[/yellow]\n"
            )
        else:
            console.print("[bold red]✗ All files failed[/bold red]\n")

        # Output location
        console.print(f"Output files: [cyan]{self.output_dir}[/cyan]\n")
