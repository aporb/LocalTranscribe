# LocalTranscribe

> **Alpha Release** - A command-line tool for local audio transcription with speaker diarization, optimized for Apple Silicon (M4 Pro)

Transform your audio recordings into detailed, speaker-labeled transcripts entirely offline on your Mac. This tool combines state-of-the-art speech recognition with speaker diarization to identify who said what and when.

## Features

- **🎯 Speaker Diarization** - Automatically identify and separate different speakers
- **📝 Speech-to-Text** - High-quality transcription using Whisper models
- **🍎 Apple Silicon Optimized** - Leverages Metal Performance Shaders (MPS) for GPU acceleration on M4 Pro
- **🔒 100% Offline** - All processing done locally, no data sent to the cloud
- **📊 Multiple Output Formats** - Generate TXT, SRT, JSON, and Markdown files
- **⚡ Fast Processing** - Optimized for macOS with MLX-Whisper integration
- **🎚️ Flexible Configuration** - Support for multiple Whisper implementations and model sizes
- **📈 Confidence Scoring** - Quality metrics for both transcription and speaker assignment

## Prerequisites

- macOS (Apple Silicon recommended, tested on M4 Pro)
- Python 3.8+
- FFmpeg (for audio format conversion)
- Hugging Face account (free) for speaker diarization models

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/aporb/LocalTranscribe.git
cd LocalTranscribe

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install FFmpeg (required for audio processing)
brew install ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Install MLX-Whisper (recommended for Apple Silicon)
pip install mlx-whisper mlx
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Hugging Face token
# Get your token from: https://huggingface.co/settings/tokens
```

### 3. Usage

```bash
# Place your audio file in the input/ directory
cp your_audio.mp3 input/audio.ogg

# Run speaker diarization
cd scripts
python3 diarization.py

# Run transcription
python3 transcription.py

# Combine results
python3 combine.py
```

Your results will be in the `output/` directory!

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Usage Guide](docs/USAGE.md)** - Step-by-step examples and workflows
- **[Configuration](docs/CONFIGURATION.md)** - Environment variables and settings
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Output Formats

The tool generates multiple output formats for different use cases:

| Format | Description | Use Case |
|--------|-------------|----------|
| **TXT** | Plain text transcript | Simple reading, text analysis |
| **SRT** | Subtitle file with timestamps | Video subtitles, time-synced viewing |
| **JSON** | Structured data with metadata | Programmatic access, data processing |
| **MD** | Markdown with formatting | Documentation, easy reading with structure |

### Combined Output

The combined transcript includes:
- Speaker-labeled dialogue
- Timestamp ranges for each speaker turn
- Confidence scores for speaker assignment
- Audio quality metrics
- Speaking time distribution statistics

## Project Structure

```
LocalTranscribe/
├── scripts/
│   ├── transcription.py    # Speech-to-text processing
│   ├── diarization.py      # Speaker identification
│   └── combine.py          # Merge diarization + transcription
├── input/                  # Place your audio files here
├── output/                 # Generated transcripts appear here
├── docs/                   # Detailed documentation
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## Technology Stack

- **[Whisper](https://github.com/openai/whisper)** - OpenAI's speech recognition model
- **[MLX-Whisper](https://github.com/ml-explore/mlx-examples)** - Apple Silicon optimized Whisper
- **[Pyannote Audio](https://github.com/pyannote/pyannote-audio)** - Speaker diarization toolkit
- **[PyTorch](https://pytorch.org/)** - Deep learning framework with MPS support
- **[Pydub](https://github.com/jiaaro/pydub)** - Audio manipulation library

## System Requirements

### Recommended
- Apple Silicon Mac (M1, M2, M3, M4)
- 16GB RAM or more
- 10GB free disk space (for models and processing)
- macOS 12.0 (Monterey) or later

### Minimum
- Any Mac with Python 3.8+
- 8GB RAM
- 5GB free disk space

## Known Limitations (Alpha)

- Audio files must be manually placed in `input/` directory
- File names are currently hardcoded in scripts
- No batch processing support yet
- Limited error recovery in pipeline
- Speaker labels are generic (SPEAKER_00, SPEAKER_01, etc.)

## Roadmap

- [ ] CLI interface with argument parsing
- [ ] Batch processing support
- [ ] Custom speaker labels
- [ ] Real-time processing mode
- [ ] Web UI
- [ ] Docker containerization
- [ ] Additional language support optimization

## Contributing

This is an early alpha project. Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for the Whisper model
- Apple for MLX framework
- Pyannote team for speaker diarization models
- Hugging Face for model hosting infrastructure

## Support

If you encounter issues or have questions:

1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/aporb/LocalTranscribe/issues)
3. Open a [new issue](https://github.com/aporb/LocalTranscribe/issues/new) with details

---

**Note**: This is an alpha release under active development. Features and APIs may change.
