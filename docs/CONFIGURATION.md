# Configuration Guide

Learn how to configure LocalTranscribe for optimal performance and customize behavior.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Script Configuration](#script-configuration)
- [Model Selection](#model-selection)
- [Performance Tuning](#performance-tuning)
- [Output Customization](#output-customization)

## Environment Variables

### Hugging Face Token

**Required** for speaker diarization.

**File**: `.env`

```bash
HUGGINGFACE_TOKEN="your_token_here"
```

**How to get**:
1. Create account at [huggingface.co](https://huggingface.co/)
2. Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Create new token with "Read" permissions
4. Accept license at [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)

### Alternative: System Environment Variable

Instead of `.env` file, you can set system-wide:

```bash
# Add to ~/.zshrc or ~/.bash_profile
export HUGGINGFACE_TOKEN="your_token_here"

# Reload shell configuration
source ~/.zshrc  # or source ~/.bash_profile
```

## Script Configuration

### Transcription Settings

**File**: `scripts/transcription.py`

#### Audio File Path

**Line**: ~454

```python
audio_file = "../input/audio.ogg"
```

Change to your audio file name:
```python
audio_file = "../input/my_meeting.mp3"
```

#### Model Size

**Line**: ~463

```python
model_size="base"
```

Options:
- `"tiny"` - Fastest, lowest accuracy (~1GB RAM)
- `"base"` - Balanced (default) (~1.5GB RAM)
- `"small"` - Better accuracy (~2.5GB RAM)
- `"medium"` - High accuracy (~5GB RAM)
- `"large"` - Best accuracy (~10GB RAM)

#### Language Detection

**Line**: ~464

```python
language=None  # Auto-detect
```

Force specific language:
```python
language="en"  # English
language="es"  # Spanish
language="fr"  # French
language="de"  # German
language="it"  # Italian
language="ja"  # Japanese
language="zh"  # Chinese
# See Whisper docs for full list
```

#### Whisper Implementation

**Line**: ~465

```python
implementation="auto"  # Automatically select best
```

Force specific implementation:
```python
implementation="mlx"       # MLX-Whisper (best for Apple Silicon)
implementation="faster"    # Faster-Whisper
implementation="original"  # Original OpenAI Whisper
```

#### Output Formats

**Line**: ~479

```python
output_formats=['txt', 'srt', 'json', 'md']
```

Customize which formats to generate:
```python
# Only text and markdown
output_formats=['txt', 'md']

# Only JSON for programmatic use
output_formats=['json']

# Everything
output_formats=['txt', 'srt', 'json', 'md']
```

### Diarization Settings

**File**: `scripts/diarization.py`

#### Audio File Path

**Line**: ~172

```python
audio_file = "../input/audio.ogg"
```

#### Speaker Configuration

**Line**: ~185-188

```python
num_speakers=2,      # Exact number of speakers
min_speakers=1,      # Minimum speakers
max_speakers=3       # Maximum speakers
```

**Scenarios**:

**Known speaker count**:
```python
num_speakers=2,
min_speakers=None,
max_speakers=None
```

**Auto-detect (2-4 speakers)**:
```python
num_speakers=None,
min_speakers=2,
max_speakers=4
```

**Auto-detect (unlimited)**:
```python
num_speakers=None,
min_speakers=None,
max_speakers=None
```

#### Diarization Pipeline Model

**Line**: ~91

```python
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-community-1",
    token=token
)
```

Alternative models (if available):
```python
# Newer version (check Hugging Face for availability)
"pyannote/speaker-diarization-3.1"
```

### Combine Script Settings

**File**: `scripts/combine.py`

#### Input File Paths

**Lines**: ~227-230

```python
diarization_file = "../output/audio_diarization_results.md"
transcription_json = "../output/audio_transcript.json"
transcription_txt = "../output/audio_transcript.txt"
audio_file = "../input/audio.ogg"
```

#### Output File Path

**Line**: ~265

```python
output_filename = "../output/audio_combined_transcript.md"
```

## Model Selection

### Whisper Model Comparison

| Model | Parameters | Speed | Accuracy | VRAM | Best Use Case |
|-------|-----------|-------|----------|------|---------------|
| tiny | 39M | 32x | ~65% | 1GB | Testing, drafts |
| base | 74M | 16x | ~75% | 1.5GB | General use |
| small | 244M | 6x | ~85% | 2.5GB | Important work |
| medium | 769M | 2x | ~92% | 5GB | Professional |
| large | 1550M | 1x | ~95% | 10GB | Critical accuracy |

*Speed relative to audio length on M4 Pro

### Selecting the Right Model

**Use tiny when**:
- Testing the pipeline
- Processing very long files (3+ hours)
- RAM limited (<8GB)
- Speed is critical

**Use base when** (default):
- General meetings and interviews
- Balanced speed/accuracy needed
- Standard use case

**Use small when**:
- Important business meetings
- Interviews for publication
- Need better accuracy without long wait

**Use medium when**:
- Legal depositions
- Medical transcriptions
- Professional documentation
- Willing to wait for quality

**Use large when**:
- Critical accuracy required
- Technical/scientific content
- Multiple speakers with accents
- Have 16GB+ RAM

## Performance Tuning

### CPU Thread Optimization

**File**: `scripts/transcription.py`

For non-MPS processing:

**Line**: ~46 (in setup_device function)

```python
torch.set_num_threads(8)  # M4 Pro has 10 cores
```

Adjust based on your CPU:
- M1/M2/M3 Base: `6`
- M1/M2/M3 Pro: `8`
- M1/M2/M3 Max: `10-12`
- M4 Pro: `8-10`
- Intel Macs: `4-8`

### MLX Memory Limit

**File**: `scripts/transcription.py`

**Line**: ~99 (in transcribe_with_mlx_whisper function)

```python
mx.set_cache_limit(1024 * 1024 * 1024)  # 1GB
```

Adjust based on available RAM:
```python
# 8GB total RAM
mx.set_cache_limit(512 * 1024 * 1024)  # 512MB

# 16GB total RAM
mx.set_cache_limit(1024 * 1024 * 1024)  # 1GB (default)

# 32GB+ total RAM
mx.set_cache_limit(2048 * 1024 * 1024)  # 2GB
```

### PyTorch MPS Configuration

PyTorch will automatically use MPS on Apple Silicon. To force CPU:

```python
import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
```

## Output Customization

### Changing Output Directory

**Current**: All outputs go to `../output/`

**To customize**, update in each script:

```python
# Instead of:
txt_filename = f"../output/{base_name}_transcript.txt"

# Use custom path:
txt_filename = f"/Users/you/Desktop/transcripts/{base_name}_transcript.txt"
```

### Custom Filename Patterns

**Example**: Add timestamp to filenames

```python
from datetime import datetime

# Get timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create filename
txt_filename = f"../output/{base_name}_{timestamp}_transcript.txt"
```

### Adjusting Markdown Output Format

**File**: `scripts/combine.py`

The `create_combined_transcript` function (line 81) controls output format.

**Customize sections**:
```python
# Add custom header
transcript_lines.append(f"**Project:** My Project Name")
transcript_lines.append(f"**Client:** Client Name")

# Change speaker formatting
transcript_lines.append(f"## {current_segments[0]['speaker']} says:")

# Add custom footer
transcript_lines.append(f"---")
transcript_lines.append(f"Transcribed with LocalTranscribe")
```

## Environment-Specific Settings

### Development Environment

Create `.env.development`:

```bash
HUGGINGFACE_TOKEN="your_dev_token"
DEBUG=true
LOG_LEVEL=debug
```

Load in scripts:
```python
from dotenv import load_dotenv
load_dotenv('.env.development')
```

### Production Environment

Create `.env.production`:

```bash
HUGGINGFACE_TOKEN="your_prod_token"
DEBUG=false
LOG_LEVEL=info
```

## Advanced Configuration

### Custom Audio Preprocessing

**File**: `scripts/transcription.py` or `scripts/diarization.py`

Modify `preprocess_audio` function (~line 55):

```python
def preprocess_audio(input_file):
    audio = AudioSegment.from_file(input_file)

    # Custom sample rate
    target_rate = 16000  # Change to 22050, 44100, etc.

    # Keep stereo instead of mono
    audio = audio.set_frame_rate(target_rate)  # Remove .set_channels(1)

    # Apply filters
    # audio = audio.high_pass_filter(80)  # Remove low frequency noise
    # audio = audio.low_pass_filter(8000)  # Remove high frequency noise

    wav_file = f"../input/{base_name}_processed.wav"
    audio.export(wav_file, format='wav')
    return wav_file
```

### Logging Configuration

Add logging to any script:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../output/transcription.log'),
        logging.StreamHandler()
    ]
)

# Use in script
logging.info("Starting transcription...")
logging.error(f"Error: {e}")
```

## Configuration Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Document custom changes** - Comment your modifications
3. **Test incrementally** - Change one setting at a time
4. **Backup originals** - Keep copies of original scripts
5. **Use version control** - Track configuration changes
6. **Environment-specific configs** - Separate dev/prod settings

## Next Steps

- Apply configurations and test with sample audio
- Review [Usage Guide](USAGE.md) for running scripts
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) if issues arise

## Getting Help

For configuration questions:

1. Check if your setting is supported
2. Review error messages for invalid values
3. Test with default settings first
4. Open issue with your configuration and error details
