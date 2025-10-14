# LocalTranscribe SDK Reference

The LocalTranscribe SDK provides a high-level, Pythonic API for programmatic audio transcription with speaker diarization.

## Installation

```bash
pip install localtranscribe

# For Apple Silicon (recommended)
pip install localtranscribe[mlx]

# For GPU acceleration
pip install localtranscribe[faster]
```

## Quick Start

```python
from localtranscribe import LocalTranscribe

# Initialize client
lt = LocalTranscribe(model_size="base", num_speakers=2)

# Process single file
result = lt.process("meeting.mp3")
print(result.transcript)

# Process multiple files
results = lt.process_batch("./audio_files/")
print(f"Processed {results.successful}/{results.total} files")
```

## API Reference

### LocalTranscribe

Main client class for transcription operations.

#### `__init__(...)`

Initialize the client with default settings.

**Parameters:**
- `model_size` (str): Whisper model size. Options: "tiny", "base", "small", "medium", "large". Default: "base"
- `num_speakers` (Optional[int]): Exact number of speakers if known
- `min_speakers` (Optional[int]): Minimum speakers to detect
- `max_speakers` (Optional[int]): Maximum speakers to detect
- `language` (Optional[str]): Force language (e.g., "en", "es", "fr")
- `implementation` (str): Whisper implementation. Options: "auto", "mlx", "faster", "original". Default: "auto"
- `output_dir` (Optional[Path]): Default output directory. Default: "./output"
- `hf_token` (Optional[str]): HuggingFace token. Defaults to `HUGGINGFACE_TOKEN` env var
- `config_file` (Optional[Path]): Path to configuration file
- `verbose` (bool): Enable verbose logging. Default: False

**Example:**
```python
lt = LocalTranscribe(
    model_size="medium",
    num_speakers=3,
    language="en",
    output_dir="./transcripts",
    verbose=True
)
```

#### `process(audio_file, **kwargs) -> ProcessResult`

Process a single audio file.

**Parameters:**
- `audio_file` (Union[str, Path]): Path to audio file
- `output_dir` (Optional[Path]): Override default output directory
- `output_formats` (Optional[List[str]]): Output formats. Options: "txt", "json", "srt", "vtt", "md"
- `skip_diarization` (bool): Skip speaker diarization. Default: False
- `**kwargs`: Override any initialization parameters

**Returns:** `ProcessResult`

**Example:**
```python
result = lt.process(
    "meeting.mp3",
    output_dir="./results",
    output_formats=["txt", "srt"],
    model_size="large"  # Override for this call
)

print(f"Speakers: {result.num_speakers}")
print(f"Processing time: {result.processing_time:.1f}s")
print(result.transcript)

# Access individual segments
for segment in result.segments:
    print(f"[{segment.speaker}] {segment.text}")
```

#### `process_batch(input_dir, **kwargs) -> BatchResult`

Process multiple audio files in a directory.

**Parameters:**
- `input_dir` (Union[str, Path]): Directory containing audio files
- `output_dir` (Optional[Path]): Override default output directory
- `max_workers` (int): Maximum parallel workers. Default: 2
- `skip_existing` (bool): Skip files with existing outputs. Default: False
- `recursive` (bool): Search subdirectories. Default: False
- `**kwargs`: Override any initialization parameters

**Returns:** `BatchResult`

**Example:**
```python
results = lt.process_batch(
    "./audio_files",
    max_workers=4,
    skip_existing=True,
    recursive=True
)

print(f"Success rate: {results.successful}/{results.total}")
print(f"Total time: {results.processing_time:.1f}s")

# Handle failures
for result in results.get_failed():
    print(f"Failed: {result.audio_file} - {result.error}")
```

### ProcessResult

Result from processing a single audio file.

**Attributes:**
- `success` (bool): Whether processing succeeded
- `audio_file` (Path): Path to input audio file
- `processing_time` (float): Time taken in seconds
- `transcript` (str): Full transcript text
- `segments` (List[Segment]): Individual speech segments
- `num_speakers` (Optional[int]): Number of speakers detected
- `speaker_durations` (Dict[str, float]): Speaking time per speaker
- `output_files` (Dict[str, Path]): Generated output files by format
- `model_size` (str): Model size used
- `language` (Optional[str]): Detected or forced language
- `error` (Optional[str]): Error message if failed

### BatchResult

Result from batch processing multiple files.

**Attributes:**
- `total` (int): Total files processed
- `successful` (int): Number of successful files
- `failed` (int): Number of failed files
- `processing_time` (float): Total time in seconds
- `results` (List[ProcessResult]): Individual results

**Methods:**
- `get_successful() -> List[ProcessResult]`: Get successful results
- `get_failed() -> List[ProcessResult]`: Get failed results

### Segment

A single speech segment with speaker and timestamp.

**Attributes:**
- `speaker` (str): Speaker label (e.g., "SPEAKER_00")
- `text` (str): Transcript text for this segment
- `start` (float): Start time in seconds
- `end` (float): End time in seconds
- `confidence` (Optional[float]): Confidence score (if available)

## Usage Examples

### Basic Transcription

```python
from localtranscribe import LocalTranscribe

# Initialize with basic settings
lt = LocalTranscribe(model_size="base")

# Process single file
result = lt.process("audio.mp3")

if result.success:
    print(result.transcript)
else:
    print(f"Error: {result.error}")
```

### Transcribe with Known Speakers

```python
from localtranscribe import LocalTranscribe

# Initialize with speaker count
lt = LocalTranscribe(
    model_size="medium",
    num_speakers=2  # We know there are 2 speakers
)

# Process
result = lt.process("interview.mp3")

print(f"Detected {result.num_speakers} speakers")
for segment in result.segments[:10]:
    print(f"[{segment.speaker}] {segment.text}")
```

### Batch Processing

```python
from localtranscribe import LocalTranscribe

# Initialize for batch processing
lt = LocalTranscribe(
    model_size="small",
    skip_diarization=True  # Faster for single-speaker content
)

# Process entire directory
results = lt.process_batch(
    "./lectures",
    output_dir="./transcripts",
    max_workers=4,
    recursive=True
)

print(f"Processed {results.successful}/{results.total} files")

# Export summary
with open("summary.txt", "w") as f:
    for result in results.get_successful():
        f.write(f"{result.audio_file.name}: {len(result.transcript)} chars\n")
```

### Error Handling

```python
from localtranscribe import LocalTranscribe, LocalTranscribeError

lt = LocalTranscribe()

try:
    result = lt.process("audio.mp3")
    if result.success:
        print(result.transcript)
    else:
        print(f"Processing failed: {result.error}")
except LocalTranscribeError as e:
    print(f"Error: {e}")
```

### Custom Configuration

```python
from localtranscribe import LocalTranscribe

# Use configuration file
lt = LocalTranscribe(config_file="./my-config.yaml")

# Override specific settings for a call
result = lt.process(
    "audio.mp3",
    model_size="large",
    num_speakers=3
)
```

### Multilingual Support

```python
from localtranscribe import LocalTranscribe

# Auto-detect language
lt = LocalTranscribe(model_size="base")
result = lt.process("spanish_audio.mp3")
print(f"Detected language: {result.language}")

# Force specific language
lt = LocalTranscribe(model_size="base", language="es")
result = lt.process("spanish_audio.mp3")
```

## Advanced Usage

### Accessing Segment Details

```python
result = lt.process("meeting.mp3")

for segment in result.segments:
    duration = segment.end - segment.start
    print(f"[{segment.speaker}] ({segment.start:.1f}s - {segment.end:.1f}s, {duration:.1f}s)")
    print(f"  {segment.text}")
    print()
```

### Speaker Duration Analysis

```python
result = lt.process("panel_discussion.mp3")

print("Speaker durations:")
for speaker, duration in result.speaker_durations.items():
    percentage = (duration / result.processing_time) * 100
    print(f"{speaker}: {duration:.1f}s ({percentage:.1f}%)")
```

### Parallel Processing with Custom Logic

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from localtranscribe import LocalTranscribe

lt = LocalTranscribe(model_size="base")
files = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(lt.process, f): f for f in files}

    for future in as_completed(futures):
        file = futures[future]
        try:
            result = future.result()
            print(f"✓ {file}: {result.processing_time:.1f}s")
        except Exception as e:
            print(f"✗ {file}: {e}")
```

## Environment Variables

The SDK respects the following environment variables:

- `HUGGINGFACE_TOKEN`: HuggingFace API token for diarization models
- Other configuration can be set via `config.yaml` file

## See Also

- [CLI Reference](CLI_REFERENCE.md) - Command-line interface documentation
- [Configuration Guide](CONFIGURATION.md) - Configuration file format
- [Contributing](guides/contributing.md) - How to contribute to the project
