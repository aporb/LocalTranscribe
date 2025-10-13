# Phase 1 Implementation Plan - Critical Usability Fixes

**Project**: LocalTranscribe v2.0
**Goal**: Make tool usable without code editing
**Timeline**: 2-4 weeks
**Success Criteria**: Time-to-first-success < 30 minutes

## Executive Summary

This plan transforms LocalTranscribe from an alpha tool requiring code editing into a professional CLI application. Phase 1 focuses on the 4 critical issues identified in the usability review:

1. **No CLI arguments** → Add Typer-based CLI
2. **Hardcoded file paths** → Dynamic path resolution
3. **Manual 3-step pipeline** → Single command orchestrator
4. **No batch processing** → (Deferred to Phase 2, but foundation laid here)

## Current State Analysis

### Existing Files
- `scripts/diarization.py` (305 lines) - Hardcoded at line 259
- `scripts/transcription.py` (463 lines) - Hardcoded at line 410
- `scripts/combine.py` (385 lines) - Hardcoded at lines 310-313
- Example implementations in `docs/examples/` (reference only)

### Critical Hardcoded Lines
```python
# diarization.py:259
audio_file = "../input/audio.ogg"

# transcription.py:410
audio_file = "../input/audio.ogg"

# combine.py:310-313
diarization_file = "../output/audio_diarization_results.md"
transcription_json = "../output/audio_transcript.json"
transcription_txt = "../output/audio_transcript.txt"
audio_file = "../input/audio.ogg"
```

---

## Implementation Strategy

### Architecture Decision: Hybrid Refactor

Instead of a complete rewrite, we'll use a **hybrid approach**:
- Keep existing `scripts/` directory functioning (deprecated)
- Create new `localtranscribe/` package structure
- Extract core logic from scripts into importable modules
- Add CLI wrapper using Typer

**Benefits**:
- Maintains backward compatibility during transition
- Allows gradual migration
- Reduces risk of breaking working code
- Enables testing at each step

### New Project Structure
```
transcribe-diarization/
├── localtranscribe/              # New package (Phase 1)
│   ├── __init__.py
│   ├── cli.py                    # Main CLI entry point
│   ├── core/                     # Business logic
│   │   ├── __init__.py
│   │   ├── diarization.py        # Extracted from scripts/
│   │   ├── transcription.py      # Extracted from scripts/
│   │   ├── combination.py        # Extracted from scripts/combine.py
│   │   ├── audio_utils.py        # Audio preprocessing
│   │   └── path_resolver.py      # Smart path resolution
│   ├── pipeline/                 # Pipeline orchestration
│   │   ├── __init__.py
│   │   └── orchestrator.py       # Manages 3-step pipeline
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   ├── loader.py             # Load YAML configs
│   │   └── defaults.py           # Default settings
│   ├── health/                   # Health checks
│   │   ├── __init__.py
│   │   └── doctor.py             # System validation
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── errors.py             # Custom exceptions
│       └── progress.py           # Progress tracking
│
├── scripts/                      # Legacy scripts (keep for now)
│   ├── diarization.py            # Mark as deprecated
│   ├── transcription.py          # Mark as deprecated
│   └── combine.py                # Mark as deprecated
│
├── docs/
│   ├── USABILITY_REVIEW.md       # ✅ Exists
│   ├── PHASE1_IMPLEMENTATION_PLAN.md  # This document
│   ├── MIGRATION_GUIDE.md        # How to migrate from old to new
│   └── examples/                 # ✅ Reference implementations exist
│
├── pyproject.toml                # Modern Python packaging
├── requirements.txt              # Updated dependencies
├── config.yaml.example           # Example configuration
├── install.sh                    # Installation script
└── README.md                     # Updated with CLI usage
```

---

## Task Breakdown

### Task 1: Project Structure Setup (Day 1)
**Priority**: 1
**Dependencies**: None
**Effort**: 4 hours

**Actions**:
1. Create `localtranscribe/` directory structure
2. Create all `__init__.py` files
3. Create `pyproject.toml` with package metadata
4. Update `.gitignore` if needed

**Success Criteria**:
- Directory structure matches design
- Can import `localtranscribe` as package
- `pip install -e .` works

**Files to Create**:
- `localtranscribe/__init__.py`
- `localtranscribe/core/__init__.py`
- `localtranscribe/pipeline/__init__.py`
- `localtranscribe/config/__init__.py`
- `localtranscribe/health/__init__.py`
- `localtranscribe/utils/__init__.py`
- `pyproject.toml`

---

### Task 2: Extract Core Logic - Path Resolution (Day 1-2)
**Priority**: 2
**Dependencies**: Task 1
**Effort**: 6 hours

**Actions**:
1. Create `localtranscribe/utils/errors.py` with custom exceptions
2. Create `localtranscribe/core/path_resolver.py`
3. Implement smart path resolution logic
4. Add comprehensive error messages

**Implementation**:
```python
# localtranscribe/core/path_resolver.py
from pathlib import Path
from typing import Optional
from ..utils.errors import AudioFileNotFoundError

class PathResolver:
    """Smart path resolution for audio files and outputs."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"

    def resolve_audio_file(self, file_path: str | Path) -> Path:
        """Find audio file in multiple locations."""
        path = Path(file_path)

        # Try absolute path
        if path.is_absolute() and path.exists():
            return path

        # Try current directory
        if path.exists():
            return path.resolve()

        # Try input directory
        if (self.input_dir / path.name).exists():
            return (self.input_dir / path.name).resolve()

        # Not found - provide helpful error
        raise AudioFileNotFoundError(
            f"Audio file not found: {file_path}",
            suggestions=[
                f"Place file in {self.input_dir}",
                f"Provide absolute path",
                f"Check file name spelling"
            ],
            context={
                'searched_path': str(file_path),
                'current_dir': str(Path.cwd()),
                'input_dir': str(self.input_dir),
                'files_in_input': list(self.input_dir.glob("*")) if self.input_dir.exists() else []
            }
        )

    def resolve_output_path(self, input_file: Path, suffix: str, extension: str) -> Path:
        """Generate output path based on input filename."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        base_name = input_file.stem
        return self.output_dir / f"{base_name}_{suffix}.{extension}"
```

**Success Criteria**:
- Path resolver finds files in multiple locations
- Error messages include actionable suggestions
- Works with relative and absolute paths

---

### Task 3: Extract Core Logic - Diarization (Day 2-3)
**Priority**: 3
**Dependencies**: Task 2
**Effort**: 8 hours

**Actions**:
1. Create `localtranscribe/core/diarization.py`
2. Extract core diarization logic from `scripts/diarization.py`
3. Remove hardcoded paths, add parameters
4. Keep audio preprocessing logic
5. Return structured results instead of writing files directly

**Key Changes**:
```python
# Before (scripts/diarization.py:259)
audio_file = "../input/audio.ogg"

# After (localtranscribe/core/diarization.py)
def run_diarization(
    audio_file: Path,
    output_dir: Path,
    num_speakers: Optional[int] = None,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
    device: Optional[torch.device] = None,
) -> DiarizationResult:
    """Run speaker diarization on audio file."""
    # Implementation uses parameters instead of hardcoded values
    ...
```

**Testing**:
- Can import and call `run_diarization()` function
- Works with any file path
- Returns structured results

---

### Task 4: Extract Core Logic - Transcription (Day 3-4)
**Priority**: 4
**Dependencies**: Task 2
**Effort**: 8 hours

**Actions**:
1. Create `localtranscribe/core/transcription.py`
2. Extract core transcription logic from `scripts/transcription.py`
3. Remove hardcoded paths, add parameters
4. Keep implementation detection logic
5. Return structured results

**Key Changes**:
```python
# Before (scripts/transcription.py:410)
audio_file = "../input/audio.ogg"

# After (localtranscribe/core/transcription.py)
def run_transcription(
    audio_file: Path,
    output_dir: Path,
    model_size: str = "base",
    language: Optional[str] = None,
    implementation: str = "auto",
    output_formats: List[str] = ["txt", "json"],
) -> TranscriptionResult:
    """Run speech-to-text transcription."""
    # Implementation uses parameters instead of hardcoded values
    ...
```

**Testing**:
- Can import and call `run_transcription()` function
- Works with any file path
- Detects best implementation automatically

---

### Task 5: Extract Core Logic - Combination (Day 4-5)
**Priority**: 5
**Dependencies**: Task 3, Task 4
**Effort**: 6 hours

**Actions**:
1. Create `localtranscribe/core/combination.py`
2. Extract combination logic from `scripts/combine.py`
3. Remove hardcoded paths, add parameters
4. Accept results from previous stages
5. Return structured combined results

**Key Changes**:
```python
# Before (scripts/combine.py:310-313)
diarization_file = "../output/audio_diarization_results.md"
transcription_json = "../output/audio_transcript.json"

# After (localtranscribe/core/combination.py)
def combine_results(
    diarization_file: Path,
    transcription_file: Path,
    audio_file: Path,
    output_dir: Path,
) -> CombinedResult:
    """Combine diarization and transcription results."""
    # Implementation uses parameters instead of hardcoded values
    ...
```

**Testing**:
- Can import and call `combine_results()` function
- Works with any file paths
- Produces readable output

---

### Task 6: Create Pipeline Orchestrator (Day 5-6)
**Priority**: 6
**Dependencies**: Task 3, Task 4, Task 5
**Effort**: 12 hours

**Actions**:
1. Create `localtranscribe/pipeline/orchestrator.py`
2. Implement `PipelineOrchestrator` class
3. Add prerequisite validation
4. Add stage-by-stage execution
5. Add error recovery and helpful messages
6. Add progress tracking with Rich

**Implementation** (based on `docs/examples/pipeline_orchestrator.py`):
```python
class PipelineOrchestrator:
    """Orchestrate the full transcription pipeline."""

    def __init__(
        self,
        audio_file: Path,
        output_dir: Path,
        model_size: str = "base",
        num_speakers: Optional[int] = None,
        skip_diarization: bool = False,
        **kwargs
    ):
        self.audio_file = Path(audio_file)
        self.output_dir = Path(output_dir)
        self.model_size = model_size
        self.num_speakers = num_speakers
        self.skip_diarization = skip_diarization
        # ... other parameters

    def run(self) -> Dict[str, Any]:
        """Execute full pipeline."""
        # 1. Validate prerequisites
        # 2. Run diarization (optional)
        # 3. Run transcription
        # 4. Combine results
        # 5. Return structured results
        ...
```

**Success Criteria**:
- Single command replaces 3 separate commands
- Progress tracking shows current stage
- Errors include helpful recovery suggestions
- Can skip diarization for transcription-only mode

---

### Task 7: Create CLI Interface with Typer (Day 6-8)
**Priority**: 7
**Dependencies**: Task 6
**Effort**: 16 hours

**Actions**:
1. Create `localtranscribe/cli.py`
2. Implement `process` command
3. Implement `doctor` command (basic health check)
4. Implement `config-show` command
5. Add global options (--version, --help)
6. Integrate Rich for beautiful output

**Implementation** (based on `docs/examples/cli_interface.py`):
```python
# localtranscribe/cli.py
import typer
from rich.console import Console
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="localtranscribe",
    help="Offline audio transcription with speaker diarization",
    add_completion=True,
)

@app.command()
def process(
    input_file: Path = typer.Argument(..., help="Audio file to process"),
    output_dir: Path = typer.Option("output", "--output", "-o"),
    model: str = typer.Option("base", "--model", "-m"),
    speakers: Optional[int] = typer.Option(None, "--speakers", "-s"),
    skip_diarization: bool = typer.Option(False, "--skip-diarization"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose"),
):
    """Process audio file through full pipeline."""
    from .pipeline.orchestrator import PipelineOrchestrator

    orchestrator = PipelineOrchestrator(
        audio_file=input_file,
        output_dir=output_dir,
        model_size=model,
        num_speakers=speakers,
        skip_diarization=skip_diarization,
    )

    result = orchestrator.run()

    if not result['success']:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
```

**Success Criteria**:
- `localtranscribe process audio.mp3` works
- All CLI arguments functional
- Beautiful Rich UI output
- Help text is comprehensive (`--help`)
- Auto-completion available

---

### Task 8: Add Configuration File Support (Day 8-9)
**Priority**: 8
**Dependencies**: Task 7
**Effort**: 6 hours

**Actions**:
1. Create `localtranscribe/config/defaults.py`
2. Create `localtranscribe/config/loader.py`
3. Add YAML parsing with PyYAML
4. Implement config merging (defaults < file < CLI args)
5. Create `config.yaml.example`

**Implementation**:
```python
# localtranscribe/config/loader.py
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .defaults import DEFAULT_CONFIG

class ConfigLoader:
    """Load and merge configuration from multiple sources."""

    def load_config(
        self,
        config_file: Optional[Path] = None,
        cli_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load configuration with priority: CLI > File > Defaults."""
        config = DEFAULT_CONFIG.copy()

        # Load from file if provided
        if config_file and config_file.exists():
            with open(config_file) as f:
                file_config = yaml.safe_load(f)
                config.update(file_config)

        # Apply CLI overrides
        if cli_overrides:
            config.update(cli_overrides)

        return config
```

**Success Criteria**:
- Can load `config.yaml` file
- CLI arguments override config file
- Config file overrides defaults
- Example config created

---

### Task 9: Implement Doctor Health Check (Day 9-10)
**Priority**: 9
**Dependencies**: Task 7
**Effort**: 6 hours

**Actions**:
1. Create `localtranscribe/health/doctor.py`
2. Add checks for Python version, FFmpeg, PyTorch, Whisper, Pyannote, HuggingFace token
3. Add checks for directories
4. Display results in Rich table
5. Provide actionable suggestions for failures

**Implementation**:
```python
# localtranscribe/health/doctor.py
from rich.console import Console
from rich.table import Table

def check_python_version() -> tuple[bool, str]:
    """Check Python version is compatible."""
    import sys
    version = sys.version_info
    if version >= (3, 8):
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    return False, f"❌ Python {version.major}.{version.minor} (requires 3.8+)"

def run_health_check() -> bool:
    """Run all health checks and display results."""
    checks = [
        ("Python", check_python_version),
        ("FFmpeg", check_ffmpeg),
        ("PyTorch", check_pytorch),
        # ... more checks
    ]

    # Display in Rich table
    # Return True if all passed
    ...
```

**Success Criteria**:
- `localtranscribe doctor` runs all checks
- Displays results in formatted table
- Provides suggestions for failures
- Returns exit code 0 if all passed, 1 if failures

---

### Task 10: Improve Error Messages (Day 10-11)
**Priority**: 10
**Dependencies**: Task 2
**Effort**: 6 hours

**Actions**:
1. Create `localtranscribe/utils/errors.py` with custom exception classes
2. Add context and suggestions to all exceptions
3. Update all modules to use new exceptions
4. Add error formatting with Rich

**Implementation**:
```python
# localtranscribe/utils/errors.py
class LocalTranscribeError(Exception):
    """Base exception with helpful context."""

    def __init__(
        self,
        message: str,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.suggestions = suggestions or []
        self.context = context or {}
        super().__init__(self.format_error())

    def format_error(self) -> str:
        """Format error with suggestions and context."""
        lines = [f"❌ {self.message}", ""]

        if self.suggestions:
            lines.append("Suggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
            lines.append("")

        if self.context:
            lines.append("Context:")
            for key, value in self.context.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)

class AudioFileNotFoundError(LocalTranscribeError):
    """Audio file not found."""
    pass

class ModelDownloadError(LocalTranscribeError):
    """Model download failed."""
    pass

class HuggingFaceTokenError(LocalTranscribeError):
    """HuggingFace token missing or invalid."""
    pass
```

**Success Criteria**:
- All errors include helpful suggestions
- Context shows relevant file paths and state
- Error messages are user-friendly, not technical
- Can recover from common errors

---

### Task 11: Create Installation Script (Day 11)
**Priority**: 11
**Dependencies**: Task 1
**Effort**: 4 hours

**Actions**:
1. Create `install.sh` script
2. Add checks for Python version
3. Install FFmpeg if missing (macOS via Homebrew)
4. Create virtual environment
5. Install dependencies
6. Detect Apple Silicon and install MLX-Whisper
7. Setup `.env` file from example

**Implementation**:
```bash
#!/bin/bash
set -e

echo "🎙️  LocalTranscribe Installer"
echo "=============================="

# Check Python
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing FFmpeg via Homebrew..."
    brew install ffmpeg
fi

# Create venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e .

# Detect Apple Silicon
if [[ $(uname -m) == 'arm64' ]]; then
    echo "✓ Apple Silicon detected, installing MLX-Whisper..."
    pip install mlx-whisper mlx
fi

# Setup .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env and add your HUGGINGFACE_TOKEN"
fi

echo "✅ Installation complete!"
```

**Success Criteria**:
- Script runs without errors
- All dependencies installed
- Virtual environment created
- `.env` file created

---

### Task 12: Update Dependencies (Day 11)
**Priority**: 12
**Dependencies**: Task 7
**Effort**: 2 hours

**Actions**:
1. Update `requirements.txt` with new dependencies
2. Add Typer and Rich
3. Add PyYAML for config
4. Keep existing ML dependencies
5. Add platform-specific requirements

**New Dependencies**:
```txt
# CLI and UI
typer[all]>=0.9.0
rich>=13.0.0

# Configuration
pyyaml>=6.0

# Existing dependencies (keep)
torch>=2.0.0
torchaudio>=2.0.0
pyannote.audio>=3.0.0
pydub>=0.25.1
python-dotenv>=1.0.0

# Platform-specific
mlx-whisper>=0.1.0; sys_platform == "darwin" and platform_machine == "arm64"
faster-whisper>=0.10.0
```

---

### Task 13: Create pyproject.toml (Day 11-12)
**Priority**: 13
**Dependencies**: Task 1, Task 12
**Effort**: 4 hours

**Actions**:
1. Create `pyproject.toml` for modern packaging
2. Define entry points for CLI
3. Add project metadata
4. Configure development dependencies

**Implementation**:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "localtranscribe"
version = "2.0.0"
description = "Offline audio transcription with speaker diarization"
authors = [{name = "Your Name"}]
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}

dependencies = [
    "torch>=2.0.0",
    "torchaudio>=2.0.0",
    "pyannote.audio>=3.0.0",
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
    "pydub>=0.25.1",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
mlx = ["mlx-whisper>=0.1.0", "mlx>=0.1.0"]
faster = ["faster-whisper>=0.10.0"]
dev = ["pytest", "black", "mypy"]

[project.scripts]
localtranscribe = "localtranscribe.cli:app"

[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/transcribe-diarization"
Repository = "https://github.com/YOUR_USERNAME/transcribe-diarization"
```

**Success Criteria**:
- `pip install -e .` installs package
- `localtranscribe` command available in terminal
- Dependencies installed correctly

---

### Task 14: Update README.md (Day 12)
**Priority**: 14
**Dependencies**: Task 13
**Effort**: 4 hours

**Actions**:
1. Update README with new CLI usage
2. Add installation instructions
3. Add quick start guide
4. Add examples for all commands
5. Update architecture diagram
6. Add migration notes

**New README Structure**:
```markdown
# LocalTranscribe v2.0

Offline audio transcription with speaker diarization, optimized for Apple Silicon.

## Quick Start

```bash
# Install
curl -sSL https://raw.githubusercontent.com/.../install.sh | bash

# Or manual install
pip install localtranscribe

# Process audio file
localtranscribe process meeting.mp3

# Check health
localtranscribe doctor
```

## Features

- ✅ CLI interface (no code editing required)
- ✅ Single command replaces 3-step process
- ✅ Beautiful progress tracking
- ✅ Smart file path resolution
- ✅ Configuration file support
- ✅ Health check command

## Usage

### Basic Processing

```bash
localtranscribe process audio.mp3
```

### Advanced Options

```bash
localtranscribe process interview.mp3 \
  --model medium \
  --speakers 2 \
  --output ./transcripts/
```

### With Configuration File

```bash
localtranscribe process audio.mp3 --config config.yaml
```

## Migration from v1.x

If you were using the old scripts:

```bash
# Old way (v1.x)
cd scripts
python3 diarization.py
python3 transcription.py
python3 combine.py

# New way (v2.0)
localtranscribe process audio.mp3
```

See [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) for details.
```

---

### Task 15: Create Migration Guide (Day 12-13)
**Priority**: 15
**Dependencies**: Task 14
**Effort**: 3 hours

**Actions**:
1. Create `docs/MIGRATION_GUIDE.md`
2. Document old vs new usage
3. Provide code comparison examples
4. Add troubleshooting section

---

### Task 16: End-to-End Testing (Day 13-14)
**Priority**: 16
**Dependencies**: All previous tasks
**Effort**: 8 hours

**Actions**:
1. Test `localtranscribe process` with various audio files
2. Test all CLI options and flags
3. Test config file loading
4. Test doctor command
5. Test error scenarios
6. Verify output files are correct
7. Test on different audio formats

**Test Cases**:
- ✅ Single audio file processing
- ✅ Different model sizes
- ✅ Skip diarization mode
- ✅ Custom output directory
- ✅ Config file usage
- ✅ Error handling (missing file, invalid token, etc.)
- ✅ Progress tracking displays correctly
- ✅ Output files match expected format

---

## Timeline and Milestones

### Week 1 (Days 1-7)
- ✅ **Milestone 1**: Project structure and core extraction complete
  - Tasks 1-5 complete
  - Can import core modules
  - Core logic extracted from scripts

### Week 2 (Days 8-14)
- ✅ **Milestone 2**: CLI and orchestration complete
  - Tasks 6-10 complete
  - CLI commands working
  - Single command pipeline functional

### Week 3 (Days 15-21) - If needed
- ✅ **Milestone 3**: Installation, documentation, testing
  - Tasks 11-16 complete
  - Installation script working
  - Documentation updated
  - All tests passing

---

## Success Metrics

### Phase 1 Deliverables

**Must Have**:
- ✅ CLI works: `localtranscribe process audio.mp3`
- ✅ No code editing required for basic usage
- ✅ Single command replaces 3-step process
- ✅ Error messages include actionable suggestions
- ✅ Installation takes < 15 minutes
- ✅ Health check validates environment

**Should Have**:
- ✅ Configuration file support
- ✅ Beautiful Rich UI output
- ✅ Smart path resolution
- ✅ Progress tracking

**Nice to Have**:
- ⏰ Shell auto-completion (comes free with Typer)
- ⏰ Multiple output formats support

### User Experience Goals

**Before Phase 1**:
- Time-to-first-success: 1-2 hours
- Commands per file: 3
- Code editing required: Yes (3 files)
- Error messages: Technical, not helpful

**After Phase 1**:
- Time-to-first-success: < 30 minutes
- Commands per file: 1
- Code editing required: No
- Error messages: User-friendly with suggestions

---

## Risk Mitigation

### Risk 1: Breaking Existing Functionality
**Mitigation**:
- Keep old scripts in place (deprecated)
- Gradual migration approach
- Test suite for core functionality

### Risk 2: Complex Refactoring Takes Longer
**Mitigation**:
- Start with simplest task (project structure)
- Extract one module at a time
- Test each extraction before moving on

### Risk 3: Dependencies Conflict
**Mitigation**:
- Use virtual environment
- Pin dependency versions
- Test on clean environment

### Risk 4: User Adoption of New CLI
**Mitigation**:
- Create comprehensive migration guide
- Keep old scripts working with deprecation warnings
- Provide side-by-side examples

---

## Post-Phase 1 Next Steps

After Phase 1 is complete, we'll be ready for:

**Phase 2 (Core Features)**:
- Batch processing command
- Speaker labeling command
- Download progress indicators
- Output format selection

**Phase 3 (Architecture & Polish)**:
- Full package refactor
- Test suite (80% coverage)
- PyPI distribution
- CI/CD pipeline

**Phase 4 (Advanced Features)**:
- Real-time transcription
- Web UI
- Docker container
- Plugin system

---

## Appendix A: Command Reference

After Phase 1, these commands will be available:

```bash
# Main processing command
localtranscribe process <audio-file> [OPTIONS]

# Health check
localtranscribe doctor

# Show configuration
localtranscribe config-show

# Version
localtranscribe --version

# Help
localtranscribe --help
localtranscribe process --help
```

---

## Appendix B: File Size Estimates

- `localtranscribe/cli.py`: ~400-500 lines
- `localtranscribe/core/diarization.py`: ~250 lines
- `localtranscribe/core/transcription.py`: ~350 lines
- `localtranscribe/core/combination.py`: ~300 lines
- `localtranscribe/pipeline/orchestrator.py`: ~500 lines
- `localtranscribe/utils/errors.py`: ~150 lines
- `localtranscribe/core/path_resolver.py`: ~150 lines
- **Total new code**: ~2,100-2,200 lines

---

## Appendix C: Testing Checklist

Before declaring Phase 1 complete:

**Installation**:
- [ ] `install.sh` completes without errors
- [ ] `pip install -e .` works
- [ ] `localtranscribe --version` displays version
- [ ] Virtual environment activates correctly

**Basic Functionality**:
- [ ] `localtranscribe process audio.mp3` completes successfully
- [ ] Output files created in correct location
- [ ] Progress bars display correctly
- [ ] Diarization + transcription + combination all work

**CLI Options**:
- [ ] `--model` flag changes model
- [ ] `--speakers` flag sets speaker count
- [ ] `--output` flag changes output directory
- [ ] `--skip-diarization` skips diarization
- [ ] `--config` loads config file
- [ ] `--verbose` shows detailed output

**Error Handling**:
- [ ] Missing audio file shows helpful error
- [ ] Missing HuggingFace token shows setup instructions
- [ ] Invalid model size shows available options
- [ ] Permission errors show actionable suggestions

**Health Check**:
- [ ] `localtranscribe doctor` runs all checks
- [ ] Displays results in formatted table
- [ ] Shows pass/fail for each component
- [ ] Provides installation suggestions for failures

**Documentation**:
- [ ] README updated with CLI usage
- [ ] Examples work as documented
- [ ] Migration guide complete
- [ ] API documentation accurate

---

**Document Status**: Ready for Implementation
**Last Updated**: 2025-10-13
**Next Review**: After Week 1 Milestone
