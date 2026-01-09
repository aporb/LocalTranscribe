"""
Hardware detection and model recommendations.

Analyzes system capabilities and recommends optimal model configurations.
"""

import platform
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Tuple
from enum import Enum


class DeviceType(str, Enum):
    """Available device types."""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"


class ModelRecommendation(str, Enum):
    """Whisper model size recommendations."""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class HardwareInfo:
    """System hardware information."""
    device_type: DeviceType
    device_name: str
    ram_gb: float
    cpu_count: int
    platform_system: str
    platform_machine: str
    has_gpu_acceleration: bool
    gpu_memory_gb: Optional[float] = None


@dataclass
class RecommendationResult:
    """Model recommendation with rationale."""
    recommended_model: ModelRecommendation
    alternative_models: List[ModelRecommendation]
    rationale: str
    expected_performance: str
    warnings: List[str]
    hardware_info: HardwareInfo


class HardwareDetector:
    """Detect system hardware capabilities."""

    @staticmethod
    def detect_device() -> Tuple[DeviceType, str, bool, Optional[float]]:
        """
        Detect available compute device.

        Returns:
            Tuple of (device_type, device_name, has_acceleration, gpu_memory_gb)
        """
        try:
            import torch

            # Check Apple Silicon (MPS)
            if torch.backends.mps.is_available():
                return DeviceType.MPS, "Apple Silicon (MPS)", True, None

            # Check CUDA
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                # Try to get GPU memory
                try:
                    gpu_memory_bytes = torch.cuda.get_device_properties(0).total_memory
                    gpu_memory_gb = gpu_memory_bytes / (1024 ** 3)
                except Exception:
                    gpu_memory_gb = None

                return DeviceType.CUDA, f"NVIDIA {device_name}", True, gpu_memory_gb

            # Fallback to CPU
            cpu_name = platform.processor() or "CPU"
            return DeviceType.CPU, cpu_name, False, None

        except ImportError:
            # PyTorch not installed
            cpu_name = platform.processor() or "CPU"
            return DeviceType.CPU, cpu_name, False, None

    @staticmethod
    def detect_ram() -> float:
        """
        Detect system RAM in GB.

        Returns:
            RAM in gigabytes
        """
        try:
            import psutil
            ram_bytes = psutil.virtual_memory().total
            return ram_bytes / (1024 ** 3)
        except ImportError:
            # Fallback: try platform-specific commands
            system = platform.system()
            try:
                if system == "Darwin":  # macOS
                    result = subprocess.run(
                        ["sysctl", "-n", "hw.memsize"],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        return int(result.stdout.strip()) / (1024 ** 3)
                elif system == "Linux":
                    result = subprocess.run(
                        ["grep", "MemTotal", "/proc/meminfo"],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        # Extract KB value and convert to GB
                        mem_kb = int(result.stdout.split()[1])
                        return mem_kb / (1024 ** 2)
            except Exception:
                pass

            # Default fallback
            return 8.0  # Assume 8GB

    @staticmethod
    def detect_cpu_count() -> int:
        """Detect number of CPU cores."""
        try:
            import os
            return os.cpu_count() or 4
        except Exception:
            return 4

    @classmethod
    def get_hardware_info(cls) -> HardwareInfo:
        """
        Get complete hardware information.

        Returns:
            HardwareInfo object with system capabilities
        """
        device_type, device_name, has_acceleration, gpu_memory = cls.detect_device()
        ram_gb = cls.detect_ram()
        cpu_count = cls.detect_cpu_count()

        return HardwareInfo(
            device_type=device_type,
            device_name=device_name,
            ram_gb=ram_gb,
            cpu_count=cpu_count,
            platform_system=platform.system(),
            platform_machine=platform.machine(),
            has_gpu_acceleration=has_acceleration,
            gpu_memory_gb=gpu_memory,
        )


class ModelRecommender:
    """Recommend optimal model size based on hardware."""

    @staticmethod
    def recommend_model(
        hardware_info: Optional[HardwareInfo] = None,
        audio_duration_minutes: Optional[float] = None,
        priority: str = "balanced",  # "speed", "balanced", "quality"
    ) -> RecommendationResult:
        """
        Recommend optimal Whisper model size.

        Args:
            hardware_info: System hardware information (auto-detected if None)
            audio_duration_minutes: Duration of audio to process
            priority: User priority ("speed", "balanced", "quality")

        Returns:
            RecommendationResult with model recommendation and rationale
        """
        if hardware_info is None:
            hardware_info = HardwareDetector.get_hardware_info()

        warnings = []
        alternative_models = []

        # Base recommendations on hardware
        if hardware_info.has_gpu_acceleration:
            # GPU/MPS available - can handle larger models
            if hardware_info.ram_gb >= 16:
                if priority == "speed":
                    recommended = ModelRecommendation.SMALL
                    alternative_models = [ModelRecommendation.MEDIUM, ModelRecommendation.BASE]
                    rationale = "Small model recommended for fast processing with GPU acceleration"
                    expected = "Very fast (2-5x realtime)"
                elif priority == "quality":
                    recommended = ModelRecommendation.LARGE
                    alternative_models = [ModelRecommendation.MEDIUM, ModelRecommendation.SMALL]
                    rationale = "Large model recommended for highest accuracy with sufficient RAM and GPU"
                    expected = "Slower but highest quality (0.5-1x realtime)"
                else:  # balanced
                    recommended = ModelRecommendation.MEDIUM
                    alternative_models = [ModelRecommendation.SMALL, ModelRecommendation.LARGE]
                    rationale = "Medium model provides excellent balance of speed and accuracy with GPU"
                    expected = "Fast (1-3x realtime)"
            else:  # 8-16 GB RAM
                if priority == "quality":
                    recommended = ModelRecommendation.MEDIUM
                    alternative_models = [ModelRecommendation.SMALL, ModelRecommendation.BASE]
                    rationale = "Medium model recommended with GPU (limited by RAM)"
                    expected = "Moderate speed (1-2x realtime)"
                    warnings.append("Consider upgrading RAM for large model support")
                else:
                    recommended = ModelRecommendation.SMALL
                    alternative_models = [ModelRecommendation.MEDIUM, ModelRecommendation.BASE]
                    rationale = "Small model recommended for reliable performance"
                    expected = "Fast (2-4x realtime)"
        else:
            # CPU only - recommend smaller models
            if hardware_info.ram_gb >= 16 and hardware_info.cpu_count >= 8:
                if priority == "quality":
                    recommended = ModelRecommendation.MEDIUM
                    alternative_models = [ModelRecommendation.SMALL, ModelRecommendation.BASE]
                    rationale = "Medium model feasible on powerful CPU (will be slower than GPU)"
                    expected = "Slow (0.3-0.5x realtime)"
                    warnings.append("Consider GPU for faster processing")
                else:
                    recommended = ModelRecommendation.SMALL
                    alternative_models = [ModelRecommendation.MEDIUM, ModelRecommendation.BASE]
                    rationale = "Small model recommended for CPU-only processing"
                    expected = "Moderate speed (0.5-1x realtime)"
            elif hardware_info.ram_gb >= 8:
                if priority == "speed":
                    recommended = ModelRecommendation.BASE
                    alternative_models = [ModelRecommendation.SMALL, ModelRecommendation.TINY]
                    rationale = "Base model recommended for faster CPU processing"
                    expected = "Moderate (0.8-1.5x realtime)"
                else:
                    recommended = ModelRecommendation.SMALL
                    alternative_models = [ModelRecommendation.BASE, ModelRecommendation.MEDIUM]
                    rationale = "Small model balances quality and speed on CPU"
                    expected = "Slow (0.3-0.6x realtime)"
                warnings.append("Processing will be slower without GPU acceleration")
            else:  # < 8 GB RAM
                recommended = ModelRecommendation.BASE
                alternative_models = [ModelRecommendation.TINY, ModelRecommendation.SMALL]
                rationale = "Base model recommended due to limited RAM"
                expected = "Slow (0.5-1x realtime)"
                warnings.append("Limited RAM may cause performance issues")
                warnings.append("Consider closing other applications")

        # Adjust for long audio files
        if audio_duration_minutes and audio_duration_minutes > 120:  # 2+ hours
            warnings.append(f"Long audio file ({audio_duration_minutes:.0f} min) - consider smaller model for faster processing")

        return RecommendationResult(
            recommended_model=recommended,
            alternative_models=alternative_models,
            rationale=rationale,
            expected_performance=expected,
            warnings=warnings,
            hardware_info=hardware_info,
        )


def get_model_recommendation(
    audio_duration_minutes: Optional[float] = None,
    priority: str = "balanced",
) -> RecommendationResult:
    """
    Convenience function to get model recommendation.

    Args:
        audio_duration_minutes: Duration of audio to process
        priority: User priority ("speed", "balanced", "quality")

    Returns:
        RecommendationResult with model recommendation
    """
    hardware_info = HardwareDetector.get_hardware_info()
    return ModelRecommender.recommend_model(hardware_info, audio_duration_minutes, priority)


def print_hardware_summary(hardware_info: Optional[HardwareInfo] = None):
    """
    Print hardware summary in a formatted way.

    Args:
        hardware_info: Hardware information (auto-detected if None)
    """
    if hardware_info is None:
        hardware_info = HardwareDetector.get_hardware_info()

    try:
        from rich.console import Console
        from rich.table import Table

        console = Console()

        table = Table(title="System Hardware", show_header=False)
        table.add_column("Component", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Platform", f"{hardware_info.platform_system} ({hardware_info.platform_machine})")
        table.add_row("Device", hardware_info.device_name)
        table.add_row("Device Type", hardware_info.device_type.value.upper())
        table.add_row("RAM", f"{hardware_info.ram_gb:.1f} GB")
        table.add_row("CPU Cores", str(hardware_info.cpu_count))

        if hardware_info.gpu_memory_gb:
            table.add_row("GPU Memory", f"{hardware_info.gpu_memory_gb:.1f} GB")

        table.add_row(
            "Acceleration",
            "✓ Available" if hardware_info.has_gpu_acceleration else "✗ CPU Only"
        )

        console.print(table)
    except ImportError:
        # Fallback without Rich
        print("\n=== System Hardware ===")
        print(f"Platform: {hardware_info.platform_system} ({hardware_info.platform_machine})")
        print(f"Device: {hardware_info.device_name}")
        print(f"Device Type: {hardware_info.device_type.value.upper()}")
        print(f"RAM: {hardware_info.ram_gb:.1f} GB")
        print(f"CPU Cores: {hardware_info.cpu_count}")
        if hardware_info.gpu_memory_gb:
            print(f"GPU Memory: {hardware_info.gpu_memory_gb:.1f} GB")
        print(f"Acceleration: {'Available' if hardware_info.has_gpu_acceleration else 'CPU Only'}")
        print()


def print_recommendation(recommendation: RecommendationResult):
    """
    Print model recommendation in a formatted way.

    Args:
        recommendation: Model recommendation result
    """
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()

        lines = [
            f"[bold green]Recommended Model:[/bold green] {recommendation.recommended_model.value}",
            f"[dim]{recommendation.rationale}[/dim]",
            "",
            f"[cyan]Expected Performance:[/cyan] {recommendation.expected_performance}",
        ]

        if recommendation.alternative_models:
            alt_str = ", ".join(m.value for m in recommendation.alternative_models)
            lines.append(f"[cyan]Alternatives:[/cyan] {alt_str}")

        if recommendation.warnings:
            lines.append("")
            lines.append("[yellow]⚠️  Warnings:[/yellow]")
            for warning in recommendation.warnings:
                lines.append(f"  • {warning}")

        console.print(Panel("\n".join(lines), title="Model Recommendation", border_style="green"))
    except ImportError:
        # Fallback without Rich
        print("\n=== Model Recommendation ===")
        print(f"Recommended: {recommendation.recommended_model.value}")
        print(f"Rationale: {recommendation.rationale}")
        print(f"Expected Performance: {recommendation.expected_performance}")
        if recommendation.alternative_models:
            alt_str = ", ".join(m.value for m in recommendation.alternative_models)
            print(f"Alternatives: {alt_str}")
        if recommendation.warnings:
            print("\nWarnings:")
            for warning in recommendation.warnings:
                print(f"  • {warning}")
        print()
