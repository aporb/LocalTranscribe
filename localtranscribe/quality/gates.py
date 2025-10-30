"""
Quality assessment and gating for pipeline stages.

Implements quality gates to identify issues and trigger re-processing when needed.
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class QualitySeverity(Enum):
    """Severity levels for quality issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QualityThresholds:
    """Configurable quality thresholds for assessment."""

    # Diarization thresholds
    max_micro_segment_ratio: float = 0.15  # Max 15% micro-segments (<0.5s)
    min_avg_segment_duration: float = 2.0  # Min 2s average segment duration
    max_speaker_switches_per_minute: float = 8.0  # Max speaker switches per minute

    # Transcription thresholds
    min_avg_confidence: float = 0.7  # Min average confidence score
    max_no_speech_prob: float = 0.3  # Max no-speech probability
    max_compression_ratio: float = 2.5  # Max compression ratio

    # Combination thresholds
    min_speaker_mapping_confidence: float = 0.6  # Min speaker mapping confidence
    max_ambiguous_segments_ratio: float = 0.1  # Max 10% ambiguous segments


@dataclass
class QualityIssue:
    """Single quality issue detected during assessment."""

    severity: QualitySeverity
    message: str
    suggestion: str
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None


@dataclass
class QualityAssessment:
    """Quality assessment result for a pipeline stage."""

    stage: str
    overall_score: float  # 0-1 scale
    passed: bool
    issues: List[QualityIssue] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_critical_issues(self) -> List[QualityIssue]:
        """Get only critical issues."""
        return [i for i in self.issues if i.severity == QualitySeverity.CRITICAL]

    def get_high_issues(self) -> List[QualityIssue]:
        """Get high and critical issues."""
        return [i for i in self.issues if i.severity in [QualitySeverity.HIGH, QualitySeverity.CRITICAL]]

    def has_blocking_issues(self) -> bool:
        """Check if there are any blocking (critical) issues."""
        return len(self.get_critical_issues()) > 0


@dataclass
class ReprocessDecision:
    """Decision on whether and how to reprocess."""

    should_reprocess: bool
    reason: str
    strategy: Optional[str] = None  # 'use_better_model', 'apply_postprocessing', etc.
    suggested_model: Optional[str] = None
    suggested_processing: List[str] = field(default_factory=list)


class QualityGate:
    """
    Quality assessment and gating for pipeline stages.

    Implements quality gates to identify issues early and recommend
    improvements or re-processing.
    """

    def __init__(self, thresholds: Optional[QualityThresholds] = None, verbose: bool = False):
        """
        Initialize quality gate.

        Args:
            thresholds: Custom quality thresholds (defaults if None)
            verbose: Enable verbose output
        """
        self.thresholds = thresholds or QualityThresholds()
        self.verbose = verbose

    def assess_diarization_quality(self, diarization_result) -> QualityAssessment:
        """
        Assess quality of diarization output.

        Args:
            diarization_result: DiarizationResult object

        Returns:
            QualityAssessment with quality metrics and issues
        """
        issues = []
        metrics = {}
        recommendations = []

        # Extract segments
        segments = diarization_result.segments
        total_segments = len(segments)

        if total_segments == 0:
            return QualityAssessment(
                stage='diarization',
                overall_score=0.0,
                passed=False,
                issues=[QualityIssue(
                    severity=QualitySeverity.CRITICAL,
                    message="No segments detected",
                    suggestion="Check audio file contains speech"
                )],
                recommendations=["Verify audio file is not empty", "Check audio quality"]
            )

        # 1. Check micro-segment ratio
        micro_segments = sum(1 for s in segments if s.get('duration', 0) < 0.5)
        micro_ratio = micro_segments / total_segments
        metrics['micro_segment_ratio'] = micro_ratio
        metrics['micro_segment_count'] = micro_segments

        if micro_ratio > self.thresholds.max_micro_segment_ratio:
            severity = QualitySeverity.HIGH if micro_ratio > 0.25 else QualitySeverity.MEDIUM
            issues.append(QualityIssue(
                severity=severity,
                message=f'High micro-segment ratio: {micro_ratio:.1%}',
                suggestion='Apply segment post-processing to merge short segments',
                metric_name='micro_segment_ratio',
                metric_value=micro_ratio,
                threshold_value=self.thresholds.max_micro_segment_ratio
            ))
            recommendations.append("Enable segment post-processing")

        # 2. Check average segment duration
        avg_duration = np.mean([s.get('duration', 0) for s in segments])
        metrics['avg_segment_duration'] = avg_duration

        if avg_duration < self.thresholds.min_avg_segment_duration:
            issues.append(QualityIssue(
                severity=QualitySeverity.MEDIUM,
                message=f'Short average segment duration: {avg_duration:.2f}s',
                suggestion='May indicate over-segmentation, apply smoothing',
                metric_name='avg_segment_duration',
                metric_value=avg_duration,
                threshold_value=self.thresholds.min_avg_segment_duration
            ))
            recommendations.append("Apply temporal smoothing to reduce fragmentation")

        # 3. Check speaker switch rate
        switches = self._count_speaker_switches(segments)
        duration = diarization_result.processing_time if hasattr(diarization_result, 'processing_time') else 60
        # Estimate actual audio duration from segments
        if segments:
            duration = max(s.get('end', 0) for s in segments)

        switch_rate = switches / (duration / 60) if duration > 0 else 0  # switches per minute
        metrics['speaker_switches_per_minute'] = switch_rate
        metrics['total_speaker_switches'] = switches

        if switch_rate > self.thresholds.max_speaker_switches_per_minute:
            issues.append(QualityIssue(
                severity=QualitySeverity.HIGH,
                message=f'High speaker switch rate: {switch_rate:.1f}/min',
                suggestion='Likely over-segmentation, apply smoothing and merging',
                metric_name='speaker_switches_per_minute',
                metric_value=switch_rate,
                threshold_value=self.thresholds.max_speaker_switches_per_minute
            ))
            recommendations.append("Increase merge_gap_threshold in segment processing")

        # 4. Check speaker distribution
        speaker_durations = diarization_result.speaker_durations
        if speaker_durations:
            total_duration = sum(speaker_durations.values())
            speaker_percentages = {
                spk: (dur / total_duration) * 100
                for spk, dur in speaker_durations.items()
            }

            # Check for severely imbalanced speakers (one speaker < 5%)
            min_percentage = min(speaker_percentages.values())
            metrics['min_speaker_percentage'] = min_percentage

            if min_percentage < 5.0 and len(speaker_percentages) > 2:
                issues.append(QualityIssue(
                    severity=QualitySeverity.LOW,
                    message=f'Imbalanced speaker distribution (min: {min_percentage:.1f}%)',
                    suggestion='Some speakers may be incorrectly merged or split',
                    metric_name='min_speaker_percentage',
                    metric_value=min_percentage
                ))

        # Calculate overall score
        score_components = []

        # Micro-segment score (30%)
        micro_score = 1.0 - min(1.0, micro_ratio / 0.3)
        score_components.append(micro_score * 0.3)

        # Average duration score (30%)
        duration_score = min(1.0, avg_duration / 3.0)  # Normalize to 3s
        score_components.append(duration_score * 0.3)

        # Switch rate score (30%)
        switch_score = 1.0 - min(1.0, switch_rate / 15.0)  # Normalize to 15/min
        score_components.append(switch_score * 0.3)

        # Issue penalty (10%)
        critical_count = len([i for i in issues if i.severity == QualitySeverity.CRITICAL])
        high_count = len([i for i in issues if i.severity == QualitySeverity.HIGH])
        issue_score = 1.0 - (critical_count * 0.3 + high_count * 0.1)
        score_components.append(max(0, issue_score) * 0.1)

        overall_score = sum(score_components)

        # Determine if passed
        passed = overall_score >= 0.7 and critical_count == 0

        return QualityAssessment(
            stage='diarization',
            overall_score=overall_score,
            passed=passed,
            issues=issues,
            metrics=metrics,
            recommendations=recommendations,
            metadata={
                'total_segments': total_segments,
                'num_speakers': diarization_result.num_speakers
            }
        )

    def assess_transcription_quality(self, transcription_result) -> QualityAssessment:
        """
        Assess quality of transcription output.

        Args:
            transcription_result: TranscriptionResult object

        Returns:
            QualityAssessment with quality metrics and issues
        """
        issues = []
        metrics = {}
        recommendations = []

        segments = transcription_result.segments
        if not segments:
            return QualityAssessment(
                stage='transcription',
                overall_score=0.0,
                passed=False,
                issues=[QualityIssue(
                    severity=QualitySeverity.CRITICAL,
                    message="No transcription segments",
                    suggestion="Check if audio contains speech"
                )]
            )

        # 1. Check average confidence (if available)
        confidences = []
        no_speech_probs = []
        compression_ratios = []

        for seg in segments:
            if hasattr(seg, 'avg_logprob'):
                # Convert logprob to approximate confidence
                confidence = np.exp(seg.avg_logprob) if seg.avg_logprob > -10 else 0.0
                confidences.append(confidence)

            if hasattr(seg, 'no_speech_prob'):
                no_speech_probs.append(seg.no_speech_prob)

            if hasattr(seg, 'compression_ratio'):
                compression_ratios.append(seg.compression_ratio)

        if confidences:
            avg_confidence = np.mean(confidences)
            metrics['avg_confidence'] = avg_confidence

            if avg_confidence < self.thresholds.min_avg_confidence:
                issues.append(QualityIssue(
                    severity=QualitySeverity.MEDIUM,
                    message=f'Low average confidence: {avg_confidence:.2f}',
                    suggestion='Consider using larger model or checking audio quality',
                    metric_name='avg_confidence',
                    metric_value=avg_confidence,
                    threshold_value=self.thresholds.min_avg_confidence
                ))
                recommendations.append("Use larger Whisper model (e.g., medium or large)")

        # 2. Check no-speech probability
        if no_speech_probs:
            avg_no_speech = np.mean(no_speech_probs)
            metrics['avg_no_speech_prob'] = avg_no_speech

            if avg_no_speech > self.thresholds.max_no_speech_prob:
                issues.append(QualityIssue(
                    severity=QualitySeverity.HIGH,
                    message=f'High no-speech probability: {avg_no_speech:.2f}',
                    suggestion='Audio may not contain clear speech',
                    metric_name='avg_no_speech_prob',
                    metric_value=avg_no_speech,
                    threshold_value=self.thresholds.max_no_speech_prob
                ))
                recommendations.append("Verify audio quality and speech content")

        # 3. Check compression ratio
        if compression_ratios:
            avg_compression = np.mean(compression_ratios)
            metrics['avg_compression_ratio'] = avg_compression

            if avg_compression > self.thresholds.max_compression_ratio:
                issues.append(QualityIssue(
                    severity=QualitySeverity.MEDIUM,
                    message=f'High compression ratio: {avg_compression:.2f}',
                    suggestion='May indicate repetitive or problematic transcription',
                    metric_name='avg_compression_ratio',
                    metric_value=avg_compression,
                    threshold_value=self.thresholds.max_compression_ratio
                ))
                recommendations.append("Review transcription for repetitions")

        # 4. Check segment count and duration
        total_segments = len(segments)
        avg_segment_duration = np.mean([s.end - s.start for s in segments])
        metrics['total_segments'] = total_segments
        metrics['avg_segment_duration'] = avg_segment_duration

        # Very short segments may indicate issues
        if avg_segment_duration < 1.0:
            issues.append(QualityIssue(
                severity=QualitySeverity.LOW,
                message=f'Very short average segments: {avg_segment_duration:.2f}s',
                suggestion='May make speaker mapping more difficult'
            ))

        # Calculate overall score
        score_components = []

        # Confidence score (40%)
        if confidences:
            conf_score = avg_confidence / self.thresholds.min_avg_confidence
            score_components.append(min(1.0, conf_score) * 0.4)
        else:
            score_components.append(0.7 * 0.4)  # Neutral score if no confidence

        # No-speech score (30%)
        if no_speech_probs:
            no_speech_score = 1.0 - (avg_no_speech / self.thresholds.max_no_speech_prob)
            score_components.append(max(0, min(1.0, no_speech_score)) * 0.3)
        else:
            score_components.append(0.8 * 0.3)

        # Compression score (20%)
        if compression_ratios:
            comp_score = 1.0 - max(0, (avg_compression - 1.5) / self.thresholds.max_compression_ratio)
            score_components.append(max(0, min(1.0, comp_score)) * 0.2)
        else:
            score_components.append(0.8 * 0.2)

        # Issue penalty (10%)
        critical_count = len([i for i in issues if i.severity == QualitySeverity.CRITICAL])
        high_count = len([i for i in issues if i.severity == QualitySeverity.HIGH])
        issue_score = 1.0 - (critical_count * 0.3 + high_count * 0.1)
        score_components.append(max(0, issue_score) * 0.1)

        overall_score = sum(score_components)
        passed = overall_score >= 0.7 and critical_count == 0

        return QualityAssessment(
            stage='transcription',
            overall_score=overall_score,
            passed=passed,
            issues=issues,
            metrics=metrics,
            recommendations=recommendations,
            metadata={
                'total_segments': total_segments,
                'language': transcription_result.language
            }
        )

    def assess_combination_quality(self, combination_result) -> QualityAssessment:
        """
        Assess quality of speaker-text mapping.

        Args:
            combination_result: CombinationResult object

        Returns:
            QualityAssessment with quality metrics and issues
        """
        issues = []
        metrics = {}
        recommendations = []

        segments = combination_result.segments
        if not segments:
            return QualityAssessment(
                stage='combination',
                overall_score=0.0,
                passed=False,
                issues=[QualityIssue(
                    severity=QualitySeverity.CRITICAL,
                    message="No combined segments",
                    suggestion="Check diarization and transcription results"
                )]
            )

        # 1. Check speaker mapping confidence (if available)
        confidences = []
        for seg in segments:
            if hasattr(seg, 'confidence'):
                confidences.append(seg.confidence)

        if confidences:
            avg_confidence = np.mean(confidences)
            metrics['avg_speaker_mapping_confidence'] = avg_confidence

            if avg_confidence < self.thresholds.min_speaker_mapping_confidence:
                issues.append(QualityIssue(
                    severity=QualitySeverity.HIGH,
                    message=f'Low speaker mapping confidence: {avg_confidence:.2f}',
                    suggestion='Speaker assignments may be unreliable',
                    metric_name='avg_speaker_mapping_confidence',
                    metric_value=avg_confidence,
                    threshold_value=self.thresholds.min_speaker_mapping_confidence
                ))
                recommendations.append("Review speaker assignments manually")
                recommendations.append("Enable enhanced speaker mapping features")

        # 2. Check for ambiguous segments
        low_conf_segments = sum(1 for c in confidences if c < 0.5) if confidences else 0
        ambiguous_ratio = low_conf_segments / len(segments) if segments else 0
        metrics['ambiguous_segments_ratio'] = ambiguous_ratio

        if ambiguous_ratio > self.thresholds.max_ambiguous_segments_ratio:
            issues.append(QualityIssue(
                severity=QualitySeverity.MEDIUM,
                message=f'High ambiguous segments ratio: {ambiguous_ratio:.1%}',
                suggestion='Many segments have low confidence speaker assignments',
                metric_name='ambiguous_segments_ratio',
                metric_value=ambiguous_ratio,
                threshold_value=self.thresholds.max_ambiguous_segments_ratio
            ))
            recommendations.append("Review ambiguous segments")

        # 3. Check speaker distribution in combined result
        speaker_counts = {}
        for seg in segments:
            speaker = seg.speaker if hasattr(seg, 'speaker') else getattr(seg, 'speaker', 'UNKNOWN')
            speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1

        metrics['num_speakers'] = len(speaker_counts)

        # 4. Check for rapid speaker alternation in combined segments
        rapid_switches = 0
        for i in range(1, len(segments)):
            prev_seg = segments[i-1]
            curr_seg = segments[i]

            prev_speaker = prev_seg.speaker if hasattr(prev_seg, 'speaker') else getattr(prev_seg, 'speaker', '')
            curr_speaker = curr_seg.speaker if hasattr(curr_seg, 'speaker') else getattr(curr_seg, 'speaker', '')
            prev_end = prev_seg.end if hasattr(prev_seg, 'end') else 0
            curr_start = curr_seg.start if hasattr(curr_seg, 'start') else 0

            if prev_speaker != curr_speaker and (curr_start - prev_end) < 0.5:
                rapid_switches += 1

        rapid_switch_ratio = rapid_switches / len(segments) if segments else 0
        metrics['rapid_switch_ratio'] = rapid_switch_ratio

        if rapid_switch_ratio > 0.15:  # More than 15% rapid switches
            issues.append(QualityIssue(
                severity=QualitySeverity.MEDIUM,
                message=f'High rapid speaker switch ratio: {rapid_switch_ratio:.1%}',
                suggestion='May indicate speaker mapping issues',
                metric_name='rapid_switch_ratio',
                metric_value=rapid_switch_ratio
            ))

        # Calculate overall score
        score_components = []

        # Confidence score (50%)
        if confidences:
            conf_score = avg_confidence / self.thresholds.min_speaker_mapping_confidence
            score_components.append(min(1.0, conf_score) * 0.5)
        else:
            score_components.append(0.7 * 0.5)  # Neutral if no confidence

        # Ambiguous segments score (30%)
        amb_score = 1.0 - (ambiguous_ratio / self.thresholds.max_ambiguous_segments_ratio)
        score_components.append(max(0, min(1.0, amb_score)) * 0.3)

        # Rapid switches score (10%)
        switch_score = 1.0 - rapid_switch_ratio
        score_components.append(max(0, switch_score) * 0.1)

        # Issue penalty (10%)
        critical_count = len([i for i in issues if i.severity == QualitySeverity.CRITICAL])
        high_count = len([i for i in issues if i.severity == QualitySeverity.HIGH])
        issue_score = 1.0 - (critical_count * 0.3 + high_count * 0.1)
        score_components.append(max(0, issue_score) * 0.1)

        overall_score = sum(score_components)
        passed = overall_score >= 0.7 and critical_count == 0

        return QualityAssessment(
            stage='combination',
            overall_score=overall_score,
            passed=passed,
            issues=issues,
            metrics=metrics,
            recommendations=recommendations,
            metadata={
                'total_segments': len(segments),
                'num_speakers': len(speaker_counts)
            }
        )

    def should_reprocess(self, assessment: QualityAssessment) -> ReprocessDecision:
        """
        Determine if and how to reprocess based on quality assessment.

        Args:
            assessment: QualityAssessment result

        Returns:
            ReprocessDecision with recommendations
        """
        if assessment.overall_score >= 0.85:
            return ReprocessDecision(
                should_reprocess=False,
                reason='Quality acceptable (score: {:.2f})'.format(assessment.overall_score)
            )

        if assessment.overall_score < 0.4:
            return ReprocessDecision(
                should_reprocess=True,
                strategy='use_better_model',
                suggested_model='large',
                reason='Quality too low (score: {:.2f}), recommend better model'.format(assessment.overall_score)
            )

        if assessment.overall_score < 0.7:
            # Determine strategy based on issues
            suggested_processing = []

            for issue in assessment.issues:
                if 'micro-segment' in issue.message.lower():
                    suggested_processing.append('segment_filtering')
                if 'switch' in issue.message.lower():
                    suggested_processing.append('temporal_smoothing')
                if 'confidence' in issue.message.lower():
                    suggested_processing.append('enhanced_mapping')

            if not suggested_processing:
                suggested_processing = ['post_processing']

            return ReprocessDecision(
                should_reprocess=True,
                strategy='apply_postprocessing',
                suggested_processing=suggested_processing,
                reason='Quality marginal (score: {:.2f}), apply post-processing'.format(assessment.overall_score)
            )

        return ReprocessDecision(
            should_reprocess=False,
            reason='Quality adequate (score: {:.2f})'.format(assessment.overall_score)
        )

    def generate_quality_report(
        self,
        assessments: Dict[str, QualityAssessment],
        audio_analysis: Optional[Any] = None
    ) -> str:
        """
        Generate comprehensive quality report.

        Args:
            assessments: Dictionary of stage name to QualityAssessment
            audio_analysis: Optional AudioAnalysisResult

        Returns:
            Formatted quality report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("QUALITY ASSESSMENT REPORT")
        lines.append("=" * 70)

        # Audio analysis section
        if audio_analysis:
            lines.append("\n📊 AUDIO ANALYSIS")
            lines.append("-" * 70)
            lines.append(f"  Duration: {audio_analysis.duration:.1f}s ({audio_analysis.duration_bucket.value})")
            lines.append(f"  Quality Level: {audio_analysis.quality_level.value}")
            if audio_analysis.snr_db:
                lines.append(f"  SNR: {audio_analysis.snr_db:.1f} dB")
            lines.append(f"  Overall Score: {audio_analysis.overall_quality_score:.2f}")

            if audio_analysis.quality_issues:
                lines.append("\n  Issues:")
                for issue in audio_analysis.quality_issues[:3]:  # Top 3
                    lines.append(f"    • {issue}")

            if audio_analysis.recommended_preprocessing:
                lines.append("\n  Recommended Preprocessing:")
                for prep in audio_analysis.recommended_preprocessing:
                    lines.append(f"    • {prep}")

        # Pipeline stage assessments
        for stage_name, assessment in assessments.items():
            lines.append(f"\n🔍 {stage_name.upper()} QUALITY")
            lines.append("-" * 70)
            lines.append(f"  Overall Score: {assessment.overall_score:.2f}/1.00")
            lines.append(f"  Status: {'✅ PASSED' if assessment.passed else '❌ FAILED'}")

            if assessment.metrics:
                lines.append("\n  Key Metrics:")
                for metric, value in sorted(assessment.metrics.items())[:5]:  # Top 5 metrics
                    if isinstance(value, float):
                        lines.append(f"    • {metric}: {value:.3f}")
                    else:
                        lines.append(f"    • {metric}: {value}")

            if assessment.issues:
                lines.append("\n  Issues:")
                for issue in assessment.issues[:5]:  # Top 5 issues
                    severity_icon = {
                        QualitySeverity.CRITICAL: "🔴",
                        QualitySeverity.HIGH: "🟠",
                        QualitySeverity.MEDIUM: "🟡",
                        QualitySeverity.LOW: "🟢"
                    }.get(issue.severity, "⚪")
                    lines.append(f"    {severity_icon} [{issue.severity.value.upper()}] {issue.message}")
                    lines.append(f"       → {issue.suggestion}")

            if assessment.recommendations:
                lines.append("\n  Recommendations:")
                for rec in assessment.recommendations[:3]:  # Top 3 recommendations
                    lines.append(f"    • {rec}")

        # Overall summary
        lines.append("\n" + "=" * 70)
        lines.append("SUMMARY")
        lines.append("=" * 70)

        overall_scores = [a.overall_score for a in assessments.values()]
        if overall_scores:
            avg_score = np.mean(overall_scores)
            lines.append(f"  Average Quality Score: {avg_score:.2f}/1.00")

            passed_count = sum(1 for a in assessments.values() if a.passed)
            total_count = len(assessments)
            lines.append(f"  Stages Passed: {passed_count}/{total_count}")

            # Overall status
            if avg_score >= 0.85:
                lines.append("\n  ✅ EXCELLENT - Processing quality is very high")
            elif avg_score >= 0.7:
                lines.append("\n  ✅ GOOD - Processing quality is acceptable")
            elif avg_score >= 0.5:
                lines.append("\n  ⚠️  FAIR - Consider reviewing results and reprocessing")
            else:
                lines.append("\n  ❌ POOR - Recommend reprocessing with better parameters")

        lines.append("=" * 70)

        return "\n".join(lines)

    def _count_speaker_switches(self, segments: List[Dict]) -> int:
        """Count number of speaker switches in segments."""
        if len(segments) < 2:
            return 0

        switches = 0
        for i in range(1, len(segments)):
            if segments[i].get('speaker') != segments[i-1].get('speaker'):
                switches += 1

        return switches
