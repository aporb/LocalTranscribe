# Usage Guide

Learn how to use LocalTranscribe to transcribe and diarize your audio files.

## Table of Contents

- [Basic Workflow](#basic-workflow)
- [Step-by-Step Guide](#step-by-step-guide)
- [Understanding Output Files](#understanding-output-files)
- [Advanced Usage](#advanced-usage)
- [Model Selection](#model-selection)
- [Best Practices](#best-practices)

## Basic Workflow

The typical workflow consists of three steps:

```
1. Diarization    →    2. Transcription    →    3. Combine
   (Who spoke?)         (What was said?)          (Merge results)
```

## Step-by-Step Guide

### Step 1: Prepare Your Audio File

1. Place your audio file in the `input/` directory
2. Currently supported formats: MP3, WAV, OGG, M4A, FLAC
3. Rename your file to `audio.ogg` (or update the script file paths)

```bash
cp ~/Downloads/my_meeting.mp3 input/audio.ogg
```

**Note**: The current alpha version uses hardcoded filenames. Future versions will support command-line arguments.

### Step 2: Run Speaker Diarization

Identify who is speaking and when:

```bash
cd scripts
python3 diarization.py
```

**What happens**:
- Audio is preprocessed (converted to mono, 16kHz)
- Pyannote model identifies speaker segments
- Results saved to `output/audio_diarization_results.md`

**Expected output**:
```
🎙️  Speaker Diarization for macOS M4 Pro
==================================================
🚀 Using Apple Silicon GPU acceleration (MPS) on M4 Pro
🔑 Using Hugging Face token: hf_xxxxxxx...
📁 Processing audio file: ../input/audio.ogg
🔄 Converting OGG to WAV...
✅ Conversion complete: ../input/audio.wav
📥 Loading pyannote/speaker-diarization-community-1...
✅ Pipeline loaded successfully!
🎯 Starting speaker diarization...
⏱️  Processing completed in 45.23 seconds
✅ Speaker diarization completed successfully!
```

**Processing time**: Varies by audio length and hardware. Typical: 2-5x real-time on M4 Pro.

### Step 3: Run Speech-to-Text Transcription

Convert speech to text:

```bash
python3 transcription.py
```

**What happens**:
- Checks for best available Whisper implementation
- Loads the Whisper model (downloads on first run)
- Transcribes audio to text
- Generates multiple output formats

**Expected output**:
```
🎙️  Optimized Speech-to-Text Transcription for macOS M4 Pro
🚀 Using MLX-Whisper for optimal Apple Silicon performance
======================================================================
📁 Processing audio file: ../input/audio.ogg
✅ Conversion complete: ../input/audio_processed.wav
🔍 Checking available Whisper implementations...
✅ MLX-Whisper available with Metal support - Primary choice for M4 Pro
🎯 Starting transcription with mlx implementation...
🔄 Using MLX-Whisper with base model
⏱️  MLX-Whisper completed in 32.45 seconds
✅ Transcription completed successfully!
```

**Output files created**:
- `audio_transcript.txt` - Plain text
- `audio_transcript.srt` - Subtitles
- `audio_transcript.json` - Structured data
- `audio_transcript.md` - Markdown with timestamps

### Step 4: Combine Results

Merge diarization and transcription:

```bash
python3 combine.py
```

**What happens**:
- Loads diarization results
- Loads transcription segments
- Maps speakers to transcript segments
- Calculates confidence scores
- Generates combined transcript

**Expected output**:
```
🎙️  Combining Speaker Diarization and Transcription Results
============================================================
📁 Loading diarization results from: ../output/audio_diarization_results.md
📁 Loading transcription results from: ../output/audio_transcript.json
📊 Diarization segments: 47
📊 Transcription segments: 152
🔄 Mapping speakers to transcription segments...
📝 Creating combined transcript...
✅ Combined transcript created successfully!
📄 Output saved to: ../output/audio_combined_transcript.md
```

### Step 5: Review Your Results

Open the combined transcript:

```bash
# From scripts directory
open ../output/audio_combined_transcript.md
```

Or navigate to `output/` directory and open the markdown file in your preferred editor.

## Understanding Output Files

### Diarization Output

**File**: `audio_diarization_results.md`

Contains:
- Speaker segments with timestamps
- Speaker time distribution
- Summary statistics

Example:
```markdown
## Regular Speaker Diarization

| Speaker | Start Time (s) | End Time (s) | Duration (s) |
|---------|----------------|--------------|--------------|
| SPEAKER_00 | 0.003 | 5.234 | 5.231 |
| SPEAKER_01 | 5.456 | 12.789 | 7.333 |
```

### Transcription Outputs

#### TXT Format
**File**: `audio_transcript.txt`

Plain text transcription, no timestamps:
```
Hello, welcome to the meeting. Today we're discussing...
```

#### SRT Format
**File**: `audio_transcript.srt`

Standard subtitle format:
```
1
00:00:00,000 --> 00:00:05,000
Hello, welcome to the meeting.

2
00:00:05,000 --> 00:00:10,000
Today we're discussing the quarterly results.
```

#### JSON Format
**File**: `audio_transcript.json`

Structured data with metadata:
```json
{
  "transcript": "Full text here...",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.0,
      "text": "Hello, welcome to the meeting.",
      "temperature": 0.0,
      "avg_logprob": -0.234,
      "compression_ratio": 1.456,
      "no_speech_prob": 0.012
    }
  ],
  "processing_info": {
    "audio_file": "../input/audio.wav",
    "language": "en",
    "duration": 450.5
  }
}
```

#### Markdown Format
**File**: `audio_transcript.md`

Formatted document with timestamps:
```markdown
# Audio Transcript

**Audio File:** ../input/audio.wav
**Detected Language:** en
**Total Duration:** 450.50s

## Transcript

**[0.000s - 5.000s]** Hello, welcome to the meeting.
**[5.000s - 10.000s]** Today we're discussing the quarterly results.
```

### Combined Transcript

**File**: `audio_combined_transcript.md`

The most useful output, includes:

1. **Speaker-labeled transcript**:
```markdown
### SPEAKER_00
**Time:** [0.000s - 15.234s]

Hello, welcome to the meeting. Today we're discussing the quarterly results.
```

2. **Detailed segment breakdown** with confidence scores
3. **Speaking time distribution** per speaker
4. **Audio quality metrics**
5. **Overall statistics**

## Advanced Usage

### Changing Model Size

Edit `transcription.py`, line 463:

```python
# Current
model_size="base",  # Options: tiny, base, small, medium, large

# For better accuracy (slower):
model_size="medium",

# For faster processing (lower accuracy):
model_size="tiny",
```

Model comparison:

| Model | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|--------|----------|
| tiny | Fastest | Basic | ~1GB | Quick drafts, testing |
| base | Fast | Good | ~1.5GB | General use (default) |
| small | Medium | Better | ~2.5GB | Important meetings |
| medium | Slow | Great | ~5GB | Critical transcripts |
| large | Slowest | Best | ~10GB | Professional use |

### Specifying Number of Speakers

Edit `diarization.py`, line 185:

```python
# Current
num_speakers=2,  # Specify exact number

# Or use min/max range:
min_speakers=2,
max_speakers=4,

# Or let it auto-detect:
# num_speakers=None,
# min_speakers=None,
# max_speakers=None,
```

### Forcing Specific Language

Edit `transcription.py`, line 464:

```python
# Current (auto-detect)
language=None,

# Force English
language='en',

# Other languages: 'es', 'fr', 'de', 'it', 'ja', 'zh', etc.
```

### Choosing Whisper Implementation

Edit `transcription.py`, line 465:

```python
# Current (auto-select best)
implementation="auto"

# Force specific implementation:
implementation="mlx"       # MLX-Whisper (best for M4)
implementation="faster"    # Faster-Whisper
implementation="original"  # Original Whisper
```

## Best Practices

### Audio Quality

**For best results**:
- Use high-quality audio (44.1kHz or higher)
- Minimize background noise
- Ensure clear speaker separation
- Avoid heavy background music
- Use lossless formats when possible (WAV, FLAC)

**Acceptable formats**:
- MP3 (320kbps recommended)
- M4A / AAC
- OGG Vorbis
- WAV (any sample rate)
- FLAC

### Speaker Diarization Tips

**Optimal conditions**:
- 2-4 speakers work best
- Clear speaker transitions
- Minimal speaker overlap
- Consistent audio levels per speaker
- At least 30 seconds of audio per speaker

**Challenging scenarios**:
- More than 4 speakers (may confuse identities)
- Heavy speaker overlap
- Very short speaker turns (<2 seconds)
- Similar voice characteristics

### Processing Long Files

For files longer than 60 minutes:

1. **Ensure sufficient RAM** (16GB recommended)
2. **Use smaller model** (base or small)
3. **Process overnight** if using large models
4. **Consider splitting** very long files (3+ hours)

### Batch Processing

Current alpha doesn't support batch processing. For multiple files:

```bash
# Manual approach
for file in input/*.mp3; do
    # Copy and rename
    cp "$file" input/audio.ogg

    # Run pipeline
    python3 scripts/diarization.py
    python3 scripts/transcription.py
    python3 scripts/combine.py

    # Rename outputs
    base=$(basename "$file" .mp3)
    mv output/audio_combined_transcript.md "output/${base}_combined.md"
done
```

## Common Workflows

### Workflow 1: Quick Meeting Notes

```bash
# Use fastest settings
# Edit transcription.py: model_size="tiny"
python3 scripts/transcription.py
# Read: output/audio_transcript.txt
```

### Workflow 2: Interview Transcription

```bash
# Run full pipeline with base model
python3 scripts/diarization.py
python3 scripts/transcription.py
python3 scripts/combine.py
# Review: output/audio_combined_transcript.md
```

### Workflow 3: Subtitle Creation

```bash
# Run transcription only
python3 scripts/transcription.py
# Use: output/audio_transcript.srt
```

### Workflow 4: Data Analysis

```bash
# Run full pipeline
python3 scripts/diarization.py
python3 scripts/transcription.py
python3 scripts/combine.py
# Parse: output/audio_transcript.json
```

## Next Steps

- Review [Configuration Guide](CONFIGURATION.md) for environment variables
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues
- Explore output files and adjust settings for your needs

## Getting Help

If you encounter issues during usage:

1. Check error messages for specific problems
2. Review [Troubleshooting Guide](TROUBLESHOOTING.md)
3. Verify [Installation Guide](INSTALLATION.md) steps
4. Open an issue at [github.com/aporb/LocalTranscribe/issues](https://github.com/aporb/LocalTranscribe/issues) with example audio characteristics and error logs
