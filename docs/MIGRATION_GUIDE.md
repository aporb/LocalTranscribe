# Migration Guide: Alpha to v2.0

This guide helps you migrate from LocalTranscribe alpha (scripts-based) to v2.0 (CLI-based).

## Summary of Changes

LocalTranscribe v2.0 is a major upgrade that transforms the project from a collection of scripts into a professional CLI tool. All functionality remains the same, but the interface is dramatically improved.

### What Changed

| Aspect | Alpha | v2.0 |
|--------|-------|------|
| **Interface** | 3 separate Python scripts | Single CLI command |
| **Installation** | Manual pip install | Automated installer + pip |
| **Configuration** | Hardcoded in scripts | YAML + env vars + CLI args |
| **File paths** | Hardcoded paths | Smart path resolution |
| **Error messages** | Basic tracebacks | Helpful suggestions + context |
| **Health checks** | Manual verification | Built-in `doctor` command |
| **Package structure** | Loose scripts | Proper Python package |

### What Stayed the Same

- ✅ Core algorithms (Pyannote, Whisper)
- ✅ Output formats (TXT, JSON, SRT, MD)
- ✅ Speaker diarization quality
- ✅ Transcription accuracy
- ✅ Offline processing
- ✅ Apple Silicon optimization

## Installation Migration

### Alpha Installation

```bash
# Old way (alpha)
pip install -r requirements.txt
pip install mlx-whisper mlx
```

### v2.0 Installation

```bash
# New way (automated)
./install.sh

# Or manual
pip install -e .
localtranscribe doctor
```

**Migration steps:**
1. Pull the latest code: `git pull origin main`
2. Run the installer: `./install.sh`
3. Or install manually: `pip install -e .`
4. Verify installation: `localtranscribe doctor`

## Usage Migration

### Alpha Workflow

The old 3-step manual process:

```bash
# 1. Edit scripts/diarization.py to set audio file path (line 259)
# 2. Run diarization
cd scripts
python3 diarization.py

# 3. Edit scripts/transcription.py to set audio file path (line 410)
# 4. Run transcription
python3 transcription.py

# 5. Edit scripts/combine.py to set file paths (lines 310-313)
# 6. Run combination
python3 combine.py
```

### v2.0 Workflow

The new single-command process:

```bash
# Everything in one command!
localtranscribe process audio.mp3

# With options
localtranscribe process audio.mp3 -o results/ -m small -s 2
```

## Command Mapping

### Processing Audio

| Alpha | v2.0 |
|-------|------|
| Edit `scripts/diarization.py` line 259<br>`python3 scripts/diarization.py`<br>Edit `scripts/transcription.py` line 410<br>`python3 scripts/transcription.py`<br>Edit `scripts/combine.py` lines 310-313<br>`python3 scripts/combine.py` | `localtranscribe process audio.mp3` |

### Transcription Only (No Diarization)

| Alpha | v2.0 |
|-------|------|
| Comment out diarization<br>`python3 scripts/transcription.py` | `localtranscribe process audio.mp3 --skip-diarization` |

### Changing Model Size

| Alpha | v2.0 |
|-------|------|
| Edit script, find model_size variable<br>Change to "small"<br>Run script | `localtranscribe process audio.mp3 --model small` |

### Specifying Number of Speakers

| Alpha | v2.0 |
|-------|------|
| Edit `scripts/diarization.py`<br>Set `num_speakers = 2` | `localtranscribe process audio.mp3 --speakers 2` |

### Changing Output Directory

| Alpha | v2.0 |
|-------|------|
| Edit multiple files<br>Change `OUTPUT_DIR` | `localtranscribe process audio.mp3 --output results/` |

## Configuration Migration

### Alpha Configuration

Configuration was hardcoded in each script:

```python
# scripts/diarization.py (line 259)
audio_file = "../input/audio.ogg"

# scripts/transcription.py (line 410)
audio_file = Path("../input/audio.ogg")

# scripts/combine.py (lines 310-313)
diarization_file = Path("../output/audio_diarization.md")
transcription_file = Path("../output/audio_transcript.json")
```

### v2.0 Configuration

Multiple configuration methods (priority order):

#### 1. Command-line Arguments (Highest Priority)

```bash
localtranscribe process audio.mp3 \
  --output results/ \
  --model small \
  --speakers 2
```

#### 2. Environment Variables

```bash
export LOCALTRANSCRIBE_MODEL_WHISPER_SIZE=small
export LOCALTRANSCRIBE_OUTPUT_DIRECTORY=./results
export HUGGINGFACE_TOKEN=your_token
```

#### 3. Configuration File

Create `localtranscribe.yaml` or `~/.localtranscribe/config.yaml`:

```yaml
model:
  whisper_size: small
  whisper_implementation: mlx

processing:
  num_speakers: 2

output:
  directory: ./results
  formats:
    - txt
    - json
    - md
```

#### 4. Default Values (Lowest Priority)

Built-in sensible defaults.

## File Path Migration

### Alpha: Hardcoded Paths

```python
# Had to edit source code
audio_file = "../input/audio.ogg"
```

### v2.0: Smart Path Resolution

```bash
# Works with any path
localtranscribe process ~/Downloads/audio.mp3
localtranscribe process input/audio.ogg
localtranscribe process ./audio.wav

# Automatically searches:
# 1. Absolute path
# 2. Current directory
# 3. ./input directory
# 4. Relative paths
```

## HuggingFace Token Migration

### Alpha

```bash
# .env file only
HUGGINGFACE_TOKEN=your_token
```

### v2.0

Multiple options:

```bash
# 1. .env file (recommended)
echo "HUGGINGFACE_TOKEN=your_token" > .env

# 2. Environment variable
export HUGGINGFACE_TOKEN=your_token

# 3. Command-line argument
localtranscribe process audio.mp3 --hf-token your_token

# 4. During installation
./install.sh  # Prompts for token
```

## Output Files Migration

### Output File Naming

| Alpha | v2.0 |
|-------|------|
| `audio_diarization.md` | `{filename}_diarization.md` |
| `audio_transcript.txt` | `{filename}_transcript.txt` |
| `audio_transcript.json` | `{filename}_transcript.json` |
| (manual combination) | `{filename}_combined.md` |

### Output Structure

Both versions produce the same files, but v2.0 uses the original filename:

```
# Alpha output
output/
├── audio_diarization.md
├── audio_transcript.txt
├── audio_transcript.json
└── audio_combined.md  (if manually combined)

# v2.0 output (for "interview.mp3")
output/
├── interview_diarization.md
├── interview_transcript.txt
├── interview_transcript.json
└── interview_combined.md  (automatically created)
```

## Error Handling Migration

### Alpha Error Messages

```
Traceback (most recent call last):
  File "diarization.py", line 259
    ...
FileNotFoundError: [Errno 2] No such file or directory: '../input/audio.ogg'
```

### v2.0 Error Messages

```
❌ Audio file not found: ../input/audio.ogg

💡 Suggestions:
  1. Check the file path is correct
  2. Verify the file exists: ls -la ../input/audio.ogg
  3. Try using an absolute path: /full/path/to/audio.ogg
  4. Ensure the file has proper permissions

Context:
  search_locations: ['.', './input', '../input']
  attempted_paths: ['audio.ogg', 'input/audio.ogg', '../input/audio.ogg']
```

## Health Check Migration

### Alpha

No built-in health check. Users had to manually verify:
- Python version
- Dependencies installed
- HF token configured
- FFmpeg available

### v2.0

```bash
# Comprehensive health check
localtranscribe doctor

# With detailed diagnostics
localtranscribe doctor -v
```

Checks:
- ✅ Python version (3.9+)
- ✅ PyTorch + device (MPS/CUDA/CPU)
- ✅ Whisper implementations
- ✅ Pyannote.audio
- ✅ HuggingFace token
- ✅ FFmpeg
- ✅ All dependencies

## Legacy Scripts

### What Happens to Old Scripts?

The `scripts/` directory is **deprecated but kept** for reference:

```
LocalTranscribe/
├── localtranscribe/     # ← New package (use this)
├── scripts/             # ← Old scripts (deprecated)
│   ├── diarization.py   # Still works, but deprecated
│   ├── transcription.py
│   └── combine.py
```

**Recommendation:** Migrate to the new CLI. The old scripts may be removed in v3.0.

### Can I Still Use Old Scripts?

Yes, but:
- ⚠️  No new features
- ⚠️  No bug fixes
- ⚠️  May be removed in future versions
- ✅ New CLI is much better

## Common Migration Issues

### Issue 1: "localtranscribe: command not found"

**Cause:** Package not installed or virtual environment not activated.

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install package
pip install -e .

# Verify
localtranscribe version
```

### Issue 2: "No module named 'localtranscribe'"

**Cause:** Trying to import old scripts or package not installed.

**Solution:**
```bash
# Don't import scripts directly
# Use the CLI instead
localtranscribe process audio.mp3
```

### Issue 3: File paths not working

**Cause:** Using old hardcoded paths.

**Solution:**
```bash
# Don't edit source files
# Use CLI arguments instead
localtranscribe process /full/path/to/audio.mp3
```

### Issue 4: HuggingFace token not found

**Cause:** `.env` file not in correct location.

**Solution:**
```bash
# Create .env in project root
echo "HUGGINGFACE_TOKEN=your_token" > .env

# Or set environment variable
export HUGGINGFACE_TOKEN=your_token

# Verify with doctor
localtranscribe doctor
```

## Feature Comparison Table

| Feature | Alpha | v2.0 |
|---------|-------|------|
| **CLI Interface** | ❌ | ✅ |
| **Single Command** | ❌ | ✅ |
| **Smart Path Resolution** | ❌ | ✅ |
| **Configuration Files** | ❌ | ✅ |
| **Environment Variables** | Partial | ✅ |
| **Health Checks** | ❌ | ✅ |
| **Helpful Errors** | ❌ | ✅ |
| **Auto Installation** | ❌ | ✅ |
| **Verbose Mode** | ❌ | ✅ |
| **Multiple Whisper Implementations** | ✅ | ✅ |
| **Speaker Diarization** | ✅ | ✅ |
| **Output Formats** | ✅ | ✅ |
| **Offline Processing** | ✅ | ✅ |

## Next Steps

1. **Install v2.0**
   ```bash
   git pull origin main
   ./install.sh
   ```

2. **Verify Installation**
   ```bash
   localtranscribe doctor -v
   ```

3. **Try the New CLI**
   ```bash
   localtranscribe process your_audio.mp3
   ```

4. **Explore Options**
   ```bash
   localtranscribe --help
   localtranscribe process --help
   ```

5. **Set Up Configuration** (Optional)
   ```bash
   cp config.yaml.example localtranscribe.yaml
   # Edit localtranscribe.yaml with your preferences
   ```

## Getting Help

If you encounter issues during migration:

1. Run `localtranscribe doctor` to check your setup
2. Check this guide for common issues
3. Review the [README.md](../README.md) for CLI usage
4. Search [GitHub issues](https://github.com/aporb/LocalTranscribe/issues)
5. Open a new issue with the `migration` label

## Feedback

We'd love to hear about your migration experience! Please:
- Report issues on [GitHub](https://github.com/aporb/LocalTranscribe/issues)
- Share feedback in [discussions](https://github.com/aporb/LocalTranscribe/discussions)
- Suggest improvements to this guide

---

**Welcome to LocalTranscribe v2.0!** 🎉
