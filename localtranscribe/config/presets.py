"""
Configuration presets for common use cases.

Based on Docker Compose profiles pattern and npm scripts best practices:
- https://docs.docker.com/compose/how-tos/profiles/
- https://dev.to/altairlage/docker-compose-speed-up-your-workflow-with-profiles-extends-and-dependson-4df8
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class PresetType(str, Enum):
    """Available configuration presets."""

    PODCAST = "podcast"
    MEETING = "meeting"
    INTERVIEW = "interview"
    LECTURE = "lecture"
    QUICK = "quick"
    ACCURATE = "accurate"


@dataclass
class PresetConfig:
    """Configuration preset with all settings."""

    name: str
    description: str

    # Model settings
    model_size: str = "medium"
    whisper_implementation: str = "auto"

    # Speaker settings
    num_speakers: Optional[int] = None
    min_speakers: Optional[int] = None
    max_speakers: Optional[int] = None
    skip_diarization: bool = False

    # Processing settings
    language: Optional[str] = None

    # Output settings
    output_formats: List[str] = None

    # Proofreading settings
    proofread: bool = True
    proofread_level: str = "standard"
    domains: List[str] = None
    expand_acronyms: bool = False
    context_aware: bool = False

    def __post_init__(self):
        """Set default values for mutable fields."""
        if self.output_formats is None:
            self.output_formats = ["txt", "json", "md"]
        if self.domains is None:
            self.domains = ["common"]


# Define presets based on common use cases
PRESETS = {
    PresetType.PODCAST: PresetConfig(
        name="Podcast",
        description="Optimized for podcast/interview transcription with 2 speakers",
        model_size="medium",
        num_speakers=2,
        proofread=True,
        proofread_level="standard",
        domains=["common", "media"],
        expand_acronyms=True,
        output_formats=["md", "json", "srt"],
    ),

    PresetType.MEETING: PresetConfig(
        name="Business Meeting",
        description="Optimized for business meetings with multiple speakers (3-8)",
        model_size="medium",
        min_speakers=3,
        max_speakers=8,
        proofread=True,
        proofread_level="thorough",
        domains=["business", "technical", "common"],
        expand_acronyms=True,
        context_aware=True,
        output_formats=["md", "json", "txt"],
    ),

    PresetType.INTERVIEW: PresetConfig(
        name="Interview",
        description="Optimized for structured interviews with 2-3 speakers",
        model_size="medium",
        min_speakers=2,
        max_speakers=3,
        proofread=True,
        proofread_level="thorough",
        domains=["common", "academic"],
        expand_acronyms=True,
        context_aware=True,
        output_formats=["md", "json"],
    ),

    PresetType.LECTURE: PresetConfig(
        name="Lecture/Presentation",
        description="Optimized for single speaker lectures or presentations",
        model_size="medium",
        num_speakers=1,
        skip_diarization=True,  # Single speaker, skip diarization for speed
        proofread=True,
        proofread_level="thorough",
        domains=["academic", "technical", "common"],
        expand_acronyms=True,
        context_aware=True,
        output_formats=["md", "txt"],
    ),

    PresetType.QUICK: PresetConfig(
        name="Quick Draft",
        description="Fast transcription for quick drafts, minimal processing",
        model_size="small",
        skip_diarization=True,
        proofread=False,
        output_formats=["txt"],
    ),

    PresetType.ACCURATE: PresetConfig(
        name="Maximum Accuracy",
        description="Highest quality transcription with all enhancements",
        model_size="large",
        proofread=True,
        proofread_level="thorough",
        domains=["common", "technical", "business", "academic"],
        expand_acronyms=True,
        context_aware=True,
        output_formats=["md", "json", "txt", "srt"],
    ),
}


def get_preset(preset_type: PresetType) -> PresetConfig:
    """
    Get configuration preset by type.

    Args:
        preset_type: Type of preset to retrieve

    Returns:
        PresetConfig object with all settings

    Raises:
        KeyError: If preset type doesn't exist
    """
    return PRESETS[preset_type]


def list_presets() -> List[PresetConfig]:
    """
    List all available presets.

    Returns:
        List of all PresetConfig objects
    """
    return list(PRESETS.values())


def apply_preset_to_args(preset: PresetConfig, **override_args) -> dict:
    """
    Apply preset configuration to command arguments.

    Allows individual arguments to override preset values.

    Args:
        preset: PresetConfig to apply
        **override_args: Arguments that should override preset values

    Returns:
        Dictionary of final arguments
    """
    # Start with preset values
    args = {
        "model_size": preset.model_size,
        "num_speakers": preset.num_speakers,
        "min_speakers": preset.min_speakers,
        "max_speakers": preset.max_speakers,
        "skip_diarization": preset.skip_diarization,
        "language": preset.language,
        "formats": preset.output_formats,
        "proofread": preset.proofread,
        "proofread_level": preset.proofread_level,
        "domains": preset.domains,
        "expand_acronyms": preset.expand_acronyms,
        "context_aware": preset.context_aware,
    }

    # Override with any explicitly provided arguments
    for key, value in override_args.items():
        if value is not None:  # Only override if explicitly set
            args[key] = value

    # Remove None values
    return {k: v for k, v in args.items() if v is not None}


def show_preset_info(preset_type: PresetType) -> str:
    """
    Get formatted information about a preset.

    Args:
        preset_type: Type of preset

    Returns:
        Formatted string describing the preset
    """
    preset = get_preset(preset_type)

    lines = [
        f"📋 {preset.name}",
        f"   {preset.description}",
        "",
        "Settings:",
        f"  • Model: {preset.model_size}",
    ]

    if preset.skip_diarization:
        lines.append("  • Speaker detection: Skipped")
    elif preset.num_speakers:
        lines.append(f"  • Speakers: {preset.num_speakers} (exact)")
    elif preset.min_speakers or preset.max_speakers:
        min_s = preset.min_speakers or "any"
        max_s = preset.max_speakers or "any"
        lines.append(f"  • Speakers: {min_s}-{max_s}")

    if preset.proofread:
        lines.append(f"  • Proofreading: {preset.proofread_level}")
        lines.append(f"  • Domains: {', '.join(preset.domains)}")
        if preset.expand_acronyms:
            lines.append("  • Acronym expansion: Yes")
        if preset.context_aware:
            lines.append("  • Context-aware: Yes")

    lines.append(f"  • Output formats: {', '.join(preset.output_formats)}")

    return "\n".join(lines)
