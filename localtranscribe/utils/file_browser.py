"""
Interactive file browser for selecting audio/video files.
"""

from pathlib import Path
from typing import Optional, List
import questionary
from questionary import Style


# Supported audio and video extensions
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


# Custom style for file browser
BROWSER_STYLE = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#00bcd4 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#00bcd4'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])


def get_file_icon(path: Path) -> str:
    """Get emoji icon for file type."""
    if path.is_dir():
        return "📁"
    elif path.suffix.lower() in AUDIO_EXTENSIONS:
        return "🎵"
    elif path.suffix.lower() in VIDEO_EXTENSIONS:
        return "🎬"
    else:
        return "📄"


def get_media_files_and_dirs(directory: Path) -> List[Path]:
    """
    Get all media files and directories in the given directory.

    Args:
        directory: Path to search

    Returns:
        List of paths (directories first, then media files)
    """
    try:
        items = list(directory.iterdir())
    except PermissionError:
        return []

    # Separate directories and media files
    directories = []
    media_files = []

    for item in items:
        # Skip hidden files/folders
        if item.name.startswith('.'):
            continue

        if item.is_dir():
            directories.append(item)
        elif item.suffix.lower() in MEDIA_EXTENSIONS:
            media_files.append(item)

    # Sort each group alphabetically
    directories.sort(key=lambda x: x.name.lower())
    media_files.sort(key=lambda x: x.name.lower())

    return directories + media_files


def format_choice(path: Path, current_dir: Path) -> str:
    """
    Format a file/directory choice for display.

    Args:
        path: Path to format
        current_dir: Current directory for relative display

    Returns:
        Formatted string with icon and name
    """
    icon = get_file_icon(path)
    name = path.name

    if path.is_dir():
        return f"{icon}  {name}/"
    else:
        # Show file size for media files
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            return f"{icon}  {name} ({size_mb:.1f} MB)"
        except:
            return f"{icon}  {name}"


def browse_files(start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Interactive file browser to select an audio/video file.

    Args:
        start_dir: Starting directory (defaults to current directory)

    Returns:
        Selected file path or None if cancelled
    """
    current_dir = start_dir or Path.cwd()

    while True:
        # Get items in current directory
        items = get_media_files_and_dirs(current_dir)

        # Build choices list
        choices = []

        # Add "Go up" option if not at root
        if current_dir.parent != current_dir:
            choices.append({
                'name': '⬆️  .. (Go up)',
                'value': 'GO_UP'
            })

        # Add all items
        for item in items:
            choices.append({
                'name': format_choice(item, current_dir),
                'value': item
            })

        # Add cancel option
        choices.append({
            'name': '❌ Cancel',
            'value': 'CANCEL'
        })

        # If no media files or directories found
        if len(choices) == 1 or (len(choices) == 2 and current_dir.parent != current_dir):
            # Only cancel (or cancel + go up)
            print(f"\n📂 {current_dir}")
            print("No audio or video files found in this directory.\n")

            if current_dir.parent != current_dir:
                go_up = questionary.confirm(
                    "Go up to parent directory?",
                    default=True,
                    style=BROWSER_STYLE
                ).ask()

                if go_up:
                    current_dir = current_dir.parent
                    continue

            return None

        # Show file browser
        question_text = f"📂 {current_dir}\n\nSelect an audio or video file to transcribe:"

        selected = questionary.select(
            question_text,
            choices=choices,
            style=BROWSER_STYLE,
            use_arrow_keys=True,
            use_shortcuts=False
        ).ask()

        # Handle selection
        if selected == 'CANCEL' or selected is None:
            return None
        elif selected == 'GO_UP':
            current_dir = current_dir.parent
        elif isinstance(selected, Path):
            if selected.is_dir():
                # Navigate into directory
                current_dir = selected
            else:
                # File selected - return it
                return selected


def prompt_for_file() -> Optional[Path]:
    """
    Prompt user to select a file using the interactive browser.

    Returns:
        Selected file path or None if cancelled
    """
    print("\n" + "="*60)
    print("🎙️  LocalTranscribe - Audio File Browser")
    print("="*60)
    print("\nUse ↑/↓ arrow keys to navigate, Enter to select\n")

    selected = browse_files()

    if selected:
        print(f"\n✅ Selected: {selected.name}\n")
    else:
        print("\n❌ No file selected.\n")

    return selected
