# LocalTranscribe

**Turn audio into speaker-labeled transcripts. Entirely offline. One command.**

Transform recordings into detailed transcripts showing who said what and when—all on your Mac, no cloud services required.

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0--beta-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)
![License](https://img.shields.io/badge/license-MIT-orange)

[Quick Start](#quick-start) • [Examples](#examples) • [SDK](docs/SDK_REFERENCE.md) • [Troubleshooting](docs/TROUBLESHOOTING.md)

</div>

---

## Why LocalTranscribe?

| Feature | LocalTranscribe | Cloud Services |
|---------|----------------|----------------|
| **Privacy** | 100% offline | Data uploaded to servers |
| **Cost** | Free forever | $10-50/month |
| **Speaker ID** | Automatic | Often extra cost |
| **Speed (M1/M2)** | Real-time to 2x | Depends on upload |
| **Quality** | OpenAI Whisper | Varies |

**Built for:** Researchers, podcasters, journalists, lawyers, content creators—anyone who needs accurate transcripts with speaker labels and complete privacy.

---

## Quick Start

### 1. Install

```bash
# Clone repository
git clone https://github.com/yourusername/transcribe-diarization.git
cd transcribe-diarization

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

### 2. Setup HuggingFace Token (One-Time)

Required for speaker diarization:

1. **Get token** (free): https://huggingface.co/settings/tokens
2. **Accept model licenses** (required for both models):
   - Main: https://huggingface.co/pyannote/speaker-diarization-3.1
   - Dependency: https://huggingface.co/pyannote/segmentation-3.0
3. **Add to project**:
   ```bash
   echo "HUGGINGFACE_TOKEN=hf_your_token_here" > .env
   ```

### 3. Process Audio

```bash
localtranscribe process your-audio.mp3
```

**That's it!** Results appear in `./output/` with:
- Speaker labels (who spoke)
- Timestamps (when they spoke)
- Full transcript (what they said)

---

## Examples

### Basic Usage

```bash
# Transcribe with automatic settings
localtranscribe process meeting.mp3

# Know how many speakers? Tell it for better accuracy
localtranscribe process interview.wav --speakers 2

# Use larger model for higher quality
localtranscribe process podcast.m4a --model medium

# Save to custom location
localtranscribe process audio.mp3 --output ./results/
```

### Batch Processing

```bash
# Process entire folder
localtranscribe batch ./audio-files/ --workers 2

# With custom settings
localtranscribe batch ./recordings/ --model small --output ./transcripts/
```

### Single-Speaker Content

```bash
# Skip speaker detection for faster processing
localtranscribe process lecture.mp3 --skip-diarization
```

### Advanced Options

```bash
localtranscribe process audio.mp3 \
  --model medium \              # Model size: tiny|base|small|medium|large
  --speakers 3 \                # Number of speakers (if known)
  --language en \               # Force language
  --format txt json srt \       # Output formats
  --output ./results/ \         # Output directory
  --verbose                     # Show detailed progress
```

---

## Python SDK

Use programmatically in your Python projects:

```python
from localtranscribe import LocalTranscribe

# Initialize
lt = LocalTranscribe(model_size="base", num_speakers=2)

# Process single file
result = lt.process("meeting.mp3")
print(result.transcript)
print(f"Found {result.num_speakers} speakers")

# Access detailed segments
for segment in result.segments:
    print(f"[{segment.speaker}] ({segment.start:.1f}s): {segment.text}")

# Batch processing
results = lt.process_batch("./audio-files/", max_workers=4)
print(f"Processed {results.successful}/{results.total} files")

# Handle errors
for failed in results.get_failed():
    print(f"Failed: {failed.audio_file} - {failed.error}")
```

**[→ Full SDK Documentation](docs/SDK_REFERENCE.md)**

---

## Commands

| Command | Description |
|---------|-------------|
| `process` | Transcribe single audio file |
| `batch` | Process multiple files |
| `doctor` | Verify installation and system setup |
| `label` | Replace generic speaker IDs with real names |
| `version` | Show version and system info |
| `config` | Manage configuration |

Get help: `localtranscribe --help` or `localtranscribe <command> --help`

---

## Output Formats

Every run creates multiple files for different use cases:

| Format | File | Best For |
|--------|------|----------|
| **Markdown** | `*_combined.md` | Reading, documentation, sharing |
| **Plain Text** | `*_transcript.txt` | Simple text analysis |
| **JSON** | `*_transcript.json` | Programming, data processing |
| **SRT** | `*_transcript.srt` | Video subtitles |

**Combined transcript includes:**
- Speaker labels (SPEAKER_00, SPEAKER_01, etc.)
- Timestamp ranges for each speaker turn
- Full transcript with proper formatting
- Speaker statistics (who spoke most, how long)

---

## System Requirements

**Recommended:**
- Mac with Apple Silicon (M1/M2/M3/M4)
- 16GB RAM
- 10GB free space
- macOS 12.0+

**Minimum:**
- Any Mac with Python 3.9+
- 8GB RAM
- 5GB free space

**Performance (10-minute audio on M2):**
- `tiny` model: ~30 seconds
- `base` model: ~2 minutes
- `small` model: ~5 minutes
- `medium` model: ~10 minutes

---

## Model Selection Guide

| Model | Speed | Quality | RAM | Best For |
|-------|-------|---------|-----|----------|
| **tiny** | Fastest | Basic | 1GB | Quick drafts, testing |
| **base** | Fast | Good | 1GB | Most use cases |
| **small** | Moderate | Better | 2GB | Professional work |
| **medium** | Slow | Best | 5GB | Publication-quality |
| **large** | Very slow | Best+ | 10GB | Maximum accuracy |

**Recommendation:** Start with `base`, upgrade to `medium` if accuracy matters more than speed.

---

## What's New in v2.0

Complete rewrite focused on usability:

**Before (v1.x):** Three manual steps
```bash
cd scripts
python3 diarization.py      # Step 1
python3 transcription.py    # Step 2
python3 combine.py          # Step 3
```

**Now (v2.0):** One command
```bash
localtranscribe process audio.mp3
```

**Other improvements:**
- Professional CLI with helpful error messages
- Python SDK for programmatic use
- Batch processing support
- Health check (`doctor` command)
- Modular architecture
- Beautiful terminal output

**[→ Full Changelog](docs/CHANGELOG.md)**

---

## Installation Options

### Option 1: Development (Recommended)

```bash
git clone https://github.com/yourusername/transcribe-diarization.git
cd transcribe-diarization
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Option 2: PyPI (Coming Soon)

```bash
# When published
pip install localtranscribe

# With Apple Silicon optimization
pip install localtranscribe[mlx]
```

---

## Troubleshooting

### Common Issues

**Command not found:**
```bash
source .venv/bin/activate  # Activate virtual environment first
```

**HuggingFace token error:**
```bash
# Check .env file exists and has correct format
cat .env
# Should show: HUGGINGFACE_TOKEN="hf_..."
```

**Slow processing:**
```bash
localtranscribe process audio.mp3 --model tiny  # Use faster model
```

**Run health check:**
```bash
localtranscribe doctor  # Diagnoses setup issues
```

**[→ Full Troubleshooting Guide](docs/TROUBLESHOOTING.md)**

---

## How It Works

1. **Speaker Diarization** (pyannote.audio)
   - Analyzes audio waveforms
   - Identifies when different speakers talk
   - Creates speaker timeline

2. **Speech-to-Text** (Whisper)
   - Converts speech to text
   - Detects language automatically
   - Creates timestamped segments

3. **Intelligent Combination**
   - Matches speaker labels to transcript segments
   - Aligns timestamps
   - Generates formatted output

**Technology:**
- [Whisper](https://github.com/openai/whisper) - OpenAI's speech recognition
- [MLX-Whisper](https://github.com/ml-explore/mlx-examples) - Apple Silicon optimization
- [Pyannote](https://github.com/pyannote/pyannote-audio) - Speaker diarization
- [Typer](https://typer.tiangolo.com/) - Modern CLI
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output

---

## Documentation

📚 **[SDK Reference](docs/SDK_REFERENCE.md)** - Python API for developers
🐛 **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues & solutions
📝 **[Changelog](docs/CHANGELOG.md)** - Version history
🚀 **[PyPI Release Guide](docs/PYPI_RELEASE.md)** - For maintainers

---

## Roadmap

**v2.0-beta (Current):**
- ✅ Modern CLI
- ✅ Python SDK
- ✅ Batch processing
- ✅ Health checks

**v2.1 (Next):**
- [ ] Interactive speaker labeling (replace SPEAKER_00 with names)
- [ ] Progress bars for large files
- [ ] Resume interrupted jobs
- [ ] Audio quality analysis

**v3.0 (Future):**
- [ ] Real-time transcription
- [ ] Web interface
- [ ] Docker support
- [ ] Cloud sync (optional)

---

## Contributing

Contributions welcome! Please:

1. Check [existing issues](https://github.com/yourusername/transcribe-diarization/issues)
2. Fork the repository
3. Create feature branch (`git checkout -b feature/amazing-feature`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

---

## License

MIT License - free for personal and commercial use.

---

## Support

**Need help?**

1. Run `localtranscribe doctor` to check your setup
2. Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. Search [existing issues](https://github.com/yourusername/transcribe-diarization/issues)
4. Open new issue with `doctor` output and error message

---

## Credits

Built by the LocalTranscribe community.

**Special thanks:**
- **OpenAI** - Whisper model
- **Apple** - MLX framework
- **Pyannote team** - Speaker diarization models
- **HuggingFace** - Model hosting

---

<div align="center">

**[⭐ Star on GitHub](https://github.com/yourusername/transcribe-diarization)** • **[🐛 Report Bug](https://github.com/yourusername/transcribe-diarization/issues)** • **[💡 Request Feature](https://github.com/yourusername/transcribe-diarization/issues)**

Made with ❤️ for privacy-conscious professionals

*Transform audio to text. Know who said what. Keep it private.*

</div>
