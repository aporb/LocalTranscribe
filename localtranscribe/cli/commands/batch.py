"""Batch command - process multiple files."""

import sys
from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel

from ...utils.errors import LocalTranscribeError

# Create sub-app for batch command
app = typer.Typer()
console = Console()


class ModelSize(str, Enum):
    """Whisper model sizes."""

    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"


class Implementation(str, Enum):
    """Whisper implementation options."""

    auto = "auto"
    mlx = "mlx"
    faster = "faster"
    original = "original"


@app.command()
def batch(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing audio files to process",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for results (default: ./output)",
    ),
    model_size: ModelSize = typer.Option(
        ModelSize.base,
        "--model",
        "-m",
        help="Whisper model size",
    ),
    num_speakers: Optional[int] = typer.Option(
        None,
        "--speakers",
        "-s",
        help="Exact number of speakers (if known)",
        min=1,
        max=20,
    ),
    min_speakers: Optional[int] = typer.Option(
        None,
        "--min-speakers",
        help="Minimum number of speakers",
        min=1,
        max=20,
    ),
    max_speakers: Optional[int] = typer.Option(
        None,
        "--max-speakers",
        help="Maximum number of speakers",
        min=1,
        max=20,
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Force specific language (e.g., 'en', 'es', 'fr')",
    ),
    implementation: Implementation = typer.Option(
        Implementation.auto,
        "--implementation",
        "-i",
        help="Whisper implementation to use",
    ),
    skip_diarization: bool = typer.Option(
        False,
        "--skip-diarization",
        help="Skip speaker diarization (transcription only)",
    ),
    formats: Optional[List[str]] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output formats (txt, json, srt, md)",
    ),
    workers: int = typer.Option(
        2,
        "--workers",
        "-w",
        help="Maximum parallel workers (default: 2 for GPU memory)",
        min=1,
        max=16,
    ),
    skip_existing: bool = typer.Option(
        False,
        "--skip-existing",
        help="Skip files that already have outputs",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Recursively search subdirectories",
    ),
    hf_token: Optional[str] = typer.Option(
        None,
        "--hf-token",
        help="HuggingFace token (overrides .env)",
        envvar="HUGGINGFACE_TOKEN",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
):
    """
    📦 Process multiple audio files in a directory (batch mode).

    This command processes all audio files in a directory through the complete pipeline.
    Files are processed in parallel for efficiency, with configurable worker count.

    Supported formats: MP3, WAV, OGG, M4A, FLAC, AAC, WMA, OPUS

    Example:
        localtranscribe batch ./audio_files/
        localtranscribe batch ./audio/ -o ./transcripts/ -m small --workers 4
        localtranscribe batch ./audio/ --skip-existing --recursive
    """
    try:
        from ...batch import BatchProcessor

        # Set defaults
        if output_dir is None:
            output_dir = Path("./output")

        if formats is None:
            formats = ["txt", "json", "md"]

        # Print header
        console.print()
        console.print(
            Panel.fit(
                "📦 [bold cyan]LocalTranscribe Batch Mode[/bold cyan]\n"
                "Processing Multiple Audio Files",
                border_style="cyan",
            )
        )
        console.print()

        # Initialize batch processor
        processor = BatchProcessor(
            input_dir=input_dir,
            output_dir=output_dir,
            model_size=model_size.value,
            num_speakers=num_speakers,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
            language=language,
            implementation=implementation.value,
            skip_diarization=skip_diarization,
            output_formats=formats,
            max_workers=workers,
            skip_existing=skip_existing,
            recursive=recursive,
            hf_token=hf_token,
            verbose=verbose,
        )

        # Run batch processing
        result = processor.process_batch()

        # Exit with appropriate code
        if result.failed == 0:
            sys.exit(0)
        elif result.successful > 0:
            # Partial success
            sys.exit(0)
        else:
            # Complete failure
            sys.exit(1)

    except LocalTranscribeError as e:
        console.print(f"\n{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Batch processing interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print("\n[dim]Traceback:[/dim]")
            console.print(traceback.format_exc())
        sys.exit(1)
