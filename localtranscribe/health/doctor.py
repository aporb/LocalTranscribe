"""
Health check system for LocalTranscribe.

Validates dependencies, environment, and system configuration.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class CheckResult:
    """Result from a health check."""

    name: str
    status: str  # "pass", "warning", "fail"
    message: str
    details: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []


class HealthChecker:
    """System health checker for LocalTranscribe."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console() if RICH_AVAILABLE else None
        self.checks: List[CheckResult] = []

    def _print(self, message: str, style: str = None):
        """Print message with optional Rich styling."""
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)

    def check_python_version(self) -> CheckResult:
        """Check Python version."""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major == 3 and version.minor >= 9:
            return CheckResult(
                name="Python Version",
                status="pass",
                message=f"Python {version_str}",
                details=[f"Minimum required: Python 3.9+"],
            )
        else:
            return CheckResult(
                name="Python Version",
                status="fail",
                message=f"Python {version_str} (unsupported)",
                details=[
                    "LocalTranscribe requires Python 3.9 or higher",
                    "Current version is too old",
                ],
            )

    def check_dependency(self, name: str, import_name: str) -> CheckResult:
        """Check if a dependency is installed."""
        try:
            __import__(import_name)
            return CheckResult(
                name=name, status="pass", message="Installed", details=[]
            )
        except ImportError:
            return CheckResult(
                name=name,
                status="fail",
                message="Not installed",
                details=[f"Install with: pip install {import_name}"],
            )

    def check_torch(self) -> CheckResult:
        """Check PyTorch installation and device availability."""
        try:
            import torch

            version = torch.__version__
            details = [f"Version: {version}"]

            # Check device availability
            if torch.backends.mps.is_available():
                details.append("✓ Apple Silicon (MPS) available")
                device = "MPS"
            elif torch.cuda.is_available():
                details.append(f"✓ CUDA available (GPU: {torch.cuda.get_device_name(0)})")
                device = "CUDA"
            else:
                details.append("! CPU only (slower performance)")
                device = "CPU"

            return CheckResult(
                name="PyTorch",
                status="pass",
                message=f"Installed ({device})",
                details=details,
            )
        except ImportError:
            return CheckResult(
                name="PyTorch",
                status="fail",
                message="Not installed",
                details=["Install with: pip install torch torchaudio"],
            )

    def check_whisper_implementations(self) -> CheckResult:
        """Check available Whisper implementations."""
        implementations = []
        details = []

        # Check MLX-Whisper
        try:
            import mlx_whisper
            import mlx.core as mx

            if mx.metal.is_available():
                implementations.append("mlx")
                details.append("✓ MLX-Whisper (Apple Silicon optimized)")
        except ImportError:
            details.append("✗ MLX-Whisper (install: pip install mlx-whisper mlx)")

        # Check Faster-Whisper
        try:
            import faster_whisper

            implementations.append("faster")
            details.append("✓ Faster-Whisper")
        except ImportError:
            details.append("✗ Faster-Whisper (install: pip install faster-whisper)")

        # Check Original Whisper
        try:
            import whisper

            implementations.append("original")
            details.append("✓ OpenAI Whisper")
        except ImportError:
            details.append("✗ OpenAI Whisper (install: pip install openai-whisper)")

        if implementations:
            return CheckResult(
                name="Whisper Implementations",
                status="pass",
                message=f"{len(implementations)} available: {', '.join(implementations)}",
                details=details,
            )
        else:
            return CheckResult(
                name="Whisper Implementations",
                status="fail",
                message="No Whisper implementation found",
                details=details + ["At least one Whisper implementation is required"],
            )

    def check_pyannote(self) -> CheckResult:
        """Check pyannote.audio installation."""
        try:
            import pyannote.audio

            version = pyannote.audio.__version__
            return CheckResult(
                name="Pyannote.audio",
                status="pass",
                message="Installed",
                details=[f"Version: {version}"],
            )
        except ImportError:
            return CheckResult(
                name="Pyannote.audio",
                status="fail",
                message="Not installed",
                details=["Install with: pip install pyannote-audio"],
            )

    def check_hf_token(self) -> CheckResult:
        """Check HuggingFace token."""
        from dotenv import load_dotenv

        load_dotenv()
        token = os.getenv("HUGGINGFACE_TOKEN")

        if token and token != "your_token_here":
            # Basic validation (tokens are typically long strings)
            if len(token) > 20:
                return CheckResult(
                    name="HuggingFace Token",
                    status="pass",
                    message="Configured",
                    details=["Token found in environment"],
                )
            else:
                return CheckResult(
                    name="HuggingFace Token",
                    status="warning",
                    message="Token looks invalid",
                    details=[
                        "Token is too short to be valid",
                        "Get token from: https://huggingface.co/settings/tokens",
                    ],
                )
        else:
            return CheckResult(
                name="HuggingFace Token",
                status="warning",
                message="Not configured",
                details=[
                    "Required for speaker diarization",
                    "Add to .env file: HUGGINGFACE_TOKEN=your_token",
                    "Get token from: https://huggingface.co/settings/tokens",
                    "Accept license: https://huggingface.co/pyannote/speaker-diarization-3.1",
                    "Or use --skip-diarization for transcription only",
                ],
            )

    def check_ffmpeg(self) -> CheckResult:
        """Check FFmpeg installation."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                # Extract version from output
                version_line = result.stdout.split("\n")[0]
                return CheckResult(
                    name="FFmpeg",
                    status="pass",
                    message="Installed",
                    details=[version_line],
                )
            else:
                return CheckResult(
                    name="FFmpeg",
                    status="fail",
                    message="Not working",
                    details=["FFmpeg command failed"],
                )
        except FileNotFoundError:
            return CheckResult(
                name="FFmpeg",
                status="fail",
                message="Not installed",
                details=[
                    "Required for audio processing",
                    "Install with: brew install ffmpeg (macOS)",
                    "Or visit: https://ffmpeg.org/download.html",
                ],
            )
        except Exception as e:
            return CheckResult(
                name="FFmpeg",
                status="warning",
                message="Check failed",
                details=[f"Error: {str(e)}"],
            )

    def check_pydub(self) -> CheckResult:
        """Check pydub installation."""
        return self.check_dependency("Pydub", "pydub")

    def check_typer(self) -> CheckResult:
        """Check Typer installation."""
        return self.check_dependency("Typer", "typer")

    def check_rich(self) -> CheckResult:
        """Check Rich installation."""
        return self.check_dependency("Rich", "rich")

    def check_dotenv(self) -> CheckResult:
        """Check python-dotenv installation."""
        return self.check_dependency("Python-dotenv", "dotenv")

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        self._print("\n[bold]Running health checks...[/bold]\n" if self.console else "\nRunning health checks...\n")

        # Core checks (critical)
        core_checks = [
            ("Python Version", self.check_python_version),
            ("PyTorch", self.check_torch),
            ("Pyannote.audio", self.check_pyannote),
            ("FFmpeg", self.check_ffmpeg),
            ("Pydub", self.check_pydub),
        ]

        # Whisper implementations (at least one required)
        whisper_check = ("Whisper", self.check_whisper_implementations)

        # Optional checks
        optional_checks = [
            ("HuggingFace Token", self.check_hf_token),
            ("Typer", self.check_typer),
            ("Rich", self.check_rich),
            ("Python-dotenv", self.check_dotenv),
        ]

        # Run checks
        results = {"core": [], "whisper": None, "optional": []}

        # Core checks
        for name, check_func in core_checks:
            result = check_func()
            results["core"].append(result)
            self._print_check_result(result)

        # Whisper check
        result = whisper_check[1]()
        results["whisper"] = result
        self._print_check_result(result)

        # Optional checks
        for name, check_func in optional_checks:
            result = check_func()
            results["optional"].append(result)
            self._print_check_result(result)

        # Determine overall status
        core_failures = [r for r in results["core"] if r.status == "fail"]
        whisper_failure = results["whisper"].status == "fail"

        if core_failures or whisper_failure:
            overall_status = "critical"
        elif any(r.status == "warning" for r in results["core"] + results["optional"] + [results["whisper"]]):
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return {
            "overall_status": overall_status,
            "core_checks": results["core"],
            "whisper_check": results["whisper"],
            "optional_checks": results["optional"],
        }

    def _print_check_result(self, result: CheckResult):
        """Print a single check result."""
        # Status indicator
        if result.status == "pass":
            indicator = "✅" if self.console else "[PASS]"
            style = "green"
        elif result.status == "warning":
            indicator = "⚠️ " if self.console else "[WARN]"
            style = "yellow"
        else:
            indicator = "❌" if self.console else "[FAIL]"
            style = "red"

        # Main message
        self._print(f"{indicator} {result.name}: {result.message}", style=style)

        # Details (in verbose mode)
        if self.verbose and result.details:
            for detail in result.details:
                self._print(f"   {detail}", style="dim")


def run_health_check(verbose: bool = False) -> Dict[str, Any]:
    """
    Run health check and return results.

    Args:
        verbose: Show detailed information

    Returns:
        Dictionary with check results and overall status
    """
    checker = HealthChecker(verbose=verbose)
    return checker.run_all_checks()
