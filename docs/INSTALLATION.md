# Installation Guide

Complete step-by-step installation instructions for Transcribe-Diarization.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installing Prerequisites](#installing-prerequisites)
- [Setting Up Python Environment](#setting-up-python-environment)
- [Installing Dependencies](#installing-dependencies)
- [Configuring Hugging Face](#configuring-hugging-face)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting Installation](#troubleshooting-installation)

## System Requirements

### Recommended Configuration
- **OS**: macOS 12.0 (Monterey) or later
- **Hardware**: Apple Silicon (M1/M2/M3/M4 Pro recommended)
- **RAM**: 16GB or more
- **Storage**: 10GB free space
- **Python**: 3.8, 3.9, 3.10, or 3.11

### Minimum Configuration
- **OS**: macOS 10.15 (Catalina) or later
- **Hardware**: Any Mac with Python support
- **RAM**: 8GB
- **Storage**: 5GB free space
- **Python**: 3.8+

## Installing Prerequisites

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python 3

```bash
# Check if Python 3 is installed
python3 --version

# If not installed, install via Homebrew
brew install python@3.11
```

### 3. Install FFmpeg

FFmpeg is required for audio format conversion:

```bash
brew install ffmpeg
```

Verify installation:

```bash
ffmpeg -version
```

## Setting Up Python Environment

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/aporb/LocalTranscribe.git
cd LocalTranscribe
```

### 2. Create Virtual Environment

Using a virtual environment is strongly recommended:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Your terminal prompt should now show (.venv)
```

To deactivate the virtual environment later:

```bash
deactivate
```

## Installing Dependencies

### Option 1: Install All Dependencies (Recommended)

This installs all implementations and options:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 2: Install Specific Whisper Implementation

#### For MLX-Whisper (Best for Apple Silicon)

```bash
# Install core dependencies first
pip install torch torchaudio pyannote-audio pydub soundfile librosa python-dotenv tqdm rich

# Install MLX-Whisper
pip install mlx-whisper mlx
```

#### For Faster-Whisper

```bash
# Install core dependencies first
pip install torch torchaudio pyannote-audio pydub soundfile librosa python-dotenv tqdm rich

# Install Faster-Whisper
pip install faster-whisper
```

#### For Original Whisper

```bash
# Install core dependencies first
pip install torch torchaudio pyannote-audio pydub soundfile librosa python-dotenv tqdm rich

# Install OpenAI Whisper
pip install openai-whisper
```

## Configuring Hugging Face

### 1. Create Hugging Face Account

1. Go to [huggingface.co](https://huggingface.co/)
2. Click "Sign Up" and create a free account
3. Verify your email address

### 2. Generate Access Token

1. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "transcribe-diarization")
4. Select "Read" permissions
5. Click "Generate token"
6. Copy the token (you'll need it in the next step)

### 3. Accept Model License

1. Visit [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
2. Read and accept the license agreement
3. This is required for the diarization model to work

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
nano .env  # or use your preferred text editor

# Replace 'your_token_here' with your actual token
HUGGINGFACE_TOKEN="hf_YourActualTokenHere"

# Save and exit (Ctrl+X, then Y, then Enter in nano)
```

## Verifying Installation

### 1. Check Python Packages

```bash
# Activate virtual environment if not already activated
source .venv/bin/activate

# Check installed packages
pip list | grep -E "torch|whisper|pyannote|mlx"
```

You should see packages like:
- `torch`
- `torchaudio`
- `pyannote-audio`
- `mlx-whisper` (if installed)
- `openai-whisper` (if installed)

### 2. Check PyTorch MPS Support

```bash
python3 -c "import torch; print('MPS Available:', torch.backends.mps.is_available())"
```

Expected output on Apple Silicon:
```
MPS Available: True
```

### 3. Check MLX Support (if installed)

```bash
python3 -c "import mlx.core as mx; print('Metal Available:', mx.metal.is_available())"
```

Expected output on Apple Silicon:
```
Metal Available: True
```

### 4. Test Whisper Implementation

```bash
cd scripts
python3 -c "
import sys
sys.path.insert(0, '.')
from transcription import check_implementations
impl = check_implementations()
print(f'Best implementation: {impl}')
"
```

### 5. Verify Directory Structure

```bash
# Return to project root
cd ..

# Check directory structure
ls -la
```

You should see:
- `input/` directory
- `output/` directory
- `scripts/` directory
- `docs/` directory
- `.env` file
- `requirements.txt`

## Troubleshooting Installation

### Issue: "Command not found: pip"

**Solution**: Use `pip3` instead:
```bash
pip3 install -r requirements.txt
```

### Issue: "ERROR: Could not build wheels for pyannote-audio"

**Solution**: Install Xcode Command Line Tools:
```bash
xcode-select --install
```

### Issue: "ModuleNotFoundError: No module named 'torch'"

**Solution**: Ensure virtual environment is activated and reinstall:
```bash
source .venv/bin/activate
pip install torch torchaudio
```

### Issue: "MPS backend not available"

**Cause**: You might be on Intel Mac or older macOS.

**Solution**: The tool will automatically fall back to CPU mode. For better performance, consider:
1. Updating to latest macOS
2. Using MLX-Whisper if on Apple Silicon
3. Using CPU with optimized thread settings

### Issue: FFmpeg not found

**Solution**: Install FFmpeg:
```bash
brew install ffmpeg
```

If Homebrew isn't working:
```bash
# Download FFmpeg binary from ffmpeg.org
# Or use MacPorts: sudo port install ffmpeg
```

### Issue: Hugging Face token not working

**Solution**:
1. Check that you've accepted the pyannote model license
2. Verify token has "Read" permissions
3. Ensure no extra spaces in `.env` file
4. Token format: `HUGGINGFACE_TOKEN="hf_..."`

### Issue: Virtual environment activation fails

**Solution**:
```bash
# Remove old virtual environment
rm -rf .venv

# Create new one
python3 -m venv .venv

# Activate
source .venv/bin/activate
```

## Next Steps

Once installation is complete:

1. Read the [Configuration Guide](CONFIGURATION.md) for advanced settings
2. Follow the [Usage Guide](USAGE.md) to process your first audio file
3. Check [Troubleshooting Guide](TROUBLESHOOTING.md) if you encounter issues

## Getting Help

If you continue to have installation issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [GitHub Issues](https://github.com/aporb/LocalTranscribe/issues)
3. Open a new issue with:
   - Your OS version
   - Python version (`python3 --version`)
   - Error messages
   - Steps you've already tried
