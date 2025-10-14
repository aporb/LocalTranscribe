# Changelog

All notable changes to LocalTranscribe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.2b2] - 2025-10-14

### ✨ Added

**Video Format Support (Phase 1 Complete)**
- Added support for video file audio extraction: MP4, MOV, AVI, MKV, WEBM
- Video formats now work seamlessly through existing pydub/FFmpeg integration
- Updated `PathResolver` and `BatchProcessor` to accept video file extensions

### 📝 Documentation

**Format Support Documentation**
- Updated README to accurately reflect all supported formats including OPUS
- Clarified that video files will have audio automatically extracted
- Documentation now matches actual code capabilities

### 🔧 Technical

**Implementation Details**
- Video format extensions added to `localtranscribe/core/path_resolver.py:18-23`
- Video format extensions added to `localtranscribe/batch/processor.py:71-76`
- No breaking changes - all existing functionality preserved
- Leverages existing FFmpeg dependency for video audio extraction

**Supported Formats (Total: 13)**
- Audio (8): MP3, WAV, OGG, M4A, FLAC, AAC, WMA, OPUS
- Video (5): MP4, MOV, AVI, MKV, WEBM

---

## [2.0.2b1] - 2025-10-13

### 📝 Documentation

**Package Metadata Updates**
- Updated PyPI package description to match README tagline
- Added prominent PyPI package link in Quick Start section
- Enhanced professional polish across all documentation
- Clarified installation instructions with package URL

---

## [2.0.1-beta] - 2025-10-13

### 🐛 Fixed

**Pyannote API Compatibility**
- Fixed authentication parameter: Changed `use_auth_token` to `token` in pipeline loading
- Fixed output iteration: Updated to use `.speaker_diarization` attribute instead of deprecated `.itertracks()` method
- Updated documentation to require accepting both model licenses (main + dependency)

These fixes ensure full compatibility with pyannote.audio 3.x API changes.

---

## [2.0.0-beta] - 2025-10-13

### 🎉 Complete Rewrite

Version 2.0 is a ground-up rebuild focused on usability, architecture, and developer experience.

### ✨ Added

**Professional CLI**
- Modern command-line interface using Typer framework
- Beautiful terminal output with Rich
- Single command replaces 3-step manual workflow
- Comprehensive `--help` for all commands
- Shell autocompletion support

**Python SDK**
- High-level `LocalTranscribe` class for programmatic use
- Type-safe result objects: `ProcessResult`, `BatchResult`, `Segment`
- Fluent API with method chaining
- Comprehensive docstrings and type hints

**New Commands**
- `process` - Main transcription command (replaces 3 scripts)
- `batch` - Process multiple files in parallel
- `doctor` - System health check and validation
- `label` - Custom speaker name assignment
- `version` - Version and system information
- `config` - Configuration management

**Modular Architecture**
- Separated CLI, SDK, and Core into distinct modules
- Clean imports: `from localtranscribe import LocalTranscribe`
- Testable, maintainable code structure
- Proper Python package with `pyproject.toml`

**Better UX**
- Smart path resolution (works with any file location)
- Helpful error messages with suggestions
- Progress indicators for long operations
- Validation before processing starts

### 🔄 Changed

**Breaking Changes**
- Old 3-script workflow deprecated (scripts preserved as `.backup`)
- Entry point changed from `python3 scripts/*.py` to `localtranscribe` command
- Configuration now uses YAML instead of hardcoded values

**Improvements**
- Installation simplified to `pip install -e .`
- No more manual file renaming required
- Output directory auto-created
- HuggingFace token validation improved

### 🗑️ Deprecated

- `scripts/diarization.py` - Use `localtranscribe process` instead
- `scripts/transcription.py` - Use `localtranscribe process` instead
- `scripts/combine.py` - Use `localtranscribe process` instead

Old scripts backed up as `.backup` files for reference.

### 📚 Documentation

- New SDK Reference guide
- Updated README with clear examples
- Phase 3 completion summary
- Implementation checklist

### 🐛 Fixed

- Path resolution issues with different working directories
- Error messages now include actionable suggestions
- Better handling of missing dependencies
- Improved model download feedback

---

## [1.0.0] - 2025-10-10

### Initial Release

**Core Features**
- Speaker diarization using pyannote.audio
- Speech-to-text using Whisper (MLX, Faster, Original)
- Combined output with speaker labels
- Multiple output formats (TXT, JSON, SRT, MD)
- Apple Silicon optimization with MLX-Whisper

**Manual Workflow**
- Three-step process: diarization → transcription → combine
- Scripts in `scripts/` directory
- Manual configuration via source code editing

**Documentation**
- Installation guide
- Usage instructions
- Troubleshooting guide
- Configuration reference

---

## Upgrade Guide

### From 1.0 to 2.0

**Old workflow:**
```bash
cd scripts
python3 diarization.py
python3 transcription.py
python3 combine.py
```

**New workflow:**
```bash
# One command does everything
localtranscribe process audio.mp3

# Or with options
localtranscribe process audio.mp3 --model small --speakers 2
```

**Migration steps:**

1. **Install v2.0:**
   ```bash
   pip install -e .  # From project root
   ```

2. **Verify installation:**
   ```bash
   localtranscribe doctor
   ```

3. **Test with your files:**
   ```bash
   localtranscribe process your-audio.mp3
   ```

**What stays the same:**
- HuggingFace token still required
- Same models and quality
- Same output formats
- Same system requirements

**What changed:**
- Command-line interface (much simpler!)
- No more manual script execution
- Better error messages
- Automatic path handling

---

## Version History

- **2.0.2b1** (2025-10-13) - Package metadata and documentation updates
- **2.0.1-beta** (2025-10-13) - Pyannote API compatibility fixes
- **2.0.0-beta** (2025-10-13) - Complete rewrite with CLI and SDK
- **1.0.0** (2025-10-10) - Initial release with 3-script workflow

---

## Coming Soon

**v2.1.0** (Planned)
- Interactive speaker labeling
- Better progress indicators
- Resume failed jobs
- Audio quality analysis

**v3.0.0** (Future)
- Real-time transcription
- Web interface
- Docker support
- Plugin system

---

**[View all releases on GitHub](https://github.com/aporb/transcribe-diarization/releases)**
