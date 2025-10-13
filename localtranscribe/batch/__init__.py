"""
Batch processing module for LocalTranscribe.

Provides functionality to process multiple audio files in a single operation.
"""

from .processor import BatchProcessor, BatchResult, ProcessResult

__all__ = ["BatchProcessor", "BatchResult", "ProcessResult"]
