# Troubleshooting

Common issues and quick fixes.

---

## Quick Checks

Before diving deep, try these:

```bash
# 1. Virtual environment activated?
source .venv/bin/activate

# 2. Run health check
localtranscribe doctor

# 3. Check version
localtranscribe version
```

---

## Installation Issues

### Command not found: `localtranscribe`

**Fix:**
```bash
# Install from PyPI
pip install localtranscribe

# Or if installed from source, activate virtual environment
source .venv/bin/activate
```

### PyTorch or dependencies failed to install

**Fix:**
```bash
# Update pip first
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

### FFmpeg not found

**Fix:**
```bash
# macOS with Homebrew
brew install ffmpeg

# Verify
ffmpeg -version
```

---

## HuggingFace Token Issues

### Token not found or invalid

**Fix:**

1. Create `.env` file in project root:
   ```bash
   echo "HUGGINGFACE_TOKEN=your_token_here" > .env
   ```

2. Get token:
   - Visit https://huggingface.co/settings/tokens
   - Create new token with "read" access
   - Copy to `.env` file

3. Accept model licenses (required for both models):
   - Main: https://huggingface.co/pyannote/speaker-diarization-3.1
   - Dependency: https://huggingface.co/pyannote/segmentation-3.0
   - Click "Agree and access repository" on each page

### 401 Unauthorized error

**Fix:**
- Token expired → Generate new one
- License not accepted → Visit model page and accept terms
- Wrong token → Check `.env` has correct format: `HUGGINGFACE_TOKEN="hf_..."`

---

## Processing Issues

### Slow transcription

**Fixes:**

1. Use smaller model:
   ```bash
   localtranscribe process audio.mp3 --model tiny
   ```

2. Check if MLX is being used (Apple Silicon):
   ```bash
   localtranscribe doctor  # Look for MLX-Whisper status
   ```

3. Close memory-intensive apps

### Poor transcription quality

**Fixes:**

1. Use larger model:
   ```bash
   localtranscribe process audio.mp3 --model medium
   ```

2. Specify language if known:
   ```bash
   localtranscribe process audio.mp3 --language en
   ```

3. Improve audio quality:
   - Use higher bitrate
   - Reduce background noise
   - Ensure clear speech

### Poor speaker separation

**Fixes:**

1. Specify exact speaker count:
   ```bash
   localtranscribe process audio.mp3 --speakers 2
   ```

2. Use higher quality audio:
   - Clear speaker distinction
   - Minimal overlap
   - At least 30 seconds per speaker

### Out of memory errors

**Fixes:**

1. Use smaller model:
   ```bash
   localtranscribe process audio.mp3 --model tiny
   ```

2. Close other applications

3. For large files, split into chunks:
   ```bash
   ffmpeg -i long.mp3 -f segment -segment_time 1800 -c copy chunk_%03d.mp3
   ```

---

## Audio Format Issues

### Unsupported format

**Fix:**
```bash
# Convert to MP3
ffmpeg -i input.webm -acodec libmp3lame output.mp3

# Then process
localtranscribe process output.mp3
```

**Supported formats:** MP3, WAV, OGG, M4A, FLAC

### File not found

**Fix:**
- Use absolute path: `localtranscribe process /full/path/to/audio.mp3`
- Or navigate to directory: `cd /path/to/files && localtranscribe process audio.mp3`

---

## Common Error Messages

### `ModuleNotFoundError`

**Meaning:** Missing Python package

**Fix:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### `RuntimeError: MPS backend out of memory`

**Meaning:** Insufficient GPU memory

**Fix:**
```bash
# Use smaller model
localtranscribe process audio.mp3 --model tiny
```

### `Pipeline.from_pretrained() got an unexpected keyword argument 'use_auth_token'`

**Meaning:** Outdated version of LocalTranscribe

**Fix:** Update to the latest version:
```bash
pip install --upgrade localtranscribe
```

This issue was fixed in v2.0.1-beta with updated pyannote.audio 3.x compatibility.

---

## NLP Model Issues (v3.1.1)

### Context-aware features not working

**Fix:**

1. Check model status:
   ```bash
   localtranscribe check-models
   ```

2. Download required model:
   ```bash
   localtranscribe check-models --download en_core_web_sm
   ```

3. Or install manually:
   ```bash
   python -m spacy download en_core_web_sm
   ```

### spaCy not installed

**Symptoms:** `check-models` shows spaCy missing

**Fix:**
```bash
pip install spacy>=3.7.0
```

### Model download fails

**Fix:**

1. Check internet connection

2. Try manual download:
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. If behind proxy, configure:
   ```bash
   export HTTP_PROXY="http://proxy.example.com:8080"
   export HTTPS_PROXY="https://proxy.example.com:8080"
   python -m spacy download en_core_web_sm
   ```

### FlashText or RapidFuzz missing

**Symptoms:** Features work but performance is reduced

**Fix:**
```bash
# Install optional performance dependencies
pip install flashtext>=2.7
pip install rapidfuzz>=3.6.0
```

**Note:** These are optional. Basic proofreading works without them, just slower.

### Wrong model installed

**Fix:**

1. Check installed models:
   ```bash
   localtranscribe check-models --detailed
   ```

2. Install preferred model:
   ```bash
   # Small (13 MB) - Good for most use cases
   localtranscribe check-models --download en_core_web_sm

   # Medium (43 MB) - Better accuracy
   localtranscribe check-models --download en_core_web_md

   # Large (741 MB) - Maximum accuracy
   localtranscribe check-models --download en_core_web_lg
   ```

3. Specify in code:
   ```python
   from localtranscribe.proofreading import Proofreader

   proofreader = Proofreader(
       enable_context_matching=True,
       spacy_model="en_core_web_md",  # Use medium model
       auto_download_model=True
   )
   ```

### Context matching accuracy too low

**Fix:**

1. Try larger model for better NER:
   ```bash
   localtranscribe check-models --download en_core_web_md
   ```

2. Adjust confidence threshold:
   ```python
   proofreader = Proofreader(
       enable_context_matching=True,
       context_confidence_threshold=0.6,  # Lower = more aggressive (default: 0.7)
       context_window=7  # Wider context (default: 5)
   )
   ```

### Fuzzy matching making wrong corrections

**Fix:**

Increase similarity threshold:
```python
proofreader = Proofreader(
    enable_fuzzy_matching=True,
    fuzzy_threshold=90  # Stricter matching (default: 85)
)
```

Or disable for specific use cases:
```python
proofreader = Proofreader(
    enable_fuzzy_matching=False  # Disable if causing issues
)
```

---

## Getting Help

### Health Check

Run the doctor command first:
```bash
localtranscribe doctor -v
```

This checks:
- Python version
- Dependencies
- HuggingFace token
- System capabilities

### Report an Issue

Include this info:

```bash
# System info
localtranscribe version

# Python packages
pip list | grep -E "localtranscribe|torch|pyannote|whisper"

# Error message (full output)
```

**Open issue:** https://github.com/aporb/LocalTranscribe/issues

---

## Performance Tips

**Expected processing times (M1/M2/M3):**

| Model | 10min audio | Quality |
|-------|-------------|---------|
| tiny | 30 sec | Basic |
| base | 1-2 min | Good |
| small | 3-5 min | Better |
| medium | 8-12 min | Best |

**Speed up processing:**
- Use `tiny` or `base` model
- Ensure MLX is installed (Apple Silicon)
- Close other apps
- Skip diarization if not needed: `--skip-diarization`

---

**Still stuck?** Open an issue with your `localtranscribe doctor` output and error message.
