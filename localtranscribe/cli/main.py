"""Main CLI application entry point."""

import typer
from rich.console import Console

from . import commands
from .. import __version__

# Initialize main app
app = typer.Typer(
    name="localtranscribe",
    help="LocalTranscribe - Speaker diarization and transcription made easy",
    add_completion=False,
)
console = Console()

# Add commands
app.command(name="process")(commands.process.process)
app.command(name="batch")(commands.batch.batch)
app.command(name="doctor")(commands.doctor.doctor)
app.add_typer(commands.config.app, name="config", help="Manage configuration")
app.command(name="label")(commands.label.label)
app.command(name="version")(commands.version.version)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
