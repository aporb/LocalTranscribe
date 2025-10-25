"""Main CLI application entry point."""

import sys
from pathlib import Path
import typer
from rich.console import Console

from . import commands
from .. import __version__
from ..utils.file_browser import prompt_for_file

# Initialize main app
app = typer.Typer(
    name="localtranscribe",
    help="LocalTranscribe - Easy audio transcription with speaker diarization\n\n"
         "💡 Tip: Run 'localtranscribe audio.mp3' to start the guided wizard!\n"
         "💡 Or run 'localtranscribe' without arguments to browse files interactively!",
    add_completion=False,
)
console = Console()

# Add commands
app.command(name="wizard")(commands.wizard.wizard)
app.command(name="process")(commands.process.process)
app.command(name="batch")(commands.batch.batch)
app.command(name="doctor")(commands.doctor.doctor)
app.add_typer(commands.config.app, name="config", help="Manage configuration")
app.command(name="label")(commands.label.label)
app.command(name="version")(commands.version.version)


def is_audio_file(path_str: str) -> bool:
    """Check if the argument looks like an audio file."""
    # Audio extensions we support
    audio_extensions = {
        '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus',
        '.mp4', '.mov', '.avi', '.mkv', '.webm'  # Video files (extract audio)
    }

    path = Path(path_str)
    return path.suffix.lower() in audio_extensions or path.exists()


def main():
    """Main entry point with smart routing."""
    # No arguments provided - show interactive file browser
    if len(sys.argv) == 1:
        selected_file = prompt_for_file()
        if selected_file:
            # User selected a file - route to wizard
            sys.argv.append('wizard')
            sys.argv.append(str(selected_file))
            console.print("[dim]💡 Running guided wizard (use 'localtranscribe process' for direct mode)[/dim]\n")
        else:
            # User cancelled - exit gracefully
            return

    # Check if user provided an audio file directly (without subcommand)
    # Example: localtranscribe audio.mp3 → routes to wizard
    elif len(sys.argv) > 1:
        first_arg = sys.argv[1]

        # If first argument is not a known command and looks like a file, route to wizard
        known_commands = {'wizard', 'process', 'batch', 'doctor', 'config', 'label', 'version', '--help', '-h'}

        if first_arg not in known_commands and not first_arg.startswith('-'):
            # Check if it looks like an audio file
            if is_audio_file(first_arg):
                # Route to wizard by inserting 'wizard' command
                sys.argv.insert(1, 'wizard')
                console.print("[dim]💡 Running guided wizard (use 'localtranscribe process' for direct mode)[/dim]\n")

    app()


if __name__ == "__main__":
    main()
