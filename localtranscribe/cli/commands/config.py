"""Config command - configuration management."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Create sub-app for config command
app = typer.Typer()
console = Console()


@app.command(name="show")
def config_show():
    """
    ⚙️  Show current configuration settings.

    Displays:
    - Configuration file location
    - Current settings
    - Environment variables
    - Default values

    Example:
        localtranscribe config show
    """
    try:
        from ...config.loader import load_config, get_config_path

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
