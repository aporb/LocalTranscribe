"""
Speaker label management implementation.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class SpeakerLabelManager:
    """
    Manages speaker labels for transcripts.

    Features:
    - Load and save label mappings
    - Apply labels to transcripts
    - Interactive label assignment
    - Batch relabeling support
    """

    def __init__(self, labels: Optional[Dict[str, str]] = None):
        """
        Initialize label manager.

        Args:
            labels: Optional initial label mappings (speaker_id -> name)
        """
        self.labels = labels or {}

    def load_labels(self, path: Path) -> Dict[str, str]:
        """
        Load speaker labels from JSON file.

        Args:
            path: Path to labels JSON file

        Returns:
            Dictionary of speaker labels

        Raises:
            FileNotFoundError: If labels file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not path.exists():
            raise FileNotFoundError(f"Labels file not found: {path}")

        with open(path, "r") as f:
            labels = json.load(f)

        if not isinstance(labels, dict):
            raise ValueError("Labels file must contain a JSON object")

        self.labels = labels
        return labels

    def save_labels(self, path: Path) -> None:
        """
        Save speaker labels to JSON file.

        Args:
            path: Path to save labels
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(self.labels, f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓[/green] Labels saved to: {path}")

    def set_label(self, speaker_id: str, label: str) -> None:
        """
        Set label for a speaker.

        Args:
            speaker_id: Speaker ID (e.g., "SPEAKER_00")
            label: Human-readable label (e.g., "John Smith")
        """
        self.labels[speaker_id] = label

    def get_label(self, speaker_id: str) -> str:
        """
        Get label for a speaker, or return original ID if not labeled.

        Args:
            speaker_id: Speaker ID

        Returns:
            Human-readable label or original ID
        """
        return self.labels.get(speaker_id, speaker_id)

    def detect_speakers(self, transcript: str) -> List[str]:
        """
        Detect all speaker IDs in a transcript.

        Args:
            transcript: Transcript text

        Returns:
            List of unique speaker IDs found
        """
        # Pattern matches SPEAKER_XX format
        pattern = r"SPEAKER_\d+"
        speaker_ids = re.findall(pattern, transcript)

        # Return unique IDs in sorted order
        return sorted(set(speaker_ids))

    def apply_labels(
        self,
        transcript: str,
        preserve_original: bool = False,
    ) -> str:
        """
        Apply speaker labels to transcript.

        Args:
            transcript: Original transcript text
            preserve_original: If True, keep original IDs in parentheses

        Returns:
            Transcript with labels applied
        """
        result = transcript

        for speaker_id, label in self.labels.items():
            if preserve_original:
                replacement = f"{label} ({speaker_id})"
            else:
                replacement = label

            # Use word boundaries to avoid partial matches
            pattern = r"\b" + re.escape(speaker_id) + r"\b"
            result = re.sub(pattern, replacement, result)

        return result

    def interactive_label(
        self,
        transcript_path: Path,
        output_path: Optional[Path] = None,
        labels_path: Optional[Path] = None,
    ) -> Dict[str, str]:
        """
        Interactively assign labels to speakers.

        Args:
            transcript_path: Path to transcript file
            output_path: Optional path for labeled transcript
            labels_path: Optional path to save label mappings

        Returns:
            Dictionary of assigned labels

        Raises:
            FileNotFoundError: If transcript file doesn't exist
        """
        if not transcript_path.exists():
            raise FileNotFoundError(f"Transcript not found: {transcript_path}")

        # Read transcript
        with open(transcript_path, "r") as f:
            transcript = f.read()

        # Detect speakers
        speaker_ids = self.detect_speakers(transcript)

        if not speaker_ids:
            console.print("[yellow]⚠️  No speaker IDs found in transcript[/yellow]")
            return {}

        # Show header
        console.print()
        console.print(
            Panel.fit(
                "[bold cyan]Interactive Speaker Labeling[/bold cyan]\n"
                f"Found {len(speaker_ids)} speakers",
                border_style="cyan",
            )
        )
        console.print()

        # Display speakers in table
        table = Table(title="Speakers Found")
        table.add_column("ID", style="cyan")
        table.add_column("Occurrences", style="white", justify="right")

        for speaker_id in speaker_ids:
            count = len(re.findall(rf"\b{re.escape(speaker_id)}\b", transcript))
            table.add_row(speaker_id, str(count))

        console.print(table)
        console.print()

        # Prompt for labels
        for speaker_id in speaker_ids:
            # Check if already labeled
            current_label = self.labels.get(speaker_id, "")
            prompt_text = f"Label for {speaker_id}"

            if current_label:
                prompt_text += f" (current: {current_label}, press Enter to keep)"

            label = typer.prompt(
                prompt_text,
                default=current_label if current_label else "",
                show_default=False,
            ).strip()

            if label:
                self.set_label(speaker_id, label)
                console.print(f"[dim]  → {speaker_id} = {label}[/dim]")
            elif current_label:
                console.print(f"[dim]  → Keeping: {speaker_id} = {current_label}[/dim]")

        console.print()

        # Apply labels
        if self.labels:
            labeled_transcript = self.apply_labels(transcript)

            # Determine output path
            if output_path is None:
                output_path = transcript_path.with_stem(
                    transcript_path.stem + "_labeled"
                )

            # Save labeled transcript
            with open(output_path, "w") as f:
                f.write(labeled_transcript)

            console.print(f"[green]✓[/green] Labeled transcript saved: {output_path}")

            # Save label mappings
            if labels_path or typer.confirm("\nSave label mappings for future use?", default=True):
                if labels_path is None:
                    labels_path = transcript_path.with_suffix(".labels.json")

                self.save_labels(labels_path)

        else:
            console.print("[yellow]⚠️  No labels assigned[/yellow]")

        return self.labels

    def batch_relabel(
        self,
        transcript_paths: List[Path],
        output_dir: Optional[Path] = None,
        preserve_original: bool = False,
    ) -> int:
        """
        Apply labels to multiple transcripts.

        Args:
            transcript_paths: List of transcript file paths
            output_dir: Optional output directory (default: same as input)
            preserve_original: Keep original IDs in parentheses

        Returns:
            Number of files successfully relabeled
        """
        if not self.labels:
            console.print("[yellow]⚠️  No labels loaded[/yellow]")
            return 0

        success_count = 0

        for transcript_path in transcript_paths:
            try:
                # Read transcript
                with open(transcript_path, "r") as f:
                    transcript = f.read()

                # Apply labels
                labeled_transcript = self.apply_labels(transcript, preserve_original)

                # Determine output path
                if output_dir:
                    output_path = output_dir / transcript_path.name
                else:
                    output_path = transcript_path.with_stem(
                        transcript_path.stem + "_labeled"
                    )

                # Save labeled transcript
                with open(output_path, "w") as f:
                    f.write(labeled_transcript)

                console.print(f"[green]✓[/green] {transcript_path.name}")
                success_count += 1

            except Exception as e:
                console.print(f"[red]✗[/red] {transcript_path.name}: {e}")

        console.print(f"\n[green]Relabeled {success_count} of {len(transcript_paths)} files[/green]")

        return success_count
