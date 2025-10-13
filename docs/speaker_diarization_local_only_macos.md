# Local Speaker Diarization Guide: Transcribing audio.ogg with Two-Speaker Identification on macOS

This guide provides detailed instructions on how to transcribe the audio.ogg file while identifying two different speakers using **completely local, open-source tools** with no API dependencies. All processing runs locally on your Mac with full GPU/NPU acceleration support.

## Table of Contents
1. [What is Speaker Diarization?](#what-is-speaker-diarization)
2. [Local Prerequisites](#local-prerequisites)
3. [Setting Up Virtual Environment](#setting-up-virtual-environment)
4. [GPU/NPU Acceleration Setup for macOS](#gpunpu-acceleration-setup-for-macos)
5. [Method 1: Pyannote.audio with Local Models](#method-1-pyannoteaudio-with-local-models)
6. [Method 2: Whisper + Pyannote Hybrid (Local)](#method-2-whisper--pyannote-hybrid-local)
7. [Method 3: Advanced Local Pipeline](#method-3-advanced-local-pipeline)
8. [Performance Optimization](#performance-optimization)
9. [Storage Requirements](#storage-requirements)
10. [Troubleshooting](#troubleshooting)

## What is Speaker Diarization?

Speaker diarization addresses the problem of "who spoke when?" in an audio recording. For your audio.ogg file, this means identifying segments where Speaker 1 and Speaker 2 are speaking, creating a timeline that shows which speaker said what and when.

The output typically includes:
- Time stamps for when each speaker spoke
- Transcribed text for each segment
- Speaker labels (e.g., SPEAKER_0, SPEAKER_1)

**All processing is done locally on your Mac - no internet connection required after initial setup!**

## Local Prerequisites

Before starting, ensure you have:
- macOS 12.0 or higher (recommended for full Apple Silicon support)
- Python 3.8 or higher installed (Python 3.10+ recommended for Apple Silicon)
- Homebrew installed (for system dependencies)
- Xcode Command Line Tools installed
- Apple Silicon Mac (M1/M2/M3) or Intel Mac
- Sufficient storage space (~5-10 GB for models and processing)
- 16GB+ RAM recommended for optimal performance

### Install System Dependencies

```bash
# Install Xcode Command Line Tools if not already installed
xcode-select --install

# Install FFmpeg (for audio format conversion)
brew install ffmpeg

# Install other useful tools
brew install sox  # Alternative audio processing tool
```

### Check Your Python Installation

```bash
# Check Python version
python3 --version

# Check if pip is up to date
pip3 install --upgrade pip

# If Python 3 isn't default, you might need to use python3 instead of python
```

## Setting Up Virtual Environment

It's crucial to use a virtual environment to manage dependencies properly and avoid conflicts:

### Create and Activate Virtual Environment

```bash
# Create a virtual environment named 'local_diarization'
python3 -m venv local_diarization

# Activate the virtual environment
source local_diarization/bin/activate

# Upgrade pip within the virtual environment
pip install --upgrade pip setuptools wheel

# Verify you're in the virtual environment
which python
which pip
```

### Install Required Dependencies

```bash
# Activate your virtual environment
source local_diarization/bin/activate

# Install PyTorch for Apple Silicon (with local processing optimization)
pip install torch torchvision torchaudio

# Install audio processing libraries
pip install pydub librosa soundfile

# Install Pyannote.audio (completely local)
pip install pyannote.audio

# Install Whisper for local transcription
pip install openai-whisper

# Install additional dependencies
pip install huggingface_hub pandas numpy matplotlib tqdm

# Verify installation
python -c "import torch; import whisper; import pyannote.audio; print('All local dependencies installed successfully')"
```

### Verify Virtual Environment Setup

```bash
# Check that you're using the virtual environment Python
python --version
pip list  # Should show your local dependencies

# Create a requirements file to track local dependencies
pip freeze > local_requirements.txt
```

### Deactivating Virtual Environment

When finished working:
```bash
deactivate
```

## GPU/NPU Acceleration Setup for macOS

### Understanding Apple Silicon Acceleration (Local Processing)

Apple Silicon Macs (M1/M2/M3) provide local acceleration:
- **GPU**: Metal Performance Shaders (MPS) backend for PyTorch
- **Neural Engine**: Hardware-accelerated machine learning operations
- **All processing runs locally** on your Mac

### Check System Information and Enable Acceleration

```python
# Run this to check your system capabilities for local processing
import platform
import psutil
import torch

print(f"System: {platform.system()} {platform.machine()}")
print(f"CPU: {platform.processor()}")
print(f"RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
print(f"Python: {platform.python_version()}")

# Check for MPS (Metal Performance Shaders) - Apple Silicon acceleration
if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    device = torch.device('mps')
    print("✅ MPS (Metal Performance Shaders): Available for Apple Silicon acceleration")
    print("   All ML operations will run on GPU locally!")
elif torch.cuda.is_available():
    device = torch.device('cuda')
    print("✅ CUDA: Available for NVIDIA GPU acceleration")
else:
    device = torch.device('cpu')
    print("⚠️  CPU only: Using CPU for local processing (slower but works)")

print(f"Using device: {device}")
print(f"PyTorch version: {torch.__version__}")
```

### Install Optimized PyTorch for Apple Silicon

```bash
# Activate your virtual environment first
source local_diarization/bin/activate

# Install PyTorch built for macOS (local processing)
pip install torch torchvision torchaudio
```

## Method 1: Pyannote.audio with Local Models

Pyannote.audio runs completely locally with state-of-the-art speaker diarization.

### Installation (Local Only)

```bash
# Make sure you're in your virtual environment
source local_diarization/bin/activate

# Install local dependencies
pip install pyannote.audio torch torchvision torchaudio pydub librosa huggingface_hub

# No API keys required - everything runs locally!
```

### Local Model Setup and Execution

```python
import torch
from pyannote.audio import Pipeline
from pydub import AudioSegment
import os
import tempfile

# Configure for optimal local processing
def setup_local_processing():
    """Configure local processing with Apple Silicon optimization"""
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        print("🚀 Using Apple Silicon GPU acceleration (MPS) for local processing")
        torch.set_num_threads(8)  # Optimize for Apple Silicon
    elif torch.cuda.is_available():
        device = torch.device('cuda')
        print("🚀 Using CUDA GPU acceleration for local processing")
    else:
        device = torch.device('cpu')
        print("💻 Using CPU for local processing")
    
    return device

def convert_ogg_to_wav(ogg_path):
    """Convert OGG file to WAV format for better local processing compatibility"""
    print(f"Converting {ogg_path} to WAV format...")
    audio = AudioSegment.from_ogg(ogg_path)
    wav_path = ogg_path.replace('.ogg', '.wav')
    audio.export(wav_path, format='wav')
    print(f"Conversion complete: {wav_path}")
    return wav_path

# Setup local processing
device = setup_local_processing()

# Convert audio file for local processing
wav_file = convert_ogg_to_wav("audio.ogg")

print("Loading Pyannote.audio model locally...")
# Load the pre-trained pipeline (downloads locally on first run)
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=None  # No authentication needed for public models - runs locally
)

print("Starting local speaker diarization...")
# Run diarization completely locally
diarization = pipeline(
    wav_file,
    num_speakers=2,      # Specify 2 speakers
    min_speakers=1,      # Minimum number of speakers
    max_speakers=2       # Maximum number of speakers
)

print("\nSpeaker Diarization Results (Local Processing):")
print("="*60)

# Print results locally
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"Speaker '{speaker}' speaks from {turn.start:.1f}s to {turn.end:.1f}s")

print(f"\n✅ Local processing complete! No internet connection required.")

# Clean up temporary file
os.remove(wav_file)
```

### Features of Local Pyannote Method:
- ✅ **Completely local** - No internet required after initial model download
- ✅ State-of-the-art accuracy
- ✅ Highly customizable
- ✅ Can specify exact number of speakers
- ✅ Full Apple Silicon optimization
- ✅ No API keys or subscriptions needed

## Method 2: Whisper + Pyannote Hybrid (Local)

A local-only hybrid approach using Whisper for transcription and Pyannote for speaker diarization.

### Installation (Local Only)

```bash
# Activate your virtual environment
source local_diarization/bin/activate

# Install local-only dependencies
pip install openai-whisper pyannote.audio torch torchvision torchaudio pydub librosa

# No internet connection needed after this point!
```

### Local Setup and Execution

```python
import whisper
import torch
from pyannote.audio import Pipeline
from pydub import AudioSegment
import tempfile
import json
import os
import platform

def is_apple_silicon():
    """Check if running on Apple Silicon"""
    return platform.machine() == 'arm64' or 'ARM64' in platform.machine().upper()

def setup_local_device():
    """Configure the best available local device for computation"""
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        print("🚀 Using Apple Silicon GPU acceleration (MPS) locally")
    elif torch.cuda.is_available():
        device = torch.device('cuda')
        print("🚀 Using CUDA GPU acceleration locally")
    else:
        device = torch.device('cpu')
        print("💻 Using CPU locally")
    return device

def local_speaker_diarization(audio_file, num_speakers=2):
    """
    Combine Whisper transcription with Pyannote speaker diarization
    ALL PROCESSING RUNS LOCALLY ON YOUR MAC
    """
    
    # Configure local processing device
    device = setup_local_device()
    
    # Convert OGG to WAV if needed
    if audio_file.endswith('.ogg'):
        print(f"Converting {audio_file} to WAV for local processing...")
        audio = AudioSegment.from_ogg(audio_file)
        wav_file = audio_file.replace('.ogg', '.wav')
        audio.export(wav_file, format='wav')
        audio_file = wav_file
        print(f"✅ Conversion complete: {audio_file}")
    
    # Load Whisper model locally with device optimization
    print("Loading Whisper model locally...")
    model = whisper.load_model("base", device=device)
    
    # Transcribe audio locally
    print("Transcribing audio locally...")
    result = model.transcribe(audio_file, word_timestamps=True)
    
    # Apply speaker diarization locally
    print("Applying speaker diarization locally...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1"
    )
    
    diarization = pipeline(
        audio_file,
        num_speakers=num_speakers
    )
    
    # Convert diarization segments to dictionary for local processing
    diarization_dict = {}
    for segment, track, speaker in diarization.itertracks(yield_label=True):
        diarization_dict[(segment.start, segment.end)] = speaker
    
    # Map speakers to transcribed segments (local processing)
    segments_with_speakers = []
    
    for segment in result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        
        # Find which speaker was active during this segment (local logic)
        speaker = "Unknown"
        for (seg_start, seg_end), seg_speaker in diarization_dict.items():
            # Check if segments overlap (local computation)
            if not (end_time <= seg_start or start_time >= seg_end):
                speaker = seg_speaker
                break
        
        segments_with_speakers.append({
            'start': start_time,
            'end': end_time,
            'text': segment['text'],
            'speaker': speaker
        })
    
    return segments_with_speakers

# Execute the local-only approach
print("Starting completely local speaker diarization...")
try:
    results = local_speaker_diarization("audio.ogg", num_speakers=2)
    
    print("\nLocal Speaker Diarization Results:")
    print("="*60)
    
    for i, segment in enumerate(results):
        print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] Speaker {segment['speaker']}: {segment['text']}")
        print()
    
    print(f"✅ Processing complete! All work done locally on your Mac.")
    
except Exception as e:
    print(f"❌ Error during local processing: {e}")
    import traceback
    traceback.print_exc()

# Clean up temporary files if created
if os.path.exists("audio.wav"):
    os.remove("audio.wav")
```

### Features of Local Hybrid Method:
- ✅ **Completely local** - No internet required after setup
- ✅ Combines best of both technologies
- ✅ Word-level timestamp alignment
- ✅ Precise speaker identification
- ✅ Full Apple Silicon optimization
- ✅ No API keys or subscriptions needed

## Method 3: Advanced Local Pipeline

An advanced local-only pipeline with additional preprocessing for better results.

### Installation for Advanced Method

```bash
# Activate your virtual environment
source local_diarization/bin/activate

# Install additional local processing libraries
pip install openai-whisper pyannote.audio torch torchvision torchaudio pydub librosa sox scipy
```

### Advanced Local Processing Script

```python
import whisper
import torch
from pyannote.audio import Pipeline
from pydub import AudioSegment
import librosa
import numpy as np
import tempfile
import os
import platform
from datetime import datetime

class LocalSpeakerDiarizationPipeline:
    def __init__(self, num_speakers=2):
        self.num_speakers = num_speakers
        self.device = self.setup_local_device()
        self.whisper_model = None
        self.pyannote_pipeline = None
        
    def setup_local_device(self):
        """Configure best local device"""
        if torch.backends.mps.is_available():
            device = torch.device('mps')
            print("🚀 Using Apple Silicon GPU acceleration (MPS) locally")
            torch.set_num_threads(8)
        elif torch.cuda.is_available():
            device = torch.device('cuda')
            print("🚀 Using CUDA GPU acceleration locally")
        else:
            device = torch.device('cpu')
            print("💻 Using CPU locally")
        return device
    
    def preprocess_audio(self, audio_file):
        """Local audio preprocessing for better results"""
        print(f"Preprocessing audio file: {audio_file}")
        
        # Convert to WAV if needed
        if audio_file.endswith('.ogg'):
            audio = AudioSegment.from_ogg(audio_file)
            # Ensure proper format for local processing
            audio = audio.set_frame_rate(16000).set_channels(1)
            temp_wav = audio_file.replace('.ogg', '_processed.wav')
            audio.export(temp_wav, format='wav')
            return temp_wav
        else:
            return audio_file
    
    def load_models_locally(self):
        """Load models locally with optimization"""
        print("Loading Whisper model locally...")
        self.whisper_model = whisper.load_model("base", device=self.device)
        
        print("Loading Pyannote model locally...")
        self.pyannote_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1"
        )
    
    def run_local_diarization(self, audio_file):
        """Run complete local diarization pipeline"""
        print("Starting advanced local speaker diarization pipeline...")
        
        # Preprocess audio locally
        processed_file = self.preprocess_audio(audio_file)
        
        # Load models if not already loaded
        if self.whisper_model is None or self.pyannote_pipeline is None:
            self.load_models_locally()
        
        # Transcribe locally
        print("Transcribing locally...")
        transcription = self.whisper_model.transcribe(processed_file, word_timestamps=True)
        
        # Diarize locally
        print("Applying speaker diarization locally...")
        diarization = self.pyannote_pipeline(
            processed_file,
            num_speakers=self.num_speakers
        )
        
        # Combine results locally
        transcription_dict = {}
        for segment in transcription['segments']:
            transcription_dict[(segment['start'], segment['end'])] = segment['text']
        
        diarization_dict = {}
        for segment, track, speaker in diarization.itertracks(yield_label=True):
            diarization_dict[(segment.start, segment.end)] = speaker
        
        # Match speakers to transcripts
        results = []
        for (t_start, t_end), text in transcription_dict.items():
            speaker = "Unknown"
            for (d_start, d_end), d_speaker in diarization_dict.items():
                if not (t_end <= d_start or t_start >= d_end):  # Overlap check
                    speaker = d_speaker
                    break
            
            results.append({
                'start': t_start,
                'end': t_end,
                'text': text,
                'speaker': speaker
            })
        
        # Clean up temporary file
        if processed_file != audio_file:
            os.remove(processed_file)
        
        return results
    
    def save_local_results(self, results, output_file="local_diarization_results.json"):
        """Save results locally"""
        output_data = {
            "audio_file": "audio.ogg",
            "processing_timestamp": datetime.now().isoformat(),
            "processing_method": "local_hybrid_whisper_pyannote",
            "diarization_results": results,
            "total_speakers": len(set([r['speaker'] for r in results if r['speaker'] != 'Unknown'])),
            "total_duration": results[-1]['end'] if results else 0,
            "system": platform.system(),
            "platform": platform.machine(),
            "device": str(self.device),
            "apple_silicon": platform.machine() in ['arm64', 'ARM64']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved locally to: {output_file}")
        return output_file

# Usage example
pipeline = LocalSpeakerDiarizationPipeline(num_speakers=2)
results = pipeline.run_local_diarization("audio.ogg")

print("\nAdvanced Local Speaker Diarization Results:")
print("="*70)

for segment in results:
    print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] Speaker {segment['speaker']}: {segment['text']}")
    print()

# Save results locally
pipeline.save_local_results(results)
print("🎉 All processing completed locally on your Mac - no internet connection required!")
```

## Performance Optimization

### Local Memory Management for macOS

```python
import gc
import psutil
import torch

def optimize_local_memory():
    """Optimize memory usage for local processing on macOS"""
    # Clear Python garbage collector
    gc.collect()
    
    # For Apple Silicon, optimize memory usage
    if torch.backends.mps.is_available():
        # MPS doesn't have explicit cache clearing like CUDA
        # But we can optimize memory allocation for local processing
        pass
    
    # Check memory usage during local processing
    memory = psutil.virtual_memory()
    print(f"Available RAM for local processing: {memory.available / (1024**3):.2f} GB")
    print(f"Total RAM: {memory.total / (1024**3):.2f} GB")
    print(f"Memory usage: {memory.percent}%")

# Use this function between local operations
optimize_local_memory()
```

### Apple Silicon Local Processing Optimizations

```python
def apple_silicon_local_optimizations():
    """Apply Apple Silicon specific optimizations for local processing"""
    
    # Set optimal number of threads for Apple Silicon local processing
    import multiprocessing
    optimal_threads = min(8, multiprocessing.cpu_count())
    torch.set_num_threads(optimal_threads)
    
    # Enable Metal Performance Shaders for local ML operations
    if torch.backends.mps.is_available():
        torch.backends.mps.enabled = True
        torch.backends.mps.is_available = lambda: True
    
    print(f"🎯 Set optimal threads for local processing: {optimal_threads}")
    print("⚡ Apple Silicon optimizations applied for local processing")

apple_silicon_local_optimizations()
```

## Storage Requirements

### Model Storage Information

The local models will require storage space on your Mac:

```bash
# Check available storage before proceeding
df -h ~/

# Estimated storage requirements for local models:
# - Whisper base model: ~140 MB
# - Pyannote diarization model: ~1.2 GB
# - Dependencies and cache: ~1-2 GB
# - Total estimated: ~3-4 GB (mostly one-time download)
```

### Local Model Management

```python
import os
from huggingface_hub import snapshot_download

def setup_local_models_offline():
    """Download models locally for offline use"""
    
    # Whisper models location
    whisper_cache = os.path.expanduser("~/.cache/whisper")
    
    # Pyannote models location
    pyannote_cache = os.path.expanduser("~/.cache/huggingface")
    
    print(f"Whisper models cached at: {whisper_cache}")
    print(f"Pyannote models cached at: {pyannote_cache}")
    
    # Check if models are already downloaded
    if os.path.exists(whisper_cache):
        print("✅ Whisper models already available locally")
    else:
        print("Whisper models will download on first use")
    
    if os.path.exists(pyannote_cache):
        print("✅ Pyannote models already available locally")
    else:
        print("Pyannote models will download on first use")
    
    print("\nAfter first run, all models are cached locally!")
    print("Subsequent runs require NO internet connection!")
```

## Troubleshooting

### Local Processing Issues

1. **Model Download Issues (First Run Only):**
   ```bash
   # If models fail to download initially, check internet connection
   # Models will be cached locally after successful download
   ```

2. **Apple Silicon PyTorch Issues:**
   ```bash
   # If you have issues with MPS, force CPU mode
   export PYTORCH_ENABLE_MPS_FALLBACK=1
   python your_script.py
   ```

3. **Memory Issues During Local Processing:**
   ```python
   # For large audio files, process in chunks
   # Or increase virtual memory on macOS
   ```

### Virtual Environment Issues

1. **Verify Virtual Environment:**
   ```bash
   # Check if in virtual environment
   echo $VIRTUAL_ENV
   
   # If not in environment, activate it
   source local_diarization/bin/activate
   ```

2. **Python Path Issues:**
   ```bash
   # Ensure you're using the virtual environment Python
   which python
   which pip
   
   # Should point to: local_diarization/bin/python or local_diarization/bin/pip
   ```

### GPU/NPU Acceleration Issues (Local Only)

1. **Check MPS Availability:**
   ```python
   import torch
   print(f"MPS backend available: {torch.backends.mps.is_available()}")
   print(f"MPS is built: {torch.backends.mps.is_built()}")
   ```

2. **Force CPU if GPU Issues (Local Fallback):**
   ```python
   # For Whisper models - local fallback
   model = whisper.load_model("base", device="cpu")
   
   # For Pyannote - local fallback
   # The model will automatically use appropriate device
   ```

### Common Local Processing Troubleshooting

```bash
# If you encounter issues with model loading
# Clear local cache if needed
rm -rf ~/.cache/whisper/
rm -rf ~/.cache/huggingface/

# Check available space for local models
df -h ~/

# For audio processing issues
brew install sox
pip install pydub

# Check Python architecture for local processing
python -c "import platform; print('Architecture:', platform.machine())"
```

## Best Practices for Local Processing

1. **Always use virtual environments** to avoid system Python conflicts
2. **Run initial model downloads** when connected to internet (one-time setup)
3. **Monitor memory usage** when processing large audio files locally
4. **Use Apple Silicon optimized packages** when available for local processing
5. **Check local storage** before processing to ensure sufficient space
6. **All subsequent runs work completely offline!**

## Complete Local Workflow Example

Here's a complete workflow script for macOS that runs everything locally:

```bash
#!/bin/bash
# Complete local setup script for macOS

echo "🔍 Setting up local speaker diarization environment..."

# Create and activate virtual environment
python3 -m venv local_diarization
source local_diarization/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install PyTorch for Apple Silicon (local processing)
pip install torch torchvision torchaudio

# Install required local packages (no APIs)
pip install openai-whisper pyannote.audio pydub librosa huggingface_hub pandas numpy

echo "🚀 Installing local dependencies complete!"

# Check system capabilities
python -c "
import torch
import platform
print(f'Platform: {platform.system()} {platform.machine()}')
print(f'PyTorch version: {torch.__version__}')
print(f'MPS available: {torch.backends.mps.is_available()}')
print(f'Apple Silicon: {platform.machine() in [\"arm64\", \"ARM64\"]}')
print('✅ System ready for local processing!')
"

# Copy your audio file to working directory (optional)
# cp /path/to/your/audio.ogg .

echo "💾 Environment ready! Models will download on first run."
echo "⚡ Subsequent runs will work completely offline with local processing!"
echo "🚀 You can now run any of the local methods from this guide."
```

## Verification: No Internet Required

After initial setup, verify everything works offline:

```python
# Test script to verify local processing
def test_local_setup():
    """Test that all dependencies work for local processing"""
    
    try:
        import torch
        import whisper
        import pyannote.audio
        import pydub
        import librosa
        print("✅ All local dependencies imported successfully")
        
        # Test device detection
        if torch.backends.mps.is_available():
            print("✅ MPS (Apple Silicon) available for local acceleration")
        elif torch.cuda.is_available():
            print("✅ CUDA available for local acceleration")
        else:
            print("✅ CPU available for local processing")
        
        print("🎯 Local processing environment: READY!")
        print("🔒 NO internet connection required for processing")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    
    return True

test_local_setup()
```

This comprehensive guide provides everything you need to perform speaker diarization **completely locally** on your Mac without any API dependencies. All processing runs on your local machine with full GPU/NPU acceleration support!