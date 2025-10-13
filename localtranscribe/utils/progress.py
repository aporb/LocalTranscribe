"""
Progress tracking utilities for LocalTranscribe.

Provides consistent progress tracking across all pipeline stages.
"""

from contextlib import contextmanager
from typing import Optional
import time

from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    TaskID,
)
from rich.console import Console

console = Console()


class ProgressTracker:
    """
    Tracks progress for long-running operations.

    Features:
    - Consistent progress bars across pipeline
    - ETA calculation
    - Time elapsed tracking
    - Update throttling for performance
    """

    def __init__(self, description: str, total: Optional[int] = None, visible: bool = True):
        """
        Initialize progress tracker.

        Args:
            description: Description of the operation
            total: Total number of steps (None for indeterminate)
            visible: Whether to show progress (False for testing)
        """
        self.description = description
        self.total = total
        self.visible = visible
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.start_time = time.time()
        self.last_update = 0.0
        self.update_interval = 0.1  # Update max 10 times/second

    def __enter__(self):
        """Start progress tracking."""
        if self.visible:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn() if self.total else TextColumn(""),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%") if self.total else TextColumn(""),
                TimeRemainingColumn() if self.total else TextColumn(""),
                console=console,
            )
            self.progress.__enter__()
            self.task_id = self.progress.add_task(self.description, total=self.total)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop progress tracking."""
        if self.progress:
            self.progress.__exit__(exc_type, exc_val, exc_tb)
        return False

    def update(self, advance: int = 1, description: Optional[str] = None):
        """
        Update progress.

        Args:
            advance: Number of steps to advance
            description: Optional new description
        """
        if not self.visible or not self.progress or self.task_id is None:
            return

        # Throttle updates for performance
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return

        self.last_update = current_time

        if description:
            self.progress.update(self.task_id, advance=advance, description=description)
        else:
            self.progress.update(self.task_id, advance=advance)

    def set_total(self, total: int):
        """
        Set total steps (for operations where total becomes known later).

        Args:
            total: Total number of steps
        """
        if self.visible and self.progress and self.task_id is not None:
            self.progress.update(self.task_id, total=total)
            self.total = total

    def complete(self, description: Optional[str] = None):
        """
        Mark progress as complete.

        Args:
            description: Optional completion message
        """
        if self.visible and self.progress and self.task_id is not None:
            if description:
                self.progress.update(self.task_id, description=description)
            if self.total:
                self.progress.update(self.task_id, completed=self.total)

    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time


@contextmanager
def track_progress(description: str, total: Optional[int] = None, visible: bool = True):
    """
    Context manager for tracking progress.

    Example:
        with track_progress("Processing", total=100) as progress:
            for i in range(100):
                # Do work
                progress.update()

    Args:
        description: Description of the operation
        total: Total number of steps
        visible: Whether to show progress

    Yields:
        ProgressTracker instance
    """
    tracker = ProgressTracker(description, total, visible)
    with tracker:
        yield tracker


class StageProgress:
    """
    Tracks progress across multiple pipeline stages.

    Features:
    - Multi-stage progress tracking
    - Stage completion indicators
    - Overall ETA
    """

    def __init__(self, stages: list[str], visible: bool = True):
        """
        Initialize stage progress tracker.

        Args:
            stages: List of stage names
            visible: Whether to show progress
        """
        self.stages = stages
        self.current_stage_index = 0
        self.visible = visible
        self.progress: Optional[Progress] = None
        self.task_ids: dict[str, TaskID] = {}
        self.start_time = time.time()

    def __enter__(self):
        """Start tracking stages."""
        if self.visible:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console,
            )
            self.progress.__enter__()

            # Add task for each stage
            for i, stage in enumerate(self.stages):
                status = "⏳" if i == 0 else "⏸️"
                task_id = self.progress.add_task(
                    f"{status} Stage {i+1}/{len(self.stages)}: {stage}",
                    total=100,
                    completed=0 if i == 0 else 0,
                )
                self.task_ids[stage] = task_id

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop tracking stages."""
        if self.progress:
            self.progress.__exit__(exc_type, exc_val, exc_tb)
        return False

    def update_stage(self, stage: str, progress: int, description: Optional[str] = None):
        """
        Update progress for a specific stage.

        Args:
            stage: Stage name
            progress: Progress percentage (0-100)
            description: Optional description update
        """
        if not self.visible or not self.progress:
            return

        task_id = self.task_ids.get(stage)
        if task_id is not None:
            stage_index = self.stages.index(stage)
            status = "⏳"
            stage_desc = f"{status} Stage {stage_index+1}/{len(self.stages)}: {stage}"

            if description:
                stage_desc += f" - {description}"

            self.progress.update(task_id, completed=progress, description=stage_desc)

    def complete_stage(self, stage: str):
        """
        Mark a stage as complete.

        Args:
            stage: Stage name
        """
        if not self.visible or not self.progress:
            return

        task_id = self.task_ids.get(stage)
        if task_id is not None:
            stage_index = self.stages.index(stage)
            self.progress.update(
                task_id,
                completed=100,
                description=f"✅ Stage {stage_index+1}/{len(self.stages)}: {stage} - Complete",
            )

            # Start next stage if available
            if stage_index + 1 < len(self.stages):
                next_stage = self.stages[stage_index + 1]
                next_task_id = self.task_ids[next_stage]
                self.progress.update(
                    next_task_id,
                    description=f"⏳ Stage {stage_index+2}/{len(self.stages)}: {next_stage}",
                    completed=0,
                )

    @property
    def elapsed(self) -> float:
        """Get total elapsed time in seconds."""
        return time.time() - self.start_time


def should_show_progress(operation_duration: float, threshold: float = 5.0) -> bool:
    """
    Determine if progress should be shown for an operation.

    Operations shorter than threshold don't need progress tracking.

    Args:
        operation_duration: Expected operation duration in seconds
        threshold: Minimum duration to show progress (default: 5 seconds)

    Returns:
        True if progress should be shown
    """
    return operation_duration >= threshold
