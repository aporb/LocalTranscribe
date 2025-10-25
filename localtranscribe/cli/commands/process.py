"""Process command - single file processing."""

import sys
from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...pipeline import PipelineOrchestrator, PipelineResult
from ...utils.errors import (
    LocalTranscribeError,
    AudioFileNotFoundError,
    HuggingFaceTokenError,
)

# Create sub-app for process command
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
        ModelSize.medium,
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
    # New options for labeling and proofreading
    labels: Optional[Path] = typer.Option(
        None,
        "--labels",
        "-L",
        help="JSON file with speaker labels (SPEAKER_00: Name)",
        exists=True,
    ),
    save_labels: Optional[Path] = typer.Option(
        None,
        "--save-labels",
        help="Save detected speaker IDs to JSON file",
    ),
    proofread: bool = typer.Option(
        False,
        "--proofread",
        "-p",
        help="Enable automatic proofreading of transcript",
    ),
    proofread_rules: Optional[Path] = typer.Option(
        None,
        "--proofread-rules",
        help="Custom proofreading rules file (JSON/YAML)",
        exists=True,
    ),
    proofread_level: str = typer.Option(
        "standard",
        "--proofread-level",
        help="Proofreading level: minimal, standard, or thorough",
    ),
    simple: bool = typer.Option(
        False,
        "--simple",
        help="Simple mode with smart defaults and interactive prompts",
    ),
):
    """
    🎙️ Process audio file with speaker diarization and transcription.

    This is the main command that runs the complete pipeline:
    1. Speaker diarization (identifies who spoke when)
    2. Speech-to-text transcription (converts speech to text)
    3. Combination (creates speaker-labeled transcript)
    4. Speaker labeling (optional - replace IDs with names)
    5. Proofreading (optional - fix common transcription errors)

    Examples:
        # Simple mode - interactive and beginner-friendly
        localtranscribe process audio.mp3 --simple

        # Basic usage
        localtranscribe process audio.mp3

        # With speaker labels and proofreading
        localtranscribe process audio.mp3 --labels speakers.json --proofread

        # Advanced usage
        localtranscribe process audio.mp3 -o results/ -m medium -s 2 \\
            --labels speakers.json --proofread --proofread-level thorough

        # Skip diarization (single speaker)
        localtranscribe process lecture.mp3 --skip-diarization
    """
    try:
        # Set defaults
        if output_dir is None:
            output_dir = Path("./output")

        if formats is None:
            formats = ["txt", "json", "md"]

        # Simple mode: Interactive setup with smart defaults
        if simple:
            console.print()
            console.print(
                Panel.fit(
                    "🎙️ [bold cyan]LocalTranscribe - Simple Mode[/bold cyan]\n"
                    "Easy setup with smart defaults",
                    border_style="cyan",
                )
            )
            console.print()

            # Use base model by default (good balance)
            if model_size == ModelSize.base:
                console.print("[dim]Using 'base' model (good balance of speed and quality)[/dim]")

            # Ask if they know number of speakers
            if num_speakers is None:
                if typer.confirm("Do you know the exact number of speakers?", default=False):
                    num_speakers = typer.prompt("How many speakers?", type=int)

            # Auto-detect labels file if present
            if labels is None:
                auto_labels = audio_file.parent / "speaker_labels.json"
                if auto_labels.exists():
                    console.print(f"[cyan]✓ Found speaker labels: {auto_labels}[/cyan]")
                    if typer.confirm("Use these speaker labels?", default=True):
                        labels = auto_labels

            # Enable proofreading by default in simple mode
            if not proofread:
                proofread = typer.confirm("Enable automatic proofreading?", default=True)

            # Enable verbose in simple mode for better feedback
            verbose = True

            console.print()

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
            if labels:
                config_table.add_row("Speaker Labels", str(labels))
            if save_labels:
                config_table.add_row("Save Labels To", str(save_labels))
            if proofread:
                config_table.add_row("Proofreading", f"Enabled ({proofread_level})")
                if proofread_rules:
                    config_table.add_row("Custom Rules", str(proofread_rules))

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
            # New parameters
            labels_file=labels,
            save_labels=save_labels,
            enable_proofreading=proofread,
            proofreading_rules=proofread_rules,
            proofreading_level=proofread_level,
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
