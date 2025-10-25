"""
Pipeline orchestrator that manages the complete transcription workflow.

Coordinates diarization, transcription, and combination into a single pipeline.
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from dotenv import load_dotenv

from ..core import (
    run_diarization,
    run_transcription,
    combine_results,
    DiarizationResult,
    TranscriptionResult,
    CombinationResult,
    PathResolver,
)
from ..utils.errors import (
    PipelineError,
    HuggingFaceTokenError,
    AudioFileNotFoundError,
)
from ..utils.file_safety import FileSafetyManager, OverwriteAction


class PipelineStage(Enum):
    """Pipeline execution stages."""

    VALIDATION = "validation"
    DIARIZATION = "diarization"
    TRANSCRIPTION = "transcription"
    COMBINATION = "combination"
    LABELING = "labeling"
    PROOFREADING = "proofreading"


@dataclass
class PipelineResult:
    """Complete pipeline execution result."""

    success: bool
    audio_file: Path
    total_duration: float
    stages_completed: List[str] = field(default_factory=list)
    diarization_result: Optional[DiarizationResult] = None
    transcription_result: Optional[TranscriptionResult] = None
    combination_result: Optional[CombinationResult] = None
    output_files: Dict[str, Path] = field(default_factory=dict)
    error: Optional[str] = None
    error_stage: Optional[str] = None


class PipelineOrchestrator:
    """
    Orchestrate the full transcription pipeline.

    Manages diarization, transcription, and combination in a single workflow.
    """

    def __init__(
        self,
        audio_file: Path,
        output_dir: Path,
        model_size: str = "base",
        num_speakers: Optional[int] = None,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        language: Optional[str] = None,
        implementation: str = "auto",
        skip_diarization: bool = False,
        output_formats: List[str] = ["txt", "json", "md"],
        hf_token: Optional[str] = None,
        base_dir: Optional[Path] = None,
        force_overwrite: bool = False,
        skip_existing: bool = False,
        create_backup: bool = False,
        verbose: bool = False,
        # New parameters for Phase 1
        labels_file: Optional[Path] = None,
        save_labels: Optional[Path] = None,
        enable_proofreading: bool = False,
        proofreading_rules: Optional[Path] = None,
        proofreading_level: str = "standard",
    ):
        """
        Initialize pipeline orchestrator.

        Args:
            audio_file: Path to audio file to process
            output_dir: Directory for all output files
            model_size: Whisper model size (tiny, base, small, medium, large)
            num_speakers: Exact number of speakers (if known)
            min_speakers: Minimum number of speakers
            max_speakers: Maximum number of speakers
            language: Force specific language (None for auto-detect)
            implementation: Whisper implementation (auto, mlx, faster, original)
            skip_diarization: Skip speaker diarization (transcription only)
            output_formats: Output formats for transcription
            hf_token: HuggingFace token (loads from env if None)
            base_dir: Base directory for path resolution
            force_overwrite: Force overwrite existing files without prompting
            skip_existing: Skip processing if output files already exist
            create_backup: Create backup of existing files before overwriting
            verbose: Enable verbose output
            labels_file: Path to JSON file with speaker labels
            save_labels: Path to save speaker label mappings
            enable_proofreading: Enable automatic proofreading
            proofreading_rules: Path to custom proofreading rules file
            proofreading_level: Proofreading level (minimal, standard, thorough)
        """
        self.audio_file = Path(audio_file)
        self.output_dir = Path(output_dir)
        self.model_size = model_size
        self.num_speakers = num_speakers
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.language = language
        self.implementation = implementation
        self.skip_diarization = skip_diarization
        self.output_formats = output_formats
        self.verbose = verbose

        # New features
        self.labels_file = Path(labels_file) if labels_file else None
        self.save_labels = Path(save_labels) if save_labels else None
        self.enable_proofreading = enable_proofreading
        self.proofreading_rules = Path(proofreading_rules) if proofreading_rules else None
        self.proofreading_level = proofreading_level

        # Setup console for Rich output
        self.console = Console() if RICH_AVAILABLE else None

        # Setup file safety manager
        self.file_safety = FileSafetyManager(
            force=force_overwrite,
            skip_existing=skip_existing,
            create_backup=create_backup,
            interactive=not (force_overwrite or skip_existing),
        )

        # Path resolver
        self.path_resolver = PathResolver(base_dir=base_dir)

        # Load HuggingFace token
        load_dotenv()
        self.hf_token = hf_token or os.getenv('HUGGINGFACE_TOKEN')

        # State tracking
        self.stage_results: Dict[PipelineStage, Any] = {}
        self.stage_times: Dict[PipelineStage, float] = {}

    def _print(self, message: str, style: Optional[str] = None):
        """Print message with optional Rich styling."""
        if self.console:
            self.console.print(message, style=style)
        else:
            print(message)

    def _print_panel(self, message: str, title: Optional[str] = None, style: str = "blue"):
        """Print message in a panel."""
        if self.console:
            self.console.print(Panel.fit(message, title=title, border_style=style))
        else:
            if title:
                print(f"\n{'=' * 60}")
                print(f"{title}")
                print(f"{'=' * 60}")
            print(message)
            if title:
                print(f"{'=' * 60}\n")

    def validate_prerequisites(self) -> None:
        """
        Validate all prerequisites before starting pipeline.

        Raises:
            AudioFileNotFoundError: If audio file not found
            HuggingFaceTokenError: If HF token missing (when diarization enabled)
        """
        stage_start = time.time()

        # Resolve audio file path
        try:
            self.audio_file = self.path_resolver.resolve_audio_file(self.audio_file)
            self.path_resolver.validate_audio_file(self.audio_file)
        except AudioFileNotFoundError:
            raise

        # Check HuggingFace token if diarization enabled
        if not self.skip_diarization:
            if not self.hf_token or self.hf_token == "your_token_here":
                raise HuggingFaceTokenError(
                    "HuggingFace token not found or invalid",
                    suggestions=[
                        "Add token to .env file: HUGGINGFACE_TOKEN=your_token",
                        "Get token from: https://huggingface.co/settings/tokens",
                        "Accept model license at: https://huggingface.co/pyannote/speaker-diarization-3.1",
                        "Or skip diarization with --skip-diarization flag",
                    ],
                    context={'env_file': '.env'},
                )

        # Ensure output directory exists
        self.output_dir = self.path_resolver.ensure_directory(self.output_dir)

        # Check for existing output files
        base_name = self.audio_file.stem
        potential_outputs = [
            self.output_dir / f"{base_name}_diarization.md",
            self.output_dir / f"{base_name}_transcript.txt",
            self.output_dir / f"{base_name}_transcript.json",
            self.output_dir / f"{base_name}_transcript.md",
            self.output_dir / f"{base_name}_combined.md",
        ]

        existing_files = [f for f in potential_outputs if f.exists()]
        if existing_files and self.file_safety.skip_existing:
            files_list = "\n  • ".join(str(f.name) for f in existing_files)
            raise PipelineError(
                f"Output files already exist:\n  • {files_list}",
                suggestions=[
                    "Use --force to overwrite existing files",
                    "Use --backup to create backups before overwriting",
                    "Specify a different output directory",
                    "Rename or move existing files",
                ],
                context={"existing_files": [str(f) for f in existing_files]},
            )

        self.stage_times[PipelineStage.VALIDATION] = time.time() - stage_start

        if self.verbose:
            self._print("✅ Prerequisites validated", style="green")

    def run_diarization_stage(self) -> DiarizationResult:
        """Run speaker diarization stage."""
        stage_start = time.time()

        self._print("\n[bold]Stage 1/3: Speaker Diarization[/bold]" if self.console else "\n=== Stage 1/3: Speaker Diarization ===")

        try:
            result = run_diarization(
                audio_file=self.audio_file,
                hf_token=self.hf_token,
                output_dir=self.output_dir,
                num_speakers=self.num_speakers,
                min_speakers=self.min_speakers,
                max_speakers=self.max_speakers,
            )

            self.stage_times[PipelineStage.DIARIZATION] = time.time() - stage_start

            if self.verbose:
                self._print(
                    f"✅ Diarization complete: {result.num_speakers} speakers found ({result.processing_time:.1f}s)",
                    style="green",
                )

            return result

        except Exception as e:
            self.stage_times[PipelineStage.DIARIZATION] = time.time() - stage_start
            raise

    def run_transcription_stage(self) -> TranscriptionResult:
        """Run speech-to-text transcription stage."""
        stage_start = time.time()

        stage_num = "1/2" if self.skip_diarization else "2/3"
        self._print(f"\n[bold]Stage {stage_num}: Speech-to-Text Transcription[/bold]" if self.console else f"\n=== Stage {stage_num}: Transcription ===")

        try:
            result = run_transcription(
                audio_file=self.audio_file,
                output_dir=self.output_dir,
                model_size=self.model_size,
                language=self.language,
                implementation=self.implementation,
                output_formats=self.output_formats,
            )

            self.stage_times[PipelineStage.TRANSCRIPTION] = time.time() - stage_start

            if self.verbose:
                self._print(
                    f"✅ Transcription complete: {result.language} detected ({result.processing_time:.1f}s)",
                    style="green",
                )

            return result

        except Exception as e:
            self.stage_times[PipelineStage.TRANSCRIPTION] = time.time() - stage_start
            raise

    def run_combination_stage(
        self, diarization_result: DiarizationResult, transcription_result: TranscriptionResult
    ) -> CombinationResult:
        """Run combination stage to merge diarization and transcription."""
        stage_start = time.time()

        self._print("\n[bold]Stage 3/3: Combining Results[/bold]" if self.console else "\n=== Stage 3/3: Combining Results ===")

        try:
            result = combine_results(
                diarization_result=diarization_result,
                transcription_result=transcription_result,
                output_dir=self.output_dir,
                save_markdown=True,
                include_confidence=True,
            )

            self.stage_times[PipelineStage.COMBINATION] = time.time() - stage_start

            if self.verbose:
                self._print(
                    f"✅ Combination complete: {result.num_speakers} speakers mapped to {len(result.segments)} segments",
                    style="green",
                )

            return result

        except Exception as e:
            self.stage_times[PipelineStage.COMBINATION] = time.time() - stage_start
            raise

    def run_labeling_stage(self, output_file: Path) -> Path:
        """Run speaker labeling stage to replace speaker IDs with names."""
        from ..labels import SpeakerLabelManager

        stage_start = time.time()

        self._print("\n[bold]Speaker Labeling[/bold]" if self.console else "\n=== Speaker Labeling ===")

        try:
            # Initialize label manager
            manager = SpeakerLabelManager()

            # Load labels from file
            if self.labels_file and self.labels_file.exists():
                manager.load_labels(self.labels_file)
                if self.verbose:
                    self._print(f"Loaded labels from: {self.labels_file}", style="cyan")

            # Read the output file
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Detect speakers if saving labels
            if self.save_labels:
                speakers = manager.detect_speakers(content)
                if self.verbose:
                    self._print(f"Detected {len(speakers)} speakers", style="cyan")

            # Apply labels
            labeled_content = manager.apply_labels(content)

            # Save labeled version
            labeled_file = output_file.with_stem(output_file.stem + "_labeled")
            with open(labeled_file, "w", encoding="utf-8") as f:
                f.write(labeled_content)

            # Save label mappings if requested
            if self.save_labels and manager.labels:
                manager.save_labels(self.save_labels)

            self.stage_times[PipelineStage.LABELING] = time.time() - stage_start

            if self.verbose:
                self._print(
                    f"✅ Labeling complete: Applied {len(manager.labels)} speaker labels ({time.time() - stage_start:.1f}s)",
                    style="green",
                )

            return labeled_file

        except Exception as e:
            self.stage_times[PipelineStage.LABELING] = time.time() - stage_start
            raise

    def run_proofreading_stage(self, input_file: Path) -> Path:
        """Run proofreading stage to fix common transcription errors."""
        from ..proofreading import Proofreader, ProofreadingLevel

        stage_start = time.time()

        self._print("\n[bold]Proofreading Transcript[/bold]" if self.console else "\n=== Proofreading ===")

        try:
            # Initialize proofreader
            proofreader = Proofreader(
                level=ProofreadingLevel(self.proofreading_level),
                track_changes=self.verbose,
                verbose=self.verbose
            )

            # Load custom rules if provided
            if self.proofreading_rules and self.proofreading_rules.exists():
                proofreader.load_rules_from_file(self.proofreading_rules)
                if self.verbose:
                    self._print(f"Loaded custom rules from: {self.proofreading_rules}", style="cyan")

            # Proofread the file
            result = proofreader.proofread_file(
                input_path=input_file,
                output_path=None,  # Will create _proofread version
                create_backup=False
            )

            self.stage_times[PipelineStage.PROOFREADING] = time.time() - stage_start

            if result.success and result.has_changes:
                output_file = input_file.with_stem(input_file.stem + "_proofread")
                if self.verbose:
                    self._print(
                        f"✅ Proofreading complete: {result.total_changes} corrections made ({result.processing_time:.1f}s)",
                        style="green",
                    )
                    # Show summary
                    self._print(result.get_summary(), style="dim")

                return output_file
            else:
                if self.verbose:
                    self._print("✅ Proofreading complete: No corrections needed", style="green")
                return input_file

        except Exception as e:
            self.stage_times[PipelineStage.PROOFREADING] = time.time() - stage_start
            if self.verbose:
                self._print(f"⚠️  Proofreading failed: {e}", style="yellow")
            # Return original file if proofreading fails
            return input_file

    def run(self) -> PipelineResult:
        """
        Execute complete pipeline.

        Returns:
            PipelineResult with all stage results and output files
        """
        total_start = time.time()
        stages_completed = []

        # Print header
        self._print_panel(
            f"🎙️ LocalTranscribe Pipeline\n\nAudio: {self.audio_file.name}\nOutput: {self.output_dir}",
            title="Pipeline Started",
            style="blue",
        )

        try:
            # Stage 0: Validation
            if self.verbose:
                self._print("\n[bold]Validating prerequisites...[/bold]" if self.console else "\nValidating prerequisites...")
            self.validate_prerequisites()
            stages_completed.append("validation")

            # Stage 1: Diarization (optional)
            diarization_result = None
            if not self.skip_diarization:
                diarization_result = self.run_diarization_stage()
                stages_completed.append("diarization")

            # Stage 2: Transcription
            transcription_result = self.run_transcription_stage()
            stages_completed.append("transcription")

            # Stage 3: Combination (only if diarization was done)
            combination_result = None
            if not self.skip_diarization:
                combination_result = self.run_combination_stage(diarization_result, transcription_result)
                stages_completed.append("combination")

            # Determine the main output file for labeling/proofreading
            main_output_file = None
            if combination_result and combination_result.output_file:
                main_output_file = combination_result.output_file
            elif transcription_result.output_files.get("md"):
                main_output_file = transcription_result.output_files.get("md")

            # Stage 4: Speaker Labeling (optional)
            if self.labels_file and main_output_file:
                labeled_file = self.run_labeling_stage(main_output_file)
                stages_completed.append("labeling")
                main_output_file = labeled_file  # Update for proofreading

            # Stage 5: Proofreading (optional)
            final_output_file = main_output_file
            if self.enable_proofreading and main_output_file:
                final_output_file = self.run_proofreading_stage(main_output_file)
                stages_completed.append("proofreading")

            # Calculate total time
            total_duration = time.time() - total_start

            # Collect output files
            output_files = {}
            if diarization_result and diarization_result.output_file:
                output_files['diarization'] = diarization_result.output_file
            if transcription_result.output_files:
                output_files.update(transcription_result.output_files)
            if combination_result and combination_result.output_file:
                output_files['combined'] = combination_result.output_file

            # Add final processed file if different from combined
            if final_output_file and final_output_file != combination_result.output_file if combination_result else None:
                output_files['final'] = final_output_file

            # Print success summary
            self._print("\n" + "=" * 60, style="green")
            self._print("✅ Pipeline completed successfully!", style="bold green")
            self._print(f"Total processing time: {total_duration:.1f}s", style="green")
            self._print(f"\nOutput files in: {self.output_dir}", style="cyan")
            for key, path in output_files.items():
                self._print(f"  • {key}: {path.name}", style="cyan")
            self._print("=" * 60, style="green")

            return PipelineResult(
                success=True,
                audio_file=self.audio_file,
                total_duration=total_duration,
                stages_completed=stages_completed,
                diarization_result=diarization_result,
                transcription_result=transcription_result,
                combination_result=combination_result,
                output_files=output_files,
            )

        except Exception as e:
            # Determine which stage failed
            error_stage = stages_completed[-1] if stages_completed else "validation"

            total_duration = time.time() - total_start

            # Print error
            self._print("\n" + "=" * 60, style="red")
            self._print(f"❌ Pipeline failed at stage: {error_stage}", style="bold red")
            self._print(f"Error: {str(e)}", style="red")
            self._print("=" * 60, style="red")

            return PipelineResult(
                success=False,
                audio_file=self.audio_file,
                total_duration=total_duration,
                stages_completed=stages_completed,
                error=str(e),
                error_stage=error_stage,
            )
