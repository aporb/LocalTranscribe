"""
Core business logic for LocalTranscribe.

Contains diarization, transcription, combination, and path resolution modules.
"""

# Imports will be enabled as modules are implemented
from .diarization import run_diarization, DiarizationResult, setup_device
# from .transcription import run_transcription
# from .combination import combine_results
from .path_resolver import PathResolver

__all__ = [
    "run_diarization",
    "DiarizationResult",
    "setup_device",
    # "run_transcription",
    # "combine_results",
    "PathResolver",
]
