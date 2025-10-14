"""Version command - show version information."""

import platform
import sys

import typer
from rich.console import Console
from rich.table import Table

# Create sub-app for version command
app = typer.Typer()
console = Console()


@app.command()
def version():
    """
    📦 Show LocalTranscribe version information.

    Example:
        localtranscribe version
    """
    from ... import __version__

    console.print()
    console.print(f"🎙️  [bold cyan]LocalTranscribe[/bold cyan] v{__version__}")
    console.print()

    # Show system info
    table = Table(show_header=False, box=None)
    table.add_column("Label", style="dim")
    table.add_column("Value", style="white")

    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("Platform", platform.platform())
    table.add_row("Architecture", platform.machine())

    console.print(table)
    console.print()
