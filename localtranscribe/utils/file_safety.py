"""
File safety utilities for LocalTranscribe.

Provides file overwrite protection and backup functionality.
"""

import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


class OverwriteAction(Enum):
    """Action to take when file exists."""

    OVERWRITE = "overwrite"
    SKIP = "skip"
    BACKUP = "backup"
    RENAME = "rename"


class FileSafetyManager:
    """
    Manages file safety operations.

    Features:
    - Overwrite detection
    - Interactive prompts
    - Backup creation
    - Safe filename generation
    """

    def __init__(
        self,
        force: bool = False,
        skip_existing: bool = False,
        create_backup: bool = False,
        interactive: bool = True,
    ):
        """
        Initialize file safety manager.

        Args:
            force: Force overwrite without prompting
            skip_existing: Skip files that already exist
            create_backup: Create backup before overwriting
            interactive: Prompt user for decisions
        """
        self.force = force
        self.skip_existing = skip_existing
        self.create_backup = create_backup
        self.interactive = interactive

    def check_overwrite(self, path: Path) -> OverwriteAction:
        """
        Check if file can be written safely.

        Args:
            path: Path to check

        Returns:
            OverwriteAction to take
        """
        if not path.exists():
            return OverwriteAction.OVERWRITE

        # Force overwrite
        if self.force:
            if self.create_backup:
                return OverwriteAction.BACKUP
            return OverwriteAction.OVERWRITE

        # Skip existing
        if self.skip_existing:
            return OverwriteAction.SKIP

        # Backup before overwriting
        if self.create_backup:
            return OverwriteAction.BACKUP

        # Interactive prompt
        if self.interactive:
            return self._prompt_overwrite(path)

        # Default: skip to be safe
        return OverwriteAction.SKIP

    def _prompt_overwrite(self, path: Path) -> OverwriteAction:
        """
        Prompt user for overwrite decision.

        Args:
            path: Path that exists

        Returns:
            User's chosen action
        """
        console.print(f"\n[yellow]⚠️  File exists: {path}[/yellow]")

        choice = typer.prompt(
            "Action: [o]verwrite, [s]kip, [b]ackup, [r]ename",
            type=str,
            default="s",
        ).lower()

        if choice == "o":
            return OverwriteAction.OVERWRITE
        elif choice == "b":
            return OverwriteAction.BACKUP
        elif choice == "r":
            return OverwriteAction.RENAME
        else:
            return OverwriteAction.SKIP

    def backup_file(self, path: Path, backup_dir: Optional[Path] = None) -> Path:
        """
        Create backup of existing file.

        Args:
            path: File to backup
            backup_dir: Directory for backups (default: .backup in same dir)

        Returns:
            Path to backup file
        """
        if not path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {path}")

        # Determine backup directory
        if backup_dir is None:
            backup_dir = path.parent / ".backup"

        backup_dir.mkdir(parents=True, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{path.stem}_{timestamp}{path.suffix}"
        backup_path = backup_dir / backup_name

        # Ensure unique backup name
        counter = 1
        while backup_path.exists():
            backup_name = f"{path.stem}_{timestamp}_{counter}{path.suffix}"
            backup_path = backup_dir / backup_name
            counter += 1

        # Copy file to backup
        shutil.copy2(path, backup_path)

        console.print(f"[dim]📦 Backup created: {backup_path}[/dim]")

        return backup_path

    def generate_safe_filename(self, base_path: Path, max_attempts: int = 1000) -> Path:
        """
        Generate a safe filename that doesn't exist.

        Args:
            base_path: Desired file path
            max_attempts: Maximum number of attempts

        Returns:
            Path that doesn't exist

        Raises:
            RuntimeError: If unable to generate unique filename
        """
        if not base_path.exists():
            return base_path

        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent

        for i in range(1, max_attempts):
            new_path = parent / f"{stem}_{i}{suffix}"
            if not new_path.exists():
                return new_path

        raise RuntimeError(f"Unable to generate unique filename after {max_attempts} attempts")

    def safe_write(self, path: Path, action: OverwriteAction) -> Optional[Path]:
        """
        Prepare path for safe writing.

        Args:
            path: Desired file path
            action: Overwrite action to take

        Returns:
            Path to write to, or None if should skip
        """
        if action == OverwriteAction.SKIP:
            console.print(f"[yellow]⏭️  Skipping: {path}[/yellow]")
            return None

        elif action == OverwriteAction.BACKUP:
            if path.exists():
                self.backup_file(path)
            return path

        elif action == OverwriteAction.RENAME:
            new_path = self.generate_safe_filename(path)
            console.print(f"[cyan]📝 Writing to: {new_path.name}[/cyan]")
            return new_path

        elif action == OverwriteAction.OVERWRITE:
            return path

        return None


def cleanup_old_backups(
    backup_dir: Path,
    retention_days: int = 7,
    dry_run: bool = False,
) -> int:
    """
    Clean up old backup files.

    Args:
        backup_dir: Directory containing backups
        retention_days: Keep backups newer than this many days
        dry_run: If True, only report what would be deleted

    Returns:
        Number of files deleted (or would be deleted)
    """
    if not backup_dir.exists():
        return 0

    current_time = datetime.now().timestamp()
    retention_seconds = retention_days * 24 * 60 * 60
    deleted_count = 0

    for backup_file in backup_dir.glob("*"):
        if not backup_file.is_file():
            continue

        # Check file age
        file_age = current_time - backup_file.stat().st_mtime
        if file_age > retention_seconds:
            if dry_run:
                console.print(f"[dim]Would delete: {backup_file.name}[/dim]")
            else:
                backup_file.unlink()
                console.print(f"[dim]Deleted old backup: {backup_file.name}[/dim]")
            deleted_count += 1

    return deleted_count


def get_backup_info(backup_dir: Path) -> dict:
    """
    Get information about backups.

    Args:
        backup_dir: Directory containing backups

    Returns:
        Dictionary with backup statistics
    """
    if not backup_dir.exists():
        return {
            "exists": False,
            "count": 0,
            "total_size": 0,
            "oldest": None,
            "newest": None,
        }

    backup_files = list(backup_dir.glob("*"))
    backup_files = [f for f in backup_files if f.is_file()]

    if not backup_files:
        return {
            "exists": True,
            "count": 0,
            "total_size": 0,
            "oldest": None,
            "newest": None,
        }

    total_size = sum(f.stat().st_size for f in backup_files)
    mtimes = [f.stat().st_mtime for f in backup_files]

    return {
        "exists": True,
        "count": len(backup_files),
        "total_size": total_size,
        "total_size_mb": total_size / (1024 * 1024),
        "oldest": datetime.fromtimestamp(min(mtimes)),
        "newest": datetime.fromtimestamp(max(mtimes)),
        "directory": str(backup_dir),
    }
