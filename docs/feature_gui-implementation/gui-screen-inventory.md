# LocalTranscribe GUI Screen Inventory & UI/UX Specifications for SuperDesign Implementation

## Product Overview
LocalTranscribe is a privacy-first desktop application for audio transcription with speaker diarization, entirely offline and running locally on user machines. The GUI transforms the existing CLI functionality into an intuitive, modern desktop application with comprehensive workflow management and real-time progress tracking. The application supports advanced features including quality gates, proofreading, batch processing, and context-aware NLP processing.

**Implementation Stack**: SvelteKit + Tauri + Tailwind CSS + shadcn-svelte components
**Design Framework**: Flowbite components with custom styling
**Styling Approach**: Tailwind CSS with custom CSS variables for theme consistency
**Responsive Design**: Mobile-first approach with desktop optimization

---

## Core Application Screens for SuperDesign Implementation

### 1. Main Dashboard / Welcome Screen
**Purpose**: Primary landing screen for new and returning users with comprehensive workflow initiation
**Implementation Requirements**:
- Use Flowbite card components for feature highlights with custom styling
- Implement responsive grid layout using Tailwind with mobile-first approach
- Create prominent CTA button with Flowbite styling and hover effects
- Add file drag-and-drop zone with animated visual feedback
- Include recent files list with Flowbite list components and status indicators
- Add system health status indicator with click-to-expand details
- Implement privacy assurance badges and security indicators
- Include version information and update notifier

**UI Components Needed**:
- Hero card with application branding and value proposition
- Primary action button (File selection) with prominent styling
- Feature cards grid (3-4 cards in 2x2 grid on desktop)
- Recent files list with Flowbite list and status badges
- System status indicator with health check results
- Header with navigation controls and settings access
- Privacy/security assurance badges
- Version information and update status
- Quick access buttons for common workflows

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│  🎙️ LocalTranscribe                   🔔 ⚙️ 🔍 [Recent]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                 🎯 Privacy-First Audio Transcription            │
│                    All processing on your machine               │
│              🔒 100% Offline • 🔐 No Cloud Uploads            │
│                                                                 │
│        ┌─────────────────────────────────────────────────────┐  │
│        │              📁 Select Audio File                   │  │
│        │        ┌─────────────────────────────────────────┐  │  │
│        │        │        [  📁 SELECT FILE  ]             │  │  │
│        │        └─────────────────────────────────────────┘  │  │
│        │    Supports MP3, WAV, M4A, FLAC, MP4, MOV, MKV, AVI│  │
│        │             Drag & drop anywhere                    │  │
│        └─────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🏷️ Key Features                                            ││
│  │ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐││
│  │ │     🔒           │ │      🎯          │ │     📊         │││
│  │ │  Privacy First   │ │  Speaker         │ │   Batch        │││
│  │ │  100% Local     │ │  Detection       │ │   Processing   │││
│  │ │  No Cloud Upload│ │  Auto-ID        │ │   Multi-file   │││
│  │ └──────────────────┘ └──────────────────┘ └────────────────┘││
│  │ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐││
│  │ │     🎨           │ │      🧪          │ │     📝         │││
│  │ │  Quality         │ │  Advanced       │ │   Export       │││
│  │ │  Gates          │ │  Proofreading    │ │   Formats      │││
│  │ │  Auto-Assess    │ │  AI-Enhanced    │ │   Multi-Format │││
│  │ └──────────────────┘ └──────────────────┘ └────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📄 Recent Files & Status                                   ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎤 interview_123.mp3 • 2 days ago • ✅ Complete      │ ││
│  │ │ 📹 meeting_notes.wav • 1 week ago • ✅ Complete       │ ││
│  │ │ 🗣️  lecture_456.m4a • 3 days ago • 🔄 Processing    │ ││
│  │ │ 🎯 podcast_789.mov • 5 hours ago • ❌ Failed         │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ 📊 Stats: 4 files • 2 completed • 1 processing • 1 failed │ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🏥 System Status: 🔵 Healthy • 🧠 GPU Ready • 📁 85% Free ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [Quick Start] [Advanced] [Settings] [Help]                     │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Primary color: Custom OKLCH theme (avoid indigo/blue)
- Typography: Inter font family with appropriate heading hierarchy
- Spacing: Tailwind spacing classes (p-4, m-6, gap-6, consistent padding)
- Responsive: Single column on mobile, 2-column on tablet, 3-column on desktop
- Theme: Dark/light mode support with system auto-detection
- Accessibility: Proper ARIA labels, keyboard navigation, screen reader support
- Animations: Subtle hover effects, entrance animations for cards
- Security indicators: Prominent privacy badges and offline processing badges
- File drag-and-drop: Visual feedback with border highlights and animations
- Status indicators: Color-coded badges with hover details

---

### 2. Interactive File Browser / File Explorer
**Purpose**: Advanced file selection with arrow-key navigation, audio analysis, and batch processing capabilities
**Implementation Requirements**:
- Use Flowbite file upload component with custom styling and progress indicators
- Implement dual view modes (grid/list) with toggle functionality
- Add comprehensive search and filter functionality with multiple criteria
- Create file preview cards with detailed audio metadata and thumbnails
- Include multi-select with Flowbite checkboxes and keyboard shortcuts
- Add folder navigation with breadcrumb trail and quick access
- Implement audio file preview with waveform visualization
- Add file validation and compatibility checking
- Include batch selection tools and smart grouping
- Add file tagging and rating capabilities for future use

**UI Components Needed**:
- File upload area with drag-and-drop zone and visual feedback
- File browser table/list with Flowbite styling and view toggles
- Search and filter controls with advanced options (duration, quality, size)
- File preview cards with detailed audio metadata and thumbnail previews
- Selection controls and bulk action buttons
- Folder navigation breadcrumb with quick folder access
- Audio preview player with waveform visualization
- File validation indicators and compatibility warnings
- Batch selection tools with smart grouping
- File tagging and rating system
- File size and quality indicators
- Quick actions toolbar

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📁 /Users/Audio Files | 🔍 [Search files...] | 📋 [Recent Folders]     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🎵 Audio Only │ 📹 Video │ 📁 Folders │ 📄 All │ [View: 📋 Grid]      │
│  📭 Recent │ 🔍 Name │ ⏱️ Duration │ 📊 Size │ 🎵 Quality │ ⬇️ Modified │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 📤 File Upload Zone - Drag & Drop Audio Files Here                 ││
│  │                                                                    ││
│  │  ┌──────────────────────────────────────────────────────────────┐ ││
│  │  │ 📁 [  SELECT FILES  ] └─ 📂 [  BROWSE FOLDER  ]            │ ││
│  │  └──────────────────────────────────────────────────────────────┘ ││
│  │  📁 .mp3 .wav .m4a .flac .aac .wma .opus │ 📹 .mp4 .mov .avi .mkv ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 🔍 Filter: [Duration: 0-60min ▼] [Size: All ▼] [Quality: All ▼]  ││
│  │ 🏷️ Tags: [Meeting] [Interview] [Lecture] [All]                    ││
│  │ 📊 [Min Quality: 70% ▼] [Format: All ▼] [Channels: All ▼]        ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ Grid View:                                                         ││
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   ││
│  │ │ 🎵 interview│ │ 🎵 meeting  │ │ 🎵 presen-  │ │ 🎵 lecture  │   ││
│  │ │  [🖼️ wave]  │ │  [🖼️ wave]  │ │  tation   │ │  [🖼️ wave]  │   ││
│  │ │  mp3        │ │  wav        │ │  m4a       │ │  mov        │   ││
│  │ │  🔘☐ 2:30   │ │  🔘☐ 6:12   │ │  🔘☐ 4:15   │ │  🔘☐ 15:30  │   ││
│  │ │  2.5MB      │ │  5.1MB      │ │  3.2MB      │ │  8.7MB      │   ││
│  │ │  🟢 Good Q  │ │  🟡 Avg Q   │ │  🟢 Good Q  │ │  🟢 Good Q  │   ││
│  │ │  [Play ▶️]  │ │  [Play ▶️]  │ │  [Play ▶️]  │ │  [Play ▶️]  │   ││
│  │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ Detail View:                                                        ││
│  │ ┌─┐ 🎵 interview.mp3 • 2:30 • 2.5MB • 🔘☐ • 🟢 Good Quality      ││
│  │ │☐│ Duration: 2:30 • Size: 2.5MB • Format: MP3 • Codec: AAC      │││
│  │ │  │ Sample Rate: 44.1kHz • Channels: 2 • Bitrate: 128kbps       │││
│  │ │  │ Quality Score: 8.2/10 • SNR: 25dB • Recommended: Medium     │││
│  │ │  │ [Tags: Meeting, Interview] • [Rate: ⭐⭐⭐⭐☆]                │││
│  │ │  │ [Play] [Preview] [Analyze] [Info ▼]                           │││
│  │ └─┘ ────────────────────────────────────────────────────────────── ││
│  │ ┌─┐ 🎵 meeting.wav • 6:12 • 5.1MB • 🔘☐ • 🟡 Average Quality    ││
│  │ │☐│ Duration: 4:45 • Size: 5.1MB • Format: WAV • Codec: PCM      │││
│  │ │  │ Sample Rate: 48kHz • Channels: 2 • Bitrate: Uncompressed     │││
│  │ │  │ Quality Score: 6.8/10 • SNR: 18dB • Recommended: Small      │││
│  │ │  │ [Tags: Meeting, Team] • [Rate: ⭐⭐⭐☆☆]                      │││
│  │ │  │ [Play] [Preview] [Analyze] [Info ▼]                           │││
│  │ └─┘ ────────────────────────────────────────────────────────────── ││
│  │ ... (more files)                                                    ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 📋 Selected: 2 of 45 files | 🏷️ [Add Tag] [Rate] [Batch Process] ││
│  │ 📊 Stats: 2.5MB-5.1MB, 2:30-6:12, Mixed Quality, 2 Files         ││
│  │ [➡️ PROCESS SELECTED (Batch)] [📋 COMPARE FILES] [❌ CANCEL]      ││
│  │ [📋 SELECT ALL] [📋 CLEAR] [🔍 FIND SIMILAR] [💾 SAVE SELECTION] ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  [Smart Select: Long Files] [Smart Select: High Quality] [Sort: Name] │
└─────────────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Dual view modes: Grid view for quick scanning, Detail view for metadata
- Card-based file display with hover states and selection indicators
- Selection states with Flowbite checkboxes and keyboard navigation support
- Responsive grid layout that adapts to screen size (1 column mobile, 2 tablet, 4 desktop)
- File type icons with color coding (audio: blue, video: purple, folders: gray)
- Quality indicators with color coding (green/excellent, yellow/good, red/poor)
- Audio preview with embedded player and waveform visualization
- Advanced filtering with multiple criteria and saved filter presets
- Bulk selection tools with shift-click and Ctrl-click functionality
- Drag-and-drop reordering for batch processing
- Keyboard shortcuts for power users (arrow keys, spacebar for select, etc.)
- File tagging system with searchable tags
- Smart selection features (select similar files, files with similar properties)
- File rating system with star ratings
- Recent files and folder breadcrumbs for quick navigation
- File validation indicators showing compatibility with current settings
- Preview thumbnails showing waveform or video frame
- Progress indicators for ongoing operations
- Contextual right-click menus for file actions

---

### 3. Audio Analysis & Quality Assessment Screen
**Purpose**: Comprehensive audio file analysis with detailed quality metrics, recommendations, and preprocessing insights for optimal transcription results
**Implementation Requirements**:
- Create interactive audio waveform visualization using HTML5 Canvas with zoom and pan capabilities
- Implement full-featured audio player controls with Flowbite styling and detailed playback information
- Display comprehensive technical metadata in structured, expandable cards with searchable details
- Show detailed quality score indicators with color coding and confidence levels
- Add advanced playback scrubbing with zoom functionality
- Include spectral analysis with frequency spectrum visualization
- Provide detailed audio quality metrics with SNR, THD, and dynamic range measurements
- Show preprocessing recommendations based on audio characteristics
- Include speaker activity visualization and estimated speaker count
- Provide detailed format compatibility checks and recommended processing parameters
- Add export quality report functionality
- Include comparison tools with other files
- Provide detailed file statistics (bitrate, compression, etc.)

**UI Components Needed**:
- Interactive audio player with waveform visualization (zoomable/pannable)
- Spectral analysis display with frequency spectrum visualization
- Metadata display cards with expandable sections
- Quality assessment indicators with detailed metrics
- Advanced audio preview controls (play/pause/scrub/volume/loop)
- Technical specifications panel with detailed codec info
- Quality recommendations panel with actionable suggestions
- Speaker activity timeline visualization
- Audio quality metrics panel with confidence indicators
- Preprocessing recommendations with parameter suggestions
- Format compatibility checker with detailed reports
- File statistics panel with detailed bitrates and compression info
- Comparison tools for multiple files
- Export quality report functionality
- Advanced analysis controls (zoom, filters, EQ preview)

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│                    📊 Audio Analysis Dashboard                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 🎵 Full-Featured Player & Waveform                                  ││
│  │ ┌─────────────────────────────────────────────────────────────────┐ ││
│  │ │ ▁▂▃▄▅▆▇███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ││
│  │ │ ▁▂▃▄▅▆▇███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████████████████████████░░░░░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████████████████████████████░░░░░░░░░░░░░░░░ │ ││
│  │ │ ▁▂▃▄▅▆▇███████████████████████████████████████████░░░░░░░░ │ ││
│  │ └─────────────────────────────────────────────────────────────────┘ ││
│  │ ⏱️ 0:00                                         ⏱️ 2:30  [🔍 Zoom] ││
│  │                                                                     ││
│  │ [▶️ PLAY] [⏸️ PAUSE] [⏮️ PREV] [⏭️ NEXT] [🔁 LOOP] [🔈 VOL: 85%] ││
│  │ [⏱️ SPEED: 1.0x ▼] [EQ: OFF ▼] [FILTER: OFF ▼] [EXPORT PCM]     ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 🎵 Spectral Analysis & Frequency Spectrum                          ││
│  │ ┌─────────────────────────────────────────────────────────────────┐ ││
│  │ │ [Spectrogram Visualization: Low/Mid/High Freq Distribution]   │ ││
│  │ │ [Frequency Response Chart: 20Hz-20kHz]                        │ ││
│  │ │ [Dynamic Range: -12dBFS] • [THD: 0.1%] • [SNR: 25dB]        │ ││
│  │ │ [Peak Levels: L:-3.2dB, R:-2.8dB] • [RMS: -18.5dBFS]         │ ││
│  │ └─────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 📋 Detailed File Metadata & Properties                            ││
│  │ ┌─────────────────────────────────────────────────────────────────┐ ││
│  │ │ 📄 General:                                                     │ ││
│  │ │ • Name: interview_long.wav • Size: 2.54GB • Duration: 2:30:15 │ ││
│  │ │ • Created: 2024-01-15 14:32 • Modified: 2024-01-15 15:45      │ ││
│  │ │ • Access: 2024-01-15 16:20 • Location: /Users/audio/          │ ││
│  │ │                                                              │ ││
│  │ │ 🎵 Audio Properties:                                          │ ││
│  │ │ • Format: WAV (.wav) • Codec: PCM_S16LE • Bit Depth: 16-bit │ ││
│  │ │ • Channels: 2 (Stereo) • Sample Rate: 44.1kHz • Bitrate: 1411kbps│ ││
│  │ │ • Block Align: 4 • Frame Size: 4 • Endianness: Little-endian│ ││
│  │ │                                                              │ ││
│  │ │ 🔧 Technical Details:                                         │ ││
│  │ │ • Compression: None • Quality: Lossless • Encoding: Linear PCM │ ││
│  │ │ • Interleaving: Interleaved • Channel Layout: Stereo (L,R)  │ ││
│  │ │ • Bits per Sample: 16 • Samples per Frame: 2               │ ││
│  │ └─────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 🎯 Comprehensive Quality Assessment                               ││
│  │ ┌─────────────────────────────────────────────────────────────────┐ ││
│  │ │ 📊 Overall Score: 🟢 8.2/10.0 • Excellent Quality           │ ││
│  │ │ 🧪 SNR: 25.4dB • Recommended Model: 🎙️ Medium              │ ││
│  │ │ 📈 Dynamic Range: 68dB • THD: 0.1% • Peak Level: -2.8dBFS   │ ││
│  │ │ ✅ Status: No critical issues detected • Quality: Optimal    │ ││
│  │ │ 💡 Suggestion: Perfect for transcription with medium model   │ ││
│  │ └─────────────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────────────┐ ││
│  │ │ 📊 Detailed Metrics:                                          │ ││
│  │ │ • Volume Level: 🟢 Good (-18.5dBFS RMS) • Peak: -2.8dBFS   │ ││
│  │ │ • Noise Floor: 🟢 Low (-40.2dBFS) • SNR Margin: 15.1dB     │ ││
│  │ │ • Clipping: 🟢 None Detected • Distortion: 🟢 Minimal      │ ││
│  │ │ • Sampling: 🟢 Accurate • Compression: 🟢 Lossless         │ ││
│  │ │ • Frequency: 🟢 Flat Response • Channels: 🟢 Balanced      │ ││
│  │ └─────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 👥 Speaker Activity & Detection Preview                           ││
│  │ ┌─────────────────────────────────────────────────────────────────┐ ││
│  │ │ Estimated Speakers: 🎤 2-3 • Dominant: 65%-35% Split         │ ││
│  │ │ Speaker Timeline: [███░░░░░░░░░░░░░░░░░░░░░░░ 65%]           │ ││
│  │ │ [░░░░░░░░░░░░░░░███████░░░░░░░░░░░░░░░░░░░░ 35%]           │ ││
│  │ │ [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%]           │ ││
│  │ │ Activity Confidence: 92% • Overlap: 8% • Switch Rate: 4/min │ ││
│  │ └─────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 🛠️ Preprocessing Recommendations                                 ││
│  │ ┌─────────────────────────────────────────────────────────────────┐ ││
│  │ │ 🎙️ Recommended Settings:                                      │ ││
│  │ │ • Model: Medium (optimal for 2:30 duration & 8.2 quality)    │ ││
│  │ │ • Speakers: Auto-detect (likely 2-3 speakers present)         │ ││
│  │ │ • Quality Gates: ON (recommended for this quality level)      │ ││
│  │ │ • Proofreading: Standard (handles minor imperfections)        │ ││
│  │ │ • Advanced: Enable segment post-processing                    │ ││
│  │ │                                                              │ ││
│  │ │ ⚙️ Optimization Suggestions:                                  │ ││
│  │ │ • Normalization: Not needed (good volume levels)             │ ││
│  │ │ • Denoising: Not needed (low noise floor)                   │ ││
│  │ │ • Equalization: Not needed (flat frequency response)        │ ││
│  │ │ • Trimming: Optional (has 15s of silence at start/end)      │ ││
│  │ └─────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  [🔙 Back] [➡️ Continue to Processing] [📋 Full Report] [💾 Export]    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Interactive waveform visualization with zoom/pan capabilities using Canvas/WebGL
- Color-coded quality indicators with detailed confidence levels (green/excellent, yellow/good, red/poor)
- Responsive layout with stacked panels on mobile, side-by-side on desktop
- Audio controls with detailed playback information including time, speed, and volume
- Expandable/collapsible sections for detailed metadata and analysis
- Spectral analysis visualization using Web Audio API
- Speaker activity timeline with color-coded identification
- Detailed technical specifications with searchable/metric-specific views
- Preprocessing recommendations with confidence indicators
- Export functionality for quality reports and analysis data
- Advanced comparison tools for multiple audio files
- Keyboard shortcuts for playback and navigation
- Multiple visualization modes (waveform, spectrogram, frequency response)
- Real-time analysis during playback
- Customizable visualization settings (zoom levels, color schemes)
- Detailed error/warning highlighting for quality issues
- Contextual help tooltips for technical terms
- Export options for analysis data (CSV, JSON, reports)
- Integration with next processing steps
- Performance optimization for large audio files
- Memory-efficient rendering for long audio files
- Accessibility features for audio analysis visualization

---

### 4. Advanced Processing Configuration Screen
**Purpose**: Comprehensive processing options and model configuration
**Implementation Requirements**:
- Create collapsible sections for advanced options
- Implement form controls with Flowbite styling
- Add model selection dropdowns with descriptions
- Create toggle switches for boolean options
- Add input validation and real-time feedback
- Include HuggingFace token input with validation

**UI Components Needed**:
- Form sections with collapsible panels
- Model selection dropdowns
- Toggle switches for boolean options
- Slider controls for numerical values
- Input validation feedback
- Token input with secure display
- Preset configuration templates

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                     ⚙️ Processing Configuration                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🎛️ Basic Settings                                          ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🤖 Model: [.medium ▼.] ┌─────────────────────────────┐ │ ││
│  │ │ 🌐 Language: [.Auto Detect ▼.] │ Quality: 8.2/10 🟢 │ │ ││
│  │ │ 👥 Speakers: [.Auto ▼.] └─────────────────────────────┘ │ ││
│  │ │ 🎯 Implementation: [.Auto ▼.]                            │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ ▷ 🎚️ Advanced Features (Click to expand)                 ││
│  │ │ ┌─────────────────────────────────────────────────────┐ │ ││
│  │ │ │ 🔊 Segment Processing                             │ │ ││
│  │ │ │    • Min Duration: [0.5s ▼.]                      │ │ ││
│  │ │ │    • Merge Gap: [0.3s ▼.]                         │ │ ││
│  │ │ │    • Smoothing: [ON ▼.]                           │ │ ││
│  │ │ └─────────────────────────────────────────────────────┘ │ ││
│  │ │ ┌─────────────────────────────────────────────────────┐ │ ││
│  │ │ │ 👥 Speaker Mapping                                │ │ ││
│  │ │ │    • Regions: [ON ▼.]                             │ │ ││
│  │ │ │    • Temporal Weight: [0.3 ▼.]                    │ │ ││
│  │ │ │    • Duration Weight: [0.4 ▼.]                    │ │ ││
│  │ │ └─────────────────────────────────────────────────────┘ │ ││
│  │ │ ┌─────────────────────────────────────────────────────┐ │ ││
│  │ │ │ 🎯 Quality Gates                                  │ │ ││
│  │ │ │    • Enable: [ON ▼.]                              │ │ ││
│  │ │ │    • Audio Analysis: [ON ▼.]                      │ │ ││
│  │ │ └─────────────────────────────────────────────────────┘ │ ││
│  │ │ ┌─────────────────────────────────────────────────────┐ │ ││
│  │ │ │ ✏️ Proofreading                                   │ │ ││
│  │ │ │    • Enable: [OFF ▼.]                             │ │ ││
│  │ │ │    • Level: [Standard ▼.]                         │ │ ││
│  │ │ │    • Acronyms: [OFF ▼.]                           │ │ ││
│  │ │ └─────────────────────────────────────────────────────┘ │ ││
│  │ │ ┌─────────────────────────────────────────────────────┐ │ ││
│  │ │ │ 📤 Output Settings                                │ │ ││
│  │ │ │    • Formats: [txt, json, md ▼.]                  │ │ ││
│  │ │ │    • Confidence: [OFF ▼.]                         │ │ ││
│  │ │ │    • Backup: [ON ▼.]                              │ │ ││
│  │ │ └─────────────────────────────────────────────────────┘ │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🔐 HuggingFace Token                                      ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ [••••••••••••••••••••••••••••••••••••] [Validate]     │ ││
│  │ │ Status: 🔴 Token Required • Accept license to continue │ ││
│  │ │ 📝 Get token: https://huggingface.co/settings/tokens    │ ││
│  │ │ 🤖 Model: https://huggingface.co/pyannote/speaker-di...│ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [❌ Cancel]                                        [🚀 Start]  │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Sectioned layout with clear visual hierarchy
- Collapsible advanced sections
- Form validation with real-time feedback
- Preset templates for common configurations
- Responsive form layout

---

### 5. Real-time Processing Progress Screen
**Purpose**: Real-time monitoring of transcription pipeline with detailed metrics
**Implementation Requirements**:
- Create multi-stage progress visualization
- Implement real-time progress bars with updates
- Show detailed metrics with charts/graphs
- Add cancellation confirmation modal
- Display pipeline stage status indicators
- Create resource utilization charts

**UI Components Needed**:
- Multi-stage progress visualization
- Real-time progress bars
- Status indicators for each stage
- Resource utilization charts
- Cancellation confirmation modal
- Detailed metrics display
- Time estimation calculator

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    🔄 Processing Progress                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📊 Overall Progress                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎯 [██████████████████████░░░░░░░░░░░░░░░] 65%        │ ││
│  │ │                                                         │ ││
│  │ │ 🎤 Stage: Transcription 📝 • ETA: ⏳ 4:32 remaining    │ ││
│  │ │ 📈 Processed: 1:35/2:30 • Speed: 2.1x • 15:23 elapsed│ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🛠️ Pipeline Stages                                        ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📋 1. Validation      🟢 [Complete] ✓ 0:05            │ ││
│  │ │ 👥 2. Diarization     🟢 [Complete] ✓ 2:15            │ ││
│  │ │ 🎙️ 3. Transcription   🟡 [Running] ▶ 1:35/2:30       │ ││
│  │ │ 🔄 4. Combination     🟠 [Pending] ⏸ ETA: 1:45        │ ││
│  │ │ 🎯 5. Quality Assess  🟠 [Pending] ⏸ ETA: 0:12        │ ││
│  │ │ 🏷️ 6. Speaker Label   🟠 [Pending] ⏸ ETA: 0:08        │ ││
│  │ │ ✏️ 7. Proofreading    🟠 [Pending] ⏸ ETA: 0:25        │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 💻 System Resources                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🧠 CPU: [███████████████████░░░░░░░░░░░░░░░░░░ 60%]    │ ││
│  │ │ 📟 GPU: [███████████████████████████░░░░░░░░░░░░ 80%]   │ ││
│  │ │ 💾 RAM: [███████████████░░░░░░░░░░░░░░░░░░░░░░ 30%]    │ ││
│  │ │ 🌱 MPS: [████████████████████████████████████ 95%]    │ ││
│  │ │ 🔋 Temp: [██████████████████████████████████░░ 82°C]  │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [❌ Cancel Processing]                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Animated progress bars with smooth updates
- Color-coded status indicators (green/running/yellow/pending/red/error)
- Resource utilization visualization
- Stage-by-stage progress tracking
- Responsive layout with stacked progress elements

---

### 6. Interactive Results Dashboard
**Purpose**: Display and manage transcribed results with speaker identification
**Implementation Requirements**:
- Create transcript display with syntax highlighting
- Implement interactive timeline visualization
- Add speaker identification with color coding
- Include search and navigation functionality
- Add export options with preview
- Create confidence score visualization

**UI Components Needed**:
- Transcript display with formatting
- Interactive timeline component
- Speaker color coding system
- Search and filter controls
- Export dropdown with format options
- Confidence visualization
- Segment editing tools

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    📑 Results Dashboard                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📊 Transcript Timeline                                      ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🕐 0:00 ┌─────────────────────────────────────────────┐ │ ││
│  │ │       │ 🎤 SPEAKER_00 ████░░░░░░░░░░░░░░░░░░░░░ 35% │ │ ││
│  │ │ 🕐 1:00 │ 🎤 SPEAKER_01 ░░░░░░░░░███████░░░░░░░░░ 25% │ │ ││
│  │ │       │ 🎤 SPEAKER_00 ░░░░░░░░░░░░░░░░░░░░█████ 20% │ │ ││
│  │ │ 🕐 2:00 │ 🎤 SPEAKER_02 ░░░░░░░░░░░░░░░░░░░░░░░░░ 15% │ │ ││
│  │ │ 🕐 2:30 └─────────────────────────────────────────────┘ │ ││
│  │ │                                                         │ ││
│  │ │ 🔴 🔵 🔵 🔴 🔴 🔵 🔴 🔴 🔵 🔴 🔵 🔴 🔵 🔴 🔴 🔴 🔴  │ ││
│  │ │ 1:00 1:05 1:12 1:18 1:25 1:30 1:35 1:42 1:50 1:55 │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📝 Transcript Content                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔴 SPEAKER_00 • 1:05-1:18 • 13s                        │ ││
│  │ │ "Hello everyone, I'm excited to be here today. We're   │ ││
│  │ │  discussing the latest developments in AI technology."  │ ││
│  │ │                                                         │ ││
│  │ │ 🔵 SPEAKER_01 • 1:20-1:35 • 15s                        │ ││
│  │ │ "Thank you for that introduction. I'd like to focus on │ ││
│  │ │  the practical applications we're seeing in the market."│ ││
│  │ │                                                         │ ││
│  │ │ 🟡 SPEAKER_02 • 1:38-1:45 • 7s                         │ ││
│  │ │ "That's a great point. What about the challenges in    │ ││
│  │ │  implementation and deployment?"                        │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🎯 Speaker Statistics                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔴 SPEAKER_00: 35% (42s) ──────────────────────────── │ ││
│  │ │ 🔵 SPEAKER_01: 25% (31s) ──────────────────────       │ ││
│  │ │ 🟡 SPEAKER_02: 15% (18s) ───────────                  │ ││
│  │ │ 🔵 SPEAKER_03: 10% (12s) ───────                      │ ││
│  │ │ Other: 15% (18s) ───────                              │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [🔍 Search] [📤 Export] [🏷️ Edit Labels] [📤 Share]        │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Color-coded speaker identification system
- Timeline with visual speaker activity
- Scrollable transcript with fixed timeline
- Responsive layout with collapsible sections
- Syntax highlighting for different speakers

---

### 7. Comprehensive Quality Assessment Dashboard
**Purpose**: Review detailed quality metrics, issues, and recommendations with reprocessing options
**Implementation Requirements**:
- Create comprehensive metrics dashboard
- Implement severity-based issue categorization
- Add recommendations with actionable steps
- Include reprocessing options with parameter adjustments
- Create quality score visualization
- Add export quality report functionality

**UI Components Needed**:
- Metrics dashboard with charts
- Severity-based issue lists
- Recommendation cards with actions
- Reprocessing parameter controls
- Quality score indicators
- Export report buttons
- Issue filtering controls

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                  🎯 Quality Assessment Report                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🏆 Overall Quality Score                                  ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │                                                        │ ││
│  │ │              🔢 8.2 / 10.0                           │ ││
│  │ │              🟢 PASSED ✓                               │ ││
│  │ │                                                        │ ││
│  │ │  🎤 Diarization: 8.5/10 │ 🎙️ Transcription: 7.2/10   │ ││
│  │ │  🔄 Combination: 9.1/10 │ 🎯 Overall: 8.2/10         │ ││
│  │ │                                                        │ ││
│  │ │  📊 Confidence: 87% │ 📈 Reliability: 92%            │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🚨 Issues by Severity                                     ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔴 Critical: 0 • No blocking issues detected         │ ││
│  │ │ 🟠 High: 2     • Moderate concerns found             │ ││
│  │ │ 🟡 Medium: 3   • Minor quality issues                │ ││
│  │ │ 🟢 Low: 5      • Minor suggestions only              │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📋 Issue Details:                                     │ ││
│  │ │ • High: Micro-segment ratio too high (18%)           │ ││
│  │ │ • High: Speaker switch rate elevated (12/min)        │ ││
│  │ │ • Med: Confidence score below threshold (0.68)       │ ││
│  │ │ • Med: No-speech probability concerns (0.28)         │ ││
│  │ │ • Med: Compression ratio high (2.8)                  │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 💡 Recommendations                                        ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎚️ Processing Improvements:                          │ ││
│  │ │    ✓ Enable segment smoothing (recommended)           │ ││
│  │ │    ✓ Increase merge gap threshold to 0.5s             │ ││
│  │ │    ✓ Use MEDIUM model for better accuracy             │ ││
│  │ │                                                         │ ││
│  │ │ 🔧 Quick Fixes:                                        │ ││
│  │ │    ✓ Apply post-processing filters                    │ ││
│  │ │    ✓ Adjust speaker mapping weights                   │ ││
│  │ │    ✓ Enable temporal consistency                      │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [🔄 Reprocess] [📤 Export Report] [✅ Accept Results]         │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Color-coded severity indicators (red/orange/yellow/green)
- Dashboard layout with metric cards
- Issue lists with actionable recommendations
- Responsive grid for metrics display
- Clear pass/fail visual indicators

---

### 8. Advanced Interactive Proofreading Screen
**Purpose**: Enhanced post-processing with domain-specific features and context-aware corrections
**Implementation Requirements**:
- Create side-by-side comparison view
- Implement domain dictionary selection
- Add acronym expansion controls
- Include NLP model selection interface
- Add manual editing with change tracking
- Create proofreading history/undo functionality

**UI Components Needed**:
- Side-by-side comparison layout
- Domain dictionary selection controls
- Acronym expansion toggle controls
- NLP model selection dropdown
- Manual edit controls
- Change tracking display
- History/undo functionality

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                   ✏️ Advanced Proofreading                     │
├─────────────────────────────────────────────────────────────────┤
│  📝 Original Text                          ✅ Corrected Text    │
│  ┌─────────────────────────────────────────┬───────────────────┐│
│  │ 🔴 Speaker 1:                         │ 🔴 Speaker 1:     ││
│  │ "Hello world, this is a test of the   │ "Hello world,    ││
│  │  API system. The technology is        │  this is a test   ││
│  │  quite advanced and works well."      │  of the API       ││
│  │                                        │  system. The      ││
│  │ 🔵 Speaker 2:                         │  technology is    ││
│  │ "Yes, it's impressive. The API        │  quite advanced   ││
│  │  integration is seamless."            │  and works well." ││
│  │                                        │                   ││
│  │ 🟡 Speaker 3:                         │ 🟡 Speaker 3:     ││
│  │ "What about the documentation?       │ "What about the   ││
│  │  It's not very clear."               │  documentation?   ││
│  │                                        │  It's not very    ││
│  │ 🔴 Speaker 1:                         │  clear."          ││
│  │ "We're updating it this week."       │                   ││
│  └─────────────────────────────────────────┴───────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🎛️ Proofreading Controls                                  ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🌐 Domain: [.Technical ▼.] ┌─────────────────────────┐ │ ││
│  │ │ 🔤 Acronyms: [.ON ▼.]      │ 🔄 Changes: 12        │ │ ││
│  │ │ ⚙️ Level: [.Standard ▼.]    │ 📊 Accuracy: +15%     │ │ ││
│  │ │ 🧠 NLP: [.en_core_web_sm ▼.]└─────────────────────────┘ │ ││
│  │ │                                                         │ ││
│  │ │ 📋 Applied Corrections:                                 │ ││
│  │ │ ✓ API → Application Programming Interface              │ ││
│  │ │ ✓ tech → technology • seamless → smooth               │ ││
│  │ │ ✓ doc → documentation • clear → comprehensive         │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🔍 Domain Dictionaries                                    ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 💻 Technical: API, SDK, HTTP, JSON, XML, SQL          │ ││
│  │ │ 💼 Business: CEO, CFO, B2B, SaaS, KPI, ROI            │ ││
│  │ │ 🏥 Medical: MRI, CT, ECG, ICU, ICU, ER                │ ││
│  │ │ 🎓 Academic: PhD, GPA, STEM, AI, ML, NLP              │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [✅ Apply Changes] [📤 Export] [↩️ Cancel] [📋 Show Diff]    │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Split-screen comparison with visual diff highlighting
- Domain selection with color coding
- Toggle controls for different features
- Responsive layout that stacks on mobile
- Visual indicators for changes made

---

### 9. Advanced Speaker Labeling Interface
**Purpose**: Interactive speaker identification, renaming, and management with bulk operations
**Implementation Requirements**:
- Create timeline visualization with speaker segments
- Implement drag-and-drop speaker assignment
- Add bulk operation controls
- Include speaker statistics display
- Create label import/export functionality
- Add speaker detection visualization

**UI Components Needed**:
- Timeline visualization component
- Speaker assignment controls
- Bulk operation buttons
- Speaker statistics table
- Label import/export controls
- Color selection for speakers

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    🏷️ Speaker Labeling                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📊 Speaker Timeline Visualization                         ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🕐 0:00 ┌─────────────────────────────────────────────┐ │ ││
│  │ │       │ 🎤 John Smith ████░░░░░░░░░░░░░░░░░░░░░ 35% │ │ ││
│  │ │ 🕐 1:00 │ 🎤 Jane Doe   ░░░░░░░░░███████░░░░░░░░░ 25% │ │ ││
│  │ │       │ 🎤 Bob Wilson  ░░░░░░░░░░░░░░░░░░░░█████ 20% │ │ ││
│  │ │ 🕐 2:00 │ 🎤 Unknown     ░░░░░░░░░░░░░░░░░░░░░░░░░ 15% │ │ ││
│  │ │ 🕐 2:30 └─────────────────────────────────────────────┘ │ ││
│  │ │                                                         │ ││
│  │ │ 🔴🔴🔴🔵🔵🔵🟡🟡🔴🔴🔴🔵🔵🔵🔴🔴🔴🔴🔴🔴🔴   │ ││
│  │ │ 0:00 0:15 0:30 0:45 1:00 1:15 1:30 1:45 2:00 2:15 │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 👥 Speaker Assignments                                    ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔴 SPEAKER_00 • 📊 35% (42s) • 🕐 0:05-1:18         │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 John Smith] [✏️ Edit] [🔄 Auto-detect]    │  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │ 🔵 SPEAKER_01 • 📊 25% (31s) • 🕐 1:20-2:05         │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 Jane Doe] [✏️ Edit] [🔄 Auto-detect]      │  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │ 🟡 SPEAKER_02 • 📊 20% (24s) • 🕐 2:10-2:22         │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 Bob Wilson] [✏️ Edit] [🔄 Auto-detect]    │  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │ ⚪ SPEAKER_03 • 📊 15% (18s) • 🕐 2:25-2:38         │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 Dr. Sarah Chen] [✏️ Edit] [🔄 Auto-detect]│  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │                                                         │ ││
│  │ │ [➕ Add New Speaker] [🔄 Auto-assign All] [📋 Import]  │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📊 Speaker Statistics                                     ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎤 John Smith: ████████████████████████████████ 35%   │ ││
│  │ │ 🎤 Jane Doe:   ████████████████████████ 25%           │ ││
│  │ │ 🎤 Bob Wilson: ████████████████████ 20%               │ ││
│  │ │ 🎤 Sarah Chen: ████████████████ 15%                   │ ││
│  │ │ 🎤 Others:     ████████████ 5%                        │ ││
│  │ │                                                         │ ││
│  │ │ 📈 Total: 100% (2:30 total) • 4 speakers detected     │ ││
│  │ │ 🔄 [Bulk Rename] [Import Labels] [Export Map]         │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [💾 Save Labels] [📤 Export Transcript] [📋 Import Labels]    │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Timeline visualization with color-coded speakers
- Speaker assignment with color coding
- Bulk operation controls with confirmation
- Responsive timeline that scales on mobile
- Color selection for speaker identification

---

### 10. Comprehensive Batch Processing Dashboard
**Purpose**: Manage multiple file processing operations with parallel execution and progress tracking
**Implementation Requirements**:
- Create file queue management table
- Implement multi-file progress tracking
- Add worker management controls
- Include file filtering and sorting options
- Create batch results summary
- Add error handling and retry mechanisms

**UI Components Needed**:
- File queue table with status indicators
- Multi-file progress bars
- Worker management controls
- Batch summary cards
- Filter and sort controls
- Retry/error resolution buttons

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                   📦 Batch Processing Dashboard                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [📁 Select Folder] [➕ Add Files] [▶️ Start Batch] [⏸️ Pause] │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📊 Batch Summary                                          ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📁 Files: 12 total │ 📝 Processed: 5 • Failed: 0      │ ││
│  │ │ 🏃 Workers: 2/4    │ ⏳ ETA: 15m • Speed: 2.1x        │ ││
│  │ │ 💾 Memory: 65%     │ 📈 Progress: 42% (5/12 done)     │ ││
│  │ │ 🕐 Started: 2:34 PM│ 📅 Completed: 3:12 PM (est)     │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎯 Batch Settings:                                    │ ││
│  │ │    🤖 Model: Medium • 🌐 Lang: Auto • 👥 Speakers: Auto│ ││
│  │ │    📤 Formats: txt, json, md • 🎯 Features: All On   │ ││
│  │ │    ⚙️ Workers: 2 • 📁 Output: /batch_output/         │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📋 Processing Queue                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎤 interview_01.mp3 • 2:30 • 2.5MB                    │ ││
│  │ │ [██████████████████████████████░░░░░░░░░░░ 75%] [✅]   │ ││
│  │ │ Status: Complete • Time: 4m 12s • Quality: 8.7/10    │ ││
│  │ │                                                         │ ││
│  │ │ 🎤 meeting_notes.wav • 4:15 • 5.1MB                   │ ││
│  │ │ [████████████████████████████████████████ 100%] [✅]  │ ││
│  │ │ Status: Done • Time: 8m 30s • Quality: 9.2/10       │ ││
│  │ │                                                         │ ││
│  │ │ 🎤 presentation.mov • 6:45 • 8.2MB                   │ ││
│  │ │ [███████████████████░░░░░░░░░░░░░░░░░░░░░ 30%] [🔄]  │ ││
│  │ │ Status: Processing • ETA: 9m 15s • Speed: 1.8x      │ ││
│  │ │                                                         │ ││
│  │ │ 🎤 lecture_recording.m4a • 3:20 • 3.7MB              │ ││
│  │ │ [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%] [⏳]   │ ││
│  │ │ Status: Waiting • Queue: #2 • Estimated: 22m         │ ││
│  │ │                                                         │ ││
│  │ │ 🎤 discussion_panel.mp3 • 5:10 • 4.3MB               │ ││
│  │ │ [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%] [⏳]   │ ││
│  │ │ Status: Pending • Queue: #3 • Estimated: 25m         │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📈 Performance Metrics                                    ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🧠 CPU: [███████████████████░░░░░░░░░░░░░░░ 60%]      │ ││
│  │ │ 💻 RAM: [███████████████░░░░░░░░░░░░░░░░░░░░ 35%]      │ ││
│  │ │ 📟 GPU: [███████████████████████████░░░░░░░░░ 75%]     │ ││
│  │ │ 🔋 Temp: [██████████████████████████████████ 85°C]    │ ││
│  │ │ 📊 Speed: ███████████████████████████████████ 2.1x   │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [⏸️ Pause All] [⏹️ Stop Batch] [⚙️ Settings] [📤 Export Results]│
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Status indicators with color coding
- Per-file progress tracking
- Worker count control with limits
- Responsive table layout
- Bulk operations with confirmation

---

### 11. Advanced Settings and Configuration Center
**Purpose**: Application-wide preferences, system management, and advanced features
**Implementation Requirements**:
- Create tabbed navigation for different settings
- Implement form controls for all settings
- Add model management interface
- Include system health monitoring
- Create configuration import/export
- Add theme and appearance controls

**UI Components Needed**:
- Tab navigation component
- Settings form sections
- Model management controls
- System health indicators
- Theme selection controls
- Import/export functionality

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                      ⚙️ Settings Center                        │
├─────────────────────────────────────────────────────────────────┤
│ 🏠 General │ 🤖 Models │ 🔐 Privacy │ 🎨 Theme │ 📊 Analytics │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🏠 General Settings                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📁 Output Directory: [/Users/output ▼.]                │ ││
│  │ │ 🌐 Language: [English ▼.]                              │ ││
│  │ │ 🎨 Theme: [System (Dark/Light) ▼.]                    │ ││
│  │ │ 🔔 Notifications: [🔔 Enabled ▼.]                      │ ││
│  │ │ 🔄 Auto Updates: [Weekly ▼.]                           │ ││
│  │ │ 💾 Auto Backups: [Enabled ▼.]                          │ ││
│  │ │ 🕐 Time Format: [12-hour ▼.]                           │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🤖 Model Management                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ Whisper Models:                                         │ ││
│  │ │ [ ] tiny (75MB)     [ ] base (150MB)   [ ] small (500MB) │ ││
│  │ │ [✅] medium (1.5GB)  [ ] large (3.0GB)  [ ] turbo (1.0GB)│ ││
│  │ │                                                         │ ││
│  │ │ 📥 Download Progress:                                   │ ││
│  │ │ Downloading large... [███████████████░░░░░░ 75%] 2.3GB │ ││
│  │ │                                                         │ ││
│  │ │ 🏷️ NLP Models:                                         │ ││
│  │ │ [✅] en_core_web_sm (15MB)  [ ] en_core_web_md (43MB)   │ ││
│  │ │ [ ] en_core_web_lg (741MB)  [ ] multi_model (2.1GB)     │ ││
│  │ │                                                         │ ││
│  │ │ [📥 Download More] [🗑️ Uninstall] [🔄 Refresh List]    │ ││
│  │ │ [📋 Model Info] [🔍 Check Updates]                     │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🔐 Privacy & Security                                     ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔒 Local Processing: [Enabled ▼.]                      │ ││
│  │ │ 📤 Data Sharing: [Disabled ▼.]                         │ ││
│  │ │ 🕵️ Analytics: [Opt-out ▼.]                            │ ││
│  │ │ 🗑️ Auto-delete: [30 days ▼.]                          │ ││
│  │ │ 🗝️ Token Storage: [Encrypted ▼.]                      │ ││
│  │ │ 🔐 Secure Mode: [Standard ▼.]                          │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🎨 Theme Customization                                    ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎨 Theme: [System (Auto-switch) ▼.]                   │ ││
│  │ │ 🎨 Accent Color: [🔵 Blue ▼.]                          │ ││
│  │ │ 🎨 Background: [Solid ▼.]                              │ ││
│  │ │ 🎨 Transparency: [Medium ▼.]                           │ ││
│  │ │ 📐 Radius: [Medium ▼.]                                 │ ││
│  │ │ 📐 Spacing: [Comfortable ▼.]                           │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [💾 Save Settings] [🔄 Reset to Default] [📋 Export Config]   │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Tabbed navigation for different categories
- Form sections with appropriate input types
- Modal dialogs for advanced settings
- Responsive layout with stacked sections
- Confirmation for destructive actions

---

### 12. System Health Check / Doctor Command Dashboard
**Purpose**: Comprehensive system diagnostics, dependency verification, and troubleshooting
**Implementation Requirements**:
- Create comprehensive diagnostic report
- Implement dependency status checking
- Add installation guidance with links
- Include troubleshooting steps
- Create health check scheduling
- Add auto-repair functionality

**UI Components Needed**:
- Health check results table
- Dependency status indicators
- Installation guidance cards
- Troubleshooting steps list
- Repair action buttons
- Health status dashboard

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    🏥 Health Check Report                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📊 Overall System Status                                  ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │                                                        │ ││
│  │ │              🟢 Excellent (10/10) ✓                   │ ││
│  │ │                                                        │ ││
│  │ │ 🏥 Health Score: ████████████████████████████████ 10/10│ ││
│  │ │ 📅 Last Check: Today at 2:34 PM • Next: In 7 days    │ ││
│  │ │ ⏱️ Duration: 12s • Version: v3.1.1                   │ ││
│  │ │ 🛠️ Platform: macOS 14.0 • Architecture: ARM64       │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔁 Auto-check: [Enabled ▼.] • Frequency: Weekly      │ ││
│  │ │ [🔄 Run Check Now] [⏰ Schedule] [📋 View Detailed]   │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🧪 Dependencies Status                                    ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🐍 Python: v3.11.0 [🟢 OK]                           │ ││
│  │ │ 🧠 PyTorch: v2.1.0 [🟢 OK] • MPS: Available          │ ││
│  │ │ 🤖 Pyannote: v2.1.2 [🟢 OK] • License: Accepted      │ ││
│  │ │ 🎵 FFmpeg: v6.1 [🟢 OK] • Codec: Enabled             │ ││
│  │ │ 🐙 HuggingFace: v0.18.0 [⚠️ Token Missing]           │ ││
│  │ │ 🌐 Pydub: v0.25.1 [🟢 OK] • Audio: Supported        │ ││
│  │ │ 📝 Rich: v13.7.0 [🟢 OK] • Terminal: Compatible     │ ││
│  │ │ 🖥️ Typer: v0.9.0 [🟢 OK] • CLI: Working             │ ││
│  │ │ 🏷️ TorchCodec: v0.1.0 [🟢 OK] • Optional: ✓         │ ││
│  │ │ 🔐 Python-dotenv: v1.0.0 [🟢 OK] • Env: Working     │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 💡 Recommendations & Actions                              ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🎯 Critical: 0 issues requiring immediate attention    │ ││
│  │ │ 🟠 High: 1 item needs configuration                    │ ││
│  │ │ 🟡 Medium: 3 optional improvements                     │ ││
│  │ │ 🟢 Low: 2 informational items                          │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔧 Required Action:                                   │ ││
│  │ │ [🔐 Add HuggingFace Token] • Required for diarization │ ││
│  │ │ 🤖 Accept license: https://huggingface.co/pyannote... │ ││
│  │ │                                                         │ ││
│  │ │ 📦 Optional Improvements:                              │ ││
│  │ │ [📥 Install spaCy models] • For proofreading          │ ││
│  │ │ [🔄 Update FFmpeg] • Latest features available        │ ││
│  │ │ [💾 Download Whisper models] • Faster processing      │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📋 Detailed Results                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📁 Config Path: ~/.localtranscribe/config.yaml         │ ││
│  │ │ 📁 Output Dir: ~/Documents/transcripts                 │ ││
│  │ │ 💾 Storage: 345GB free out of 512GB (67% used)        │ ││
│  │ │ 🧠 Memory: 16GB RAM • 4.2GB used (26%)               │ ││
│  │ │ 🏃 Processes: 12 active • 3 background                │ ││
│  │ │ 🔐 Permissions: All required permissions granted       │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [🔧 Install Missing] [📋 View Full Report] [🔄 Run Again]     │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Clear status indicators (green/yellow/red)
- Detailed dependency information
- Actionable recommendations
- Responsive layout with stacked sections
- Health score visualization

---

### 13. Guided Onboarding Wizard
**Purpose**: New user setup and guided first-time experience with smart defaults
**Implementation Requirements**:
- Create step-by-step wizard interface
- Implement progress indication
- Add smart defaults and suggestions
- Include skip/advanced options
- Add contextual help tooltips
- Create summary confirmation page

**UI Components Needed**:
- Step navigation with progress bar
- Wizard step content panels
- Help tooltips and contextual guidance
- Skip and advanced mode toggles
- Summary review section
- Confirmation controls

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    🧙‍♂️ Setup Wizard (Step 2/5)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [⏮️] ┌──┐ ┌●──┐ ┌────┐ ┌────┐ ┌────┐ [⏭️]                 │
│      │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │                      │
│      │File│ │Quality│ │Speakers│ │Review│ │Export│           │
│      └────┘ └─────┘ └────────┘ └────┘ └──────┘              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🎯 Quality vs Speed Preference                            ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🚀 Quick Mode                                         │ ││
│  │ │    • Model: Tiny (75MB)                              │ ││
│  │ │    • Process Time: ~5 min                            │ ││
│  │ │    • Accuracy: Good (75%)                            │ ││
│  │ │    • GPU Usage: Low • Memory: 2GB                    │ ││
│  │ │    • Best for: Short files, quick results            │ ││
│  │ │ [✅ Select]                                           │ ││
│  │ │                                                         │ ││
│  │ │ ⚖️  Balanced Mode                                     │ ││
│  │ │    • Model: Medium (1.5GB)                           │ ││
│  │ │    • Process Time: ~15 min                           │ ││
│  │ │    • Accuracy: Very Good (90%)                       │ ││
│  │ │    • GPU Usage: Medium • Memory: 4GB                 │ ││
│  │ │    • Best for: Most files, good quality              │ ││
│  │ │ [✅ Select]                                           │ ││
│  │ │                                                         │ ││
│  │ │ 🔍 Thorough Mode                                      │ ││
│  │ │    • Model: Large (3.0GB)                            │ ││
│  │ │    • Process Time: ~30 min                           │ ││
│  │ │    • Accuracy: Excellent (95%)                       │ ││
│  │ │    • GPU Usage: High • Memory: 8GB                   │ ││
│  │ │    • Best for: Professional results, accuracy        │ ││
│  │ │ [✅ Select]                                           │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🤖 Recommended: Balanced Mode                         │ ││
│  │ │    Based on your file size (2:30) and quality needs   │ ││
│  │ │    Estimated processing time: 12-18 minutes         │ ││
│  │ │    Confidence level: High for this choice            │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 💡 Tips & Information                                     ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📝 Large files take proportionally longer processing   │ ││
│  │ │ 🧠 GPU acceleration can improve speed by 2-5x         │ ││
│  │ │ 🔊 Quality of audio affects processing time          │ ││
│  │ │ 📊 You can change settings later in the configuration │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│                    [⏮️ Back] [⏭️ Next Step]                  │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Clear step progression with visual indicators
- Contextual explanations with time estimates
- Responsive step navigation
- Skip options for advanced users
- Confirmation step with summary

---

### 14. Advanced Export and Sharing Options
**Purpose**: Comprehensive output format management with advanced sharing capabilities
**Implementation Requirements**:
- Create multi-format export interface
- Implement format-specific options
- Add sharing functionality
- Include file naming conventions
- Provide export previews
- Add batch export templates

**UI Components Needed**:
- Format selection with preview
- Format-specific configuration
- File naming controls
- Sharing method selection
- Export preview pane
- Batch export controls

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    📤 Advanced Export Options                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📋 Format Selection                                       ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📄 [✅] TXT - Plain text, simple format               │ ││
│  │ │ 📊 [✅] JSON - Structured data, for developers        │ ││
│  │ │ 📝 [✅] MD - Markdown, formatted text                 │ ││
│  │ │ 🎞️ [❌] SRT - Subtitles, video synchronization       │ ││
│  │ │ 🎬 [❌] VTT - WebVTT, browser subtitles               │ ││
│  │ │ 📎 [❌] DOCX - Microsoft Word document                │ ││
│  │ │ 📊 [❌] CSV - Comma-separated values, for spreadsheets │ ││
│  │ │ 📈 [❌] XML - XML format, for data exchange           │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ ⚙️ Format-Specific Options:                           │ ││
│  │ │ 🕐 Include timestamps: [Yes ▼.]                       │ ││
│  │ │ 🎯 Include confidence scores: [No ▼.]                 │ ││
│  │ │ 👥 Speaker format: [Name ▼.] • Options: ID/Name/Both  │ ││
│  │ │ 🔤 Text formatting: [Basic ▼.] • Options: Basic/Rich │ ││
│  │ │ 📋 Include metadata: [Yes ▼.] • File info, settings   │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🏷️ File Naming & Organization                             ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📁 Output Directory: [/Users/output ▼.]               │ ││
│  │ │ 🏷️ File Template: [Original Name ▼.]                 │ ││
│  │ │    Options: Original Name, Timestamp, Custom Pattern  │ ││
│  │ │ 📝 Custom Pattern: [file_{{timestamp}}_{{speakers}}]  │ ││
│  │ │    Available: {{timestamp}}, {{speakers}}, {{duration}},│ ││
│  │ │             {{model}}, {{quality}}                    │ ││
│  │ │ 📋 Filename Preview: interview_20240115_2speakers.md │ ││
│  │ │ 💾 File Organization: [Single File ▼.]               │ ││
│  │ │    Options: Single File, Per Speaker, Per Segment    │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📤 Export Options                                         ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔄 Include backup: [✅ Enabled]                       │ ││
│  │ │ 🔐 Secure export: [❌ Disabled]                       │ ││
│  │ │ 📦 Compress output: [❌ Disabled] • ZIP format        │ ││
│  │ │ 🏷️ Add export notes: [✅ Enabled]                     │ ││
│  │ │ 📊 Generate report: [✅ Enabled] • Quality metrics    │ ││
│  │ │ 📅 Schedule export: [❌ Disabled] • Delayed processing│ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📊 Export Summary:                                    │ ││
│  │ │ • Formats: 3 selected (TXT, JSON, MD)                │ ││
│  │ │ • Files to create: 3                                 │ ││
│  │ │ • Estimated size: ~2.5MB                             │ ││
│  │ │ • Processing time: ~2-5 seconds                      │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [📤 Export Now] [👁️ Preview] [📋 Show Sample] [❌ Cancel]    │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Format selection with visual previews
- Configuration options that appear per format
- File naming with template system
- Preview functionality for export
- Responsive layout for options

---

### 15. Configuration Management Interface
**Purpose**: Advanced configuration file management and environment variable handling
**Implementation Requirements**:
- Create YAML configuration editor
- Implement configuration validation
- Add import/export functionality
- Include environment variable management
- Provide configuration templates
- Add validation error highlighting

**UI Components Needed**:
- YAML editor with syntax highlighting
- Configuration validation indicators
- Import/export controls
- Environment variable editor
- Template selection
- Validation error display

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                ⚙️ Configuration Management                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📝 Configuration Editor                                   ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ # 🎙️ LocalTranscribe Configuration                  │ ││
│  │ │ # Generated: 2024-01-15 14:32:45                     │ ││
│  │ │ # Version: 3.1.1                                      │ ││
│  │ │                                                       │ ││
│  │ │ model:                                                │ ││
│  │ │   size: "medium"           # Whisper model size       │ ││
│  │ │   implementation: "auto"   # auto, mlx, faster, orig  │ ││
│  │ │   language: null           # null for auto-detect     │ ││
│  │ │   quantize: false          # quantized models         │ ││
│  │ │                                                       │ ││
│  │ │ processing:                                           │ ││
│  │ │   batch_size: 16           # transcription batch size │ ││
│  │ │   num_workers: 2           # parallel processing      │ ││
│  │ │   cache_dir: "~/.cache"    # cache location           │ ││
│  │ │   verbose: false           # detailed logging         │ ││
│  │ │                                                       │ ││
│  │ │ output:                                               │ ││
│  │ │   formats: ["txt", "json"] # default export formats   │ ││
│  │ │   directory: "./output"    # output directory         │ ││
│  │ │   include_timestamps: true # add timestamps           │ ││
│  │ │   include_confidence: false # add confidence scores    │ ││
│  │ │                                                       │ ││
│  │ │ features:                                             │ ││
│  │ │   diarization: true        # speaker identification   │ ││
│  │ │   quality_gates: false     # automatic quality checks │ ││
│  │ │   proofreading: "minimal"  # minimal/standard/thorough│ ││
│  │ │   backup: true             # create backup files      │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔍 Syntax: YAML format • Comments supported           │ ││
│  │ │ 💾 Auto-save: [Enabled ▼.] • Interval: 30s           │ ││
│  │ │ 🚨 Validation: [Enabled ▼.] • On change/save          │ ││
│  │ │ [📋 Format Code] [🔍 Find/Replace] [📖 Documentation] │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🌍 Environment Variables                                  ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔐 LOCALTRANSCRIBE_HF_TOKEN = ••••••••••••••••••     │ ││
│  │ │ 🤖 LOCALTRANSCRIBE_MODEL_SIZE = "large"               │ ││
│  │ │ 📁 LOCALTRANSCRIBE_OUTPUT_DIR = "/custom_output"      │ ││
│  │ │ 🎯 LOCALTRANSCRIBE_NUM_WORKERS = "4"                  │ ││
│  │ │ 🧠 LOCALTRANSCRIBE_ENABLE_DIARIZATION = "true"        │ ││
│  │ │ 📊 LOCALTRANSCRIBE_INCLUDE_CONFIDENCE = "true"        │ ││
│  │ │ 🔔 LOCALTRANSCRIBE_VERBOSE = "false"                  │ ││
│  │ │ 🏷️ LOCALTRANSCRIBE_PROOFREADING_LEVEL = "standard"    │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📋 Active Variables:                                  │ ││
│  │ │ • Overrides: 4 of 8 variables active                  │ ││
│  │ │ • Precedence: Environment > Config file > Defaults    │ ││
│  │ │ • Source: Loaded from system environment             │ ││
│  │ │ [🔄 Reload] [📋 Show All] [📋 Clear All]             │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🧰 Configuration Tools                                    ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📋 Presets: [Default ▼.] • [Custom] [Production] [Dev] │ ││
│  │ │ 💾 [💾 Save Config] [📂 Load Config] [📋 Export]      │ ││
│  │ │ 🚀 [🔧 Validate] [🔄 Reset to Defaults] [📋 Compare]   │ ││
│  │ │ 📦 [📥 Import from File] [📤 Export to File]          │ ││
│  │ │ 🔍 [🔍 Configuration Info] [📖 Help Documentation]    │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ ⚠️ Current Status:                                    │ ││
│  │ │   Configuration is valid • No errors detected         │ ││
│  │ │   Environment variables loaded • 8 of 8 valid        │ ││
│  │ │   Active configuration: ~/.localtranscribe/config.yaml│ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [🔧 Validate] [💾 Save] [📋 Load Preset] [❓ Help]           │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- Code editor with syntax highlighting
- Visual validation status
- Split view for config and environment vars
- Template management system
- Error highlighting and validation

---

### 16. Label Management Interface
**Purpose**: Speaker label file creation, editing, and management
**Implementation Requirements**:
- Create JSON label editor
- Implement label validation
- Add import/export functionality
- Include speaker detection assistance
- Provide label template creation
- Add bulk label operations

**UI Components Needed**:
- JSON editor with structure visualization
- Label validation and error checking
- Import/export controls
- Speaker detection suggestions
- Template creation tools
- Bulk operation controls

**Layout Structure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                    🏷️ Label Management                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 📝 Speaker Labels Editor                                  ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ {                                                     │ ││
│  │ │   "SPEAKER_00": "John Smith",  // 👨 Main presenter   │ ││
│  │ │   "SPEAKER_01": "Jane Doe",    // 👩 Co-host         │ ││
│  │ │   "SPEAKER_02": "Unknown",     // ❓ Brief speaker    │ ││
│  │ │   "SPEAKER_03": "Bob Wilson",  // 🧔 Panelist        │ ││
│  │ │   "SPEAKER_04": "Sarah Chen"   // 👩 Questioner      │ ││
│  │ │ }                                                     │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📝 Manual Edit Mode:                                  │ ││
│  │ │ [📋 Name All] [🔄 Clear All] [📋 Import from CSV]    │ ││
│  │ │ [🔍 Auto-detect Faces] [📋 Export to JSON]          │ ││
│  │ │ [📋 Generate from Transcript] [📋 Template]          │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 👥 Detected Speakers Analysis                             ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 🔴 SPEAKER_00 • 45% (2:05) • 💬 127 segments       │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 John Smith] [🔄 Auto-name] [✏️ Edit]      │  │ ││
│  │ │    │ Duration: 2:05 • Frequency: 15-18kHz           │  │ ││
│  │ │    │ Speaking style: Confident • Voice: Moderate     │  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │ 🔵 SPEAKER_01 • 35% (1:38) • 💬 98 segments        │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 Jane Doe] [🔄 Auto-name] [✏️ Edit]        │  │ ││
│  │ │    │ Duration: 1:38 • Frequency: 12-16kHz           │  │ ││
│  │ │    │ Speaking style: Conversational • Voice: Clear   │  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │ 🟡 SPEAKER_02 • 20% (0:42) • 💬 34 segments        │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 Bob Wilson] [🔄 Auto-name] [✏️ Edit]      │  │ ││
│  │ │    │ Duration: 0:42 • Frequency: 18-22kHz           │  │ ││
│  │ │    │ Speaking style: Brief • Voice: Soft             │  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │ ⚪ SPEAKER_03 • 7% (0:15) • 💬 12 segments         │ ││
│  │ │    ┌─────────────────────────────────────────────────┐  │ ││
│  │ │    │ [📋 Dr. Sarah Chen] [🔄 Auto-name] [✏️ Edit]  │  │ ││
│  │ │    │ Duration: 0:15 • Frequency: 14-17kHz           │  │ ││
│  │ │    │ Speaking style: Professional • Voice: Crisp     │  │ ││
│  │ │    └─────────────────────────────────────────────────┘  │ ││
│  │ │                                                         │ ││
│  │ │ [🔄 Auto-assign Names] [📋 Bulk Assign] [🔍 Analyze] │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 🧰 Label Management Tools                                 ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📋 Label Templates:                                   │ ││
│  │ │ • [Default Template] • [Interview] • [Meeting]      │ ││
│  │ │ • [Panel Discussion] • [Lecture] • [Custom]         │ ││
│  │ │                                                         │ ││
│  │ │ 🔧 Bulk Operations:                                   │ ││
│  │ │ [📋 Import from File] [📤 Export to File]           │ ││
│  │ │ [🔄 Replace in Bulk] [📋 Copy from Other Transcript] │ ││
│  │ │ [🔍 Match by Voice] [📋 Auto-resolve Duplicates]    │ ││
│  │ │                                                         │ ││
│  │ │ 💾 File Management:                                   │ ││
│  │ │ [💾 Save Labels] [📂 Load Labels] [📋 Save Template] │ ││
│  │ │ [📋 Export CSV] [📋 Export JSON] [🔄 Validate]      │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  │ ┌─────────────────────────────────────────────────────────┐ ││
│  │ │ 📊 Current Status:                                    │ ││
│  │ │ • Labels: 5 total • Named: 4 • Unknown: 1           │ ││
│  │ │ • File: interview_labels.json • Modified: 2 min ago │ ││
│  │ │ • Active transcription: interview_123.mp3           │ ││
│  │ │ • Validation: [✅ All valid] • [📋 Show Issues]     │ ││
│  │ └─────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  [💾 Save Labels] [📂 Load] [🔍 Validate] [❓ Help]            │
└─────────────────────────────────────────────────────────────────┘
```

**Design Specifications**:
- JSON structure visualization
- Speaker percentage indicators
- Auto-assignment suggestions
- Validation feedback
- Responsive layout for complex data

---

## Design Implementation Guidelines for SuperDesign

### Styling Framework
1. **CSS Framework**: Use Tailwind CSS with Flowbite components
2. **Theme System**: Implement CSS custom properties (variables) for theming
3. **Component Library**: Utilize shadcn-svelte components where appropriate
4. **Font Stack**: Use Google Fonts (Inter, Poppins, or Roboto as primary)
5. **Color Palette**: Avoid indigo/blue colors, use custom theme with OKLCH colors
6. **Spacing System**: Use Tailwind's spacing scale (consistent padding/margin)

### Theme Specifications
- **Primary Color**: Custom OKLCH color (avoid indigo/blue)
- **Secondary Colors**: Complementary OKLCH colors
- **Background**: Light/dark mode support
- **Card Colors**: Subtle contrasts for depth
- **Accent Colors**: For interactive elements and alerts
- **Success/Warning/Error**: Distinct color coding

### Component Requirements
1. **Responsive**: Mobile-first design approach
2. **Accessible**: ARIA labels, keyboard navigation, screen reader support
3. **Performance**: Virtualized lists for large datasets
4. **Consistency**: Shared component library across all screens
5. **State Management**: Proper loading, error, and empty states
6. **User Feedback**: Progress indicators, success messages, error alerts

### Technical Integration Points for SuperDesign
1. **File Structure**: HTML files in `.superdesign/design_iterations/`
2. **CSS Integration**: Use theme CSS with `!important` for overrides
3. **Icons**: Lucide icons via CDN script
4. **Scripts**: Tailwind via CDN, Flowbite components
5. **Naming Convention**: `{screen_name}_{version}.html`
6. **Styling**: Use OKLCH color system with custom theme

### Design Workflow Requirements
1. **Layout Design**: ASCII wireframes for each screen
2. **Theme Design**: Generate theme using generateTheme tool
3. **Animation Design**: Define micro-interactions and transitions
4. **HTML Generation**: Single HTML file per screen with embedded CSS
5. **Confirmation Required**: Each step must be approved before proceeding