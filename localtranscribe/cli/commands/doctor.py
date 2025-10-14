"""Doctor command - health checks."""

import sys

import typer
from rich.console import Console
from rich.panel import Panel

# Create sub-app for doctor command
app = typer.Typer()
console = Console()


@app.command()
def doctor(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed diagnostic information",
    ),
):
    """
    🏥 Run health check to verify LocalTranscribe setup.

    Checks:
    - Python version
    - Required dependencies
    - Optional dependencies
    - HuggingFace token
    - GPU/MPS availability
    - FFmpeg installation

    Example:
        localtranscribe doctor
        localtranscribe doctor -v
    """
    try:
        from ...health.doctor import run_health_check

        console.print()
        console.print(
            Panel.fit(
                "🏥 [bold green]LocalTranscribe Health Check[/bold green]",
                border_style="green",
            )
        )
        console.print()

        # Run health check
        result = run_health_check(verbose=verbose)

        # Exit with appropriate code
        if result["overall_status"] == "healthy":
            console.print("\n✅ [bold green]All systems operational![/bold green]\n")
            sys.exit(0)
        elif result["overall_status"] == "warning":
            console.print(
                "\n⚠️  [bold yellow]Some optional features unavailable[/bold yellow]\n"
            )
            sys.exit(0)
        else:
            console.print(
                "\n❌ [bold red]Critical issues found - setup required[/bold red]\n"
            )
            sys.exit(1)

    except ImportError:
        console.print(
            "[yellow]⚠️  Health check module not available[/yellow]\n"
            "This is expected if you haven't completed setup yet."
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Health check failed:[/bold red] {e}")
        sys.exit(1)
