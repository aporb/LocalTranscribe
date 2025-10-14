# LocalTranscribe

**Privacy-first audio transcription with speaker diarization. Entirely offline.**

Transform recordings into detailed transcripts showing who said what and when—all on your Mac, with complete privacy.

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/localtranscribe?color=blue)](https://pypi.org/project/localtranscribe/)
[![Python](https://img.shields.io/badge/python-3.9+-green)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)](https://www.apple.com/macos/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

[Quick Start](#quick-start) • [Installation](#installation) • [Examples](#usage-examples) • [Documentation](#documentation)

</div>

---

## Why LocalTranscribe?

| Feature | LocalTranscribe | Cloud Services |
|---------|----------------|----------------|
| **Privacy** | 100% offline processing | Data uploaded to third-party servers |
| **Cost** | Free forever | $10-50/month subscription |
| **Speaker Identification** | Automatic speaker detection | Often extra cost or unavailable |
| **Speed (Apple Silicon)** | Real-time to 2x audio length | Depends on upload/download speed |
| **Quality** | OpenAI Whisper models | Varies by provider |
| **Data Ownership** | All files stay on your machine | Depends on provider terms |

**Perfect for:** Researchers, podcasters, journalists, legal professionals, content creators—anyone who needs accurate transcripts with speaker labels and complete data privacy.

---

## Features

- **🔒 Complete Privacy** - All processing happens locally on your machine
- **🎯 Speaker Diarization** - Automatic detection of who spoke when
- **📝 High Accuracy** - Powered by OpenAI's Whisper models
- **⚡️ Apple Silicon Optimized** - Blazing fast on M1/M2/M3/M4 Macs
- **🚀 Simple CLI** - One command to transcribe any audio file
- **📦 Python SDK** - Integrate transcription into your applications
- **🔄 Batch Processing** - Process multiple files simultaneously
- **📊 Multiple Formats** - Output as TXT, JSON, SRT, or Markdown

---

## Quick Start

### Install from PyPI

**Package:** [pypi.org/project/localtranscribe](https://pypi.org/project/localtranscribe/)

```bash
pip install localtranscribe
```

### Setup HuggingFace Token (One-Time)

Speaker diarization requires a free HuggingFace account:

1. **Create account & get token**: https://huggingface.co/settings/tokens
2. **Accept model licenses** (click "Agree" on each):
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. **Configure token**:
   ```bash
   echo "HUGGINGFACE_TOKEN=hf_your_token_here" > .env
   ```

### Transcribe Audio

```bash
localtranscribe process your-audio.mp3
```

**Done!** Results appear in `./output/` with speaker labels, timestamps, and full transcript.

---

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Basic installation
pip install localtranscribe

# For Apple Silicon optimization (recommended for M1/M2/M3/M4)
pip install localtranscribe[mlx]

# For NVIDIA GPU support
pip install localtranscribe[faster]

# Install all optional dependencies
pip install localtranscribe[all]
```

### Option 2: Install from Source

```bash
# Clone repository
git clone https://github.com/aporb/LocalTranscribe.git
cd LocalTranscribe

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .
```

### Verify Installation

```bash
localtranscribe doctor
```

This command checks your system configuration and reports any issues.

---

## Usage Examples

### Basic Transcription

```bash
# Transcribe with automatic settings
localtranscribe process meeting.mp3

# Specify number of speakers for better accuracy
localtranscribe process interview.wav --speakers 2

# Use larger model for higher quality
localtranscribe process podcast.m4a --model medium

# Save to custom location
localtranscribe process audio.mp3 --output ./results/
```

### Batch Processing

```bash
# Process entire folder
localtranscribe batch ./audio-files/

# Process with multiple workers
localtranscribe batch ./recordings/ --workers 4

# With custom settings
localtranscribe batch ./files/ --model small --output ./transcripts/
```

### Single-Speaker Content

```bash
# Skip speaker detection for faster processing
localtranscribe process lecture.mp3 --skip-diarization
```

### Advanced Options

```bash
localtranscribe process audio.mp3 \
  --model medium \              # Model: tiny|base|small|medium|large
  --speakers 3 \                # Number of speakers (if known)
  --language en \               # Force specific language
  --format txt json srt \       # Output formats
  --output ./results/ \         # Output directory
  --verbose                     # Show detailed progress
```

### Using the Python SDK

```python
from localtranscribe import LocalTranscribe

# Initialize with options
lt = LocalTranscribe(
    model_size="base",
    num_speakers=2,
    output_dir="./transcripts"
)

# Process single file
result = lt.process("meeting.mp3")

# Access results
print(f"Transcript: {result.transcript}")
print(f"Speakers: {result.num_speakers}")
print(f"Duration: {result.duration}s")

# Access detailed segments
for segment in result.segments:
    print(f"[{segment.speaker}] {segment.text}")

# Batch processing
results = lt.process_batch("./audio-files/", max_workers=4)
print(f"Completed: {results.successful}/{results.total}")
```

**[→ Full SDK Documentation](docs/SDK_REFERENCE.md)**

---

## Output Formats

LocalTranscribe generates multiple output files for different use cases:

| Format | File | Description |
|--------|------|-------------|
| **Markdown** | `*_combined.md` | Formatted transcript with speaker labels and timestamps |
| **Plain Text** | `*_transcript.txt` | Simple text output for analysis |
| **JSON** | `*_transcript.json` | Structured data for programming |
| **SRT** | `*_transcript.srt` | Subtitle format for video |
| **Diarization** | `*_diarization.md` | Speaker timeline and statistics |

**Example Output:**

```markdown
# Combined Transcript

**Audio File:** interview.mp3
**Processing Date:** 2025-10-13 22:30:00

## SPEAKER_00
**Time:** [0.0s - 5.2s]

Hello, welcome to the show. Thanks for joining us today.

## SPEAKER_01
**Time:** [5.5s - 12.8s]

Thanks for having me. I'm excited to discuss our new project.
```

---

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `process` | Transcribe single audio file | `localtranscribe process audio.mp3` |
| `batch` | Process multiple files | `localtranscribe batch ./folder/` |
| `doctor` | Verify system setup | `localtranscribe doctor` |
| `label` | Replace speaker IDs with names | `localtranscribe label output.md` |
| `version` | Show version information | `localtranscribe version` |
| `config` | Manage configuration | `localtranscribe config show` |

Run `localtranscribe --help` or `localtranscribe <command> --help` for detailed options.

---

## Model Selection Guide

Choose the right Whisper model for your needs:

| Model | Speed | Quality | RAM | Use Case |
|-------|-------|---------|-----|----------|
| **tiny** | Fastest | Basic | 1GB | Quick drafts, testing |
| **base** | Fast | Good | 1GB | **Most use cases** |
| **small** | Moderate | Better | 2GB | Professional work |
| **medium** | Slow | Excellent | 5GB | Publication quality |
| **large** | Very slow | Best | 10GB | Maximum accuracy |

**Performance on M2 Mac (10-minute audio):**
- `tiny`: ~30 seconds
- `base`: ~2 minutes  ← **Recommended starting point**
- `small`: ~5 minutes
- `medium`: ~10 minutes

---

## System Requirements

**Recommended:**
- Mac with Apple Silicon (M1/M2/M3/M4)
- 16GB RAM
- 10GB free disk space
- macOS 12.0 or later

**Minimum:**
- Any Mac with Python 3.9+
- 8GB RAM
- 5GB free disk space
- macOS 11.0 or later

**Supported Audio Formats:**
- Audio: MP3, WAV, OGG, M4A, FLAC, AAC, WMA, OPUS
- Video: MP4, MOV, AVI, MKV, WEBM (audio will be extracted)

---

## How It Works

LocalTranscribe uses a three-stage pipeline:

### 1. Speaker Diarization (pyannote.audio)
- Analyzes audio waveform patterns
- Identifies distinct speakers
- Creates precise speaker timeline
- Optimized for 2-10 speakers

### 2. Speech-to-Text (Whisper)
- Converts speech to text using OpenAI's Whisper
- Automatically detects language
- Handles accents and background noise
- Creates timestamped segments

### 3. Intelligent Combination
- Aligns speaker labels with transcript
- Matches timestamps accurately
- Formats output for readability
- Generates multiple export formats

**Technologies:**
- [Whisper](https://github.com/openai/whisper) - State-of-the-art speech recognition
- [MLX-Whisper](https://github.com/ml-explore/mlx-examples) - Apple Silicon optimization
- [Pyannote.audio](https://github.com/pyannote/pyannote-audio) - Speaker diarization
- [Typer](https://typer.tiangolo.com/) - Modern CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output

---

## Documentation

📚 **[SDK Reference](docs/SDK_REFERENCE.md)** - Python API documentation  
🐛 **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions  
📝 **[Changelog](docs/CHANGELOG.md)** - Version history and updates  
🚀 **[Contributing Guide](CONTRIBUTING.md)** - How to contribute  

---

## Troubleshooting

### Common Issues

**Command not found after installation:**
```bash
# Ensure package is installed
pip install --upgrade localtranscribe

# If using virtual environment, activate it first
source .venv/bin/activate
```

**HuggingFace authentication error:**
```bash
# Verify token is correctly set
cat .env

# Should show: HUGGINGFACE_TOKEN=hf_...
# Make sure you accepted both model licenses
```

**Slow processing:**
```bash
# Use a faster model
localtranscribe process audio.mp3 --model tiny

# Skip diarization for single speaker
localtranscribe process audio.mp3 --skip-diarization
```

**Run system check:**
```bash
localtranscribe doctor
```

This command diagnoses common setup issues and suggests fixes.

**[→ Full Troubleshooting Guide](docs/TROUBLESHOOTING.md)**

---

## What's New

### v2.0.2b1 (Current)
- ✅ Updated package description and metadata
- ✅ Enhanced README with PyPI link
- ✅ Professional documentation polish

### v2.0.1-beta
- ✅ Published to PyPI - Install with `pip install localtranscribe`
- ✅ Fixed pyannote.audio 3.x API compatibility
- ✅ Updated documentation for model licenses

### v2.0.0-beta
- ✅ Complete rewrite with modern CLI
- ✅ Python SDK for programmatic use
- ✅ Batch processing support
- ✅ System health checks with `doctor` command
- ✅ Modular architecture

**[→ Full Changelog](docs/CHANGELOG.md)**

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Check existing issues** at [github.com/aporb/LocalTranscribe/issues](https://github.com/aporb/LocalTranscribe/issues)
2. **Fork the repository** and create your feature branch
3. **Make your changes** following the existing code style
4. **Add tests** if applicable
5. **Submit a pull request** with a clear description

**Development Setup:**
```bash
git clone https://github.com/aporb/LocalTranscribe.git
cd LocalTranscribe
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## License

MIT License - Free for personal and commercial use.

See [LICENSE](LICENSE) for full details.

---

## Support

**Need help?**

1. Run `localtranscribe doctor` to check your setup
2. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. Search [existing issues](https://github.com/aporb/LocalTranscribe/issues)
4. Open a [new issue](https://github.com/aporb/LocalTranscribe/issues/new) with:
   - Output from `localtranscribe doctor`
   - Error message or unexpected behavior
   - Your system info (OS, Python version)

---

## Acknowledgments

LocalTranscribe builds on excellent open-source work:

- **OpenAI** - Whisper speech recognition model
- **Apple** - MLX framework for Metal acceleration
- **Pyannote team** - Speaker diarization models
- **HuggingFace** - Model hosting and distribution

---

<div align="center">

**[⭐ Star on GitHub](https://github.com/aporb/LocalTranscribe)** • **[🐛 Report Bug](https://github.com/aporb/LocalTranscribe/issues)** • **[💡 Request Feature](https://github.com/aporb/LocalTranscribe/issues)**

Made for privacy-conscious professionals who value data ownership.

*Transform audio to text. Know who said what. Keep it private.*

</div>
