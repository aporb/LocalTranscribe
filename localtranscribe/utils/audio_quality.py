"""
Audio quality detection and analysis.

Provides functions to assess audio quality and make recommendations for
optimal transcription settings.
"""

import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class QualityLevel(str, Enum):
    """Audio quality levels."""
    EXCELLENT = "excellent"  # SNR > 40dB
    GOOD = "good"           # SNR 25-40dB
    FAIR = "fair"           # SNR 15-25dB
    POOR = "poor"           # SNR < 15dB


@dataclass
class AudioQualityResult:
    """Results from audio quality analysis."""
    quality_level: QualityLevel
    snr_db: Optional[float]
    sample_rate: int
    duration_seconds: float
    channels: int
    warnings: List[str]
    recommendations: List[str]
    optimal_model: str  # Recommended Whisper model size


class AudioQualityAnalyzer:
    """
    Analyze audio quality and provide recommendations.

    Uses signal-to-noise ratio (SNR), sample rate, and other metrics
    to assess audio quality and recommend optimal transcription settings.
    """

    # Sample rate thresholds
    MIN_SAMPLE_RATE = 16000  # Whisper's minimum
    OPTIMAL_SAMPLE_RATE = 44100

    # SNR thresholds
    SNR_EXCELLENT = 40.0
    SNR_GOOD = 25.0
    SNR_FAIR = 15.0

    def analyze(self, audio_path: Path) -> AudioQualityResult:
        """
        Analyze audio file quality.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioQualityResult with analysis and recommendations
        """
        # Load audio data
        audio_data, sample_rate = self._load_audio(audio_path)

        # Calculate metrics
        snr_db = self._calculate_snr(audio_data)
        duration = len(audio_data) / sample_rate
        channels = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]

        # Determine quality level
        quality_level = self._determine_quality_level(snr_db)

        # Generate warnings and recommendations
        warnings = self._generate_warnings(snr_db, sample_rate, duration)
        recommendations = self._generate_recommendations(
            quality_level, snr_db, sample_rate, duration
        )

        # Recommend optimal model
        optimal_model = self._recommend_model(quality_level, duration)

        return AudioQualityResult(
            quality_level=quality_level,
            snr_db=snr_db,
            sample_rate=sample_rate,
            duration_seconds=duration,
            channels=channels,
            warnings=warnings,
            recommendations=recommendations,
            optimal_model=optimal_model,
        )

    def _load_audio(self, audio_path: Path) -> tuple[np.ndarray, int]:
        """
        Load audio file using pydub.

        Args:
            audio_path: Path to audio file

        Returns:
            Tuple of (audio_data as numpy array, sample_rate)
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError(
                "pydub is required for audio quality analysis. "
                "Install with: pip install pydub"
            )

        # Load audio file
        audio = AudioSegment.from_file(str(audio_path))

        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())

        # Handle stereo (convert to mono for analysis)
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)

        # Normalize to [-1, 1]
        if audio.sample_width == 2:  # 16-bit
            samples = samples / 32768.0
        elif audio.sample_width == 4:  # 32-bit
            samples = samples / 2147483648.0

        return samples, audio.frame_rate

    def _calculate_snr(self, audio_data: np.ndarray) -> Optional[float]:
        """
        Calculate Signal-to-Noise Ratio (SNR) in dB.

        Uses a simple method: assumes noise is in quietest 10% of signal.

        Args:
            audio_data: Audio samples as numpy array

        Returns:
            SNR in dB, or None if calculation fails
        """
        try:
            # Calculate RMS of entire signal
            signal_rms = np.sqrt(np.mean(audio_data ** 2))

            if signal_rms == 0:
                return None

            # Estimate noise from quietest segments
            # Sort by absolute value and take bottom 10%
            abs_samples = np.abs(audio_data)
            sorted_samples = np.sort(abs_samples)
            noise_threshold_idx = int(len(sorted_samples) * 0.1)
            noise_samples = sorted_samples[:noise_threshold_idx]

            # Calculate noise RMS
            noise_rms = np.sqrt(np.mean(noise_samples ** 2))

            if noise_rms == 0:
                # Essentially perfect signal
                return 60.0  # Cap at 60dB

            # Calculate SNR in dB
            snr_db = 20 * np.log10(signal_rms / noise_rms)

            return float(snr_db)

        except Exception:
            return None

    def _determine_quality_level(self, snr_db: Optional[float]) -> QualityLevel:
        """Determine quality level from SNR."""
        if snr_db is None:
            return QualityLevel.FAIR  # Unknown, assume fair

        if snr_db >= self.SNR_EXCELLENT:
            return QualityLevel.EXCELLENT
        elif snr_db >= self.SNR_GOOD:
            return QualityLevel.GOOD
        elif snr_db >= self.SNR_FAIR:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR

    def _generate_warnings(
        self,
        snr_db: Optional[float],
        sample_rate: int,
        duration: float
    ) -> List[str]:
        """Generate warnings based on audio metrics."""
        warnings = []

        # SNR warnings
        if snr_db is not None:
            if snr_db < self.SNR_FAIR:
                warnings.append(
                    f"Low audio quality detected (SNR: {snr_db:.1f}dB). "
                    "Transcription accuracy may be reduced."
                )
            elif snr_db < self.SNR_GOOD:
                warnings.append(
                    f"Moderate background noise detected (SNR: {snr_db:.1f}dB). "
                    "Consider using noise reduction if accuracy is critical."
                )

        # Sample rate warnings
        if sample_rate < self.MIN_SAMPLE_RATE:
            warnings.append(
                f"Low sample rate ({sample_rate}Hz) may affect transcription quality. "
                f"Recommended: {self.MIN_SAMPLE_RATE}Hz or higher."
            )
        elif sample_rate < self.OPTIMAL_SAMPLE_RATE:
            warnings.append(
                f"Sample rate ({sample_rate}Hz) is below optimal. "
                f"For best results, use {self.OPTIMAL_SAMPLE_RATE}Hz."
            )

        # Duration warnings
        if duration < 1.0:
            warnings.append(
                "Very short audio (<1 second) may not transcribe reliably."
            )
        elif duration > 7200:  # 2 hours
            warnings.append(
                f"Long audio file ({duration/60:.0f} minutes). "
                "Consider using --preset quick for faster processing or splitting into smaller segments."
            )

        return warnings

    def _generate_recommendations(
        self,
        quality_level: QualityLevel,
        snr_db: Optional[float],
        sample_rate: int,
        duration: float
    ) -> List[str]:
        """Generate recommendations based on quality analysis."""
        recommendations = []

        # Model recommendations based on quality
        if quality_level == QualityLevel.POOR:
            recommendations.append(
                "Use larger model (medium or large) to compensate for audio quality issues"
            )
            recommendations.append(
                "Enable proofreading with --proofread for better accuracy"
            )
        elif quality_level == QualityLevel.FAIR:
            recommendations.append(
                "Use medium model for good balance of speed and accuracy"
            )
        elif quality_level == QualityLevel.EXCELLENT:
            recommendations.append(
                "Audio quality is excellent - small or base model may be sufficient"
            )

        # Sample rate recommendations
        if sample_rate < self.OPTIMAL_SAMPLE_RATE:
            recommendations.append(
                "Consider re-recording with higher sample rate for better quality"
            )

        # Duration-based recommendations
        if duration > 3600:  # 1 hour
            recommendations.append(
                "For long files, consider using batch processing to split audio"
            )

        # SNR-specific recommendations
        if snr_db is not None and snr_db < self.SNR_GOOD:
            recommendations.append(
                "Apply noise reduction preprocessing for better transcription accuracy"
            )

        return recommendations

    def _recommend_model(self, quality_level: QualityLevel, duration: float) -> str:
        """
        Recommend optimal Whisper model size.

        Args:
            quality_level: Determined audio quality level
            duration: Audio duration in seconds

        Returns:
            Recommended model size (tiny, base, small, medium, large)
        """
        # Very short audio - use smaller model
        if duration < 30:
            return "base"

        # Quality-based recommendations
        if quality_level == QualityLevel.POOR:
            return "large"  # Need accuracy to overcome quality issues
        elif quality_level == QualityLevel.FAIR:
            return "medium"  # Balance of speed and accuracy
        elif quality_level == QualityLevel.GOOD:
            # Duration matters more at good quality
            if duration > 1800:  # 30 minutes
                return "small"  # Faster for long files
            else:
                return "medium"
        else:  # EXCELLENT
            # Can use smaller model
            if duration > 1800:
                return "small"
            else:
                return "medium"

    def print_analysis(self, result: AudioQualityResult):
        """
        Print formatted analysis results.

        Args:
            result: AudioQualityResult to display
        """
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            console = Console()

            # Create analysis table
            table = Table(title="Audio Quality Analysis", show_header=False)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")

            # Quality level with color
            quality_colors = {
                QualityLevel.EXCELLENT: "green",
                QualityLevel.GOOD: "green",
                QualityLevel.FAIR: "yellow",
                QualityLevel.POOR: "red",
            }
            quality_color = quality_colors[result.quality_level]
            table.add_row(
                "Quality Level",
                f"[{quality_color}]{result.quality_level.value.upper()}[/{quality_color}]"
            )

            # SNR
            if result.snr_db is not None:
                table.add_row("Signal-to-Noise Ratio", f"{result.snr_db:.1f} dB")

            # Sample rate
            table.add_row("Sample Rate", f"{result.sample_rate} Hz")

            # Duration
            duration_str = f"{int(result.duration_seconds // 60)}m {int(result.duration_seconds % 60)}s"
            table.add_row("Duration", duration_str)

            # Channels
            table.add_row("Channels", str(result.channels))

            # Recommended model
            table.add_row("Recommended Model", result.optimal_model)

            console.print(table)

            # Warnings
            if result.warnings:
                console.print("\n[bold yellow]⚠️  Warnings:[/bold yellow]")
                for warning in result.warnings:
                    console.print(f"  • {warning}")

            # Recommendations
            if result.recommendations:
                console.print("\n[bold cyan]💡 Recommendations:[/bold cyan]")
                for rec in result.recommendations:
                    console.print(f"  • {rec}")

        except ImportError:
            # Fallback without Rich
            print("\n=== Audio Quality Analysis ===")
            print(f"Quality Level: {result.quality_level.value.upper()}")
            if result.snr_db:
                print(f"SNR: {result.snr_db:.1f} dB")
            print(f"Sample Rate: {result.sample_rate} Hz")
            print(f"Duration: {result.duration_seconds:.1f}s")
            print(f"Recommended Model: {result.optimal_model}")

            if result.warnings:
                print("\nWarnings:")
                for warning in result.warnings:
                    print(f"  • {warning}")

            if result.recommendations:
                print("\nRecommendations:")
                for rec in result.recommendations:
                    print(f"  • {rec}")


def analyze_audio_quality(audio_path: Path) -> AudioQualityResult:
    """
    Convenience function to analyze audio quality.

    Args:
        audio_path: Path to audio file

    Returns:
        AudioQualityResult with analysis
    """
    analyzer = AudioQualityAnalyzer()
    return analyzer.analyze(audio_path)
