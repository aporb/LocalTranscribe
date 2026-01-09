"""
Enhanced progress tracking with ETAs and stage completion estimates.

Provides real-time progress feedback for long-running pipeline operations.
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
        TimeElapsedColumn,
    )
    from rich.table import Table
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class StageType(str, Enum):
    """Pipeline stage types."""
    VALIDATION = "validation"
    DIARIZATION = "diarization"
    SEGMENT_PROCESSING = "segment_processing"
    TRANSCRIPTION = "transcription"
    COMBINATION = "combination"
    LABELING = "labeling"
    PROOFREADING = "proofreading"


@dataclass
class StageEstimate:
    """Time estimates for a pipeline stage."""
    name: str
    estimated_seconds: float
    actual_seconds: Optional[float] = None
    completed: bool = False
    started: bool = False
    start_time: Optional[float] = None


@dataclass
class PipelineProgress:
    """Track overall pipeline progress."""
    stages: List[StageEstimate] = field(default_factory=list)
    current_stage_index: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def total_estimated_seconds(self) -> float:
        """Calculate total estimated time."""
        return sum(s.estimated_seconds for s in self.stages)

    @property
    def elapsed_seconds(self) -> float:
        """Calculate elapsed time."""
        return time.time() - self.start_time

    @property
    def completed_seconds(self) -> float:
        """Calculate time spent on completed stages."""
        return sum(s.actual_seconds for s in self.stages if s.completed and s.actual_seconds)

    @property
    def remaining_estimated_seconds(self) -> float:
        """Calculate remaining estimated time."""
        completed = sum(s.estimated_seconds for s in self.stages if s.completed)
        return self.total_estimated_seconds - completed

    @property
    def progress_percentage(self) -> float:
        """Calculate overall progress percentage."""
        if not self.stages:
            return 0.0
        completed = sum(s.estimated_seconds for s in self.stages if s.completed)
        return (completed / self.total_estimated_seconds) * 100 if self.total_estimated_seconds > 0 else 0.0

    @property
    def current_stage(self) -> Optional[StageEstimate]:
        """Get current stage."""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None


class EnhancedProgressTracker:
    """
    Enhanced progress tracker with ETA calculations.

    Features:
    - Real-time progress bars with ETAs
    - Stage-by-stage completion tracking
    - Intermediate result display
    - Dynamic time estimates based on actual performance
    """

    def __init__(
        self,
        audio_duration_minutes: Optional[float] = None,
        model_size: str = "medium",
        skip_diarization: bool = False,
        enable_proofreading: bool = False,
        verbose: bool = True,
    ):
        """
        Initialize progress tracker.

        Args:
            audio_duration_minutes: Duration of audio file in minutes
            model_size: Whisper model size for time estimates
            skip_diarization: Whether diarization is skipped
            enable_proofreading: Whether proofreading is enabled
            verbose: Show detailed progress
        """
        self.audio_duration_minutes = audio_duration_minutes or 1.0
        self.model_size = model_size
        self.skip_diarization = skip_diarization
        self.enable_proofreading = enable_proofreading
        self.verbose = verbose
        self.console = Console() if RICH_AVAILABLE else None

        # Build pipeline progress tracker
        self.pipeline_progress = self._build_pipeline_progress()

        # Intermediate results storage
        self.intermediate_results: Dict[str, any] = {}

    def _estimate_stage_time(self, stage: StageType) -> float:
        """
        Estimate processing time for a stage in seconds.

        Based on empirical data:
        - Diarization: ~0.5x audio duration
        - Transcription: varies by model (tiny: 0.05x, base: 0.2x, small: 0.5x, medium: 1.0x, large: 2.0x)
        - Combination: ~5 seconds
        - Proofreading: ~0.1x audio duration
        """
        audio_seconds = self.audio_duration_minutes * 60

        # Model multipliers for transcription
        model_multipliers = {
            "tiny": 0.05,
            "base": 0.2,
            "small": 0.5,
            "medium": 1.0,
            "large": 2.0,
        }
        transcription_multiplier = model_multipliers.get(self.model_size, 1.0)

        # Stage estimates
        estimates = {
            StageType.VALIDATION: 2.0,
            StageType.DIARIZATION: audio_seconds * 0.5,
            StageType.SEGMENT_PROCESSING: 3.0,
            StageType.TRANSCRIPTION: audio_seconds * transcription_multiplier,
            StageType.COMBINATION: 5.0,
            StageType.LABELING: 2.0,
            StageType.PROOFREADING: audio_seconds * 0.1,
        }

        return estimates.get(stage, 5.0)

    def _build_pipeline_progress(self) -> PipelineProgress:
        """Build pipeline progress tracker with estimates."""
        stages = [StageEstimate("Validation", self._estimate_stage_time(StageType.VALIDATION))]

        if not self.skip_diarization:
            stages.append(StageEstimate("Speaker Diarization", self._estimate_stage_time(StageType.DIARIZATION)))
            stages.append(StageEstimate("Segment Processing", self._estimate_stage_time(StageType.SEGMENT_PROCESSING)))

        stages.append(StageEstimate("Speech-to-Text", self._estimate_stage_time(StageType.TRANSCRIPTION)))

        if not self.skip_diarization:
            stages.append(StageEstimate("Combining Results", self._estimate_stage_time(StageType.COMBINATION)))

        if self.enable_proofreading:
            stages.append(StageEstimate("Proofreading", self._estimate_stage_time(StageType.PROOFREADING)))

        return PipelineProgress(stages=stages)

    def start_stage(self, stage_name: str):
        """Mark a stage as started."""
        for i, stage in enumerate(self.pipeline_progress.stages):
            if stage.name == stage_name:
                stage.started = True
                stage.start_time = time.time()
                self.pipeline_progress.current_stage_index = i
                break

        if self.verbose and self.console:
            self._print_stage_start(stage_name)

    def complete_stage(self, stage_name: str, result_info: Optional[str] = None):
        """Mark a stage as completed."""
        for stage in self.pipeline_progress.stages:
            if stage.name == stage_name and stage.started:
                stage.completed = True
                stage.actual_seconds = time.time() - stage.start_time if stage.start_time else 0
                break

        if self.verbose and self.console:
            self._print_stage_complete(stage_name, result_info)

    def add_intermediate_result(self, key: str, value: any, display: bool = True):
        """
        Add intermediate result to display.

        Args:
            key: Result identifier
            value: Result value
            display: Whether to display immediately
        """
        self.intermediate_results[key] = value

        if display and self.verbose and self.console:
            self.console.print(f"  [cyan]→ {key}:[/cyan] {value}")

    def _print_stage_start(self, stage_name: str):
        """Print stage start message."""
        progress = self.pipeline_progress
        stage_num = progress.current_stage_index + 1
        total_stages = len(progress.stages)

        self.console.print()
        self.console.print(
            f"[bold cyan]Stage {stage_num}/{total_stages}:[/bold cyan] {stage_name}"
        )

        # Show ETA if available
        if progress.remaining_estimated_seconds > 0:
            eta_minutes = progress.remaining_estimated_seconds / 60
            if eta_minutes < 1:
                eta_str = f"{int(progress.remaining_estimated_seconds)}s"
            else:
                eta_str = f"{int(eta_minutes)}m {int(progress.remaining_estimated_seconds % 60)}s"

            self.console.print(
                f"[dim]  Progress: {progress.progress_percentage:.0f}% complete | ETA: {eta_str} remaining[/dim]"
            )

    def _print_stage_complete(self, stage_name: str, result_info: Optional[str] = None):
        """Print stage completion message."""
        for stage in self.pipeline_progress.stages:
            if stage.name == stage_name and stage.actual_seconds:
                time_str = f"{stage.actual_seconds:.1f}s"
                self.console.print(
                    f"[green]  ✓ {stage_name} complete ({time_str})[/green]"
                )
                if result_info:
                    self.console.print(f"[dim]    {result_info}[/dim]")
                break

    def print_summary(self):
        """Print final summary with timing breakdown."""
        if not self.verbose or not self.console:
            return

        self.console.print()
        self.console.print("[bold cyan]Pipeline Summary[/bold cyan]")
        self.console.print()

        # Create timing table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Stage", style="white")
        table.add_column("Time", style="green", justify="right")
        table.add_column("Status", style="cyan")

        for stage in self.pipeline_progress.stages:
            if stage.completed and stage.actual_seconds:
                time_str = f"{stage.actual_seconds:.1f}s"
                status = "✓ Complete"
            elif stage.started:
                status = "⚠ In Progress"
                time_str = "..."
            else:
                status = "○ Pending"
                time_str = "-"

            table.add_row(stage.name, time_str, status)

        # Add total
        total_time = self.pipeline_progress.elapsed_seconds
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{total_time:.1f}s[/bold]",
            "[bold]✓[/bold]" if all(s.completed for s in self.pipeline_progress.stages) else "[bold]⚠[/bold]"
        )

        self.console.print(table)
        self.console.print()

        # Show intermediate results if any
        if self.intermediate_results:
            self.console.print("[bold cyan]Results[/bold cyan]")
            for key, value in self.intermediate_results.items():
                self.console.print(f"  • {key}: [green]{value}[/green]")
            self.console.print()

    def create_rich_progress(self) -> Optional[Progress]:
        """
        Create Rich Progress instance for long-running operations.

        Returns progress bar with spinner, text, bar, percentage, and ETA.
        """
        if not RICH_AVAILABLE:
            return None

        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        )


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2m 30s", "45s", "1h 15m")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds / 3600)
        remaining_minutes = int((seconds % 3600) / 60)
        return f"{hours}h {remaining_minutes}m"
