"""Check models command - show NLP model and dependency status."""

import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Create sub-app for check-models command
app = typer.Typer()
console = Console()


@app.command()
def check_models(
    detailed: bool = typer.Option(
        False,
        "--detailed",
        "-d",
        help="Show detailed model information",
    ),
    download: str = typer.Option(
        None,
        "--download",
        help="Download a specific model (e.g., 'en_core_web_sm')",
    ),
):
    """
    🔍 Check NLP model and dependency status for context-aware proofreading.

    Shows:
    - spaCy installation status
    - Installed language models (sm/md/lg)
    - FlashText availability (high-performance matching)
    - RapidFuzz availability (typo tolerance)
    - Context-aware feature readiness

    Examples:
        localtranscribe check-models
        localtranscribe check-models --detailed
        localtranscribe check-models --download en_core_web_sm
    """
    try:
        from ...proofreading.model_manager import (
            check_dependencies,
            ModelManager,
        )

        console.print()
        console.print(
            Panel.fit(
                "🔍 [bold cyan]NLP Models & Dependencies Status[/bold cyan]",
                border_style="cyan",
            )
        )
        console.print()

        # Handle download request
        if download:
            _handle_download(download)
            return

        # Check all dependencies
        status = check_dependencies()

        # Create status table
        table = Table(
            title="📦 Dependency Status",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )
        table.add_column("Component", style="cyan", width=25)
        table.add_column("Status", width=15)
        table.add_column("Details", width=40)

        # spaCy status
        if status["spacy_installed"]:
            spacy_status = "✅ Installed"
            spacy_style = "green"
            spacy_details = "Core NLP library available"
        else:
            spacy_status = "❌ Missing"
            spacy_style = "red"
            spacy_details = "Install: pip install spacy"

        table.add_row(
            "spaCy",
            Text(spacy_status, style=spacy_style),
            spacy_details
        )

        # FlashText status
        if status["flashtext_available"]:
            ft_status = "✅ Available"
            ft_style = "green"
            ft_details = "High-performance matching enabled"
        else:
            ft_status = "⚠️  Optional"
            ft_style = "yellow"
            ft_details = "Install: pip install flashtext"

        table.add_row(
            "FlashText",
            Text(ft_status, style=ft_style),
            ft_details
        )

        # RapidFuzz status
        if status["rapidfuzz_available"]:
            rf_status = "✅ Available"
            rf_style = "green"
            rf_details = "Typo tolerance enabled"
        else:
            rf_status = "⚠️  Optional"
            rf_style = "yellow"
            rf_details = "Install: pip install rapidfuzz"

        table.add_row(
            "RapidFuzz",
            Text(rf_status, style=rf_style),
            rf_details
        )

        console.print(table)
        console.print()

        # Show installed models
        if status["spacy_installed"]:
            _show_installed_models(status["installed_models"], detailed)
        else:
            console.print("⚠️  spaCy not installed - cannot check models\n")
            console.print("Install with: [cyan]pip install spacy[/cyan]\n")
            sys.exit(1)

        # Show context-aware readiness
        _show_readiness_status(status)

        # Exit code
        if status["context_aware_ready"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]❌ Error checking models:[/bold red] {e}")
        sys.exit(1)


def _show_installed_models(installed_models: list, detailed: bool):
    """Display installed spaCy models."""
    console.print("📚 [bold]Installed spaCy Models:[/bold]\n")

    if not installed_models:
        console.print("  ⚠️  No spaCy models installed\n")
        console.print("  Available models for download:\n")

        # Show available models
        from ...proofreading.model_manager import ModelManager
        available = ModelManager.AVAILABLE_MODELS

        for model_name, info in available.items():
            console.print(f"    • [cyan]{model_name}[/cyan]")
            console.print(f"      Size: {info['size']}")
            console.print(f"      {info['description']}")
            console.print(f"      Download: [yellow]localtranscribe check-models --download {model_name}[/yellow]")
            console.print()

    else:
        for model in installed_models:
            console.print(f"  ✅ [green]{model}[/green]")

            if detailed:
                # Get model details
                from ...proofreading.model_manager import ModelManager
                info = ModelManager.AVAILABLE_MODELS.get(model, {})
                if info:
                    console.print(f"     • Size: {info.get('size', 'Unknown')}")
                    console.print(f"     • {info.get('description', 'Language model')}")
                    console.print(f"     • Accuracy: {info.get('accuracy', 'Standard')}")
                console.print()

        if not detailed:
            console.print("\n  💡 Use [cyan]--detailed[/cyan] flag for more information\n")


def _show_readiness_status(status: dict):
    """Show context-aware feature readiness."""
    console.print()

    if status["context_aware_ready"]:
        console.print(
            Panel.fit(
                "✅ [bold green]Context-Aware Features Ready![/bold green]\n\n"
                "You can now use:\n"
                "  • Intelligent acronym disambiguation\n"
                "  • Context-aware term expansion\n"
                "  • Enhanced proofreading accuracy",
                border_style="green",
                title="🎉 All Set"
            )
        )
    else:
        console.print(
            Panel.fit(
                "⚠️  [bold yellow]Context-Aware Features Unavailable[/bold yellow]\n\n"
                "To enable, download a spaCy model:\n"
                "[cyan]localtranscribe check-models --download en_core_web_sm[/cyan]\n\n"
                "Or manually:\n"
                "[cyan]python -m spacy download en_core_web_sm[/cyan]\n\n"
                "Basic proofreading will still work without these features.",
                border_style="yellow",
                title="⚡ Setup Required"
            )
        )
    console.print()


def _handle_download(model_name: str):
    """Handle model download request."""
    from ...proofreading.model_manager import ModelManager

    console.print()
    console.print(f"📥 [bold]Downloading model:[/bold] [cyan]{model_name}[/cyan]\n")

    # Check if model info exists
    if model_name not in ModelManager.AVAILABLE_MODELS:
        console.print(f"❌ Unknown model: [red]{model_name}[/red]\n")
        console.print("Available models:")
        for name in ModelManager.AVAILABLE_MODELS.keys():
            console.print(f"  • {name}")
        console.print()
        sys.exit(1)

    # Create manager and download
    manager = ModelManager(model_name=model_name)

    # Check if already installed
    if manager.is_model_installed():
        console.print(f"✅ Model '[green]{model_name}[/green]' is already installed!\n")
        sys.exit(0)

    # Download
    success = manager.download_model(quiet=False)

    if success:
        console.print()
        console.print(
            Panel.fit(
                f"✅ [bold green]Successfully downloaded {model_name}![/bold green]\n\n"
                "Context-aware proofreading is now ready to use.",
                border_style="green",
                title="🎉 Download Complete"
            )
        )
        console.print()
        sys.exit(0)
    else:
        console.print()
        console.print(
            Panel.fit(
                "❌ [bold red]Download failed[/bold red]\n\n"
                "Please try:\n"
                f"[cyan]python -m spacy download {model_name}[/cyan]\n\n"
                "Or check your internet connection.",
                border_style="red",
                title="❌ Error"
            )
        )
        console.print()
        sys.exit(1)
