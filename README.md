# LocalTranscribe

> **v2.0** - Professional CLI tool for local audio transcription with speaker diarization, optimized for Apple Silicon

Transform your audio recordings into detailed, speaker-labeled transcripts entirely offline on your Mac with a single command. LocalTranscribe combines state-of-the-art speech recognition with speaker diarization to identify who said what and when.

## Features

- **🎯 Speaker Diarization** - Automatically identify and separate different speakers
- **📝 Speech-to-Text** - High-quality transcription using Whisper models
- **🚀 Single Command Workflow** - Process audio files with one simple command
- **💻 Professional CLI** - Type-safe commands with beautiful terminal UI
- **🍎 Apple Silicon Optimized** - Leverages Metal Performance Shaders (MPS) for GPU acceleration
- **🔒 100% Offline** - All processing done locally, no data sent to the cloud
- **📊 Multiple Output Formats** - Generate TXT, SRT, JSON, and Markdown files
- **⚡ Fast Processing** - Optimized for macOS with MLX-Whisper integration
- **🎚️ Flexible Configuration** - YAML config files + environment variables + CLI arguments
- **🏥 Health Checks** - Built-in doctor command to verify system setup
- **📈 Confidence Scoring** - Quality metrics for both transcription and speaker assignment
- **🛠️ Auto Installation** - Guided setup script for all dependencies

## Prerequisites

- macOS (Apple Silicon recommended, tested on M1/M2/M3/M4)
- Python 3.9+
- FFmpeg (auto-installed by setup script)
- Hugging Face account (free) for speaker diarization models

## Quick Start

### Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/aporb/LocalTranscribe.git
cd LocalTranscribe

# Run the installation script
./install.sh
```

The installation script will:
- ✅ Check Python version
- ✅ Install Homebrew (if needed)
- ✅ Install FFmpeg
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Configure HuggingFace token
- ✅ Run health check

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/aporb/LocalTranscribe.git
cd LocalTranscribe

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt

# Add your HuggingFace token to .env
echo "HUGGINGFACE_TOKEN=your_token_here" > .env

# Verify installation
localtranscribe doctor
```

### Basic Usage

Process an audio file with a single command:

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Process audio file
localtranscribe process audio.mp3

# Process with options
localtranscribe process audio.mp3 -o results/ -m small -s 2

# Transcription only (no diarization)
localtranscribe process audio.mp3 --skip-diarization
```

Your results will be in the `./output/` directory!

## CLI Commands

LocalTranscribe provides several commands for different tasks:

### `process` - Main Processing Command

```bash
# Basic usage
localtranscribe process audio.mp3

# With all options
localtranscribe process audio.mp3 \
  --output results/ \
  --model small \
  --speakers 2 \
  --language en \
  --format txt json md \
  --verbose

# Available options:
#   -o, --output PATH            Output directory
#   -m, --model SIZE             Model size: tiny, base, small, medium, large
#   -s, --speakers N             Exact number of speakers
#   --min-speakers N             Minimum speakers
#   --max-speakers N             Maximum speakers
#   -l, --language CODE          Force language (en, es, fr, etc.)
#   -i, --implementation TYPE    Whisper implementation: auto, mlx, faster, original
#   --skip-diarization           Skip speaker diarization
#   -f, --format FORMAT          Output formats (can specify multiple)
#   --hf-token TOKEN             HuggingFace token (overrides .env)
#   -v, --verbose                Enable verbose output
```

### `doctor` - Health Check

Verify your system setup and dependencies:

```bash
# Basic health check
localtranscribe doctor

# Detailed diagnostic information
localtranscribe doctor -v
```

The doctor command checks:
- ✅ Python version
- ✅ Required dependencies (PyTorch, Pyannote, etc.)
- ✅ Optional dependencies (MLX-Whisper, Faster-Whisper)
- ✅ HuggingFace token configuration
- ✅ GPU/MPS availability
- ✅ FFmpeg installation

### `config-show` - View Configuration

Display current configuration settings:

```bash
localtranscribe config-show
```

### `version` - Show Version

Display LocalTranscribe version and system information:

```bash
localtranscribe version
```

## Configuration

LocalTranscribe supports multiple configuration methods (priority order):

1. **Command-line arguments** (highest priority)
2. **Environment variables** (`LOCALTRANSCRIBE_*`)
3. **Configuration file** (YAML)
4. **Default values** (lowest priority)

### Configuration File

Create a `localtranscribe.yaml` file in your project directory or `~/.localtranscribe/config.yaml`:

```yaml
model:
  whisper_size: base
  whisper_implementation: auto

processing:
  skip_diarization: false
  language: null  # Auto-detect

output:
  directory: ./output
  formats:
    - txt
    - json
    - md
  include_confidence: true
```

See `config.yaml.example` for all available options.

### Environment Variables

Set environment variables with the `LOCALTRANSCRIBE_` prefix:

```bash
export LOCALTRANSCRIBE_MODEL_WHISPER_SIZE=small
export LOCALTRANSCRIBE_OUTPUT_DIRECTORY=./results
export LOCALTRANSCRIBE_PROCESSING_LANGUAGE=en
export HUGGINGFACE_TOKEN=your_token_here
```

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
├── localtranscribe/          # Main package
│   ├── cli.py               # CLI interface
│   ├── core/                # Core processing modules
│   │   ├── diarization.py   # Speaker identification
│   │   ├── transcription.py # Speech-to-text
│   │   ├── combination.py   # Result merging
│   │   └── path_resolver.py # Smart path resolution
│   ├── pipeline/            # Pipeline orchestration
│   │   └── orchestrator.py  # Main pipeline controller
│   ├── config/              # Configuration management
│   │   ├── defaults.py      # Default settings
│   │   └── loader.py        # Config loading
│   ├── health/              # Health check system
│   │   └── doctor.py        # System validation
│   └── utils/               # Utilities
│       └── errors.py        # Custom exceptions
├── scripts/                 # Legacy scripts (deprecated)
├── docs/                    # Documentation
├── input/                   # Default audio input directory
├── output/                  # Default output directory
├── install.sh               # Installation script
├── pyproject.toml           # Package configuration
├── requirements.txt         # Dependencies
└── config.yaml.example      # Configuration template
```

## Technology Stack

- **[Whisper](https://github.com/openai/whisper)** - OpenAI's speech recognition model
- **[MLX-Whisper](https://github.com/ml-explore/mlx-examples)** - Apple Silicon optimized Whisper
- **[Pyannote Audio](https://github.com/pyannote/pyannote-audio)** - Speaker diarization toolkit
- **[PyTorch](https://pytorch.org/)** - Deep learning framework with MPS support
- **[Typer](https://typer.tiangolo.com/)** - Modern CLI framework
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal output
- **[Pydub](https://github.com/jiaaro/pydub)** - Audio manipulation library

## System Requirements

### Recommended
- Apple Silicon Mac (M1, M2, M3, M4)
- 16GB RAM or more
- 10GB free disk space (for models and processing)
- macOS 12.0 (Monterey) or later

### Minimum
- Any Mac with Python 3.9+
- 8GB RAM
- 5GB free disk space

## What's New in v2.0

✨ **Major improvements from alpha:**

- ✅ **CLI Interface** - Professional command-line tool with Typer
- ✅ **Single Command Processing** - No more manual 3-step workflow
- ✅ **Smart Path Resolution** - Works with any audio file location
- ✅ **Configuration System** - YAML files, environment variables, CLI arguments
- ✅ **Health Checks** - Built-in doctor command for system validation
- ✅ **Comprehensive Error Messages** - Helpful suggestions and context
- ✅ **Installation Script** - Automated setup for all dependencies
- ✅ **Package Structure** - Proper Python package with modular design

## Known Limitations

- Speaker labels remain generic (SPEAKER_00, SPEAKER_01, etc.)
- No batch processing for multiple files yet
- No real-time processing mode

## Roadmap

### Phase 2 (v2.1)
- [ ] Batch processing support for multiple files
- [ ] Custom speaker label assignment
- [ ] Enhanced audio quality analysis
- [ ] Performance profiling and optimization

### Phase 3 (Future)
- [ ] Real-time processing mode
- [ ] Web UI for browser-based access
- [ ] Docker containerization
- [ ] API server mode
- [ ] Additional language support optimization
- [ ] Speaker identification (not just diarization)

## Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for the Whisper model
- Apple for MLX framework
- Pyannote team for speaker diarization models
- Hugging Face for model hosting infrastructure

## Support

If you encounter issues or have questions:

1. Run `localtranscribe doctor` to check your system setup
2. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. Review the [Migration Guide](docs/MIGRATION_GUIDE.md) if upgrading from alpha
4. Search [existing issues](https://github.com/aporb/LocalTranscribe/issues)
5. Open a [new issue](https://github.com/aporb/LocalTranscribe/issues/new) with details

---

**LocalTranscribe v2.0** - Transform audio to text with speaker labels, entirely offline on your Mac.
