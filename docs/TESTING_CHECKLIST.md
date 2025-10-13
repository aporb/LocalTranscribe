# LocalTranscribe v2.0 - End-to-End Testing Checklist

This checklist ensures all v2.0 features work correctly after installation.

## Pre-Testing Setup

- [ ] **Fresh Installation**
  ```bash
  # Clean start
  rm -rf venv
  ./install.sh
  ```

- [ ] **Activate Environment**
  ```bash
  source venv/bin/activate
  ```

- [ ] **Verify Installation**
  ```bash
  localtranscribe version
  ```

## 1. Health Check Tests

### Basic Health Check
- [ ] **Run doctor command**
  ```bash
  localtranscribe doctor
  ```
  - [ ] Should show all green checkmarks
  - [ ] Python version detected correctly
  - [ ] PyTorch with device info (MPS/CUDA/CPU)
  - [ ] At least one Whisper implementation available
  - [ ] FFmpeg installed
  - [ ] HuggingFace token configured

### Verbose Health Check
- [ ] **Run doctor with verbose flag**
  ```bash
  localtranscribe doctor -v
  ```
  - [ ] Should show detailed version information
  - [ ] Should list available Whisper implementations
  - [ ] Should show device details

### Health Check Failure Scenarios
- [ ] **Test with missing token** (temporarily rename .env)
  ```bash
  mv .env .env.backup
  localtranscribe doctor
  # Should show warning about missing HF token
  mv .env.backup .env
  ```

## 2. Configuration Tests

### Configuration File
- [ ] **Test config file loading**
  ```bash
  cp config.yaml.example localtranscribe.yaml
  localtranscribe config-show
  ```
  - [ ] Should display configuration settings
  - [ ] Should show config file location

### Environment Variables
- [ ] **Test environment variable override**
  ```bash
  export LOCALTRANSCRIBE_MODEL_WHISPER_SIZE=small
  localtranscribe config-show
  # Should show whisper_size: small
  unset LOCALTRANSCRIBE_MODEL_WHISPER_SIZE
  ```

## 3. Basic Processing Tests

### Test Audio Setup
- [ ] **Prepare test audio file**
  ```bash
  # Use a short audio file (< 1 minute) for testing
  mkdir -p input
  # Place a test audio file: input/test.mp3
  ```

### Full Pipeline Test
- [ ] **Process with default settings**
  ```bash
  localtranscribe process input/test.mp3
  ```
  - [ ] Should complete without errors
  - [ ] Should create output directory
  - [ ] Should show progress indicators
  - [ ] Should generate all output files

### Verify Output Files
- [ ] **Check output directory**
  ```bash
  ls -la output/
  ```
  Expected files:
  - [ ] `test_diarization.md` - Speaker diarization results
  - [ ] `test_transcript.txt` - Plain text transcript
  - [ ] `test_transcript.json` - JSON with metadata
  - [ ] `test_transcript.md` - Markdown transcript
  - [ ] `test_combined.md` - Combined speaker-labeled transcript

### Verify Output Content
- [ ] **Check diarization output**
  ```bash
  cat output/test_diarization.md
  ```
  - [ ] Contains speaker segments table
  - [ ] Shows speaker time distribution
  - [ ] Includes summary statistics

- [ ] **Check combined output**
  ```bash
  cat output/test_combined.md
  ```
  - [ ] Contains speaker labels (SPEAKER_00, SPEAKER_01, etc.)
  - [ ] Shows timestamp ranges
  - [ ] Includes confidence scores
  - [ ] Shows speaking time distribution

## 4. CLI Options Tests

### Output Directory
- [ ] **Custom output directory**
  ```bash
  localtranscribe process input/test.mp3 -o custom_output/
  ls -la custom_output/
  ```
  - [ ] Should create custom_output/ directory
  - [ ] Should place files in custom location

### Model Size
- [ ] **Test different model sizes**
  ```bash
  # Tiny model (fastest)
  localtranscribe process input/test.mp3 --model tiny -o output_tiny/

  # Small model
  localtranscribe process input/test.mp3 --model small -o output_small/
  ```
  - [ ] Should use specified model
  - [ ] Tiny should be faster than small

### Speaker Count
- [ ] **Specify speaker count**
  ```bash
  localtranscribe process input/test.mp3 --speakers 2 -o output_2speakers/
  ```
  - [ ] Should detect exactly 2 speakers (if audio has 2 speakers)

### Skip Diarization
- [ ] **Transcription only**
  ```bash
  localtranscribe process input/test.mp3 --skip-diarization -o output_no_diar/
  ```
  - [ ] Should skip diarization stage
  - [ ] Should only generate transcription files
  - [ ] Should NOT generate diarization.md or combined.md

### Language Option
- [ ] **Force language**
  ```bash
  localtranscribe process input/test.mp3 --language en -o output_en/
  ```
  - [ ] Should force English language
  - [ ] Should work with other languages (es, fr, etc.)

### Output Formats
- [ ] **Specify output formats**
  ```bash
  localtranscribe process input/test.mp3 --format txt json -o output_formats/
  ```
  - [ ] Should generate only txt and json
  - [ ] Should NOT generate md or srt

### Verbose Mode
- [ ] **Test verbose output**
  ```bash
  localtranscribe process input/test.mp3 --verbose -o output_verbose/
  ```
  - [ ] Should show detailed processing information
  - [ ] Should display configuration table
  - [ ] Should show stage completion messages

### Whisper Implementation
- [ ] **Test MLX (if available on Apple Silicon)**
  ```bash
  localtranscribe process input/test.mp3 --implementation mlx
  ```

- [ ] **Test Faster-Whisper (if installed)**
  ```bash
  localtranscribe process input/test.mp3 --implementation faster
  ```

- [ ] **Test Original Whisper (if installed)**
  ```bash
  localtranscribe process input/test.mp3 --implementation original
  ```

## 5. Path Resolution Tests

### Absolute Path
- [ ] **Test absolute path**
  ```bash
  localtranscribe process /full/path/to/audio.mp3
  ```
  - [ ] Should work with absolute paths

### Relative Path
- [ ] **Test relative path**
  ```bash
  cd input
  localtranscribe process test.mp3 -o ../output_relative/
  cd ..
  ```
  - [ ] Should resolve relative paths correctly

### Different Locations
- [ ] **Test from different directories**
  ```bash
  mkdir -p ~/Music
  cp input/test.mp3 ~/Music/
  localtranscribe process ~/Music/test.mp3 -o output_music/
  ```
  - [ ] Should work with files in any location

## 6. Error Handling Tests

### Missing File
- [ ] **Test with non-existent file**
  ```bash
  localtranscribe process nonexistent.mp3
  ```
  - [ ] Should show helpful error message
  - [ ] Should suggest file locations
  - [ ] Should NOT crash with traceback

### Invalid HF Token
- [ ] **Test with invalid token**
  ```bash
  localtranscribe process input/test.mp3 --hf-token invalid_token
  ```
  - [ ] Should show helpful error about HF token
  - [ ] Should provide link to get token

### Unsupported Format
- [ ] **Test with text file**
  ```bash
  touch test.txt
  localtranscribe process test.txt
  ```
  - [ ] Should show error about invalid audio format
  - [ ] Should suggest supported formats

## 7. Integration Tests

### Full Workflow
- [ ] **Complete workflow test**
  ```bash
  # Start fresh
  rm -rf output/

  # Process audio
  localtranscribe process input/test.mp3 --model base --speakers 2 --verbose

  # Verify outputs
  test -f output/test_diarization.md && echo "✓ Diarization output exists"
  test -f output/test_transcript.txt && echo "✓ Transcript TXT exists"
  test -f output/test_transcript.json && echo "✓ Transcript JSON exists"
  test -f output/test_transcript.md && echo "✓ Transcript MD exists"
  test -f output/test_combined.md && echo "✓ Combined output exists"
  ```

### Multiple Files
- [ ] **Process multiple files**
  ```bash
  localtranscribe process input/file1.mp3 -o output1/
  localtranscribe process input/file2.mp3 -o output2/
  ```
  - [ ] Should process each file independently
  - [ ] Should not interfere with each other

### Configuration Persistence
- [ ] **Test configuration override chain**
  ```bash
  # Set in config file
  echo "model:" > localtranscribe.yaml
  echo "  whisper_size: tiny" >> localtranscribe.yaml

  # Override with env var
  export LOCALTRANSCRIBE_MODEL_WHISPER_SIZE=small

  # Override with CLI arg (should win)
  localtranscribe process input/test.mp3 --model large --verbose
  # Should use 'large' model

  unset LOCALTRANSCRIBE_MODEL_WHISPER_SIZE
  rm localtranscribe.yaml
  ```

## 8. Performance Tests

### Timing
- [ ] **Measure processing time**
  ```bash
  time localtranscribe process input/test.mp3
  ```
  - [ ] Should complete in reasonable time
  - [ ] MLX should be faster than original (on Apple Silicon)

### Memory Usage
- [ ] **Monitor memory usage**
  ```bash
  # In another terminal
  watch -n 1 "ps aux | grep localtranscribe"

  # Run processing
  localtranscribe process input/test.mp3
  ```
  - [ ] Should not leak memory
  - [ ] Should complete without OOM errors

## 9. Help and Documentation Tests

### CLI Help
- [ ] **Test help commands**
  ```bash
  localtranscribe --help
  localtranscribe process --help
  localtranscribe doctor --help
  localtranscribe config-show --help
  ```
  - [ ] Should show clear, formatted help text
  - [ ] Should list all options
  - [ ] Should include examples

### Version Command
- [ ] **Test version command**
  ```bash
  localtranscribe version
  ```
  - [ ] Should show version number (2.0.0)
  - [ ] Should show Python version
  - [ ] Should show platform information

## 10. Edge Cases

### Empty Audio
- [ ] **Test with silent audio** (if available)
  - [ ] Should handle gracefully
  - [ ] Should show appropriate message

### Very Long Audio
- [ ] **Test with long audio** (> 1 hour, if available)
  - [ ] Should process completely
  - [ ] Should show progress
  - [ ] Should handle memory efficiently

### Corrupted Audio
- [ ] **Test with corrupted file** (if available)
  - [ ] Should show helpful error
  - [ ] Should NOT crash

## Testing Summary

After completing all tests:

```bash
# Generate test report
echo "LocalTranscribe v2.0 Testing Report" > test_report.txt
echo "=====================================" >> test_report.txt
echo "" >> test_report.txt
echo "Date: $(date)" >> test_report.txt
echo "System: $(uname -a)" >> test_report.txt
echo "Python: $(python3 --version)" >> test_report.txt
echo "" >> test_report.txt
echo "Tests Completed: [X/Total]" >> test_report.txt
echo "Tests Passed: [X]" >> test_report.txt
echo "Tests Failed: [X]" >> test_report.txt
echo "" >> test_report.txt
echo "Issues Found:" >> test_report.txt
echo "1. ..." >> test_report.txt
```

## Success Criteria

Phase 1 is considered successful if:

- ✅ All health checks pass
- ✅ Basic processing completes without errors
- ✅ All output files are generated correctly
- ✅ Configuration system works (file + env + CLI)
- ✅ Error messages are helpful and clear
- ✅ Path resolution works from any location
- ✅ CLI help is clear and comprehensive
- ✅ Performance is acceptable (no major regressions)

## Known Issues to Document

List any issues found during testing:

1.
2.
3.

## Next Steps

After testing:

1. **Document Issues**: Create GitHub issues for any bugs found
2. **Performance Baseline**: Record performance metrics for future comparison
3. **User Testing**: Have external users test the installation and basic workflow
4. **Phase 2 Planning**: Use testing insights to plan Phase 2 features

---

**Note**: Save this file and check off items as you complete them. This will serve as documentation of your testing coverage.
