"""Examples command - show common use cases and examples."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()


def examples():
    """
    Display common use cases and example commands for LocalTranscribe.

    Shows practical examples for different scenarios:
    - Podcast transcription
    - Business meetings
    - Interviews
    - Quick transcription
    - Batch processing
    - Non-English audio
    """

    console.print()
    console.print(Panel.fit(
        "[bold cyan]LocalTranscribe - Common Use Cases & Examples[/bold cyan]\n\n"
        "Learn by example! Here are typical scenarios and how to handle them.",
        title="📚 Examples Guide",
        border_style="cyan"
    ))
    console.print()

    # Example 0: Using Presets (NEW!)
    console.print("[bold green]✨ Using Configuration Presets (NEW!)[/bold green]")
    console.print()
    console.print("Perfect for: Quick setup with optimized defaults")
    console.print()

    code0 = """# Podcast preset (2 speakers, medium model, standard proofreading)
localtranscribe process podcast.mp3 --preset podcast

# Meeting preset (3-8 speakers, thorough proofreading, business domains)
localtranscribe process meeting.wav --preset meeting --verbose

# Quick draft preset (small model, skip diarization, no proofreading)
localtranscribe process audio.mp3 --preset quick"""
    console.print(Syntax(code0, "bash", theme="monokai", padding=1))

    console.print("[dim]Available presets:[/dim]")
    console.print("  • [cyan]podcast[/cyan]: 2 speakers, media domain")
    console.print("  • [cyan]meeting[/cyan]: 3-8 speakers, business/technical domains")
    console.print("  • [cyan]interview[/cyan]: 2-3 speakers, academic domain")
    console.print("  • [cyan]lecture[/cyan]: Single speaker, skip diarization")
    console.print("  • [cyan]quick[/cyan]: Fast draft mode")
    console.print("  • [cyan]accurate[/cyan]: Maximum quality, all features")
    console.print()
    console.print("[dim]💡 Tip: Override preset values with specific flags[/dim]")
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 1: Podcast
    console.print("[bold green]🎙️  Podcast Transcription (2 speakers)[/bold green]")
    console.print()
    console.print("Perfect for: Interviews, conversations, podcasts")
    console.print()

    code1 = "localtranscribe podcast.mp3 --speakers 2 --proofread"
    console.print(Syntax(code1, "bash", theme="monokai", padding=1))

    console.print("[dim]Features used:[/dim]")
    console.print("  • [cyan]--speakers 2[/cyan]: Exactly 2 speakers expected")
    console.print("  • [cyan]--proofread[/cyan]: Auto-correct common transcription errors")
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 2: Business Meeting
    console.print("[bold green]👥 Business Meeting (3-5 speakers)[/bold green]")
    console.print()
    console.print("Perfect for: Team meetings, group discussions")
    console.print()

    code2 = """localtranscribe meeting.wav \\
  --min-speakers 3 \\
  --max-speakers 5 \\
  --labels speakers.json \\
  --format md json \\
  --domains business technical"""
    console.print(Syntax(code2, "bash", theme="monokai", padding=1))

    console.print("[dim]Features used:[/dim]")
    console.print("  • [cyan]--min/max-speakers[/cyan]: Range of expected speakers")
    console.print("  • [cyan]--labels speakers.json[/cyan]: Apply speaker names")
    console.print("  • [cyan]--format md json[/cyan]: Multiple output formats")
    console.print("  • [cyan]--domains[/cyan]: Business/technical vocabulary")
    console.print()

    console.print("[dim]speakers.json example:[/dim]")
    speakers_json = """{
  "SPEAKER_00": "Alice (CEO)",
  "SPEAKER_01": "Bob (CTO)",
  "SPEAKER_02": "Carol (PM)"
}"""
    console.print(Syntax(speakers_json, "json", theme="monokai", padding=1))
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 3: Quick Transcription
    console.print("[bold green]⚡ Quick Transcription (skip diarization)[/bold green]")
    console.print()
    console.print("Perfect for: Single speaker, quick drafts, lecture notes")
    console.print()

    code3 = "localtranscribe audio.mp3 --skip-diarization --model small"
    console.print(Syntax(code3, "bash", theme="monokai", padding=1))

    console.print("[dim]Features used:[/dim]")
    console.print("  • [cyan]--skip-diarization[/cyan]: Skip speaker detection (much faster)")
    console.print("  • [cyan]--model small[/cyan]: Smaller, faster model")
    console.print()
    console.print("[dim]⏱️  Processing time: ~2-3x faster than full pipeline[/dim]")
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 4: Non-English
    console.print("[bold green]🌍 Non-English Audio[/bold green]")
    console.print()
    console.print("Perfect for: Spanish, French, German, and 90+ languages")
    console.print()

    code4 = """# Spanish
localtranscribe entrevista.mp3 --language es --proofread

# French
localtranscribe interview.mp3 --language fr --speakers 2

# Auto-detect (default)
localtranscribe audio.mp3"""
    console.print(Syntax(code4, "bash", theme="monokai", padding=1))

    console.print("[dim]Supported languages: en, es, fr, de, it, pt, ru, zh, ja, ko, and more[/dim]")
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 5: Batch Processing
    console.print("[bold green]📊 Batch Processing (multiple files)[/bold green]")
    console.print()
    console.print("Perfect for: Processing many audio files at once")
    console.print()

    code5 = """localtranscribe batch ./audio-files/ \\
  --workers 4 \\
  --model medium \\
  --output ./transcripts/"""
    console.print(Syntax(code5, "bash", theme="monokai", padding=1))

    console.print("[dim]Features used:[/dim]")
    console.print("  • [cyan]--workers 4[/cyan]: Process 4 files in parallel")
    console.print("  • [cyan]--output ./transcripts/[/cyan]: Custom output directory")
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 6: Advanced Features
    console.print("[bold green]🚀 Advanced: Full Pipeline[/bold green]")
    console.print()
    console.print("Perfect for: High-quality transcripts with all features")
    console.print()

    code6 = """localtranscribe process interview.mp3 \\
  --speakers 2 \\
  --model large \\
  --proofread \\
  --proofread-level thorough \\
  --domains technical legal \\
  --expand-acronyms \\
  --context-aware \\
  --format txt json srt md \\
  --verbose"""
    console.print(Syntax(code6, "bash", theme="monokai", padding=1))

    console.print("[dim]Features used:[/dim]")
    console.print("  • [cyan]--model large[/cyan]: Most accurate model")
    console.print("  • [cyan]--proofread-level thorough[/cyan]: Deep proofreading")
    console.print("  • [cyan]--expand-acronyms[/cyan]: Explain abbreviations")
    console.print("  • [cyan]--context-aware[/cyan]: Use NLP for better accuracy")
    console.print("  • [cyan]--verbose[/cyan]: Show detailed progress")
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 7: New Export Formats & Audio Quality
    console.print("[bold green]📄 New Export Formats (HTML, DOCX) + Quality Check[/bold green]")
    console.print()
    console.print("Perfect for: Professional documents, sharing, publishing")
    console.print()

    code7 = """# Check audio quality before processing
localtranscribe process podcast.mp3 \\
  --check-quality \\
  --format html docx md json \\
  --speakers 2 \\
  --proofread"""
    console.print(Syntax(code7, "bash", theme="monokai", padding=1))

    console.print("[dim]Features used:[/dim]")
    console.print("  • [cyan]--check-quality[/cyan]: Analyze audio SNR, recommend model")
    console.print("  • [cyan]--format html[/cyan]: Color-coded speakers in browser-friendly HTML")
    console.print("  • [cyan]--format docx[/cyan]: Professional Microsoft Word document")
    console.print()
    console.print("[dim]💡 HTML includes responsive design, dark mode, and print optimization[/dim]")
    console.print("[dim]💡 DOCX includes metadata, speaker colors, and confidence indicators[/dim]")
    console.print()
    console.print("─" * 80)
    console.print()

    # Example 8: Wizard Mode
    console.print("[bold green]🧙 Wizard Mode (interactive)[/bold green]")
    console.print()
    console.print("Perfect for: First-time users, exploring options")
    console.print()

    code8 = """# Start wizard (recommended for beginners)
localtranscribe wizard audio.mp3

# Or simply
localtranscribe audio.mp3"""
    console.print(Syntax(code8, "bash", theme="monokai", padding=1))

    console.print("[dim]The wizard guides you through:[/dim]")
    console.print("  • Model selection")
    console.print("  • Speaker configuration")
    console.print("  • Output preferences")
    console.print("  • Quality settings")
    console.print()
    console.print("─" * 80)
    console.print()

    # Helpful Tips
    console.print("[bold cyan]💡 Pro Tips[/bold cyan]")
    console.print()
    tips = """
1. **First time?** Run `localtranscribe init` for guided setup
2. **System check:** Run `localtranscribe doctor` to verify dependencies
3. **See all options:** Run `localtranscribe process --help`
4. **Save time:** Use `--skip-diarization` for single-speaker audio
5. **Better quality:** Use `--model large` and `--proofread` for important work
6. **Batch processing:** Process folders with `localtranscribe batch`
7. **Custom configs:** Create `.localtranscribe/config.yaml` for defaults
8. **Check models:** Run `localtranscribe check-models` to manage NLP models
"""
    console.print(Markdown(tips))
    console.print()

    # Model Recommendations
    console.print("[bold cyan]📏 Model Size Guide[/bold cyan]")
    console.print()

    from rich.table import Table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Model", style="yellow")
    table.add_column("Speed", style="green")
    table.add_column("Accuracy", style="blue")
    table.add_column("Use Case", style="white")

    table.add_row("tiny", "⚡⚡⚡⚡⚡", "⭐", "Quick tests, drafts")
    table.add_row("base", "⚡⚡⚡⚡", "⭐⭐", "Fast transcription")
    table.add_row("small", "⚡⚡⚡", "⭐⭐⭐", "Balanced")
    table.add_row("medium", "⚡⚡", "⭐⭐⭐⭐", "Recommended default")
    table.add_row("large", "⚡", "⭐⭐⭐⭐⭐", "High-quality work")

    console.print(table)
    console.print()

    # More help
    console.print(Panel(
        "[bold]Need More Help?[/bold]\n\n"
        "• Documentation: [cyan]https://github.com/aporb/LocalTranscribe[/cyan]\n"
        "• Command help: [cyan]localtranscribe --help[/cyan]\n"
        "• Specific command: [cyan]localtranscribe process --help[/cyan]\n"
        "• System check: [cyan]localtranscribe doctor --verbose[/cyan]\n"
        "• Report issues: [cyan]https://github.com/aporb/LocalTranscribe/issues[/cyan]",
        border_style="blue"
    ))
    console.print()


# Make it callable as a Typer command
app = typer.Typer()
app.command()(examples)


if __name__ == "__main__":
    examples()
