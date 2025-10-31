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

---

## Advanced APIs (v3.1+)

LocalTranscribe v3.1 introduces comprehensive quality enhancement modules including audio analysis, quality gates, and enhanced proofreading.

### PipelineOrchestrator

Low-level pipeline orchestrator with full control over processing stages and quality features.

#### `__init__(...)`

Initialize the pipeline orchestrator with advanced options.

**Basic Parameters:**
- `audio_file` (Union[str, Path]): Path to audio file
- `output_dir` (Union[str, Path]): Output directory
- `hf_token` (Optional[str]): HuggingFace token
- `model_size` (str): Whisper model size. Default: "medium"
- `num_speakers` (Optional[int]): Exact number of speakers
- `min_speakers` (Optional[int]): Minimum speakers to detect
- `max_speakers` (Optional[int]): Maximum speakers to detect
- `language` (Optional[str]): Force language
- `verbose` (bool): Enable verbose logging. Default: False

**Phase 1 Parameters (Segment Processing):**
- `enable_segment_processing` (bool): Enable intelligent segment post-processing. Default: True
- `use_speaker_regions` (bool): Use region-based speaker mapping. Default: True
- `segment_config` (Optional[Dict]): Custom segment processing configuration

**Phase 2 Parameters (Quality Enhancements):**
- `enable_audio_analysis` (bool): Enable pre-processing audio quality analysis. Default: False
- `enable_quality_gates` (bool): Enable per-stage quality assessment. Default: False
- `quality_report_path` (Optional[Path]): Path to save quality report
- `enable_proofreading` (bool): Enable enhanced proofreading. Default: False
- `proofreading_domains` (Optional[List[str]]): Domains for proofreading (e.g., ["technical", "business"])
- `enable_acronym_expansion` (bool): Enable acronym expansion. Default: False

**Example:**
```python
from localtranscribe.pipeline import PipelineOrchestrator

# Enable all quality enhancements
pipeline = PipelineOrchestrator(
    audio_file="meeting.wav",
    output_dir="./output",
    # Phase 1: Segment Processing
    enable_segment_processing=True,
    use_speaker_regions=True,
    # Phase 2: Audio Analysis & Quality Gates
    enable_audio_analysis=True,
    enable_quality_gates=True,
    quality_report_path="./quality_report.txt",
    # Phase 2: Enhanced Proofreading
    enable_proofreading=True,
    proofreading_domains=["technical", "business"],
    enable_acronym_expansion=True,
    verbose=True
)

result = pipeline.run()
```

#### `run() -> PipelineResult`

Execute the full pipeline with all configured stages.

**Returns:** `PipelineResult` with processing results

**Pipeline Stages:**
1. Validation
2. Audio Analysis (if enabled)
3. Diarization
4. Segment Processing (Phase 1)
5. Transcription
6. Combination
7. Quality Assessment (if enabled)
8. Labeling (optional)
9. Proofreading (if enabled)

---

### AudioAnalyzer (v3.1)

Analyze audio quality and provide preprocessing recommendations.

#### `__init__(verbose=False)`

Initialize audio analyzer.

**Parameters:**
- `verbose` (bool): Enable verbose output. Default: False

#### `analyze(audio_file: Union[str, Path]) -> AudioAnalysisResult`

Analyze audio quality and characteristics.

**Parameters:**
- `audio_file`: Path to audio file

**Returns:** `AudioAnalysisResult`

**Example:**
```python
from localtranscribe.audio import AudioAnalyzer

analyzer = AudioAnalyzer(verbose=True)
analysis = analyzer.analyze("audio.wav")

print(f"Quality Level: {analysis.quality_level.value}")
print(f"SNR: {analysis.snr_db:.1f} dB")
print(f"Speech Ratio: {analysis.speech_ratio:.2%}")
print(f"Recommended Model: {analysis.recommended_whisper_model}")

if analysis.preprocessing_recommendations:
    print("Recommendations:")
    for rec in analysis.preprocessing_recommendations:
        print(f"  - {rec}")
```

### AudioAnalysisResult

Result from audio quality analysis.

**Attributes:**
- `quality_level` (AudioQualityLevel): Overall quality classification (excellent, high, medium, low, poor)
- `snr_db` (float): Signal-to-Noise Ratio in decibels
- `quality_score` (float): Overall quality score (0-1)
- `peak_amplitude` (float): Peak audio amplitude
- `rms_level` (float): RMS audio level
- `silence_ratio` (float): Percentage of silence
- `speech_ratio` (float): Percentage of speech
- `estimated_speaker_count` (Optional[int]): Rough speaker count estimate
- `is_clipped` (bool): Whether audio contains clipping
- `recommended_whisper_model` (str): Recommended Whisper model size
- `preprocessing_recommendations` (List[str]): List of preprocessing suggestions
- `spectral_centroid` (float): Spectral centroid (Hz)
- `spectral_rolloff` (float): Spectral rolloff point (Hz)

---

### QualityGate (v3.1)

Assess quality at each pipeline stage with configurable thresholds.

#### `__init__(thresholds: Optional[QualityThresholds] = None, verbose=False)`

Initialize quality gate with thresholds.

**Parameters:**
- `thresholds`: Custom quality thresholds (uses defaults if None)
- `verbose`: Enable verbose output. Default: False

#### `assess_diarization_quality(diarization_result) -> QualityAssessment`

Assess diarization quality.

**Returns:** `QualityAssessment` with diarization metrics

#### `assess_transcription_quality(transcription_result) -> QualityAssessment`

Assess transcription quality.

**Returns:** `QualityAssessment` with transcription metrics

#### `assess_combination_quality(combination_result) -> QualityAssessment`

Assess speaker-transcription combination quality.

**Returns:** `QualityAssessment` with combination metrics

#### `generate_quality_report(...) -> str`

Generate comprehensive quality report.

**Parameters:**
- `diarization_assessment`: Diarization quality assessment
- `transcription_assessment`: Transcription quality assessment
- `combination_assessment`: Combination quality assessment
- `audio_analysis`: Optional audio analysis results

**Returns:** Formatted quality report string

**Example:**
```python
from localtranscribe.quality import QualityGate, QualityThresholds

# Custom thresholds (stricter than defaults)
thresholds = QualityThresholds(
    max_micro_segment_ratio=0.10,  # Max 10% micro-segments
    min_avg_segment_duration=2.5,  # Min 2.5s average
    min_avg_confidence=0.75         # Min 75% confidence
)

gate = QualityGate(thresholds=thresholds, verbose=True)

# Assess each stage
diar_assessment = gate.assess_diarization_quality(diarization_result)
trans_assessment = gate.assess_transcription_quality(transcription_result)
comb_assessment = gate.assess_combination_quality(combination_result)

# Check if passed
if diar_assessment.passed:
    print(f"Diarization passed with score: {diar_assessment.overall_score:.2f}")
else:
    print("Issues found:")
    for issue in diar_assessment.issues:
        print(f"  [{issue.severity.value}] {issue.message}")
```

### QualityThresholds

Configurable quality thresholds for assessment.

**Attributes (with defaults):**
- `max_micro_segment_ratio` (float): Max ratio of micro-segments (<0.5s). Default: 0.15
- `min_avg_segment_duration` (float): Min average segment duration (s). Default: 2.0
- `max_speaker_switches_per_minute` (float): Max speaker switches per minute. Default: 8.0
- `min_avg_confidence` (float): Min average transcription confidence. Default: 0.7
- `max_no_speech_prob` (float): Max no-speech probability. Default: 0.3
- `max_compression_ratio` (float): Max compression ratio. Default: 2.5
- `min_speaker_mapping_confidence` (float): Min speaker mapping confidence. Default: 0.6
- `max_ambiguous_segments_ratio` (float): Max ratio of ambiguous segments. Default: 0.1

### QualityAssessment

Result from quality assessment.

**Attributes:**
- `stage` (str): Pipeline stage assessed
- `overall_score` (float): Overall quality score (0-1)
- `passed` (bool): Whether quality threshold passed
- `metrics` (Dict[str, Any]): Detailed metrics
- `issues` (List[QualityIssue]): List of quality issues found

### QualityIssue

A single quality issue with severity.

**Attributes:**
- `severity` (QualitySeverity): Issue severity (low, medium, high, critical)
- `message` (str): Human-readable issue description
- `metric_name` (str): Metric that triggered issue
- `metric_value` (Any): Actual metric value
- `threshold` (Any): Expected threshold

---

### Proofreader (v3.1.1)

Enhanced proofreading with domain dictionaries, acronym expansion, and context-aware intelligence.

#### `__init__(...)`

Initialize proofreader with enhanced features including context-aware matching and automatic model management.

**Basic Parameters:**
- `rules` (Optional[Dict]): Custom proofreading rules
- `level` (ProofreadingLevel): Thoroughness level (minimal, standard, thorough)
- `track_changes` (bool): Track individual changes. Default: True
- `verbose` (bool): Enable verbose logging. Default: False

**Domain Dictionaries (v3.1):**
- `enable_domain_dictionaries` (bool): Enable domain-specific corrections. Default: False
- `domains` (Optional[List[str]]): Domains to enable. Options: "military", "technical", "business", "medical", "legal", "academic", "common", "entities". Default: ["common"]

**Acronym Expansion (v3.1):**
- `enable_acronym_expansion` (bool): Enable acronym expansion. Default: False
- `acronym_format` (str): Expansion format: "parenthetical", "replacement", "footnote". Default: "parenthetical"
- `expand_all_occurrences` (bool): Expand all occurrences vs. first only. Default: False

**Context-Aware Features (v3.1.1 NEW):**
- `enable_context_matching` (bool): Enable spaCy NER-based context analysis for acronym disambiguation. Default: False
- `spacy_model` (str): spaCy model to use. Options: "en_core_web_sm", "en_core_web_md", "en_core_web_lg". Default: "en_core_web_sm"
- `auto_download_model` (bool): Automatically prompt to download missing models. Default: False
- `context_confidence_threshold` (float): Minimum confidence for context-based disambiguation (0-1). Default: 0.7
- `context_window` (int): Number of tokens to analyze before/after acronym. Default: 5

**Performance Features (v3.1.1 NEW):**
- `use_fast_matcher` (bool): Use FlashText for high-performance dictionary matching (10-100x faster). Default: True
- `flashtext_threshold` (int): Minimum dictionary size to trigger FlashText usage. Default: 100

**Typo Correction (v3.1.1 NEW):**
- `enable_fuzzy_matching` (bool): Enable RapidFuzz fuzzy string matching for typo correction. Default: False
- `fuzzy_threshold` (int): Similarity threshold for fuzzy matches (0-100). Default: 85
- `fuzzy_scorer` (str): Fuzzy scoring algorithm. Options: "WRatio", "QRatio". Default: "WRatio"

#### `proofread(text: str) -> ProofreadingResult`

Apply proofreading rules to text.

**Parameters:**
- `text`: Text to proofread

**Returns:** `ProofreadingResult` with corrected text and change tracking

**Example:**
```python
from localtranscribe.proofreading import Proofreader, ProofreadingLevel

# Basic proofreading
proofreader = Proofreader(level=ProofreadingLevel.STANDARD)
result = proofreader.proofread(transcript_text)
print(result.corrected_text)

# With domain dictionaries and acronym expansion (v3.1)
proofreader = Proofreader(
    level=ProofreadingLevel.THOROUGH,
    enable_domain_dictionaries=True,
    domains=["technical", "business", "common"],
    enable_acronym_expansion=True,
    acronym_format="parenthetical",  # API (Application Programming Interface)
    verbose=True
)

result = proofreader.proofread(transcript_text)

# NEW v3.1.1 - Full context-aware intelligence
proofreader = Proofreader(
    level=ProofreadingLevel.THOROUGH,
    # Context-aware features
    enable_context_matching=True,
    spacy_model="en_core_web_sm",
    auto_download_model=True,  # Will prompt if model missing
    context_confidence_threshold=0.7,
    context_window=5,
    # High-performance matching
    use_fast_matcher=True,
    # Typo tolerance
    enable_fuzzy_matching=True,
    fuzzy_threshold=85,
    # Domain dictionaries (360+ terms across 8 domains)
    enable_domain_dictionaries=True,
    domains=["technical", "business", "legal", "academic"],
    # Acronym expansion (180+ definitions)
    enable_acronym_expansion=True,
    acronym_format="parenthetical",
    verbose=True
)

result = proofreader.proofread(transcript_text)

if result.has_changes:
    print(f"Made {result.total_changes} corrections")
    print(result.get_summary())

    # See what changed
    for change in result.changes[:5]:
        print(f"  '{change.original}' → '{change.replacement}'")
```

### ProofreadingResult

Result from proofreading operation.

**Attributes:**
- `original_text` (str): Original input text
- `corrected_text` (str): Corrected output text
- `changes` (List[ProofreadingChange]): Individual changes made
- `rules_applied` (int): Number of rules that matched
- `total_changes` (int): Total number of corrections made
- `processing_time` (float): Time taken in seconds
- `success` (bool): Whether proofreading succeeded
- `has_changes` (bool): Whether any changes were made

**Methods:**
- `get_summary() -> str`: Get human-readable summary of changes

---

### ModelManager (v3.1.1)

Manages NLP model lifecycle including detection, downloading, and loading.

#### `__init__(model_name: str = "en_core_web_sm", verbose: bool = False)`

Initialize model manager for a specific spaCy model.

**Parameters:**
- `model_name` (str): spaCy model to manage. Options: "en_core_web_sm", "en_core_web_md", "en_core_web_lg". Default: "en_core_web_sm"
- `verbose` (bool): Enable verbose logging. Default: False

**Available Models:**
- `en_core_web_sm`: 13 MB, fast, good for most use cases
- `en_core_web_md`: 43 MB, medium speed, better accuracy
- `en_core_web_lg`: 741 MB, slow, maximum accuracy

#### `is_model_installed() -> bool`

Check if the configured model is installed.

**Returns:** `bool` - True if model is available

#### `download_model(quiet: bool = False) -> bool`

Download the configured model using spaCy's download mechanism.

**Parameters:**
- `quiet` (bool): Suppress download output. Default: False

**Returns:** `bool` - True if download succeeded

#### `prompt_download(model_name: Optional[str] = None) -> bool`

Interactive prompt asking user if they want to download a model.

**Parameters:**
- `model_name` (Optional[str]): Override model name for prompt

**Returns:** `bool` - True if user downloaded the model

**Example:**
```python
from localtranscribe.proofreading.model_manager import ModelManager

# Check if model is installed
manager = ModelManager(model_name="en_core_web_sm")

if not manager.is_model_installed():
    print("Model not found")
    # Interactive prompt
    if manager.prompt_download():
        print("Model downloaded successfully!")
    else:
        print("User declined download")

# Direct download without prompt
manager = ModelManager(model_name="en_core_web_md", verbose=True)
success = manager.download_model(quiet=False)
```

#### Module Functions

**`check_dependencies() -> Dict[str, Any]`**

Check status of all NLP dependencies.

**Returns:** Dictionary with:
- `spacy_installed` (bool): Whether spaCy is installed
- `flashtext_available` (bool): Whether FlashText is available
- `rapidfuzz_available` (bool): Whether RapidFuzz is available
- `installed_models` (List[str]): List of installed spaCy models
- `context_aware_ready` (bool): Whether context-aware features are ready

**Example:**
```python
from localtranscribe.proofreading.model_manager import check_dependencies

status = check_dependencies()

print(f"spaCy: {status['spacy_installed']}")
print(f"FlashText: {status['flashtext_available']}")
print(f"RapidFuzz: {status['rapidfuzz_available']}")
print(f"Installed models: {status['installed_models']}")
print(f"Context-aware ready: {status['context_aware_ready']}")
```

**`ensure_spacy_model(model_name: str = "en_core_web_sm", auto_download: bool = False, quiet: bool = False) -> Tuple[Optional[Any], bool]`**

Ensure a spaCy model is available, optionally downloading if missing.

**Parameters:**
- `model_name` (str): Model to ensure is available
- `auto_download` (bool): Automatically prompt for download if missing. Default: False
- `quiet` (bool): Suppress output. Default: False

**Returns:** Tuple of:
- `nlp` (Optional[Any]): Loaded spaCy Language object, or None if unavailable
- `ready` (bool): Whether model is ready to use

**Example:**
```python
from localtranscribe.proofreading.model_manager import ensure_spacy_model

# Load model, auto-prompt if missing
nlp, ready = ensure_spacy_model(
    model_name="en_core_web_sm",
    auto_download=True,
    quiet=False
)

if ready:
    # Use nlp for context analysis
    doc = nlp("The IP address is 192.168.1.1")
    for ent in doc.ents:
        print(f"{ent.text}: {ent.label_}")
else:
    print("Model not available, falling back to basic mode")
```

---

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
