# Changelog

All notable changes to LocalTranscribe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

**[View all releases on GitHub](https://github.com/yourusername/transcribe-diarization/releases)**
