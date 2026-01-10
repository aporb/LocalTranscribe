# LocalTranscribe GUI - User Guide

**Version:** 3.1.2
**Date:** 2026-01-10
**License:** MIT

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [First-Time Setup](#first-time-setup)
4. [User Interface Overview](#user-interface-overview)
5. [Transcribing Audio](#transcribing-audio)
6. [Advanced Features](#advanced-features)
7. [Settings](#settings)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

LocalTranscribe is a **privacy-first desktop application** for converting audio files to text. Unlike cloud-based services, all processing happens locally on your machine—your audio never leaves your computer.

### Key Features

- ✅ **100% Private & Offline** - All processing on your local machine
- ✅ **AI-Powered** - Uses OpenAI's Whisper for accurate transcription
- ✅ **Speaker Identification** - Automatically detect and label different speakers
- ✅ **Smart Proofreading** - AI-powered error correction
- ✅ **Multiple Formats** - Export to TXT, JSON, SRT, VTT, Markdown, HTML, DOCX
- ✅ **Modern Interface** - Beautiful, intuitive UI with dark mode
- ✅ **Cross-Platform** - Works on Windows, macOS, and Linux

---

## Installation

### Download

Download the latest version for your platform:

- **Windows:** `LocalTranscribe_3.1.2_x64-setup.exe` or `.msi`
- **macOS:** `LocalTranscribe_3.1.2_universal.dmg`
- **Linux:** `LocalTranscribe_3.1.2_amd64.AppImage` or `.deb`

### Platform-Specific Installation

#### Windows

1. Download the `.exe` installer
2. Double-click to run
3. Windows may show a SmartScreen warning (this is a development build without code signing)
4. Click **"More info"** → **"Run anyway"**
5. Follow the installation wizard
6. Launch from Start Menu or Desktop shortcut

#### macOS

1. Download the `.dmg` file
2. Open the DMG and drag LocalTranscribe to Applications
3. First launch: Right-click the app → **"Open"** (to bypass Gatekeeper)
4. Click **"Open"** in the security dialog
5. Subsequent launches: Normal double-click

#### Linux (AppImage)

1. Download the `.AppImage` file
2. Make it executable:
   ```bash
   chmod +x LocalTranscribe_3.1.2_amd64.AppImage
   ```
3. Run it:
   ```bash
   ./LocalTranscribe_3.1.2_amd64.AppImage
   ```

#### Linux (Debian/Ubuntu)

1. Download the `.deb` file
2. Install:
   ```bash
   sudo dpkg -i local-transcribe_3.1.2_amd64.deb
   ```
3. Launch from Applications menu or run `localtranscribe`

### System Requirements

- **Operating System:**
  - Windows 10/11 (64-bit)
  - macOS 10.13+ (Intel or Apple Silicon)
  - Linux (Ubuntu 20.04+, Fedora 35+, or equivalent)

- **Hardware:**
  - **RAM:** 8GB minimum, 16GB recommended
  - **Storage:** 5GB free space (for models and output)
  - **CPU:** Modern multi-core processor
  - **GPU:** Optional (CUDA or Apple Silicon for faster processing)

---

## First-Time Setup

### 1. Launch the Application

On first launch, you'll see the home screen with a welcome message.

### 2. HuggingFace Token (For Diarization)

If you plan to use speaker diarization, you'll need a HuggingFace token:

1. Create a free account at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create a new token (read permission is sufficient)
4. Copy the token
5. In LocalTranscribe: Click **Settings** → paste token in **HuggingFace Token** field
6. Click **Save**

**Note:** This token is stored locally and never transmitted anywhere except to HuggingFace for model downloads.

### 3. Model Downloads

Models are automatically downloaded on first use:

- **Tiny:** ~75MB - Fast, lower accuracy
- **Base:** ~150MB - Fast, moderate accuracy
- **Small:** ~500MB - Balanced speed/accuracy
- **Medium:** ~1.5GB - High accuracy (default)
- **Large:** ~3GB - Highest accuracy

Models are cached in:
- **Windows:** `%APPDATA%\localtranscribe\models`
- **macOS:** `~/Library/Application Support/localtranscribe/models`
- **Linux:** `~/.local/share/localtranscribe/models`

---

## User Interface Overview

### Home Screen

The home screen shows:
- **Quick Start** button - Begin a new transcription
- **Recent Files** - Previously transcribed files
- **Dark Mode Toggle** - Top-right corner
- **Settings** - Configure preferences
- **About** - Version and information

### Navigation

LocalTranscribe uses a 5-step workflow:

1. **Select File** - Choose audio file
2. **Quality Check** - Analyze audio quality
3. **Configure** - Set transcription options
4. **Process** - Watch real-time progress
5. **Results** - View and export transcription

---

## Transcribing Audio

### Step 1: Select Audio File

Two ways to select a file:

**Option A: Drag and Drop**
1. Drag an audio file from your file manager
2. Drop it onto the drop zone

**Option B: Browse**
1. Click **"Browse Files"** button
2. Navigate to your audio file
3. Click **"Open"**

**Supported Formats:**
- MP3, WAV, M4A, FLAC, OGG, AAC, WMA, OPUS

**File Size:** Up to 5GB recommended

### Step 2: Quality Check

LocalTranscribe automatically analyzes your audio:

- **Excellent** (Green) - SNR ≥ 40 dB - Perfect for transcription
- **Good** (Blue) - SNR ≥ 25 dB - Great quality
- **Fair** (Yellow) - SNR ≥ 15 dB - Acceptable, may have minor errors
- **Poor** (Red) - SNR < 15 dB - Low quality, use larger model

**Recommendations:**
- The app suggests the optimal model based on quality
- Warnings show if preprocessing might help
- Click **"Continue"** to proceed or **"Back"** to select a different file

### Step 3: Configure Transcription

#### A. Whisper Model

Choose the model size:

| Model | Speed | Accuracy | RAM | Use Case |
|-------|-------|----------|-----|----------|
| Tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | ~1GB | Quick drafts |
| Base | ⚡⚡⚡⚡ | ⭐⭐⭐ | ~1.5GB | Casual use |
| Small | ⚡⚡⚡ | ⭐⭐⭐⭐ | ~2GB | Balanced |
| Medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~5GB | Professional (default) |
| Large | ⚡ | ⭐⭐⭐⭐⭐ | ~10GB | Maximum accuracy |

#### B. Quick Presets

Click a preset to auto-configure settings:

- **Podcast** - 1-3 speakers, proofreading ON
- **Meeting** - 3-8 speakers, diarization ON
- **Interview** - 2 speakers, proofreading ON
- **Lecture** - 1 speaker, fast mode
- **Dictation** - 1 speaker, proofreading ON
- **Fast** - Skip diarization, small model

#### C. Speaker Diarization

**Enable:**
- Leave unchecked to auto-detect speakers
- Or manually set number of speakers (1-10)

**Advanced:**
- **Min Speakers** - Minimum expected
- **Max Speakers** - Maximum expected
- **Skip Diarization** - Faster, no speaker labels

**Note:** Requires HuggingFace token (see Setup)

#### D. Processing Options

- **AI Proofreading** - Fix common transcription errors
  - Corrects grammar and punctuation
  - Expands acronyms
  - Fixes capitalization
  - Recommended: ON

- **Language** - Leave blank for auto-detection
  - Or enter code: `en` (English), `es` (Spanish), `fr` (French), etc.

#### E. Output Formats

Select one or more formats:

- **TXT** - Plain text (.txt)
- **JSON** - Structured data with timestamps (.json)
- **SRT** - Subtitle format for video (.srt)
- **VTT** - Web subtitle format (.vtt)
- **MD** - Markdown with formatting (.md)
- **HTML** - Styled web page (.html)
- **DOCX** - Microsoft Word document (.docx)

#### F. Output Directory

- Default: Same folder as audio file
- Click to change output location

#### G. Start Transcription

Click the large **"Start Transcription"** button when ready.

### Step 4: Processing

Watch real-time progress:

- **Circular Progress** - Overall completion (0-100%)
- **Stage Indicator** - Current processing step
  - Validation
  - Diarization (if enabled)
  - Transcription
  - Export
- **ETA** - Estimated time remaining
- **Cancel** - Stop processing (with confirmation)

**Tip:** You can minimize the window—processing continues in the background.

### Step 5: Results

When complete, you'll see:

- **Success Message** - Transcription completed
- **Statistics** - Segments, speakers, duration
- **Output Files** - List of generated files

**Actions per file:**
- **Open** - View in default app
- **Show in Folder** - Reveal in file manager

**Bottom Actions:**
- **New Transcription** - Start over
- **Back to Home** - Return to main screen
- **Open Folder** - View all output files

---

## Advanced Features

### Recent Files

The home screen shows up to 5 recent transcriptions:
- Click to view details
- Quick access to outputs

### Dark Mode

Toggle between light and dark themes:
- Click the sun/moon icon (top-right)
- Setting persists across sessions

### Settings Modal

Access via **Settings** button (gear icon):

**Appearance:**
- Dark Mode toggle

**Default Preferences:**
- Default Whisper model
- Enable proofreading by default

**Advanced:**
- Model storage location
- Cache management

### Keyboard Shortcuts

*Coming soon in future release*

---

## Settings

### General Settings

- **Default Model** - Model to select by default
- **Default Formats** - Auto-select these formats
- **Default Output Directory** - Where to save files
- **Proofreading** - Enable by default

### Privacy

LocalTranscribe is **100% private:**
- No telemetry or analytics
- No cloud uploads
- No account required
- All processing happens locally

**Data Storage:**
- Audio files: Never copied (only read)
- Models: Cached locally
- Output: Saved to your chosen directory
- Settings: Stored in app config folder

---

## Troubleshooting

### Installation Issues

**Windows: "Windows protected your PC"**
- This is expected for development builds without code signing
- Click "More info" → "Run anyway"
- Future releases will be signed

**macOS: "Cannot be opened because the developer cannot be verified"**
- Right-click the app → "Open"
- Click "Open" in dialog
- This only needs to be done once

**Linux: Permission denied**
- Make AppImage executable: `chmod +x LocalTranscribe*.AppImage`

### Model Download Failures

**Error: "Failed to download model"**
- Check internet connection
- Ensure enough disk space (up to 3GB for large model)
- Try again—downloads resume automatically
- Check firewall isn't blocking HuggingFace

**Slow Downloads:**
- Models are large (75MB - 3GB)
- First download of each model takes time
- Progress shown in terminal (if launched from CLI)

### Transcription Issues

**Error: "Out of memory"**
- Try a smaller model (e.g., small instead of large)
- Close other applications
- Upgrade RAM if possible

**Poor Accuracy:**
- Use a larger model (medium or large)
- Check audio quality (re-record if possible)
- Ensure correct language selected
- Enable proofreading

**Speaker Diarization Not Working:**
- Ensure HuggingFace token is set
- Check internet for first-time model download
- Try setting speaker count manually

**Processing Very Slow:**
- Expected for large files or large models
- GPU acceleration helps (CUDA or Apple Silicon)
- Try smaller model for faster results

### Audio File Issues

**"Unsupported file format"**
- Convert to supported format: MP3, WAV, M4A, FLAC, OGG, AAC, WMA
- Use FFmpeg or online converter

**"File too large"**
- Recommended max: 5GB
- Split large files into chunks
- Consider lower bitrate audio

---

## FAQ

### General Questions

**Q: Is my audio uploaded to the cloud?**
A: No! LocalTranscribe processes everything locally. Your audio never leaves your computer.

**Q: Do I need an internet connection?**
A: Only for first-time model downloads and speaker diarization setup. After that, fully offline.

**Q: What languages are supported?**
A: Whisper supports 99+ languages. Auto-detection works for most. Specify language code for best results.

**Q: Can I transcribe video files?**
A: Not directly. Extract audio first using FFmpeg or online tool, then transcribe the audio.

**Q: How accurate is the transcription?**
A: Whisper is state-of-the-art. Accuracy depends on:
- Audio quality (clear > noisy)
- Model size (large > tiny)
- Language (English best supported)
- Speaker clarity

**Q: Can I edit the transcription?**
A: Not within the app currently. Export to TXT/DOCX and edit in your preferred editor. In-app editing coming in future release.

### Technical Questions

**Q: Where are models stored?**
A:
- Windows: `%APPDATA%\localtranscribe\models`
- macOS: `~/Library/Application Support/localtranscribe/models`
- Linux: `~/.local/share/localtranscribe/models`

**Q: How much disk space do I need?**
A: Minimum 5GB:
- Whisper models: 75MB - 3GB (per model)
- Output files: Varies by length
- Temp files: ~2x audio file size

**Q: Can I use GPU acceleration?**
A: Yes! Auto-detected:
- **NVIDIA:** CUDA GPU (10x+ faster)
- **Apple:** M1/M2/M3 Neural Engine
- **AMD:** ROCm support (Linux)
- **CPU:** Falls back automatically

**Q: What's the difference between models?**
A:
- **Tiny/Base:** Fast, basic accuracy
- **Small:** Balanced (good default)
- **Medium:** High accuracy (recommended)
- **Large:** Best accuracy, slow, memory-intensive

**Q: Why is speaker diarization slow?**
A: It's a separate AI model analyzing voice patterns. Adds ~30% processing time but identifies "who said what."

**Q: Can I batch process multiple files?**
A: Not yet. Planned for future release.

### Privacy & Security

**Q: What data does LocalTranscribe collect?**
A: None. Zero telemetry, analytics, or tracking.

**Q: Is my HuggingFace token secure?**
A: Yes. Stored locally, encrypted, only sent to HuggingFace for model downloads.

**Q: Can I use this for sensitive audio?**
A: Absolutely. 100% offline processing. Perfect for medical, legal, confidential content.

**Q: Is LocalTranscribe open source?**
A: Yes! MIT License. Source code on GitHub.

---

## Getting Help

### Documentation

- **User Guide:** This file
- **Developer Guide:** `GUI_DEVELOPER_GUIDE.md`
- **Roadmap:** `GUI_PHASE3_AND_4_ROADMAP.md`

### Support

- **Issues:** Report bugs on GitHub Issues
- **Discussions:** Ask questions on GitHub Discussions
- **Email:** Contact maintainers (see repo)

### Links

- **GitHub:** https://github.com/aporb/LocalTranscribe
- **License:** MIT
- **Version:** 3.1.2

---

## Changelog

### Version 3.1.2 (2026-01-10)

**Phase 3: Frontend UI**
- Complete 5-screen user journey
- Drag-and-drop file selection
- Audio quality analysis
- Comprehensive configuration screen
- Real-time progress tracking
- Beautiful results display
- Settings and About modals
- Reusable component library
- Full dark mode support

**Phase 4: Build & Distribution**
- Tauri bundler configuration
- Build scripts for all platforms
- User guide and documentation
- Ready for release

### Previous Versions

- **3.1.1:** Phase 2 - Backend Integration
- **3.1.0:** Phase 1 - Foundation Setup
- **3.0.0:** CLI version

---

**Thank you for using LocalTranscribe!** 🎉

*Made with ❤️ for privacy*
