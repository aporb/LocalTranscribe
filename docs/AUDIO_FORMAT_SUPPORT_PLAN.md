# Audio Format Support Analysis & Implementation Plan

**Date:** 2025-10-13
**Version:** 1.0
**Status:** Analysis Complete - Ready for Implementation

---

## Executive Summary

**Current State:** LocalTranscribe claims to support video file audio extraction but the code blocks these formats. The system is artificially limited to 8 audio formats despite having technical capability for 200+ formats through FFmpeg/pydub.

**Recommendation:** Implement phased improvements to expand format support, fix documentation mismatches, and improve architecture for long-term maintainability.

---

## Current Format Support Analysis

### ✅ Currently Supported (Code)
```python
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus'}
```

| Format | Extension | Documentation | Code Support | Notes |
|--------|-----------|--------------|--------------|-------|
| MP3 | `.mp3` | ✅ | ✅ | Working |
| WAV | `.wav` | ✅ | ✅ | Working |
| OGG | `.ogg` | ✅ | ✅ | Working |
| M4A | `.m4a` | ✅ | ✅ | Working |
| FLAC | `.flac` | ✅ | ✅ | Working |
| AAC | `.aac` | ✅ | ✅ | Working |
| WMA | `.wma` | ✅ | ✅ | Working |
| OPUS | `.opus` | ❌ | ✅ | **Undocumented** |

### ❌ Claimed But Not Supported (README)
| Format | Extension | Documentation | Code Support | Status |
|--------|-----------|--------------|--------------|--------|
| MP4 Video | `.mp4` | ✅ | ❌ | **Documentation Mismatch** |
| MOV Video | `.mov` | ✅ | ❌ | **Documentation Mismatch** |
| AVI Video | `.avi` | ✅ | ❌ | **Documentation Mismatch** |

**README Line 290-292 Claims:**
> **Supported Audio Formats:**
> - MP3, WAV, M4A, OGG, FLAC, AAC, WMA
> - Video files (MP4, MOV, AVI) - audio will be extracted

**Reality:** Video files are blocked by `PathResolver.validate_audio_file()` before reaching audio extraction logic.

---

## Technical Capability Assessment

### Dependencies Analysis

**Stack:**
1. **FFmpeg** (system dependency, installed via `brew install ffmpeg`)
2. **pydub** (Python wrapper for FFmpeg)
3. **LocalTranscribe** (uses pydub for preprocessing)

**FFmpeg Format Support:**
- 200+ container formats
- All common audio codecs
- Video audio extraction
- Format conversion

**pydub Capabilities:**
```python
# From Context7 research - pydub documentation examples:
AudioSegment.from_file("video.mp4", "mp4")     # Video audio extraction
AudioSegment.from_file("audio.flv", "flv")     # Flash video
AudioSegment.from_file("audio.wma", "wma")     # Windows Media
AudioSegment.from_file()                        # Generic - handles ANY FFmpeg format
```

**Key Insight:** `AudioSegment.from_file()` with no format parameter attempts automatic format detection and can handle any format FFmpeg supports.

### Current Architecture Bottleneck

**Problem:** Hard extension whitelist before flexible processing

**Code Flow:**
```
User provides file
  ↓
PathResolver.resolve_audio_file()
  ↓
PathResolver.validate_audio_file() ← BLOCKS HERE if extension not in whitelist
  ↓
preprocess_audio() ← NEVER REACHED for unsupported extensions
  ↓
AudioSegment.from_file() ← CAN HANDLE 200+ FORMATS
```

**Result:** Technical capability exists but is gated by artificial restriction.

---

## Code Issues Identified

### 1. Duplicated Constants ⚠️

**Location 1:** `localtranscribe/core/path_resolver.py:18`
```python
class PathResolver:
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus'}
```

**Location 2:** `localtranscribe/batch/processor.py:71`
```python
class BatchProcessor:
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma", ".opus"}
```

**Risk:** Changes must be synchronized across both files or formats diverge.

**Best Practice:** Centralize in `localtranscribe/config/defaults.py`

### 2. Overly Restrictive Validation

**Current:** `PathResolver.validate_audio_file()` raises `InvalidAudioFormatError` immediately for unknown extensions

**Better Approach:**
- Let pydub/FFmpeg attempt processing
- Catch errors at preprocessing stage
- Provide format-specific error messages

### 3. No Format Testing Feedback

**Current Behavior:**
```bash
$ localtranscribe process video.mp4
❌ Unsupported audio format: .mp4
```

**Desired Behavior:**
```bash
$ localtranscribe process video.mp4
⚠️  Video format detected - extracting audio track...
✓ Processing video.mp4
```

---

## Implementation Plan

### Phase 1: Quick Win (v2.0.3) - PRIORITY

**Goal:** Fix README claims and add video format support

**Changes Required:**

1. **Update `localtranscribe/core/path_resolver.py:18`**
   ```python
   # OLD
   AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus'}

   # NEW
   AUDIO_EXTENSIONS = {
       # Audio formats
       '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus',
       # Video formats (audio extraction)
       '.mp4', '.mov', '.avi', '.mkv', '.webm'
   }
   ```

2. **Update `localtranscribe/batch/processor.py:71`**
   ```python
   # Same change as above
   AUDIO_EXTENSIONS = {
       '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus',
       '.mp4', '.mov', '.avi', '.mkv', '.webm'
   }
   ```

3. **Update `README.md:290-292`**
   ```markdown
   **Supported Audio Formats:**
   - Audio: MP3, WAV, M4A, OGG, FLAC, AAC, WMA, OPUS
   - Video: MP4, MOV, AVI, MKV, WEBM (audio will be extracted)
   ```

**Testing:**
- Test with sample MP4 file
- Test with sample MOV file
- Verify audio extraction works correctly
- Update system requirements to emphasize FFmpeg dependency

**Effort:** 2-3 hours
**Risk:** Low (pydub already handles these formats)

---

### Phase 2: Architecture Improvement (v2.1.0)

**Goal:** Centralize configuration and add flexibility

**Changes Required:**

1. **Create `localtranscribe/config/defaults.py` constant**
   ```python
   # Add to DEFAULT_CONFIG
   "formats": {
       "supported_audio": ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.opus'],
       "supported_video": ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
       "strict_mode": False,  # If False, warn but attempt any format
   }
   ```

2. **Refactor PathResolver to use config**
   ```python
   from ..config.defaults import DEFAULT_CONFIG

   class PathResolver:
       def __init__(self, strict_mode: bool = False):
           audio_exts = set(DEFAULT_CONFIG['formats']['supported_audio'])
           video_exts = set(DEFAULT_CONFIG['formats']['supported_video'])
           self.AUDIO_EXTENSIONS = audio_exts | video_exts
           self.strict_mode = strict_mode
   ```

3. **Add non-strict mode validation**
   ```python
   def validate_audio_file(self, file_path: Path) -> bool:
       if not self.strict_mode:
           # Warn about untested formats but allow
           if file_path.suffix.lower() not in self.AUDIO_EXTENSIONS:
               logger.warning(f"Format {file_path.suffix} is untested - attempting anyway")
           return True
       else:
           # Original strict validation
           ...
   ```

4. **Add CLI flag**
   ```bash
   localtranscribe process audio.xyz --strict-formats
   ```

**Testing:**
- Test with exotic formats (AIFF, AMR, etc.)
- Verify warning messages
- Test strict mode blocks unknown formats

**Effort:** 1 week
**Risk:** Medium (refactoring requires careful testing)

---

### Phase 3: Enhanced UX (v2.2.0)

**Goal:** Better user feedback and format discovery

**Features:**

1. **Format detection feedback**
   ```python
   def detect_format_type(file_path: Path) -> str:
       """Detect if audio, video, or unknown format."""
       ext = file_path.suffix.lower()
       if ext in VIDEO_EXTENSIONS:
           return "video"
       elif ext in AUDIO_EXTENSIONS:
           return "audio"
       return "unknown"
   ```

2. **New CLI command**
   ```bash
   $ localtranscribe formats --list

   Supported Audio Formats (8):
   - MP3, WAV, OGG, M4A, FLAC, AAC, WMA, OPUS

   Supported Video Formats (5):
   - MP4, MOV, AVI, MKV, WEBM (audio extraction)

   Experimental Formats (FFmpeg required):
   - Any format supported by FFmpeg with --no-strict flag
   ```

3. **Format-specific error messages**
   ```python
   if format == "video":
       suggestions.append("Video file detected - ensure FFmpeg is installed")
   elif format == "unknown":
       suggestions.append("Try: localtranscribe process file.xyz --no-strict")
   ```

**Effort:** 1 week
**Risk:** Low (additive features only)

---

## Additional Format Candidates

### Common Formats to Consider Adding

| Format | Extension | Use Case | Priority |
|--------|-----------|----------|----------|
| AIFF | `.aiff`, `.aif` | Apple pro audio | Medium |
| AMR | `.amr` | Mobile recordings | Low |
| 3GP | `.3gp` | Mobile video | Low |
| FLV | `.flv` | Flash video | Low |
| MKA | `.mka` | Matroska audio | Low |
| WEBM | `.webm` | Web video | High (Phase 1) |

**Recommendation:** Start with Phase 1 video formats. Add others in Phase 2 with non-strict mode.

---

## Testing Strategy

### Unit Tests (To Be Created)

```python
# tests/test_formats.py
def test_video_format_support():
    """Test video file audio extraction."""
    resolver = PathResolver()
    assert resolver.validate_audio_file(Path("test.mp4"))
    assert resolver.validate_audio_file(Path("test.mov"))

def test_strict_mode():
    """Test strict mode blocks unknown formats."""
    resolver = PathResolver(strict_mode=True)
    with pytest.raises(InvalidAudioFormatError):
        resolver.validate_audio_file(Path("test.xyz"))

def test_non_strict_mode():
    """Test non-strict mode allows unknown formats."""
    resolver = PathResolver(strict_mode=False)
    assert resolver.validate_audio_file(Path("test.xyz"))
```

### Integration Tests

1. **Video Test:** Process MP4 file with known audio track
2. **Exotic Format Test:** Try AIFF, AMR with non-strict mode
3. **Error Handling:** Verify graceful failure for corrupted files

---

## Documentation Updates Required

### 1. README.md
- Add OPUS to supported audio formats list
- Update video format list to match code
- Add note about FFmpeg requirement for video
- Add troubleshooting section for format issues

### 2. TROUBLESHOOTING.md
```markdown
### Unsupported Audio Format Error

**Problem:** "Unsupported audio format: .xyz"

**Solutions:**
1. Convert file: `ffmpeg -i input.xyz output.mp3`
2. Use non-strict mode: `localtranscribe process file.xyz --no-strict`
3. Check supported formats: `localtranscribe formats --list`

**Note:** Video files require FFmpeg: `brew install ffmpeg`
```

### 3. SDK_REFERENCE.md
```python
# Example: Processing video file
lt = LocalTranscribe()
result = lt.process("meeting_recording.mp4")  # Extracts audio automatically
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Video processing fails | Low | High | Comprehensive testing with various codecs |
| Performance degradation | Low | Medium | Video preprocessing may be slower - add progress indicator |
| FFmpeg not installed | Medium | High | Enhanced error message with install instructions |
| Format confusion | Low | Low | Clear documentation and warnings |

---

## Success Metrics

### Phase 1 Success Criteria
- [ ] Video files (MP4, MOV, AVI, MKV, WEBM) process successfully
- [ ] README matches actual code support
- [ ] No breaking changes to existing functionality
- [ ] Tests pass with video files

### Phase 2 Success Criteria
- [ ] AUDIO_EXTENSIONS centralized (no duplication)
- [ ] Non-strict mode allows exotic formats
- [ ] Warning system functional
- [ ] Zero config changes needed for existing users

### Phase 3 Success Criteria
- [ ] `localtranscribe formats` command works
- [ ] Format detection provides helpful feedback
- [ ] User confusion reduced (measured by GitHub issues)

---

## Conclusion

LocalTranscribe has the **technical capability** to support any audio format that FFmpeg handles (200+), but is artificially limited by extension whitelisting.

**Immediate Action:** Implement Phase 1 to fix README claims and add video format support (2-3 hours work, high user value).

**Long-term Action:** Implement Phases 2-3 for architectural improvements and enhanced UX (2-3 weeks work, moderate user value).

**Key Takeaway:** The question "will @localtranscribe/ work with any type of audio file input?" has the answer:
- **Currently:** No - limited to 8 audio formats
- **Technically:** Yes - can support 200+ formats with minor code changes
- **After Phase 1:** Mostly - will support 8 audio + 5 video formats
- **After Phase 2:** Yes (with warnings) - will attempt any format in non-strict mode

---

## Appendix A: Code Locations

### Files Requiring Changes

**Phase 1:**
- `localtranscribe/core/path_resolver.py:18` - Add video extensions
- `localtranscribe/batch/processor.py:71` - Add video extensions
- `README.md:290-292` - Update format list

**Phase 2:**
- `localtranscribe/config/defaults.py` - Add format configuration
- `localtranscribe/core/path_resolver.py` - Refactor to use config
- `localtranscribe/batch/processor.py` - Refactor to use config
- `localtranscribe/cli/commands/process.py` - Add `--strict-formats` flag

**Phase 3:**
- `localtranscribe/cli/commands/formats.py` (new file) - Add formats command
- `localtranscribe/core/path_resolver.py` - Add format detection
- `docs/TROUBLESHOOTING.md` - Add format troubleshooting

---

## Appendix B: Research References

**pydub Documentation:**
- AudioSegment.from_file() supports any FFmpeg format
- Automatic format detection available
- Format parameter optional but recommended for clarity

**FFmpeg Format Support:**
- Full list: `ffmpeg -formats`
- Video audio extraction: `-vn` flag for audio-only
- Robust error handling for corrupted files

**LocalTranscribe Architecture:**
- Two preprocessing functions (transcription.py and diarization.py)
- Both use identical pydub logic
- Both convert to 16kHz mono WAV for processing
- Original file preserved, processed file cleaned up

---

**Document Version:** 1.0
**Last Updated:** 2025-10-13
**Prepared By:** Claude Code Analysis
**Next Review:** After Phase 1 Implementation
