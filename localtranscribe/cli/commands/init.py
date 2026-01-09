"""Init command - interactive first-run setup wizard."""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
import questionary
from questionary import Style

from ...config.loader import ConfigLoader
from ...health.doctor import check_system_health

console = Console()

# Custom style based on best practices from questionary
custom_style = Style([
    ('qmark', 'fg:#5f819d bold'),       # Question mark
    ('question', 'bold'),                # Question text
    ('answer', 'fg:#3cb371 bold'),      # Answer text
    ('pointer', 'fg:#ff9800 bold'),     # Selection pointer
    ('highlighted', 'fg:#ff9800 bold'), # Highlighted option
    ('selected', 'fg:#3cb371'),         # Selected option
    ('separator', 'fg:#6c6c6c'),        # Separator
    ('instruction', 'fg:#757575'),      # Instructions
    ('text', ''),                        # Default text
    ('disabled', 'fg:#757575 italic')   # Disabled option
])


def init():
    """
    Interactive setup wizard for LocalTranscribe first-time configuration.

    Guides users through:
    - HuggingFace token setup with validation
    - Default configuration preferences
    - System health verification
    - Model recommendations based on hardware
    """

    # Welcome banner
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Welcome to LocalTranscribe! 🎙️[/bold cyan]\n\n"
        "This wizard will help you set up LocalTranscribe in 3 quick steps.\n"
        "You can always change these settings later.",
        title="✨ Setup Wizard",
        border_style="cyan"
    ))
    console.print()

    # Check if already configured
    env_file = Path(".env")
    config_file = Path(".localtranscribe/config.yaml")

    if env_file.exists() or config_file.exists():
        console.print("[yellow]⚠ Existing configuration detected[/yellow]")

        existing_config = Table(show_header=False, box=None)
        existing_config.add_column("", style="dim")
        existing_config.add_column("")

        if env_file.exists():
            existing_config.add_row("✓", f".env file found at: {env_file.absolute()}")
        if config_file.exists():
            existing_config.add_row("✓", f"Config file found at: {config_file.absolute()}")

        console.print(existing_config)
        console.print()

        reconfigure = questionary.confirm(
            "Reconfigure settings?",
            default=False,
            style=custom_style
        ).ask()

        if not reconfigure:
            console.print("[green]✓ Keeping existing configuration[/green]")
            console.print()
            return

    # ============================================================================
    # STEP 1: HuggingFace Token
    # ============================================================================
    console.print("[bold]Step 1 of 3: HuggingFace Token Setup[/bold]")
    console.print()
    console.print("Speaker diarization requires a [cyan]free HuggingFace account[/cyan].")
    console.print("This allows the system to identify who's speaking when.")
    console.print()

    has_token = questionary.confirm(
        "Do you have a HuggingFace token?",
        default=False,
        style=custom_style
    ).ask()

    if not has_token:
        # Show detailed instructions
        console.print()
        console.print(Panel(
            "[bold]How to get your HuggingFace token:[/bold]\n\n"
            "1. Visit: [cyan]https://huggingface.co/settings/tokens[/cyan]\n"
            "2. Click [green]'New token'[/green] and select [yellow]'Read'[/yellow] permissions\n"
            "3. Copy the token (starts with 'hf_')\n\n"
            "[bold]Accept required model licenses:[/bold]\n"
            "• [cyan]https://huggingface.co/pyannote/speaker-diarization-3.1[/cyan]\n"
            "• [cyan]https://huggingface.co/pyannote/segmentation-3.0[/cyan]\n\n"
            "[dim]Note: You need to accept these licenses to use speaker diarization[/dim]",
            title="📚 Instructions",
            border_style="blue"
        ))
        console.print()

        continue_setup = questionary.confirm(
            "Ready to enter your token?",
            default=True,
            style=custom_style
        ).ask()

        if not continue_setup:
            console.print()
            console.print("[yellow]Setup paused. Run 'localtranscribe init' when ready.[/yellow]")
            console.print()
            console.print("[dim]Tip: You can skip diarization with: localtranscribe process audio.mp3 --skip-diarization[/dim]")
            console.print()
            return

    # Token entry and validation
    token = None
    token_valid = False
    attempts = 0
    max_attempts = 3

    while not token_valid and attempts < max_attempts:
        console.print()
        token = questionary.password(
            "Enter your HuggingFace token:",
            style=custom_style
        ).ask()

        if not token:
            console.print("[yellow]⚠ No token entered[/yellow]")
            skip_token = questionary.confirm(
                "Skip token setup for now?",
                default=False,
                style=custom_style
            ).ask()
            if skip_token:
                console.print("[yellow]→ Skipping token setup (you can add it later)[/yellow]")
                break
            attempts += 1
            continue

        # Validate token format
        if not token.startswith("hf_"):
            console.print("[red]✗ Invalid token format (should start with 'hf_')[/red]")
            attempts += 1
            if attempts < max_attempts:
                retry = questionary.confirm(
                    "Try again?",
                    default=True,
                    style=custom_style
                ).ask()
                if not retry:
                    break
            continue

        if len(token) < 25:
            console.print("[red]✗ Token too short (tokens are usually 37+ characters)[/red]")
            attempts += 1
            if attempts < max_attempts:
                retry = questionary.confirm(
                    "Try again?",
                    default=True,
                    style=custom_style
                ).ask()
                if not retry:
                    break
            continue

        # Token looks valid
        console.print("[green]✓ Token format looks valid[/green]")
        token_valid = True

    # Save token to .env
    if token and token_valid:
        try:
            env_content = f'HUGGINGFACE_TOKEN="{token}"\n'
            env_file.write_text(env_content)
            console.print(f"[green]✓ Token saved to {env_file.absolute()}[/green]")

            # Set environment variable for current session
            os.environ['HUGGINGFACE_TOKEN'] = token
        except Exception as e:
            console.print(f"[red]✗ Failed to save token: {e}[/red]")
            console.print("[yellow]→ You can manually create a .env file with your token[/yellow]")

    # ============================================================================
    # STEP 2: Configuration Preferences
    # ============================================================================
    console.print()
    console.print("[bold]Step 2 of 3: Default Settings[/bold]")
    console.print()

    # Model size selection
    model_choices = [
        questionary.Choice(
            "tiny - Fastest, least accurate (good for quick tests)",
            value="tiny"
        ),
        questionary.Choice(
            "base - Fast, decent accuracy",
            value="base"
        ),
        questionary.Choice(
            "small - Balanced speed/accuracy",
            value="small"
        ),
        questionary.Choice(
            "medium - Recommended (best balance) ⭐",
            value="medium"
        ),
        questionary.Choice(
            "large - Most accurate, slowest",
            value="large"
        ),
    ]

    model_size = questionary.select(
        "Default Whisper model size:",
        choices=model_choices,
        default="medium",
        style=custom_style
    ).ask()

    # Output directory
    default_output = "./output"
    output_dir = questionary.text(
        "Default output directory:",
        default=default_output,
        style=custom_style
    ).ask()

    # Output formats
    format_choices = [
        questionary.Choice("Markdown (recommended)", value="md", checked=True),
        questionary.Choice("Plain Text", value="txt", checked=True),
        questionary.Choice("JSON", value="json", checked=True),
        questionary.Choice("SRT (subtitles)", value="srt", checked=False),
        questionary.Choice("VTT (web subtitles)", value="vtt", checked=False),
    ]

    output_formats = questionary.checkbox(
        "Default output formats (select with Space):",
        choices=format_choices,
        style=custom_style
    ).ask()

    if not output_formats:
        output_formats = ["md", "txt", "json"]  # Fallback defaults

    # Proofreading preferences
    enable_proofread = questionary.confirm(
        "Enable automatic proofreading by default?",
        default=True,
        style=custom_style
    ).ask()

    # ============================================================================
    # STEP 3: System Check
    # ============================================================================
    console.print()
    console.print("[bold]Step 3 of 3: System Verification[/bold]")
    console.print()

    run_check = questionary.confirm(
        "Run system health check?",
        default=True,
        style=custom_style
    ).ask()

    # Save configuration
    console.print()
    console.print("[cyan]→ Saving configuration...[/cyan]")

    config_dir = Path(".localtranscribe")
    config_dir.mkdir(exist_ok=True)

    config_content = f"""# LocalTranscribe Configuration
# Generated by setup wizard on {Path.cwd()}

model:
  whisper_size: {model_size}
  whisper_implementation: auto
  diarization_model: pyannote/speaker-diarization-3.1

processing:
  skip_diarization: false
  language: null
  num_speakers: null

output:
  directory: {output_dir}
  formats: {output_formats}
  include_confidence: true

proofreading:
  enable_domain_dictionaries: {str(enable_proofread).lower()}
  domains: [common]
  enable_acronym_expansion: {str(enable_proofread).lower()}
  acronym_format: parenthetical

audio_analysis:
  enabled: true
  calculate_snr: true

quality_gates:
  enabled: true
  generate_report: true

logging:
  verbose: false
  log_level: INFO
"""

    try:
        config_file.write_text(config_content)
        console.print(f"[green]✓ Configuration saved to {config_file.absolute()}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to save configuration: {e}[/red]")

    # Run health check if requested
    if run_check:
        console.print()
        console.print("[cyan]→ Running system health check...[/cyan]")
        console.print()

        try:
            # Import and run doctor command
            from .doctor import doctor as run_doctor
            run_doctor(verbose=True)
        except Exception as e:
            console.print(f"[yellow]⚠ Health check failed: {e}[/yellow]")
            console.print("[dim]You can run it manually with: localtranscribe doctor[/dim]")

    # Success summary
    console.print()
    console.print(Panel.fit(
        "[bold green]Setup Complete! 🎉[/bold green]\n\n"
        "Your configuration has been saved and you're ready to start transcribing.\n\n"
        "[bold]Quick Start:[/bold]\n"
        "  • Process an audio file: [cyan]localtranscribe audio.mp3[/cyan]\n"
        "  • Use the wizard: [cyan]localtranscribe wizard audio.mp3[/cyan]\n"
        "  • See example commands: [cyan]localtranscribe --help-examples[/cyan]\n"
        "  • Get help: [cyan]localtranscribe --help[/cyan]\n\n"
        "[dim]Configuration files created:[/dim]\n"
        f"[dim]  • {env_file.absolute() if env_file.exists() else 'No .env file'}[/dim]\n"
        f"[dim]  • {config_file.absolute()}[/dim]",
        title="✨ All Set!",
        border_style="green"
    ))
    console.print()


# Make it callable as a Typer command
app = typer.Typer()
app.command()(init)


if __name__ == "__main__":
    init()
