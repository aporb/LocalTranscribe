"""Label command - speaker labeling."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

# Create sub-app for label command
app = typer.Typer()
console = Console()


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
        from ...labels import SpeakerLabelManager

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
