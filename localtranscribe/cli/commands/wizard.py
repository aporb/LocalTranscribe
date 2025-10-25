"""Wizard command - guided interactive setup for beginners."""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from ...pipeline import PipelineOrchestrator, PipelineResult
from ...utils.errors import LocalTranscribeError

# Create sub-app for wizard command
app = typer.Typer()
console = Console()


def welcome_screen():
    """Display welcome screen with overview."""
    console.clear()
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Welcome to LocalTranscribe Wizard! 🎙️[/bold cyan]\n\n"
            "This guided setup will help you:\n"
            "• Transcribe your audio file\n"
            "• Identify different speakers\n"
            "• Label speakers with names\n"
            "• Fix common transcription errors\n\n"
            "[dim]All processing happens locally on your computer.[/dim]",
            border_style="cyan",
            title="🧙‍♂️ Setup Wizard"
        )
    )
    console.print()


def analyze_audio_file(audio_file: Path) -> Dict[str, Any]:
    """Analyze audio file and provide recommendations."""
    import subprocess

    info = {
        "exists": audio_file.exists(),
        "size_mb": 0,
        "duration": None,
        "format": audio_file.suffix.lower(),
    }

    if info["exists"]:
        # Get file size
        info["size_mb"] = audio_file.stat().st_size / (1024 * 1024)

        # Try to get duration using ffprobe if available
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                duration_seconds = float(result.stdout.strip())
                info["duration"] = duration_seconds
                info["duration_minutes"] = duration_seconds / 60
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

    return info


def recommend_model(duration_minutes: Optional[float], quality_preference: str) -> str:
    """Recommend a model based on audio duration and quality preference."""
    if quality_preference == "quick":
        return "tiny"
    elif quality_preference == "balanced":
        # Default to medium for best quality/speed balance
        if duration_minutes and duration_minutes > 90:
            return "small"  # Use small for very long files
        return "medium"
    elif quality_preference == "quality":
        # High quality always uses large
        return "large"
    else:
        return "medium"


def estimate_processing_time(duration_minutes: Optional[float], model: str) -> str:
    """Estimate processing time based on duration and model."""
    if duration_minutes is None:
        return "Unknown"

    # Rough estimates for M1/M2 Mac (adjust multipliers based on model)
    multipliers = {
        "tiny": 0.05,
        "base": 0.2,
        "small": 0.5,
        "medium": 1.0,
        "large": 2.0
    }

    multiplier = multipliers.get(model, 0.2)
    estimated_minutes = duration_minutes * multiplier

    if estimated_minutes < 1:
        return f"~{int(estimated_minutes * 60)} seconds"
    elif estimated_minutes < 60:
        return f"~{int(estimated_minutes)} minutes"
    else:
        return f"~{int(estimated_minutes / 60)} hours {int(estimated_minutes % 60)} minutes"


@app.command()
def wizard(
    audio_file: Path = typer.Argument(
        ...,
        help="Path to audio file to process",
        exists=True,
    ),
):
    """
    🧙‍♂️ Guided wizard for easy transcription setup.

    Perfect for first-time users! This interactive wizard will guide you
    through all the options and help you get the best results.

    Example:
        localtranscribe wizard interview.mp3
    """
    try:
        welcome_screen()

        if not typer.confirm("Ready to get started?", default=True):
            console.print("[yellow]Wizard cancelled. Run 'localtranscribe wizard <audio-file>' when ready![/yellow]")
            sys.exit(0)

        # Step 1: Analyze audio file
        console.print()
        console.print("[bold]Step 1: Analyzing your audio file...[/bold]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing...", total=None)
            audio_info = analyze_audio_file(audio_file)
            progress.update(task, completed=True)

        # Display audio info
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("📁 File", audio_file.name)
        info_table.add_row("📦 Size", f"{audio_info['size_mb']:.1f} MB")
        info_table.add_row("🎵 Format", audio_info['format'])
        if audio_info['duration']:
            info_table.add_row("⏱️  Duration", f"{audio_info['duration_minutes']:.1f} minutes")

        console.print(info_table)
        console.print()

        # Step 2: Quality preference
        console.print("[bold]Step 2: Choose your quality vs. speed preference:[/bold]")
        console.print()
        console.print("  [cyan]1. Quick[/cyan] - Fastest processing (tiny model)")
        console.print("  [cyan]2. Balanced[/cyan] - Good quality and speed (medium model) [dim][recommended][/dim]")
        console.print("  [cyan]3. High Quality[/cyan] - Best accuracy, slower (large model)")
        console.print()

        quality_choice = typer.prompt(
            "Your choice",
            type=int,
            default=2,
            show_default=True
        )

        quality_map = {1: "quick", 2: "balanced", 3: "quality"}
        quality_preference = quality_map.get(quality_choice, "balanced")
        model_size = recommend_model(audio_info.get('duration_minutes'), quality_preference)

        console.print(f"[green]✓ Using '{model_size}' model[/green]")
        console.print()

        # Step 3: Speakers
        console.print("[bold]Step 3: Tell me about the speakers:[/bold]")
        console.print()

        know_speaker_count = typer.confirm("Do you know exactly how many speakers?", default=False)
        num_speakers = None

        if know_speaker_count:
            num_speakers = typer.prompt("How many speakers?", type=int)
            console.print(f"[green]✓ Will expect {num_speakers} speakers[/green]")
        else:
            console.print("[dim]No problem! I'll automatically detect the number of speakers.[/dim]")

        console.print()

        # Step 4: Speaker labels
        console.print("[bold]Step 4: Speaker names (optional):[/bold]")
        console.print()
        console.print("Do you want to label speakers with their actual names?")
        console.print("[dim](e.g., replace 'SPEAKER_00' with 'John Smith')[/dim]")
        console.print()

        use_labels = typer.confirm("Yes, I want to add speaker names", default=True)
        labels_file = None
        save_labels = None

        if use_labels:
            # Check for existing labels file
            auto_labels = audio_file.parent / "speaker_labels.json"
            if auto_labels.exists():
                console.print(f"[cyan]✓ Found existing labels file: {auto_labels.name}[/cyan]")
                if typer.confirm("Use this file?", default=True):
                    labels_file = auto_labels

            if labels_file is None:
                console.print()
                console.print("You can either:")
                console.print("  1. Provide labels now (I'll save them for you)")
                console.print("  2. Skip for now (you can add them later)")
                console.print()

                if typer.confirm("Would you like to provide a labels file?", default=False):
                    labels_path = typer.prompt("Path to labels JSON file")
                    labels_file = Path(labels_path)

                    if not labels_file.exists():
                        console.print(f"[yellow]⚠️  File not found: {labels_file}[/yellow]")
                        labels_file = None
                else:
                    # Offer to save labels after processing
                    save_labels = audio_file.parent / "speaker_labels.json"
                    console.print(f"[dim]I'll save speaker IDs to {save_labels.name} for you to edit later.[/dim]")

        console.print()

        # Step 5: Proofreading
        console.print("[bold]Step 5: Automatic proofreading:[/bold]")
        console.print()
        console.print("I can automatically fix common transcription errors like:")
        console.print("  • Technical terms (API → API, JavaScript → JavaScript)")
        console.print("  • Homophones (your/you're, their/there)")
        console.print("  • Business terms (CEO, VP, B2B)")
        console.print("  • Excessive repetitions")
        console.print()

        enable_proofreading = typer.confirm("Enable automatic proofreading?", default=True)
        proofreading_level = "standard"

        if enable_proofreading:
            console.print()
            console.print("Proofreading level:")
            console.print("  [cyan]1. Minimal[/cyan] - Only the most common fixes")
            console.print("  [cyan]2. Standard[/cyan] - Comprehensive corrections [dim][recommended][/dim]")
            console.print("  [cyan]3. Thorough[/cyan] - All available corrections")
            console.print()

            level_choice = typer.prompt("Your choice", type=int, default=2, show_default=True)
            level_map = {1: "minimal", 2: "standard", 3: "thorough"}
            proofreading_level = level_map.get(level_choice, "standard")

            console.print(f"[green]✓ Proofreading level: {proofreading_level}[/green]")

        console.print()

        # Step 6: Output location
        console.print("[bold]Step 6: Where should I save the results?[/bold]")
        console.print()

        default_output = Path("./output")
        custom_output = typer.confirm(
            f"Use default output directory: {default_output}?",
            default=True
        )

        if custom_output:
            output_dir = default_output
        else:
            output_path = typer.prompt("Output directory")
            output_dir = Path(output_path)

        console.print(f"[green]✓ Will save to: {output_dir}[/green]")
        console.print()

        # Step 7: Summary and confirmation
        console.print()
        console.print(Panel.fit(
            "[bold]📋 Summary[/bold]\n\n"
            f"[cyan]Audio File:[/cyan] {audio_file.name}\n"
            f"[cyan]Model:[/cyan] {model_size}\n"
            f"[cyan]Speakers:[/cyan] {num_speakers if num_speakers else 'Auto-detect'}\n"
            f"[cyan]Speaker Labels:[/cyan] {'Yes' if labels_file or save_labels else 'No'}\n"
            f"[cyan]Proofreading:[/cyan] {proofreading_level.title() if enable_proofreading else 'Disabled'}\n"
            f"[cyan]Output:[/cyan] {output_dir}",
            border_style="cyan",
            title="Configuration"
        ))
        console.print()

        # Show estimated processing time
        if audio_info.get('duration_minutes'):
            estimated_time = estimate_processing_time(audio_info['duration_minutes'], model_size)
            console.print(f"[dim]⏱️  Estimated processing time: {estimated_time}[/dim]")
            console.print()

        if not typer.confirm("Everything looks good. Start processing?", default=True):
            console.print("[yellow]Processing cancelled.[/yellow]")
            sys.exit(0)

        # Step 8: Run the pipeline!
        console.print()
        console.print("[bold green]🚀 Starting transcription pipeline...[/bold green]")
        console.print()

        # Check for HuggingFace token
        from dotenv import load_dotenv
        load_dotenv()
        hf_token = os.getenv('HUGGINGFACE_TOKEN')

        # Check if token is missing, placeholder, or skip reminder
        if not hf_token or hf_token == "your_token_here" or hf_token == "SKIP_REMINDER":
            console.print()
            console.print(Panel.fit(
                "[bold yellow]⚠️  HuggingFace Token Required[/bold yellow]\n\n"
                "For speaker diarization, you need a free HuggingFace token.\n\n"
                "[cyan]Quick setup (2 minutes):[/cyan]\n"
                "1. Visit: https://huggingface.co/settings/tokens\n"
                "2. Create a token (if you don't have one)\n"
                "3. Accept model licenses:\n"
                "   • https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                "   • https://huggingface.co/pyannote/segmentation-3.0\n"
                "4. Enter your token below (starts with 'hf_')",
                border_style="yellow"
            ))
            console.print()

            # Prompt with three options
            console.print("[bold]What would you like to do?[/bold]")
            console.print("  1. Enter token now (I'll save it for you)")
            console.print("  2. Skip for now (I'll remind you next time)")
            console.print("  3. Continue without diarization (transcription only)")
            console.print()

            choice = typer.prompt("Your choice", type=int, default=1, show_default=True)

            if choice == 1:
                # Enter token with validation
                while True:
                    token_input = typer.prompt("Enter your HuggingFace token (or 'cancel' to go back)")

                    if token_input.lower() == 'cancel':
                        console.print("[yellow]Token setup cancelled.[/yellow]")
                        sys.exit(0)

                    token_input = token_input.strip()

                    # Validate token format
                    if not token_input.startswith('hf_'):
                        console.print("[red]❌ Invalid token format. HuggingFace tokens start with 'hf_'[/red]")
                        console.print("[dim]Please try again or type 'cancel' to exit.[/dim]\n")
                        continue

                    if len(token_input) < 10:
                        console.print("[red]❌ Token seems too short. Please check and try again.[/red]\n")
                        continue

                    # Token looks valid
                    hf_token = token_input

                    # Save to .env file
                    env_path = Path(".env")

                    # Read existing .env content
                    env_content = ""
                    if env_path.exists():
                        with open(env_path, "r") as f:
                            env_content = f.read()

                    # Replace or add token
                    if "HUGGINGFACE_TOKEN=" in env_content:
                        # Replace existing token (including SKIP_REMINDER)
                        import re
                        env_content = re.sub(
                            r'HUGGINGFACE_TOKEN=.*',
                            f'HUGGINGFACE_TOKEN={hf_token}',
                            env_content
                        )
                    else:
                        # Add new token
                        if env_content and not env_content.endswith('\n'):
                            env_content += '\n'
                        env_content += f'HUGGINGFACE_TOKEN={hf_token}\n'

                    # Write back
                    with open(env_path, "w") as f:
                        f.write(env_content)

                    console.print(f"[green]✓ Token saved to {env_path}[/green]")
                    console.print("[dim]You won't be asked again on future runs.[/dim]")
                    console.print()
                    break

            elif choice == 2:
                # Skip for now - save reminder
                env_path = Path(".env")

                # Read existing .env content
                env_content = ""
                if env_path.exists():
                    with open(env_path, "r") as f:
                        env_content = f.read()

                # Replace or add SKIP_REMINDER
                if "HUGGINGFACE_TOKEN=" in env_content:
                    import re
                    env_content = re.sub(
                        r'HUGGINGFACE_TOKEN=.*',
                        'HUGGINGFACE_TOKEN=SKIP_REMINDER',
                        env_content
                    )
                else:
                    if env_content and not env_content.endswith('\n'):
                        env_content += '\n'
                    env_content += 'HUGGINGFACE_TOKEN=SKIP_REMINDER\n'

                with open(env_path, "w") as f:
                    f.write(env_content)

                console.print("[yellow]⚠️  Token setup skipped. I'll remind you next time.[/yellow]")
                console.print("[yellow]⚠️  Speaker diarization will be disabled for this run.[/yellow]")
                console.print()
                hf_token = None

            else:
                # Continue without diarization
                console.print("[yellow]⚠️  Speaker diarization will be disabled.[/yellow]")
                console.print()
                hf_token = None

        # Initialize and run the orchestrator
        orchestrator = PipelineOrchestrator(
            audio_file=audio_file,
            output_dir=output_dir,
            model_size=model_size,
            num_speakers=num_speakers,
            hf_token=hf_token,
            verbose=True,  # Always verbose in wizard
            labels_file=labels_file,
            save_labels=save_labels,
            enable_proofreading=enable_proofreading,
            proofreading_level=proofreading_level,
        )

        result: PipelineResult = orchestrator.run()

        # Show final results
        if result.success:
            console.print()
            console.print(
                Panel.fit(
                    "[bold green]🎉 Success![/bold green]\n\n"
                    f"Your transcription is complete and saved to:\n"
                    f"[cyan]{output_dir}[/cyan]\n\n"
                    "[dim]Check the output directory for all generated files.[/dim]",
                    border_style="green",
                    title="✅ Complete"
                )
            )
            console.print()

            # Provide next steps
            console.print("[bold]📚 Next steps:[/bold]")
            console.print()
            console.print("  • Review your transcript files in the output directory")
            if save_labels and save_labels.exists():
                console.print(f"  • Edit {save_labels.name} to add speaker names, then run:")
                console.print(f"    [cyan]localtranscribe label {output_dir}/*.md --labels {save_labels.name}[/cyan]")
            console.print("  • Run [cyan]localtranscribe --help[/cyan] for more advanced options")
            console.print()

            sys.exit(0)
        else:
            console.print(f"\n[bold red]❌ Pipeline failed:[/bold red] {result.error}")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Wizard interrupted by user[/yellow]")
        sys.exit(130)
    except LocalTranscribeError as e:
        console.print(f"\n{e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error:[/bold red] {e}")
        import traceback
        console.print("\n[dim]Traceback:[/dim]")
        console.print(traceback.format_exc())
        sys.exit(1)