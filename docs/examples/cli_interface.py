"""
LocalTranscribe CLI Interface - Complete Implementation Example

This is a reference implementation showing how LocalTranscribe should work
with a modern CLI interface using Typer and Rich.

Usage Examples:
    # Process single file
    localtranscribe process meeting.mp3 --model base --speakers 2

    # Batch processing
    localtranscribe batch ./audio/ --output ./transcripts/

    # Label speakers
    localtranscribe label transcript.md

    # Health check
    localtranscribe doctor

    # Show version
    localtranscribe --version
"""

from pathlib import Path
from typing import Optional, List
from enum import Enum
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
import json

# Initialize Typer app and Rich console
app = typer.Typer(
    name="localtranscribe",
    help="🎙️  Offline audio transcription with speaker diarization",
    add_completion=True,
)

console = Console()

# Version
__version__ = "2.0.0"


# Enums for type-safe options
class ModelSize(str, Enum):
    """Whisper model sizes."""
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    large = "large"


class WhisperImplementation(str, Enum):
    """Whisper implementation choices."""
    auto = "auto"
    mlx = "mlx"
    faster = "faster"
    original = "original"


class OutputFormat(str, Enum):
    """Output format choices."""
    txt = "txt"
    srt = "srt"
    json = "json"
    md = "md"


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"LocalTranscribe version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    LocalTranscribe - Offline audio transcription with speaker diarization.

    Optimized for Apple Silicon (M1/M2/M3/M4), but works on any Mac.

    Get started:
        localtranscribe process your_audio.mp3
    """
    pass


@app.command()
def process(
    input_file: Path = typer.Argument(
        ...,
        help="Audio file to process (MP3, WAV, OGG, M4A, FLAC)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        "output",
        "--output",
        "-o",
        help="Output directory for transcripts",
        file_okay=False,
        dir_okay=True,
    ),
    model: ModelSize = typer.Option(
        ModelSize.base,
        "--model",
        "-m",
        help="Whisper model size (larger = more accurate but slower)",
    ),
    implementation: WhisperImplementation = typer.Option(
        WhisperImplementation.auto,
        "--impl",
        help="Whisper implementation to use",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Force specific language (en, es, fr, de, etc.). Default: auto-detect",
    ),
    speakers: Optional[int] = typer.Option(
        None,
        "--speakers",
        "-s",
        help="Exact number of speakers (overrides min/max)",
        min=1,
        max=10,
    ),
    min_speakers: Optional[int] = typer.Option(
        None,
        "--min-speakers",
        help="Minimum number of speakers to detect",
        min=1,
        max=10,
    ),
    max_speakers: Optional[int] = typer.Option(
        None,
        "--max-speakers",
        help="Maximum number of speakers to detect",
        min=1,
        max=10,
    ),
    skip_diarization: bool = typer.Option(
        False,
        "--skip-diarization",
        help="Skip speaker diarization (transcription only)",
    ),
    formats: List[OutputFormat] = typer.Option(
        [OutputFormat.txt, OutputFormat.md],
        "--format",
        "-f",
        help="Output formats (can specify multiple times)",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (overrides defaults)",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing output files without confirmation",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed progress information",
    ),
):
    """
    Process audio file through full transcription pipeline.

    This command runs speaker diarization (who spoke when) and speech-to-text
    transcription (what was said), then combines the results into a speaker-labeled
    transcript.

    Examples:
        # Basic usage
        localtranscribe process meeting.mp3

        # With custom settings
        localtranscribe process interview.mp3 --model medium --speakers 2

        # Multiple output formats
        localtranscribe process lecture.wav --format txt --format srt --format json

        # Skip diarization (transcription only)
        localtranscribe process podcast.mp3 --skip-diarization
    """

    console.print(Panel.fit(
        "[bold blue]🎙️  LocalTranscribe Pipeline[/bold blue]",
        subtitle=f"Processing: {input_file.name}"
    ))

    # Load configuration if provided
    if config:
        console.print(f"📄 Loading configuration from: {config}")
        # Implementation would load and merge config here

    # Validate speakers configuration
    if speakers and (min_speakers or max_speakers):
        console.print(
            "[yellow]⚠️  Warning: --speakers overrides --min-speakers and --max-speakers[/yellow]"
        )

    # Check output directory exists or create it
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check for existing output files
    base_name = input_file.stem
    existing_files = list(output_dir.glob(f"{base_name}*"))

    if existing_files and not force:
        console.print(f"\n[yellow]⚠️  Found {len(existing_files)} existing output file(s)[/yellow]")
        overwrite = typer.confirm("Overwrite existing files?")
        if not overwrite:
            console.print("[red]Aborted by user[/red]")
            raise typer.Exit()

    try:
        # Import pipeline orchestrator
        # from localtranscribe.core.pipeline import PipelineOrchestrator

        # This is where the actual pipeline would be called
        console.print("\n✅ Prerequisites validated")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:

            # Stage 1: Diarization
            if not skip_diarization:
                task1 = progress.add_task(
                    "[cyan]Stage 1/3: Speaker Diarization...",
                    total=100
                )
                # Simulate progress
                for i in range(100):
                    progress.update(task1, advance=1)
                    # In real implementation: diarization_result = diarize(...)

                console.print("✅ Diarization complete")

            # Stage 2: Transcription
            stage_num = 2 if not skip_diarization else 1
            total_stages = 3 if not skip_diarization else 1

            task2 = progress.add_task(
                f"[cyan]Stage {stage_num}/{total_stages}: Transcription ({model.value} model)...",
                total=100
            )
            for i in range(100):
                progress.update(task2, advance=1)
                # In real implementation: transcription_result = transcribe(...)

            console.print("✅ Transcription complete")

            # Stage 3: Combine
            if not skip_diarization:
                task3 = progress.add_task(
                    "[cyan]Stage 3/3: Combining results...",
                    total=100
                )
                for i in range(100):
                    progress.update(task3, advance=1)
                    # In real implementation: combined_result = combine(...)

                console.print("✅ Combining complete")

        # Success message
        console.print(f"\n[bold green]✅ Pipeline completed successfully![/bold green]")
        console.print(f"\nOutput directory: {output_dir}")
        console.print("\nGenerated files:")
        for fmt in formats:
            output_file = output_dir / f"{base_name}_transcript.{fmt.value}"
            console.print(f"  - {output_file.name}")

        if not skip_diarization:
            combined_file = output_dir / f"{base_name}_combined_transcript.md"
            console.print(f"  - {combined_file.name}")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Pipeline interrupted by user[/yellow]")
        raise typer.Exit(code=130)

    except Exception as e:
        console.print(f"\n[red]❌ Pipeline failed: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def batch(
    input_dir: Path = typer.Argument(
        ...,
        help="Directory containing audio files to process",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output_dir: Path = typer.Option(
        "output",
        "--output",
        "-o",
        help="Output directory for all transcripts",
        file_okay=False,
        dir_okay=True,
    ),
    model: ModelSize = typer.Option(
        ModelSize.base,
        "--model",
        "-m",
        help="Whisper model size for all files",
    ),
    speakers: Optional[int] = typer.Option(
        None,
        "--speakers",
        "-s",
        help="Number of speakers (same for all files)",
    ),
    workers: int = typer.Option(
        2,
        "--workers",
        "-w",
        help="Maximum parallel processes (be careful with GPU memory)",
        min=1,
        max=8,
    ),
    patterns: List[str] = typer.Option(
        ["*.mp3", "*.wav", "*.ogg", "*.m4a", "*.flac"],
        "--pattern",
        "-p",
        help="File patterns to match (can specify multiple)",
    ),
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Search for audio files recursively in subdirectories",
    ),
    continue_on_error: bool = typer.Option(
        True,
        "--continue-on-error",
        help="Continue processing remaining files if one fails",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Show detailed progress for each file",
    ),
):
    """
    Process multiple audio files in a directory.

    This command automatically discovers audio files and processes them through
    the full pipeline. Files are processed with limited parallelism to avoid
    GPU memory issues.

    Examples:
        # Process all audio files in directory
        localtranscribe batch ./audio_files/

        # Custom settings and output location
        localtranscribe batch ./interviews/ --output ./transcripts/ --model medium

        # Process with more parallelism
        localtranscribe batch ./podcasts/ --workers 4

        # Recursive search
        localtranscribe batch ./archive/ --recursive
    """

    console.print(Panel.fit(
        "[bold blue]📁 LocalTranscribe Batch Processor[/bold blue]",
        subtitle=f"Scanning: {input_dir}"
    ))

    # Discover audio files
    audio_files = []
    for pattern in patterns:
        if recursive:
            audio_files.extend(input_dir.rglob(pattern))
        else:
            audio_files.extend(input_dir.glob(pattern))

    audio_files = sorted(set(audio_files))  # Remove duplicates and sort

    if not audio_files:
        console.print(f"[yellow]⚠️  No audio files found in {input_dir}[/yellow]")
        console.print(f"\nSearched for patterns: {', '.join(patterns)}")
        console.print(f"Recursive: {recursive}")
        raise typer.Exit(code=1)

    console.print(f"\n✅ Found {len(audio_files)} audio file(s)")
    console.print(f"Output directory: {output_dir}\n")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Confirm batch operation
    if len(audio_files) > 10:
        proceed = typer.confirm(
            f"Process {len(audio_files)} files with {workers} parallel workers?"
        )
        if not proceed:
            console.print("[red]Aborted by user[/red]")
            raise typer.Exit()

    # Process files
    results = {'successful': [], 'failed': []}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:

        task = progress.add_task(
            f"Processing {len(audio_files)} files...",
            total=len(audio_files)
        )

        for audio_file in audio_files:
            try:
                if verbose:
                    console.print(f"\n📄 Processing: {audio_file.name}")

                # In real implementation:
                # result = process_file(audio_file, output_dir, model, speakers)

                results['successful'].append({
                    'file': audio_file.name,
                    'status': 'success'
                })

                progress.update(task, advance=1)

            except Exception as e:
                error_msg = str(e)
                results['failed'].append({
                    'file': audio_file.name,
                    'error': error_msg
                })

                if not continue_on_error:
                    console.print(f"\n[red]❌ Failed: {audio_file.name}[/red]")
                    console.print(f"Error: {error_msg}")
                    raise typer.Exit(code=1)

                progress.update(task, advance=1)

    # Print summary
    console.print(f"\n[bold]Batch Processing Summary[/bold]")
    console.print(f"✅ Successful: {len(results['successful'])}", style="green")
    console.print(f"❌ Failed: {len(results['failed'])}", style="red")

    if results['failed']:
        console.print("\n[bold red]Failed files:[/bold red]")
        for item in results['failed']:
            console.print(f"  - {item['file']}: {item['error']}")

    # Save summary log
    summary_file = output_dir / "batch_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)

    console.print(f"\n📝 Summary saved to: {summary_file}")


@app.command()
def label(
    transcript: Path = typer.Argument(
        ...,
        help="Transcript file to label (markdown format)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for labeled transcript (default: adds '_labeled' suffix)",
    ),
    labels_file: Optional[Path] = typer.Option(
        None,
        "--labels",
        "-l",
        help="JSON file with speaker label mappings",
        exists=True,
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="Prompt for speaker names interactively",
    ),
):
    """
    Assign custom names to speakers in transcript.

    Replaces generic speaker IDs (SPEAKER_00, SPEAKER_01) with actual names.
    Can work interactively (prompts for names) or load from labels file.

    Examples:
        # Interactive labeling
        localtranscribe label transcript.md

        # Use predefined labels
        localtranscribe label transcript.md --labels speaker_names.json

        # Specify output path
        localtranscribe label transcript.md --output final_transcript.md
    """

    console.print(Panel.fit(
        "[bold blue]🏷️  Speaker Labeling Tool[/bold blue]",
        subtitle=f"File: {transcript.name}"
    ))

    # Read transcript
    with open(transcript) as f:
        content = f.read()

    # Extract speaker IDs
    import re
    speaker_ids = set(re.findall(r'SPEAKER_\d+', content))
    speaker_ids = sorted(speaker_ids)

    if not speaker_ids:
        console.print("[yellow]⚠️  No speaker IDs found in transcript[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"\n✅ Found {len(speaker_ids)} speaker(s)\n")

    # Load or create label mapping
    labels = {}

    if labels_file:
        with open(labels_file) as f:
            labels = json.load(f)
        console.print(f"📄 Loaded labels from: {labels_file}\n")

    if interactive:
        # Prompt for missing labels
        for speaker_id in speaker_ids:
            if speaker_id not in labels:
                label = typer.prompt(
                    f"Name for {speaker_id} (or press Enter to keep)",
                    default="",
                )
                if label.strip():
                    labels[speaker_id] = label.strip()

    if not labels:
        console.print("[yellow]⚠️  No labels provided, keeping original IDs[/yellow]")
        raise typer.Exit()

    # Apply labels
    labeled_content = content
    for speaker_id, label in labels.items():
        labeled_content = labeled_content.replace(speaker_id, label)

    # Determine output path
    if output is None:
        output = transcript.with_stem(transcript.stem + "_labeled")

    # Save labeled transcript
    with open(output, 'w') as f:
        f.write(labeled_content)

    console.print(f"\n✅ [green]Labeled transcript saved to:[/green] {output}")

    # Save label mapping
    labels_output = output.with_suffix('.labels.json')
    with open(labels_output, 'w') as f:
        json.dump(labels, f, indent=2)

    console.print(f"📝 [blue]Label mapping saved to:[/blue] {labels_output}")


@app.command()
def doctor():
    """
    Run health check on LocalTranscribe installation.

    Verifies that all dependencies are installed correctly and the environment
    is properly configured. Provides actionable suggestions for any issues found.

    Examples:
        localtranscribe doctor
    """

    console.print(Panel.fit(
        "[bold blue]🏥 LocalTranscribe Health Check[/bold blue]",
        subtitle="Verifying installation and environment"
    ))

    # This is a simplified version - see health_check.py for full implementation
    checks = [
        ("Python Version", lambda: (True, "✅ Python 3.11.5")),
        ("FFmpeg", lambda: (True, "✅ 6.0")),
        ("PyTorch", lambda: (True, "✅ PyTorch 2.1.0 (MPS enabled)")),
        ("Whisper", lambda: (True, "✅ MLX, Faster")),
        ("Pyannote", lambda: (True, "✅ pyannote.audio 3.1.0")),
        ("HuggingFace Token", lambda: (True, "✅ Token configured")),
        ("Directories", lambda: (True, "✅ All directories present")),
    ]

    table = Table(title="\nSystem Status", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=25)
    table.add_column("Status", width=50)

    all_passed = True

    for name, check_func in checks:
        passed, message = check_func()
        table.add_row(name, message)
        if not passed:
            all_passed = False

    console.print(table)
    console.print()

    if all_passed:
        console.print("✅ [bold green]All checks passed! Ready to transcribe.[/bold green]")
        console.print("\nTry: [cyan]localtranscribe process your_audio.mp3[/cyan]")
    else:
        console.print("❌ [bold red]Some issues found. Please fix before using.[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def config_show():
    """
    Show current configuration settings.

    Displays all configuration values from default config, project config,
    and environment variables.

    Examples:
        localtranscribe config-show
    """

    console.print(Panel.fit(
        "[bold blue]⚙️  LocalTranscribe Configuration[/bold blue]"
    ))

    # Example configuration display
    config_data = {
        "Model": "base",
        "Implementation": "auto (MLX preferred)",
        "Output Directory": "./output",
        "Cache Directory": "~/.cache/localtranscribe",
        "HuggingFace Token": "Configured ✓",
        "Max Workers": "2",
        "MPS Acceleration": "Enabled ✓",
    }

    table = Table(title="\nCurrent Settings", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config_data.items():
        table.add_row(key, str(value))

    console.print(table)


if __name__ == "__main__":
    app()
