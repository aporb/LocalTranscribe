"""
CLI interface for LocalTranscribe.

Provides commands for processing audio files, health checks, and configuration.
"""

import sys
from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .pipeline import PipelineOrchestrator, PipelineResult
from .utils.errors import (
    LocalTranscribeError,
    AudioFileNotFoundError,
    HuggingFaceTokenError,
)

# Initialize CLI app
app = typer.Typer(
    name="localtranscribe",
    help="🎙️ LocalTranscribe - Speaker diarization and transcription made easy",
    add_completion=False,
)

# Console for Rich output
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
def process(
    audio_file: Path = typer.Argument(
        ...,
        help="Path to audio file to process",
        exists=False,  # We'll handle validation ourselves
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
        help="Whisper model size (larger = more accurate but slower)",
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
    🎙️ Process audio file with speaker diarization and transcription.

    This is the main command that runs the complete pipeline:
    1. Speaker diarization (identifies who spoke when)
    2. Speech-to-text transcription (converts speech to text)
    3. Combination (creates speaker-labeled transcript)

    Example:
        localtranscribe process audio.mp3
        localtranscribe process audio.mp3 -o results/ -m small -s 2
        localtranscribe process audio.mp3 --skip-diarization
    """
    try:
        # Set defaults
        if output_dir is None:
            output_dir = Path("./output")

        if formats is None:
            formats = ["txt", "json", "md"]

        # Print header
        console.print()
        console.print(
            Panel.fit(
                "🎙️ [bold cyan]LocalTranscribe[/bold cyan]\n"
                "Speaker Diarization & Transcription",
                border_style="cyan",
            )
        )
        console.print()

        # Show configuration
        if verbose:
            config_table = Table(title="Configuration", show_header=False)
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")

            config_table.add_row("Audio File", str(audio_file))
            config_table.add_row("Output Directory", str(output_dir))
            config_table.add_row("Model Size", model_size.value)
            config_table.add_row("Implementation", implementation.value)
            config_table.add_row("Skip Diarization", "Yes" if skip_diarization else "No")
            config_table.add_row("Output Formats", ", ".join(formats))
            if num_speakers:
                config_table.add_row("Number of Speakers", str(num_speakers))
            if language:
                config_table.add_row("Language", language)

            console.print(config_table)
            console.print()

        # Initialize orchestrator
        orchestrator = PipelineOrchestrator(
            audio_file=audio_file,
            output_dir=output_dir,
            model_size=model_size.value,
            num_speakers=num_speakers,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
            language=language,
            implementation=implementation.value,
            skip_diarization=skip_diarization,
            output_formats=formats,
            hf_token=hf_token,
            verbose=verbose,
        )

        # Run pipeline
        result: PipelineResult = orchestrator.run()

        # Handle result
        if result.success:
            sys.exit(0)
        else:
            console.print(f"\n[bold red]Pipeline failed:[/bold red] {result.error}")
            sys.exit(1)

    except (AudioFileNotFoundError, HuggingFaceTokenError) as e:
        # These errors already have formatted output
        console.print(f"\n{e}")
        sys.exit(1)
    except LocalTranscribeError as e:
        console.print(f"\n{e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Process interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback

            console.print("\n[dim]Traceback:[/dim]")
            console.print(traceback.format_exc())
        sys.exit(1)


@app.command()
def doctor(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed diagnostic information",
    ),
):
    """
    🏥 Run health check to verify LocalTranscribe setup.

    Checks:
    - Python version
    - Required dependencies
    - Optional dependencies
    - HuggingFace token
    - GPU/MPS availability
    - FFmpeg installation

    Example:
        localtranscribe doctor
        localtranscribe doctor -v
    """
    try:
        from .health.doctor import run_health_check

        console.print()
        console.print(
            Panel.fit(
                "🏥 [bold green]LocalTranscribe Health Check[/bold green]",
                border_style="green",
            )
        )
        console.print()

        # Run health check
        result = run_health_check(verbose=verbose)

        # Exit with appropriate code
        if result["overall_status"] == "healthy":
            console.print("\n✅ [bold green]All systems operational![/bold green]\n")
            sys.exit(0)
        elif result["overall_status"] == "warning":
            console.print(
                "\n⚠️  [bold yellow]Some optional features unavailable[/bold yellow]\n"
            )
            sys.exit(0)
        else:
            console.print(
                "\n❌ [bold red]Critical issues found - setup required[/bold red]\n"
            )
            sys.exit(1)

    except ImportError:
        console.print(
            "[yellow]⚠️  Health check module not available[/yellow]\n"
            "This is expected if you haven't completed setup yet."
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Health check failed:[/bold red] {e}")
        sys.exit(1)


@app.command(name="config-show")
def config_show():
    """
    ⚙️  Show current configuration settings.

    Displays:
    - Configuration file location
    - Current settings
    - Environment variables
    - Default values

    Example:
        localtranscribe config-show
    """
    try:
        from .config.loader import load_config, get_config_path

        console.print()
        console.print(
            Panel.fit(
                "⚙️  [bold blue]LocalTranscribe Configuration[/bold blue]",
                border_style="blue",
            )
        )
        console.print()

        # Get config path
        config_path = get_config_path()
        if config_path and config_path.exists():
            console.print(f"📄 Config file: [cyan]{config_path}[/cyan]\n")
        else:
            console.print(
                "[yellow]ℹ️  No config file found, using defaults[/yellow]\n"
                f"   Create one at: [cyan]{Path.home() / '.localtranscribe' / 'config.yaml'}[/cyan]\n"
            )

        # Load and display config
        config = load_config()

        # Create settings table
        table = Table(title="Current Settings", show_header=True)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_column("Source", style="dim")

        # Add rows from config
        for section, settings in config.items():
            if isinstance(settings, dict):
                for key, value in settings.items():
                    table.add_row(f"{section}.{key}", str(value), "config/default")
            else:
                table.add_row(section, str(settings), "config/default")

        console.print(table)
        console.print()

    except ImportError:
        console.print(
            "[yellow]⚠️  Configuration module not available[/yellow]\n"
            "This is expected if you haven't completed setup yet."
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to load configuration:[/bold red] {e}")
        sys.exit(1)


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
        from .batch import BatchProcessor

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


@app.command()
def label(
    transcript: Path = typer.Argument(
        ...,
        help="Transcript file to relabel",
        exists=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for labeled transcript",
    ),
    labels_file: Optional[Path] = typer.Option(
        None,
        "--labels",
        "-l",
        help="Load labels from JSON file instead of interactive mode",
        exists=True,
    ),
    save_labels: Optional[Path] = typer.Option(
        None,
        "--save-labels",
        help="Path to save label mappings",
    ),
):
    """
    🏷️  Assign custom names to speaker labels in a transcript.

    Interactively assign human-readable names to generic speaker IDs
    (SPEAKER_00, SPEAKER_01) in a transcript file.

    Example:
        localtranscribe label transcript.md
        localtranscribe label transcript.md --labels speakers.json
        localtranscribe label transcript.md -o custom_output.md
    """
    try:
        from .labels import SpeakerLabelManager

        console.print()

        # Initialize label manager
        manager = SpeakerLabelManager()

        # Load existing labels if provided
        if labels_file:
            console.print(f"[cyan]📁 Loading labels from: {labels_file}[/cyan]")
            manager.load_labels(labels_file)

            # Read and apply labels
            with open(transcript, "r") as f:
                transcript_content = f.read()

            labeled_content = manager.apply_labels(transcript_content)

            # Determine output path
            if output is None:
                output = transcript.with_stem(transcript.stem + "_labeled")

            # Save
            with open(output, "w") as f:
                f.write(labeled_content)

            console.print(f"[green]✓[/green] Labeled transcript saved: {output}\n")

        else:
            # Interactive mode
            manager.interactive_label(
                transcript_path=transcript,
                output_path=output,
                labels_path=save_labels,
            )

    except FileNotFoundError as e:
        console.print(f"\n[red]✗ {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def version():
    """
    📦 Show LocalTranscribe version information.

    Example:
        localtranscribe version
    """
    from . import __version__

    console.print()
    console.print(f"🎙️  [bold cyan]LocalTranscribe[/bold cyan] v{__version__}")
    console.print()

    # Show system info
    import platform
    import sys

    table = Table(show_header=False, box=None)
    table.add_column("Label", style="dim")
    table.add_column("Value", style="white")

    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("Platform", platform.platform())
    table.add_row("Architecture", platform.machine())

    console.print(table)
    console.print()


def main():
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
