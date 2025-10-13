"""
Batch Processor - Complete Implementation Example

This module demonstrates how to process multiple audio files efficiently
with parallel processing, progress tracking, and error recovery.

Features:
- Directory scanning with configurable patterns
- Parallel processing with worker pool
- Progress tracking with Rich UI
- Per-file error handling (continues on failure)
- Results summary and detailed logging
- Resume capability for failed files

Usage:
    from batch_processor import BatchProcessor

    processor = BatchProcessor(
        input_dir="./audio_files",
        output_dir="./transcripts",
        model_size="base",
        num_speakers=2,
        max_workers=2
    )

    results = processor.process_batch()
"""

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
import logging
from datetime import datetime

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.panel import Panel

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Status of file processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class FileResult:
    """Result of processing a single file."""
    file_name: str
    file_path: str
    status: ProcessingStatus
    duration: Optional[float] = None
    output_files: Optional[Dict[str, str]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class BatchProcessor:
    """
    Process multiple audio files through the transcription pipeline.

    This class handles discovery, parallel processing, error recovery,
    and results aggregation for batch transcription operations.
    """

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        model_size: str = "base",
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        max_workers: int = 2,
        file_patterns: Optional[List[str]] = None,
        recursive: bool = False,
        continue_on_error: bool = True,
        skip_existing: bool = False,
    ):
        """
        Initialize batch processor.

        Args:
            input_dir: Directory containing audio files
            output_dir: Directory for output transcripts
            model_size: Whisper model size (tiny/base/small/medium/large)
            num_speakers: Exact number of speakers (optional)
            min_speakers: Minimum speakers to detect (optional)
            max_speakers: Maximum speakers to detect (optional)
            max_workers: Maximum parallel processes (2-4 recommended)
            file_patterns: File patterns to match (default: common audio formats)
            recursive: Search subdirectories recursively
            continue_on_error: Continue processing if a file fails
            skip_existing: Skip files that have already been processed
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.model_size = model_size
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.max_workers = max_workers
        self.file_patterns = file_patterns or [
            "*.mp3", "*.wav", "*.ogg", "*.m4a", "*.flac"
        ]
        self.recursive = recursive
        self.continue_on_error = continue_on_error
        self.skip_existing = skip_existing

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Results tracking
        self.results: List[FileResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def discover_audio_files(self) -> List[Path]:
        """
        Discover audio files in input directory.

        Returns:
            List of Path objects for discovered audio files
        """
        audio_files = []

        for pattern in self.file_patterns:
            if self.recursive:
                audio_files.extend(self.input_dir.rglob(pattern))
            else:
                audio_files.extend(self.input_dir.glob(pattern))

        # Remove duplicates and sort
        audio_files = sorted(set(audio_files))

        # Filter out already processed files if skip_existing is True
        if self.skip_existing:
            audio_files = [
                f for f in audio_files
                if not self._is_already_processed(f)
            ]

        return audio_files

    def _is_already_processed(self, audio_file: Path) -> bool:
        """
        Check if audio file has already been processed.

        Args:
            audio_file: Path to audio file

        Returns:
            True if output files exist
        """
        base_name = audio_file.stem
        expected_outputs = [
            self.output_dir / f"{base_name}_combined_transcript.md",
            self.output_dir / f"{base_name}_transcript.json",
        ]

        return all(f.exists() for f in expected_outputs)

    def process_single_file(self, audio_file: Path) -> FileResult:
        """
        Process a single audio file through the pipeline.

        Args:
            audio_file: Path to audio file

        Returns:
            FileResult with processing status and outputs
        """
        started_at = datetime.now().isoformat()

        try:
            logger.info(f"Processing: {audio_file.name}")
            start_time = time.time()

            # In real implementation, this would call the pipeline orchestrator:
            # from pipeline_orchestrator import PipelineOrchestrator
            #
            # orchestrator = PipelineOrchestrator(
            #     audio_file=audio_file,
            #     output_dir=self.output_dir,
            #     model_size=self.model_size,
            #     num_speakers=self.num_speakers,
            # )
            #
            # result = orchestrator.run()

            # Simulated successful processing
            time.sleep(0.1)  # Simulate processing time

            duration = time.time() - start_time
            base_name = audio_file.stem

            output_files = {
                'transcript_txt': str(self.output_dir / f"{base_name}_transcript.txt"),
                'transcript_json': str(self.output_dir / f"{base_name}_transcript.json"),
                'transcript_md': str(self.output_dir / f"{base_name}_transcript.md"),
                'combined': str(self.output_dir / f"{base_name}_combined_transcript.md"),
            }

            return FileResult(
                file_name=audio_file.name,
                file_path=str(audio_file),
                status=ProcessingStatus.SUCCESS,
                duration=duration,
                output_files=output_files,
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )

        except KeyboardInterrupt:
            raise  # Re-raise to stop processing

        except Exception as e:
            logger.error(f"Failed to process {audio_file.name}: {e}")

            return FileResult(
                file_name=audio_file.name,
                file_path=str(audio_file),
                status=ProcessingStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )

    def process_batch(self) -> Dict[str, Any]:
        """
        Process all discovered audio files with parallel processing.

        Returns:
            Dictionary with results summary and detailed results
        """
        console.print(Panel.fit(
            "[bold blue]📁 Batch Processing[/bold blue]",
            subtitle=f"Input: {self.input_dir}"
        ))

        # Discover files
        audio_files = self.discover_audio_files()

        if not audio_files:
            console.print(
                f"[yellow]⚠️  No audio files found in {self.input_dir}[/yellow]"
            )
            console.print(f"\nSearched for: {', '.join(self.file_patterns)}")
            console.print(f"Recursive: {self.recursive}")

            return {
                'status': 'no_files',
                'message': 'No audio files found',
                'total_files': 0,
                'results': []
            }

        console.print(f"\n✅ Found {len(audio_files)} audio file(s)")
        console.print(f"Output directory: {self.output_dir}")
        console.print(f"Model: {self.model_size}")
        console.print(f"Workers: {self.max_workers}\n")

        # Track timing
        self.start_time = time.time()

        # Process files with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        ) as progress:

            task = progress.add_task(
                f"Processing {len(audio_files)} files...",
                total=len(audio_files)
            )

            # Use ProcessPoolExecutor for true parallelism
            # Note: Limited by max_workers to avoid GPU memory issues
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:

                # Submit all jobs
                future_to_file = {
                    executor.submit(self.process_single_file, audio_file): audio_file
                    for audio_file in audio_files
                }

                # Process completed futures
                for future in as_completed(future_to_file):
                    audio_file = future_to_file[future]

                    try:
                        result = future.result()
                        self.results.append(result)

                        # Update progress
                        progress.update(task, advance=1)

                        # Log result
                        if result.status == ProcessingStatus.SUCCESS:
                            logger.info(
                                f"✓ {result.file_name} "
                                f"({result.duration:.1f}s)"
                            )
                        else:
                            logger.error(f"✗ {result.file_name}: {result.error}")

                            # Stop on first error if not continuing
                            if not self.continue_on_error:
                                console.print(
                                    f"\n[red]❌ Stopping due to error in: "
                                    f"{result.file_name}[/red]"
                                )
                                executor.shutdown(wait=False, cancel_futures=True)
                                break

                    except KeyboardInterrupt:
                        console.print("\n[yellow]⚠️  Interrupted by user[/yellow]")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

                    except Exception as e:
                        logger.exception(f"Unexpected error processing {audio_file.name}")
                        # Continue with next file

        self.end_time = time.time()

        # Generate summary
        summary = self._generate_summary()

        # Display summary
        self._display_summary(summary)

        # Save detailed results
        self._save_results(summary)

        return summary

    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary of batch processing results.

        Returns:
            Dictionary with summary statistics
        """
        successful = [r for r in self.results if r.status == ProcessingStatus.SUCCESS]
        failed = [r for r in self.results if r.status == ProcessingStatus.FAILED]

        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        processing_duration = sum(r.duration for r in successful if r.duration)

        return {
            'summary': {
                'total_files': len(self.results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': len(successful) / len(self.results) * 100 if self.results else 0,
                'total_duration_seconds': total_duration,
                'processing_duration_seconds': processing_duration,
                'average_duration_per_file': processing_duration / len(successful) if successful else 0,
            },
            'configuration': {
                'input_dir': str(self.input_dir),
                'output_dir': str(self.output_dir),
                'model_size': self.model_size,
                'num_speakers': self.num_speakers,
                'max_workers': self.max_workers,
                'file_patterns': self.file_patterns,
                'recursive': self.recursive,
            },
            'successful_files': [r.to_dict() for r in successful],
            'failed_files': [r.to_dict() for r in failed],
            'timestamp': datetime.now().isoformat(),
        }

    def _display_summary(self, summary: Dict[str, Any]):
        """
        Display batch processing summary in terminal.

        Args:
            summary: Summary dictionary from _generate_summary
        """
        stats = summary['summary']

        console.print(f"\n[bold]Batch Processing Complete[/bold]")
        console.print(f"Total time: {stats['total_duration_seconds']:.1f}s\n")

        # Summary table
        table = Table(title="Results Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Files", str(stats['total_files']))
        table.add_row(
            "Successful",
            f"[green]{stats['successful']}[/green]"
        )
        table.add_row(
            "Failed",
            f"[red]{stats['failed']}[/red]" if stats['failed'] > 0 else "0"
        )
        table.add_row(
            "Success Rate",
            f"{stats['success_rate']:.1f}%"
        )
        table.add_row(
            "Avg Duration/File",
            f"{stats['average_duration_per_file']:.1f}s"
        )

        console.print(table)

        # Failed files detail
        if summary['failed_files']:
            console.print("\n[bold red]Failed Files:[/bold red]")
            for result in summary['failed_files']:
                console.print(f"  - {result['file_name']}: {result['error']}")

    def _save_results(self, summary: Dict[str, Any]):
        """
        Save detailed results to file.

        Args:
            summary: Summary dictionary from _generate_summary
        """
        # Save JSON summary
        summary_file = self.output_dir / "batch_summary.json"

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        console.print(f"\n📝 Summary saved to: {summary_file}")

        # Save CSV for easy analysis
        csv_file = self.output_dir / "batch_results.csv"

        try:
            import csv

            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    'File Name',
                    'Status',
                    'Duration (s)',
                    'Error',
                    'Started At',
                    'Completed At'
                ])

                # Rows
                for result in self.results:
                    writer.writerow([
                        result.file_name,
                        result.status.value,
                        f"{result.duration:.2f}" if result.duration else "N/A",
                        result.error or "",
                        result.started_at or "",
                        result.completed_at or "",
                    ])

            console.print(f"📊 CSV report saved to: {csv_file}")

        except ImportError:
            logger.warning("CSV module not available, skipping CSV export")

    def retry_failed(self) -> Dict[str, Any]:
        """
        Retry processing failed files from previous batch.

        Returns:
            Summary of retry attempt
        """
        # Load previous summary
        summary_file = self.output_dir / "batch_summary.json"

        if not summary_file.exists():
            console.print(
                "[yellow]⚠️  No previous batch summary found[/yellow]"
            )
            return {'status': 'no_previous_batch'}

        with open(summary_file) as f:
            previous_summary = json.load(f)

        failed_files = previous_summary.get('failed_files', [])

        if not failed_files:
            console.print("[green]✅ No failed files to retry[/green]")
            return {'status': 'no_failures'}

        console.print(
            f"[blue]🔄 Retrying {len(failed_files)} failed file(s)[/blue]\n"
        )

        # Convert to Path objects
        audio_files = [Path(f['file_path']) for f in failed_files]

        # Reset results
        self.results = []

        # Process files (same as process_batch but with predetermined files)
        self.start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:

            task = progress.add_task(
                f"Retrying {len(audio_files)} files...",
                total=len(audio_files)
            )

            for audio_file in audio_files:
                result = self.process_single_file(audio_file)
                self.results.append(result)
                progress.update(task, advance=1)

        self.end_time = time.time()

        # Generate and display summary
        summary = self._generate_summary()
        self._display_summary(summary)

        # Save results with retry suffix
        retry_summary_file = self.output_dir / "batch_summary_retry.json"
        with open(retry_summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        console.print(f"\n📝 Retry summary saved to: {retry_summary_file}")

        return summary


# =============================================================================
# CLI Integration Example
# =============================================================================

def main():
    """Example command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch process audio files for transcription"
    )

    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing audio files"
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
        "--workers",
        "-w",
        type=int,
        default=2,
        help="Maximum parallel workers (default: 2)"
    )

    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Search subdirectories recursively"
    )

    parser.add_argument(
        "--retry",
        action="store_true",
        help="Retry previously failed files"
    )

    args = parser.parse_args()

    # Create processor
    processor = BatchProcessor(
        input_dir=args.input_dir,
        output_dir=args.output,
        model_size=args.model,
        num_speakers=args.speakers,
        max_workers=args.workers,
        recursive=args.recursive,
    )

    # Process or retry
    if args.retry:
        results = processor.retry_failed()
    else:
        results = processor.process_batch()

    # Exit with appropriate code
    if results.get('status') == 'no_files':
        return 1

    failed_count = results.get('summary', {}).get('failed', 0)
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
