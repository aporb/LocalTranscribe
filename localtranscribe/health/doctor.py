"""
Health check system for LocalTranscribe.

Validates dependencies, environment, and system configuration.
"""

# Suppress dependency warnings before any imports
import warnings
warnings.filterwarnings("ignore", message=".*torchcodec.*")
warnings.filterwarnings("ignore", module="pyannote.audio.core.io")

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
        # Suppress stderr during import to avoid torchcodec error messages
        # pyannote.audio attempts to load torchcodec which may generate C extension errors
        stderr_fd = sys.stderr.fileno()
        old_stderr_fd = os.dup(stderr_fd)

        try:
            # Redirect stderr to /dev/null during import
            with open(os.devnull, 'w') as devnull:
                os.dup2(devnull.fileno(), stderr_fd)

                # Attempt import with stderr suppressed
                try:
                    import pyannote.audio
                    has_pyannote = True
                    version = pyannote.audio.__version__
                except (ImportError, RuntimeError):
                    # ImportError: pyannote.audio not installed
                    # RuntimeError: dependency loading issues (e.g., torchcodec)
                    has_pyannote = False
                    version = None
        finally:
            # Always restore original stderr
            os.dup2(old_stderr_fd, stderr_fd)
            os.close(old_stderr_fd)

        if has_pyannote:
            return CheckResult(
                name="Pyannote.audio",
                status="pass",
                message="Installed",
                details=[f"Version: {version}"],
            )
        else:
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

    def check_disk_space(self) -> CheckResult:
        """Check available disk space."""
        try:
            import shutil

            # Check current directory space
            stat = shutil.disk_usage(Path.cwd())
            free_gb = stat.free / (1024 ** 3)
            total_gb = stat.total / (1024 ** 3)
            percent_free = (stat.free / stat.total) * 100

            details = [
                f"Free space: {free_gb:.1f} GB / {total_gb:.1f} GB ({percent_free:.1f}% free)",
                f"Location: {Path.cwd()}",
            ]

            if free_gb < 1.0:
                return CheckResult(
                    name="Disk Space",
                    status="warning",
                    message=f"Low disk space ({free_gb:.1f} GB free)",
                    details=details + [
                        "Models and output files require disk space",
                        "Recommend at least 5 GB free for smooth operation",
                    ],
                )
            elif free_gb < 5.0:
                return CheckResult(
                    name="Disk Space",
                    status="pass",
                    message=f"{free_gb:.1f} GB available",
                    details=details + ["Consider freeing up space if processing large files"],
                )
            else:
                return CheckResult(
                    name="Disk Space",
                    status="pass",
                    message=f"{free_gb:.1f} GB available",
                    details=details,
                )
        except Exception as e:
            return CheckResult(
                name="Disk Space",
                status="warning",
                message="Check failed",
                details=[f"Error: {str(e)}"],
            )

    def check_model_cache(self) -> CheckResult:
        """Check HuggingFace model cache status."""
        try:
            # Check HuggingFace cache directory
            cache_dir = Path.home() / ".cache" / "huggingface"

            if not cache_dir.exists():
                return CheckResult(
                    name="Model Cache",
                    status="pass",
                    message="No models cached yet",
                    details=[
                        "Models will be downloaded on first use",
                        "Cache location: " + str(cache_dir),
                        "Whisper medium model: ~1.5 GB",
                        "Diarization models: ~300 MB",
                    ],
                )

            # Calculate cache size
            total_size = 0
            file_count = 0
            for item in cache_dir.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1

            size_gb = total_size / (1024 ** 3)

            # Check for specific models
            hub_cache = cache_dir / "hub"
            models_found = []
            if hub_cache.exists():
                # Look for pyannote models
                for model_dir in hub_cache.glob("models--*"):
                    model_name = model_dir.name.replace("models--", "").replace("--", "/")
                    if "pyannote" in model_name or "whisper" in model_name.lower():
                        models_found.append(model_name)

            details = [
                f"Cache size: {size_gb:.2f} GB ({file_count} files)",
                f"Location: {cache_dir}",
            ]

            if models_found:
                details.append(f"Models cached: {len(models_found)}")
                if self.verbose:
                    for model in models_found[:5]:  # Show first 5
                        details.append(f"  • {model}")
                    if len(models_found) > 5:
                        details.append(f"  ... and {len(models_found) - 5} more")

            return CheckResult(
                name="Model Cache",
                status="pass",
                message=f"{size_gb:.2f} GB cached",
                details=details,
            )
        except Exception as e:
            return CheckResult(
                name="Model Cache",
                status="warning",
                message="Check failed",
                details=[f"Error: {str(e)}"],
            )

    def check_output_permissions(self) -> CheckResult:
        """Check write permissions for output directory."""
        try:
            test_dir = Path.cwd() / "output"

            # Try to create output directory
            test_dir.mkdir(parents=True, exist_ok=True)

            # Try to write a test file
            test_file = test_dir / ".localtranscribe_write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()  # Clean up

                return CheckResult(
                    name="Output Permissions",
                    status="pass",
                    message="Write access confirmed",
                    details=[f"Output directory: {test_dir}"],
                )
            except PermissionError:
                return CheckResult(
                    name="Output Permissions",
                    status="fail",
                    message="No write permission",
                    details=[
                        f"Cannot write to: {test_dir}",
                        "Check directory permissions",
                        "Try running from a different directory",
                    ],
                )
        except Exception as e:
            return CheckResult(
                name="Output Permissions",
                status="warning",
                message="Check failed",
                details=[f"Error: {str(e)}"],
            )

    def check_torchcodec(self) -> CheckResult:
        """Check torchcodec installation (optional dependency for pyannote.audio)."""
        import tempfile

        # Suppress stderr during import to avoid torchcodec error messages
        # We need to redirect at the file descriptor level because torchcodec
        # writes to stderr from C extensions
        stderr_fd = sys.stderr.fileno()
        old_stderr_fd = os.dup(stderr_fd)

        try:
            # Redirect stderr to /dev/null
            with open(os.devnull, 'w') as devnull:
                os.dup2(devnull.fileno(), stderr_fd)

                # Attempt import with stderr suppressed
                try:
                    import torchcodec
                    has_torchcodec = True
                except (ImportError, RuntimeError):
                    # ImportError: torchcodec not installed
                    # RuntimeError: torchcodec installed but can't load C extensions
                    has_torchcodec = False
        finally:
            # Always restore original stderr
            os.dup2(old_stderr_fd, stderr_fd)
            os.close(old_stderr_fd)

        if has_torchcodec:
            version = getattr(torchcodec, '__version__', 'unknown')
            return CheckResult(
                name="TorchCodec",
                status="pass",
                message=f"Installed (v{version})",
                details=[
                    "TorchCodec is an optional dependency for pyannote.audio",
                    "LocalTranscribe uses pydub/FFmpeg for audio processing instead",
                    "Having torchcodec is fine but not required",
                ],
            )
        else:
            return CheckResult(
                name="TorchCodec",
                status="pass",  # Still pass - it's optional!
                message="Not installed (optional)",
                details=[
                    "TorchCodec is an optional dependency for pyannote.audio",
                    "LocalTranscribe uses pydub/FFmpeg for audio processing - no action needed",
                    "If you see torchcodec warnings during startup, they can be safely ignored",
                    "The warnings have been automatically suppressed for cleaner output",
                ],
            )

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
            ("TorchCodec", self.check_torchcodec),
        ]

        # System resource checks (shown in verbose mode or if issues detected)
        resource_checks = [
            ("Disk Space", self.check_disk_space),
            ("Model Cache", self.check_model_cache),
            ("Output Permissions", self.check_output_permissions),
        ]

        # Run checks
        results = {"core": [], "whisper": None, "optional": [], "resources": []}

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

        # Resource checks (always show in verbose mode)
        if self.verbose:
            self._print("\n[bold]System Resources:[/bold]\n" if self.console else "\nSystem Resources:\n")
            for name, check_func in resource_checks:
                result = check_func()
                results["resources"].append(result)
                self._print_check_result(result)

        # Determine overall status
        core_failures = [r for r in results["core"] if r.status == "fail"]
        whisper_failure = results["whisper"].status == "fail"

        all_checks = results["core"] + results["optional"] + results["resources"] + [results["whisper"]]

        if core_failures or whisper_failure:
            overall_status = "critical"
        elif any(r.status == "warning" for r in all_checks):
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return {
            "overall_status": overall_status,
            "core_checks": results["core"],
            "whisper_check": results["whisper"],
            "optional_checks": results["optional"],
            "resource_checks": results["resources"],
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
