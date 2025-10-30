"""
LocalTranscribe - Offline audio transcription with speaker diarization

Optimized for Apple Silicon, works on any Mac.

Basic Usage:
    >>> from localtranscribe import LocalTranscribe
    >>> lt = LocalTranscribe(model_size="base")
    >>> result = lt.process("meeting.mp3")
    >>> print(result.transcript)

Advanced Usage:
    >>> from localtranscribe import run_diarization, run_transcription
    >>> diarization = run_diarization(audio_file, hf_token, output_dir)
    >>> transcription = run_transcription(audio_file, model_size="base")
"""

# Setup clean warning handling before any imports
# This must happen before importing dependencies to catch their warnings
from .utils.warnings_handler import setup_warning_filters
setup_warning_filters(silent=False)

__version__ = "3.1.0"
__author__ = "LocalTranscribe Contributors"
__license__ = "MIT"

# Core functionality
from .core.diarization import run_diarization
from .core.transcription import run_transcription
from .core.combination import combine_results

# Pipeline orchestration
from .pipeline.orchestrator import PipelineOrchestrator, PipelineResult

# Configuration
from .config.loader import load_config, get_config_path
from .config.defaults import DEFAULT_CONFIG

# Utilities
from .utils.errors import LocalTranscribeError

# High-level SDK
from .api.client import LocalTranscribe
from .api.types import ProcessResult, BatchResult, Segment

__all__ = [
    # Version info
    "__version__",
    # Core functions
    "run_diarization",
    "run_transcription",
    "combine_results",
    # Pipeline
    "PipelineOrchestrator",
    "PipelineResult",
    # Configuration
    "load_config",
    "get_config_path",
    "DEFAULT_CONFIG",
    # Errors
    "LocalTranscribeError",
    # SDK
    "LocalTranscribe",
    "ProcessResult",
    "BatchResult",
    "Segment",
]
