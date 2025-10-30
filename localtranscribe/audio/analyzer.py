"""
Audio analysis module for quality assessment and parameter recommendations.

Analyzes audio characteristics including SNR, quality metrics, and provides
recommendations for optimal processing parameters.
"""

import numpy as np
import soundfile as sf
import librosa
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import warnings

# Suppress librosa warnings
warnings.filterwarnings("ignore", category=UserWarning, module="librosa")


class AudioQualityLevel(Enum):
    """Audio quality classification based on SNR."""
    EXCELLENT = "excellent"  # > 30 dB SNR
    HIGH = "high"           # 25-30 dB SNR
    MEDIUM = "medium"       # 15-25 dB SNR
    LOW = "low"             # 10-15 dB SNR
    POOR = "poor"           # < 10 dB SNR


class DurationBucket(Enum):
    """Duration classification for adaptive parameter selection."""
    SHORT = "short"         # < 5 minutes
    MEDIUM = "medium"       # 5-30 minutes
    LONG = "long"           # 30-60 minutes
    VERY_LONG = "very_long" # > 60 minutes


@dataclass
class AudioAnalysisResult:
    """Comprehensive audio analysis result."""

    # Basic metrics
    duration: float
    sample_rate: int
    channels: int

    # Quality metrics
    snr_db: Optional[float] = None
    peak_amplitude: float = 0.0
    rms_level: float = 0.0
    clipping_detected: bool = False

    # Speech characteristics
    silence_ratio: float = 0.0
    speech_ratio: float = 0.0
    estimated_speakers_min: int = 1
    estimated_speakers_max: int = 4

    # Frequency analysis
    spectral_centroid_mean: float = 0.0
    spectral_rolloff_mean: float = 0.0

    # Quality assessment
    overall_quality_score: float = 0.0
    quality_level: AudioQualityLevel = AudioQualityLevel.MEDIUM
    quality_issues: List[str] = field(default_factory=list)

    # Recommendations
    recommended_preprocessing: List[str] = field(default_factory=list)
    recommended_whisper_model: str = "base"
    recommended_batch_size: int = 16
    needs_enhancement: bool = False
    duration_bucket: DurationBucket = DurationBucket.MEDIUM

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class AudioAnalyzer:
    """
    Comprehensive audio quality and characteristic analysis.

    Analyzes audio files to assess quality, detect issues, and recommend
    optimal processing parameters for transcription and diarization.
    """

    def __init__(
        self,
        target_sr: int = 16000,
        frame_length: int = 2048,
        hop_length: int = 512,
        verbose: bool = False
    ):
        """
        Initialize audio analyzer.

        Args:
            target_sr: Target sample rate for analysis
            frame_length: Frame length for spectral analysis
            hop_length: Hop length for spectral analysis
            verbose: Enable verbose output
        """
        self.target_sr = target_sr
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.verbose = verbose

    def analyze(self, audio_file: Path) -> AudioAnalysisResult:
        """
        Perform complete audio analysis.

        Args:
            audio_file: Path to audio file

        Returns:
            AudioAnalysisResult with comprehensive metrics and recommendations
        """
        if self.verbose:
            print(f"Analyzing audio file: {audio_file}")

        # Load audio
        try:
            waveform, sample_rate = sf.read(str(audio_file))

            # Convert to mono if stereo
            if len(waveform.shape) > 1:
                waveform = np.mean(waveform, axis=1)
                channels = 2
            else:
                channels = 1

            # Resample if necessary
            if sample_rate != self.target_sr:
                waveform = librosa.resample(
                    waveform,
                    orig_sr=sample_rate,
                    target_sr=self.target_sr
                )
                sample_rate = self.target_sr

        except Exception as e:
            # Return minimal result on error
            return AudioAnalysisResult(
                duration=0.0,
                sample_rate=0,
                channels=0,
                quality_issues=[f"Failed to load audio: {str(e)}"]
            )

        # Calculate duration
        duration = len(waveform) / sample_rate
        duration_bucket = self._classify_duration(duration)

        # Basic audio metrics
        peak_amplitude = float(np.max(np.abs(waveform)))
        rms_level = float(np.sqrt(np.mean(waveform**2)))
        clipping_detected = peak_amplitude > 0.99

        # Calculate SNR
        snr_db = self._calculate_snr(waveform, sample_rate)

        # Detect silence and speech ratios
        silence_ratio, speech_ratio = self._detect_silence_ratio(waveform, sample_rate)

        # Estimate speaker count (rough estimate based on spectral analysis)
        speakers_min, speakers_max = self._estimate_speaker_count(waveform, sample_rate)

        # Frequency analysis
        spectral_centroid = librosa.feature.spectral_centroid(
            y=waveform,
            sr=sample_rate,
            n_fft=self.frame_length,
            hop_length=self.hop_length
        )
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=waveform,
            sr=sample_rate,
            n_fft=self.frame_length,
            hop_length=self.hop_length
        )

        spectral_centroid_mean = float(np.mean(spectral_centroid))
        spectral_rolloff_mean = float(np.mean(spectral_rolloff))

        # Assess overall quality
        quality_score, quality_level, quality_issues = self._assess_audio_quality(
            snr_db=snr_db,
            peak_amplitude=peak_amplitude,
            rms_level=rms_level,
            clipping_detected=clipping_detected,
            silence_ratio=silence_ratio,
            speech_ratio=speech_ratio
        )

        # Generate recommendations
        preprocessing, model_size, batch_size, needs_enhancement = self._recommend_parameters(
            duration=duration,
            duration_bucket=duration_bucket,
            snr_db=snr_db,
            quality_level=quality_level,
            clipping_detected=clipping_detected,
            silence_ratio=silence_ratio,
            speech_ratio=speech_ratio
        )

        result = AudioAnalysisResult(
            duration=duration,
            sample_rate=sample_rate,
            channels=channels,
            snr_db=snr_db,
            peak_amplitude=peak_amplitude,
            rms_level=rms_level,
            clipping_detected=clipping_detected,
            silence_ratio=silence_ratio,
            speech_ratio=speech_ratio,
            estimated_speakers_min=speakers_min,
            estimated_speakers_max=speakers_max,
            spectral_centroid_mean=spectral_centroid_mean,
            spectral_rolloff_mean=spectral_rolloff_mean,
            overall_quality_score=quality_score,
            quality_level=quality_level,
            quality_issues=quality_issues,
            recommended_preprocessing=preprocessing,
            recommended_whisper_model=model_size,
            recommended_batch_size=batch_size,
            needs_enhancement=needs_enhancement,
            duration_bucket=duration_bucket,
            metadata={
                'audio_file': str(audio_file),
                'target_sr': self.target_sr
            }
        )

        if self.verbose:
            self._print_analysis_summary(result)

        return result

    def _calculate_snr(self, waveform: np.ndarray, sample_rate: int) -> Optional[float]:
        """
        Calculate Signal-to-Noise Ratio in dB.

        Uses a simple energy-based approach to estimate noise floor and signal level.

        Args:
            waveform: Audio waveform
            sample_rate: Sample rate

        Returns:
            SNR in dB, or None if calculation fails
        """
        try:
            # Split into frames
            frame_length = int(0.025 * sample_rate)  # 25ms frames
            hop_length = int(0.010 * sample_rate)    # 10ms hop

            # Calculate RMS energy for each frame
            frames = librosa.util.frame(waveform, frame_length=frame_length, hop_length=hop_length)
            frame_energies = np.sqrt(np.mean(frames**2, axis=0))

            # Assume bottom 20% of energies are noise
            noise_threshold = np.percentile(frame_energies, 20)
            noise_frames = frame_energies[frame_energies <= noise_threshold]
            signal_frames = frame_energies[frame_energies > noise_threshold]

            if len(noise_frames) == 0 or len(signal_frames) == 0:
                return None

            # Calculate average noise and signal energy
            noise_rms = np.mean(noise_frames)
            signal_rms = np.mean(signal_frames)

            # Avoid division by zero
            if noise_rms <= 0:
                return None

            # SNR in dB
            snr_db = 20 * np.log10(signal_rms / noise_rms)

            return float(snr_db)

        except Exception as e:
            if self.verbose:
                print(f"Warning: SNR calculation failed: {e}")
            return None

    def _detect_silence_ratio(self, waveform: np.ndarray, sample_rate: int) -> Tuple[float, float]:
        """
        Calculate ratio of silence to total duration.

        Args:
            waveform: Audio waveform
            sample_rate: Sample rate

        Returns:
            Tuple of (silence_ratio, speech_ratio)
        """
        try:
            # Use librosa's interval detection
            intervals = librosa.effects.split(
                waveform,
                top_db=30,  # Threshold in dB below reference
                frame_length=self.frame_length,
                hop_length=self.hop_length
            )

            # Calculate speech duration
            speech_samples = sum(end - start for start, end in intervals)
            total_samples = len(waveform)

            speech_ratio = speech_samples / total_samples if total_samples > 0 else 0.0
            silence_ratio = 1.0 - speech_ratio

            return float(silence_ratio), float(speech_ratio)

        except Exception as e:
            if self.verbose:
                print(f"Warning: Silence detection failed: {e}")
            return 0.0, 1.0

    def _estimate_speaker_count(self, waveform: np.ndarray, sample_rate: int) -> Tuple[int, int]:
        """
        Estimate minimum and maximum speaker count from spectral analysis.

        This is a rough estimate based on spectral variation.

        Args:
            waveform: Audio waveform
            sample_rate: Sample rate

        Returns:
            Tuple of (min_speakers, max_speakers)
        """
        try:
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(
                y=waveform,
                sr=sample_rate,
                n_mfcc=13,
                n_fft=self.frame_length,
                hop_length=self.hop_length
            )

            # Calculate variance across time for each coefficient
            mfcc_var = np.var(mfcc, axis=1)

            # Higher variance suggests more speaker diversity
            # This is a very rough heuristic
            avg_var = np.mean(mfcc_var)

            if avg_var < 100:
                return 1, 2
            elif avg_var < 300:
                return 2, 3
            elif avg_var < 500:
                return 2, 4
            else:
                return 3, 6

        except Exception as e:
            if self.verbose:
                print(f"Warning: Speaker estimation failed: {e}")
            return 1, 4

    def _classify_duration(self, duration: float) -> DurationBucket:
        """Classify duration into buckets."""
        if duration < 300:  # < 5 minutes
            return DurationBucket.SHORT
        elif duration < 1800:  # < 30 minutes
            return DurationBucket.MEDIUM
        elif duration < 3600:  # < 60 minutes
            return DurationBucket.LONG
        else:
            return DurationBucket.VERY_LONG

    def _assess_audio_quality(
        self,
        snr_db: Optional[float],
        peak_amplitude: float,
        rms_level: float,
        clipping_detected: bool,
        silence_ratio: float,
        speech_ratio: float
    ) -> Tuple[float, AudioQualityLevel, List[str]]:
        """
        Assess overall audio quality.

        Returns:
            Tuple of (quality_score, quality_level, issues_list)
        """
        score_components = []
        issues = []

        # SNR component (40% weight)
        if snr_db is not None:
            if snr_db > 30:
                snr_score = 1.0
            elif snr_db > 25:
                snr_score = 0.9
            elif snr_db > 20:
                snr_score = 0.8
            elif snr_db > 15:
                snr_score = 0.6
            elif snr_db > 10:
                snr_score = 0.4
            else:
                snr_score = 0.2
                issues.append(f"Low SNR: {snr_db:.1f} dB (significant background noise)")

            score_components.append(('snr', snr_score, 0.4))

        # Amplitude component (20% weight)
        if peak_amplitude < 0.1:
            amp_score = 0.3
            issues.append(f"Very low amplitude: {peak_amplitude:.2f} (may need normalization)")
        elif peak_amplitude < 0.3:
            amp_score = 0.6
            issues.append(f"Low amplitude: {peak_amplitude:.2f}")
        elif peak_amplitude > 0.99:
            amp_score = 0.4
            issues.append("Clipping detected (audio distortion)")
        else:
            amp_score = 1.0

        score_components.append(('amplitude', amp_score, 0.2))

        # Speech ratio component (30% weight)
        if speech_ratio < 0.2:
            speech_score = 0.3
            issues.append(f"Very low speech content: {speech_ratio:.1%}")
        elif speech_ratio < 0.4:
            speech_score = 0.7
        else:
            speech_score = 1.0

        score_components.append(('speech', speech_score, 0.3))

        # RMS level component (10% weight)
        if rms_level < 0.01:
            rms_score = 0.3
            issues.append(f"Very low RMS level: {rms_level:.4f}")
        elif rms_level < 0.05:
            rms_score = 0.7
        else:
            rms_score = 1.0

        score_components.append(('rms', rms_score, 0.1))

        # Calculate weighted score
        overall_score = sum(score * weight for _, score, weight in score_components)

        # Determine quality level based on SNR
        if snr_db is not None:
            if snr_db > 30:
                quality_level = AudioQualityLevel.EXCELLENT
            elif snr_db > 25:
                quality_level = AudioQualityLevel.HIGH
            elif snr_db > 15:
                quality_level = AudioQualityLevel.MEDIUM
            elif snr_db > 10:
                quality_level = AudioQualityLevel.LOW
            else:
                quality_level = AudioQualityLevel.POOR
        else:
            # Fallback to score-based classification
            if overall_score > 0.9:
                quality_level = AudioQualityLevel.EXCELLENT
            elif overall_score > 0.75:
                quality_level = AudioQualityLevel.HIGH
            elif overall_score > 0.5:
                quality_level = AudioQualityLevel.MEDIUM
            elif overall_score > 0.3:
                quality_level = AudioQualityLevel.LOW
            else:
                quality_level = AudioQualityLevel.POOR

        return float(overall_score), quality_level, issues

    def _recommend_parameters(
        self,
        duration: float,
        duration_bucket: DurationBucket,
        snr_db: Optional[float],
        quality_level: AudioQualityLevel,
        clipping_detected: bool,
        silence_ratio: float,
        speech_ratio: float
    ) -> Tuple[List[str], str, int, bool]:
        """
        Recommend optimal processing parameters.

        Returns:
            Tuple of (preprocessing_steps, model_size, batch_size, needs_enhancement)
        """
        preprocessing = []
        needs_enhancement = False

        # Model size recommendation based on duration and quality
        if duration_bucket == DurationBucket.SHORT:
            # Can afford larger model for short files
            model_size = "large-v2" if quality_level in [AudioQualityLevel.LOW, AudioQualityLevel.POOR] else "medium"
        elif duration_bucket == DurationBucket.MEDIUM:
            model_size = "medium" if quality_level in [AudioQualityLevel.LOW, AudioQualityLevel.POOR] else "base"
        else:
            # Long files need faster models
            model_size = "base"

        # Batch size recommendation
        if duration_bucket in [DurationBucket.LONG, DurationBucket.VERY_LONG]:
            batch_size = 8
        else:
            batch_size = 16

        # Preprocessing recommendations
        if clipping_detected:
            preprocessing.append("normalize_audio")
            needs_enhancement = True

        if snr_db is not None and snr_db < 15:
            preprocessing.append("noise_reduction")
            needs_enhancement = True
            # Use larger model for noisy audio
            if model_size == "base":
                model_size = "medium"

        if silence_ratio > 0.4:
            preprocessing.append("trim_silence")

        if speech_ratio < 0.3:
            preprocessing.append("voice_enhancement")
            needs_enhancement = True

        return preprocessing, model_size, batch_size, needs_enhancement

    def _print_analysis_summary(self, result: AudioAnalysisResult) -> None:
        """Print analysis summary to console."""
        print("\n=== Audio Analysis Summary ===")
        print(f"Duration: {result.duration:.1f}s ({result.duration_bucket.value})")
        print(f"Sample Rate: {result.sample_rate} Hz")
        print(f"Channels: {result.channels}")
        print(f"\nQuality Assessment:")
        print(f"  Overall Score: {result.overall_quality_score:.2f}")
        print(f"  Quality Level: {result.quality_level.value}")
        if result.snr_db:
            print(f"  SNR: {result.snr_db:.1f} dB")
        print(f"  Peak Amplitude: {result.peak_amplitude:.2f}")
        print(f"  Speech Ratio: {result.speech_ratio:.1%}")

        if result.quality_issues:
            print(f"\nQuality Issues:")
            for issue in result.quality_issues:
                print(f"  • {issue}")

        print(f"\nRecommendations:")
        print(f"  Whisper Model: {result.recommended_whisper_model}")
        print(f"  Estimated Speakers: {result.estimated_speakers_min}-{result.estimated_speakers_max}")
        if result.recommended_preprocessing:
            print(f"  Preprocessing:")
            for step in result.recommended_preprocessing:
                print(f"    • {step}")
        print("=" * 35)
