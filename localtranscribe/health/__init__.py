"""
Health check utilities for LocalTranscribe.

Validates system requirements and dependencies.
"""

from .doctor import run_health_check, HealthChecker, CheckResult

__all__ = ["run_health_check", "HealthChecker", "CheckResult"]
