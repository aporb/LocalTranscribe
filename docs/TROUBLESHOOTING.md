# Troubleshooting Guide

Common issues and solutions for LocalTranscribe.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Diarization Issues](#diarization-issues)
- [Transcription Issues](#transcription-issues)
- [Performance Issues](#performance-issues)
- [Audio Format Issues](#audio-format-issues)
- [Output Issues](#output-issues)
- [Error Reference](#error-reference)

## Installation Issues

### Issue: "No module named 'torch'"

**Symptoms**:
```
ModuleNotFoundError: No module named 'torch'
```

**Solutions**:

1. Verify virtual environment is activated:
```bash
source .venv/bin/activate
# Your prompt should show (.venv)
```

2. Install PyTorch:
```bash
pip install torch torchaudio
```

3. If still failing, reinstall from requirements:
```bash
pip install -r requirements.txt
```

### Issue: "ERROR: Could not build wheels for pyannote-audio"

**Symptoms**:
```
ERROR: Failed building wheel for pyannote-audio
```

**Solutions**:

1. Install Xcode Command Line Tools:
```bash
xcode-select --install
```

2. Update pip and setuptools:
```bash
pip install --upgrade pip setuptools wheel
```

3. Try installing dependencies individually:
```bash
pip install torch torchaudio
pip install pyannote-audio
```

### Issue: "mlx-whisper not found"

**Symptoms**:
```
⚠️ MLX-Whisper not available
```

**Solutions**:

This is not critical - the tool will use alternative implementations.

To install MLX-Whisper:
```bash
pip install mlx-whisper mlx
```

**Note**: MLX only works on Apple Silicon Macs.

### Issue: FFmpeg not found

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solutions**:

1. Install via Homebrew:
```bash
brew install ffmpeg
```

2. Verify installation:
```bash
which ffmpeg
ffmpeg -version
```

3. If Homebrew not working, download binary from [ffmpeg.org](https://ffmpeg.org/download.html)

## Diarization Issues

### Issue: "Hugging Face token not found"

**Symptoms**:
```
❌ Hugging Face token not found!
💡 Please add HUGGINGFACE_TOKEN="your_token" to your .env file
```

**Solutions**:

1. Verify `.env` file exists:
```bash
ls -la .env
```

2. Check token format in `.env`:
```bash
HUGGINGFACE_TOKEN="hf_xxxxxxxxxxxxx"
# No spaces around =
# Token in quotes
# Token starts with hf_
```

3. Get new token:
   - Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Create token with "Read" permissions
   - Copy to `.env` file

4. Accept model license:
   - Visit [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - Click "Agree and access repository"

### Issue: "401 Unauthorized" from Hugging Face

**Symptoms**:
```
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**Solutions**:

1. **Check token validity**:
   - Token might be expired or revoked
   - Generate new token at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

2. **Verify token permissions**:
   - Must have "Read" access
   - Check token settings on Hugging Face

3. **Accept model license**:
   - Visit model page: [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - Accept terms of use

### Issue: Poor speaker separation

**Symptoms**:
- Speakers frequently misidentified
- Same speaker labeled as multiple speakers
- Multiple speakers labeled as one

**Solutions**:

1. **Specify known speaker count**:
```python
# In diarization.py, line ~185
num_speakers=2,  # Change to actual number
```

2. **Improve audio quality**:
   - Ensure speakers have distinct volume levels
   - Reduce background noise
   - Avoid speaker overlap
   - Use higher quality recording

3. **Adjust min/max speakers**:
```python
min_speakers=2,
max_speakers=3,  # Constrain detection range
```

4. **Try longer audio samples**:
   - Diarization works better with more data
   - Ensure at least 30 seconds per speaker

### Issue: "MPS backend not available"

**Symptoms**:
```
💻 MPS not available, using CPU
```

**Solutions**:

This is informational, not an error. The script will use CPU.

**To enable MPS**:
- Requires Apple Silicon Mac (M1/M2/M3/M4)
- Requires macOS 12.3+
- Update to latest macOS if available

**CPU mode works fine**, just slower.

## Transcription Issues

### Issue: "No Whisper implementations available"

**Symptoms**:
```
❌ No Whisper implementation available!
```

**Solutions**:

Install at least one Whisper implementation:

**Option 1 - MLX-Whisper** (recommended for Apple Silicon):
```bash
pip install mlx-whisper mlx
```

**Option 2 - Faster-Whisper**:
```bash
pip install faster-whisper
```

**Option 3 - Original Whisper**:
```bash
pip install openai-whisper
```

### Issue: Transcription is very slow

**Symptoms**:
- Processing takes 10x+ audio length
- Computer is sluggish during processing

**Solutions**:

1. **Use smaller model**:
```python
# In transcription.py, line ~463
model_size="tiny"  # or "base" instead of "medium"/"large"
```

2. **Check implementation**:
```python
# Verify MLX-Whisper is being used on Apple Silicon
implementation="mlx"  # Force MLX if available
```

3. **Close other applications**:
   - Free up RAM and CPU
   - Stop browser with many tabs
   - Close memory-intensive apps

4. **Check Activity Monitor**:
   - Look for high CPU usage
   - Check memory pressure (should be green)
   - Verify GPU is being used

5. **For very long files**, split into chunks:
```bash
# Use FFmpeg to split
ffmpeg -i long_audio.mp3 -f segment -segment_time 1800 -c copy output_%03d.mp3
```

### Issue: Poor transcription quality

**Symptoms**:
- Many incorrect words
- Nonsensical sentences
- Missing speech sections

**Solutions**:

1. **Use larger model**:
```python
model_size="medium"  # Better accuracy than "base"
```

2. **Specify correct language**:
```python
language="en"  # Instead of None for auto-detect
```

3. **Improve audio quality**:
   - Increase recording volume
   - Reduce background noise
   - Use better microphone
   - Avoid compression artifacts

4. **Check audio preprocessing**:
   - Ensure 16kHz sample rate
   - Verify mono conversion
   - Check for audio corruption

5. **Check "no_speech_prob" values** in JSON output:
   - Values > 0.5 indicate likely non-speech
   - Review those segments manually

### Issue: "Out of memory" errors

**Symptoms**:
```
RuntimeError: MPS backend out of memory
```
or
```
MemoryError: Unable to allocate array
```

**Solutions**:

1. **Use smaller model**:
```python
model_size="tiny"  # or "base"
```

2. **Reduce MLX cache limit**:
```python
# In transcription.py, line ~99
mx.set_cache_limit(512 * 1024 * 1024)  # 512MB instead of 1GB
```

3. **Close other applications**

4. **Restart Python session**:
```bash
# Exit and restart virtual environment
deactivate
source .venv/bin/activate
```

5. **For very large files**:
   - Process in chunks
   - Use CPU instead of GPU
   - Upgrade RAM if possible

## Performance Issues

### Issue: Processing takes longer than expected

**Expected processing times on M4 Pro**:

| Model | Audio Length | Expected Time | Note |
|-------|--------------|---------------|------|
| tiny | 10 min | 30 sec | Very fast |
| base | 10 min | 1-2 min | Fast |
| small | 10 min | 3-5 min | Moderate |
| medium | 10 min | 8-12 min | Slow |
| large | 10 min | 15-25 min | Very slow |

**If much slower**:

1. **Verify MPS is active**:
```python
import torch
print(torch.backends.mps.is_available())  # Should be True
```

2. **Check CPU usage** in Activity Monitor:
   - Should be ~400-800% (using multiple cores)
   - If low, might be I/O bottleneck

3. **Use faster implementation**:
```python
implementation="mlx"  # Fastest on Apple Silicon
```

4. **Check disk space**:
```bash
df -h  # Ensure sufficient free space
```

### Issue: High CPU usage, computer overheating

**Solutions**:

1. **Reduce thread count**:
```python
# In setup_device() function
torch.set_num_threads(4)  # Lower from 8-10
```

2. **Process during off-hours**

3. **Ensure proper ventilation**

4. **Use smaller model** for less intensive processing

## Audio Format Issues

### Issue: "Audio file not found"

**Symptoms**:
```
❌ Audio file '../input/audio.ogg' not found!
```

**Solutions**:

1. **Verify file location**:
```bash
ls -la input/
```

2. **Check filename**:
   - Current scripts look for `audio.ogg`
   - Rename your file or update script

3. **Update script path**:
```python
# In diarization.py or transcription.py
audio_file = "../input/your_actual_filename.mp3"
```

4. **Check permissions**:
```bash
chmod 644 input/your_audio_file.mp3
```

### Issue: Unsupported audio format

**Symptoms**:
```
pydub.exceptions.CouldntDecodeError
```

**Solutions**:

1. **Convert to supported format**:
```bash
ffmpeg -i input.webm -acodec libmp3lame output.mp3
```

2. **Supported formats**:
   - MP3, WAV, OGG, M4A, FLAC
   - AAC, WMA (with proper codecs)

3. **Check FFmpeg installation**:
```bash
ffmpeg -formats | grep -i "your_format"
```

### Issue: Audio is distorted or garbled

**Symptoms**:
- Transcription is nonsense
- Diarization fails
- Playback sounds wrong

**Solutions**:

1. **Check source audio**:
```bash
# Play in QuickTime or VLC
open input/audio.ogg
```

2. **Try different conversion**:
```bash
ffmpeg -i input.ogg -ar 16000 -ac 1 -acodec pcm_s16le output.wav
```

3. **Check for corruption**:
```bash
ffmpeg -v error -i input/audio.ogg -f null -
# If errors shown, file is corrupted
```

## Output Issues

### Issue: Output files are empty or missing

**Symptoms**:
- Files created but contain no content
- Expected files not in `output/` directory

**Solutions**:

1. **Check for errors** in script output:
   - Review console messages
   - Look for exceptions or warnings

2. **Verify write permissions**:
```bash
ls -la output/
chmod 755 output/
```

3. **Check disk space**:
```bash
df -h
# Ensure sufficient space available
```

4. **Run scripts in order**:
   - `diarization.py` first
   - Then `transcription.py`
   - Finally `combine.py`

### Issue: Combined transcript has poor speaker matching

**Symptoms**:
- Speakers frequently switch mid-sentence
- Low confidence scores in output

**Solutions**:

1. **Check diarization quality first**:
   - Review `audio_diarization_results.md`
   - Ensure speaker segments make sense

2. **Improve diarization**:
   - Specify correct speaker count
   - Use higher quality audio
   - Ensure clear speaker separation

3. **Check timestamp alignment**:
   - Diarization and transcription should use same audio file
   - Ensure no audio preprocessing differences

## Error Reference

### Common Error Messages

#### `FileNotFoundError: [Errno 2] No such file or directory`
**Cause**: File path incorrect or file doesn't exist
**Fix**: Verify paths in scripts match actual file locations

#### `RuntimeError: MPS backend out of memory`
**Cause**: Insufficient GPU memory
**Fix**: Use smaller model or reduce cache limit

#### `ModuleNotFoundError: No module named 'X'`
**Cause**: Missing Python package
**Fix**: `pip install X` or `pip install -r requirements.txt`

#### `KeyError: 'segments'`
**Cause**: Transcription JSON malformed or incomplete
**Fix**: Re-run transcription.py, check for errors

#### `JSONDecodeError`
**Cause**: Corrupted JSON output
**Fix**: Delete output JSON files and regenerate

#### `OSError: [Errno 28] No space left on device`
**Cause**: Insufficient disk space
**Fix**: Free up space, models can be large (5-10GB)

### Debug Mode

To get more detailed error information:

**Add to top of any script**:
```python
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)

# Wrap main() in try-except
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("Detailed error:")
        traceback.print_exc()
```

## Getting More Help

### Before Opening an Issue

1. ✅ Check this troubleshooting guide
2. ✅ Review [Installation Guide](INSTALLATION.md)
3. ✅ Verify [Configuration](CONFIGURATION.md)
4. ✅ Search [existing issues](https://github.com/aporb/LocalTranscribe/issues)

### Opening an Issue

Include:

1. **System information**:
   ```bash
   sw_vers  # macOS version
   python3 --version
   pip list | grep -E "torch|whisper|pyannote"
   ```

2. **Steps to reproduce**:
   - Exact commands run
   - Which script failed
   - When error occurred

3. **Error messages**:
   - Complete error output
   - Screenshots if helpful

4. **Audio characteristics**:
   - Format (MP3, WAV, etc.)
   - Duration
   - Number of speakers
   - Quality/source

5. **What you've tried**:
   - Solutions attempted
   - Results of each attempt

### Community Resources

- **GitHub Issues**: [github.com/aporb/LocalTranscribe/issues](https://github.com/aporb/LocalTranscribe/issues)
- **Discussions**: Check repository discussions tab
- **Documentation**: [Installation](INSTALLATION.md) | [Usage](USAGE.md) | [Configuration](CONFIGURATION.md)

## Additional Resources

- **Whisper Documentation**: [github.com/openai/whisper](https://github.com/openai/whisper)
- **Pyannote Documentation**: [github.com/pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio)
- **MLX Documentation**: [ml-explore.github.io/mlx](https://ml-explore.github.io/mlx)
- **PyTorch MPS**: [pytorch.org/docs/stable/notes/mps.html](https://pytorch.org/docs/stable/notes/mps.html)
