"""Type definitions for SDK."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Segment:
    """A single speech segment with speaker and timestamp."""

    speaker: str
    text: str
    start: float
    end: float
    confidence: Optional[float] = None

    def __repr__(self) -> str:
        return f"Segment(speaker='{self.speaker}', start={self.start:.1f}s, end={self.end:.1f}s)"


@dataclass
class ProcessResult:
    """Result from processing a single audio file."""

    # Status
    success: bool
    audio_file: Path
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

    # Results
    transcript: str = ""
    segments: List[Segment] = field(default_factory=list)
    num_speakers: Optional[int] = None
    speaker_durations: Dict[str, float] = field(default_factory=dict)

    # Output files
    output_files: Dict[str, Path] = field(default_factory=dict)

    # Metadata
    model_size: str = "base"
    language: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Error info (if failed)
    error: Optional[str] = None
    error_type: Optional[str] = None

    def __repr__(self) -> str:
        status = "✅ Success" if self.success else "❌ Failed"
        return (
            f"ProcessResult({status}, "
            f"{len(self.segments)} segments, "
            f"{self.processing_time:.1f}s)"
        )


@dataclass
class BatchResult:
    """Result from batch processing multiple files."""

    total: int
    successful: int
    failed: int
    processing_time: float
    results: List[ProcessResult] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"BatchResult({self.successful}/{self.total} successful, "
            f"{self.processing_time:.1f}s total)"
        )

    def get_successful(self) -> List[ProcessResult]:
        """Get all successful results."""
        return [r for r in self.results if r.success]

    def get_failed(self) -> List[ProcessResult]:
        """Get all failed results."""
        return [r for r in self.results if not r.success]
