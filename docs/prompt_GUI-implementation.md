# LocalTranscribe GUI Implementation Prompt

## Project Overview
Transform the LocalTranscribe CLI application into a modern, feature-rich desktop GUI application using Tauri framework. The GUI should maintain all existing CLI functionality while providing an intuitive, visually appealing user experience with real-time progress monitoring, advanced configuration options, and comprehensive workflow management.

## Architecture Requirements

### Frontend Stack
- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS with shadcn-svelte components
- **State Management**: Svelte stores for reactive state management
- **Build Tool**: Vite for fast development and optimized builds

### Backend Stack
- **Framework**: Tauri v2.x with Rust
- **Runtime**: WRY webview runtime
- **Architecture**: Command-based IPC with proper error handling
- **State Management**: Tauri state management for shared data

### Project Structure
```
localtranscribe-gui/
├── src/
│   ├── lib/
│   │   ├── components/     # Reusable UI components
│   │   ├── stores/         # Svelte stores for state
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   ├── routes/            # SvelteKit routes
│   │   ├── +layout.svelte
│   │   ├── index.svelte   # Main dashboard
│   │   ├── process/+page.svelte
│   │   ├── settings/+page.svelte
│   │   └── results/+page.svelte
│   └── app.d.ts
├── src-tauri/
│   ├── src/
│   │   ├── lib.rs        # Plugin initialization
│   │   ├── main.rs       # App entry point
│   │   ├── commands/     # Tauri command handlers
│   │   ├── models/       # Data structures
│   │   └── services/     # Business logic
│   ├── Cargo.toml
│   └── tauri.conf.json
├── package.json
└── vite.config.js
```

## Core Features Implementation

### 1. Main Dashboard Window
**Rust Implementation:**
```rust
use tauri::{AppHandle, Manager, WindowBuilder, WebviewUrl, WebviewWindowBuilder};

#[tauri::command]
async fn create_main_window(app: AppHandle) -> Result<(), String> {
    let window = WebviewWindowBuilder::new(
        &app,
        "main",
        WebviewUrl::App("index.html".into())
    )
    .title("LocalTranscribe")
    .inner_size(1200.0, 800.0)
    .min_inner_size(800.0, 600.0)
    .resizable(true)
    .build()
    .map_err(|e| e.to_string())?;
    
    Ok(())
}
```

**Svelte Component:**
```svelte
<script>
  import { invoke } from '@tauri-apps/api/core';
  import { listen } from '@tauri-apps/api/event';
  import { onMount } from 'svelte';
  
  let isProcessing = $state(false);
  let progress = $state(0);
  let currentStage = $state('');
  
  onMount(async () => {
    // Listen for processing events
    const unlisten = await listen('processing-progress', (event) => {
      progress = event.payload.progress;
      currentStage = event.payload.stage;
    });
    
    return () => unlisten();
  });
  
  async function startProcessing() {
    isProcessing = true;
    await invoke('start_transcription', { filePath: selectedFile });
  }
</script>

<div class="flex flex-col h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-white shadow-sm border-b">
    <div class="px-6 py-4">
      <h1 class="text-2xl font-bold text-gray-900">LocalTranscribe</h1>
    </div>
  </header>
  
  <!-- Main Content -->
  <main class="flex-1 p-6">
    {#if isProcessing}
      <div class="max-w-2xl mx-auto">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-4">Processing Audio</h2>
          <div class="space-y-4">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style="width: {progress}%"
              ></div>
            </div>
            <p class="text-sm text-gray-600">Current stage: {currentStage}</p>
          </div>
        </div>
      </div>
    {:else}
      <!-- File selection and configuration -->
      <FileSelection />
      <ProcessingConfig />
    {/if}
  </main>
</div>
```

### 2. File Selection & Browser
**Rust Commands:**
```rust
use tauri::api::dialog::blocking::FileDialogBuilder;
use std::path::PathBuf;

#[tauri::command]
fn show_file_dialog() -> Result<Option<String>, String> {
    let file_path = FileDialogBuilder::new()
        .add_filter("Audio files", &["mp3", "wav", "m4a", "flac", "ogg", "mp4", "mov"])
        .pick_file();
    
    match file_path {
        Some(path) => Ok(Some(path.to_string_lossy().to_string())),
        None => Ok(None)
    }
}

#[tauri::command]
fn get_audio_info(path: String) -> Result<AudioInfo, String> {
    // Use existing LocalTranscribe audio analysis
    let analysis = run_audio_analysis(PathBuf::from(path))?;
    Ok(AudioInfo {
        duration: analysis.duration,
        format: analysis.format,
        quality_level: analysis.quality_level.as_str().to_string(),
        snr: analysis.snr_db,
    })
}
```

### 3. Processing Configuration Panel
**Rust State Management:**
```rust
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Clone, Serialize, Deserialize)]
struct ProcessingConfig {
    model_size: String,
    implementation: String,
    num_speakers: Option<u32>,
    min_speakers: Option<u32>,
    max_speakers: Option<u32>,
    enable_segment_processing: bool,
    min_segment_duration: f64,
    merge_gap_threshold: f64,
    enable_quality_gates: bool,
    enable_proofreading: bool,
    proofreading_level: String,
    domains: Vec<String>,
    enable_acronym_expansion: bool,
}

#[tauri::command]
fn save_config(config: ProcessingConfig, app: AppHandle) -> Result<(), String> {
    let state: tauri::State<Mutex<ProcessingConfig>> = app.state();
    let mut state_guard = state.lock().map_err(|e| e.to_string())?;
    *state_guard = config;
    Ok(())
}
```

### 4. Pipeline Execution & Progress Monitoring
**Rust Pipeline Integration:**
```rust
use tauri::{Emitter, EventTarget};

#[tauri::command]
async fn start_transcription(
    config: ProcessingConfig,
    file_path: String,
    app: AppHandle
) -> Result<ProcessResult, String> {
    let orchestrator = PipelineOrchestrator::new(
        PathBuf::from(file_path),
        PathBuf::from("./output"),
        config
    );
    
    // Spawn processing in background
    tauri::async_runtime::spawn(async move {
        let mut progress_receiver = orchestrator.run_with_progress();
        
        while let Some(progress) = progress_receiver.recv().await {
            let _ = app.emit_to(
                EventTarget::window("main"),
                "processing-progress",
                progress
            );
        }
    });
    
    Ok(ProcessResult { success: true })
}
```

### 5. Advanced Features Integration
**Quality Gates & Analysis:**
```rust
#[derive(Serialize, Deserialize)]
struct QualityReport {
    overall_score: f64,
    passed: bool,
    issues: Vec<QualityIssue>,
    metrics: QualityMetrics,
    recommendations: Vec<String>,
}

#[tauri::command]
fn get_quality_report(file_path: String) -> Result<QualityReport, String> {
    // Use existing QualityGate functionality
    let gate = QualityGate::new();
    let assessment = gate.assess_diarization_quality_from_file(file_path)?;
    Ok(QualityReport::from(assessment))
}
```

## Tauri Configuration
**tauri.conf.json:**
```json
{
  "build": {
    "beforeDevCommand": "pnpm dev",
    "beforeBuildCommand": "pnpm build",
    "devUrl": "http://localhost:1420",
    "distDir": "../dist"
  },
  "app": {
    "windows": [
      {
        "label": "main",
        "title": "LocalTranscribe",
        "width": 1200,
        "height": 800,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": "default-src 'self'; img-src 'self' asset: https://asset.localhost; media-src 'self' asset: https://asset.localhost; connect-src ipc: http://ipc.localhost"
    }
  },
  "plugins": {
    "fs": {
      "scope": ["$APPDATA/**", "$APPDATA/output/**"]
    }
  }
}
```

## Security & Permissions
- Implement Tauri's capability system for fine-grained permissions
- Secure file system access with scoped permissions
- Validate all user inputs and file paths
- Implement proper error handling and sanitization

## UI/UX Guidelines
- Follow modern desktop application patterns
- Implement responsive design for different screen sizes
- Use appropriate loading states and progress indicators
- Provide clear error messages and recovery options
- Implement keyboard shortcuts for power users
- Support dark/light mode preferences

## Development Workflow
1. Set up Tauri development environment
2. Create SvelteKit frontend with routing
3. Implement Tauri command handlers for all features
4. Build reusable UI components
5. Integrate existing LocalTranscribe functionality
6. Test cross-platform compatibility
7. Optimize performance and bundle size

This comprehensive prompt provides the foundation for building a modern, feature-complete LocalTranscribe GUI that maintains all existing functionality while providing an enhanced user experience.

---

## **Complete LocalTranscribe GUI Requirements for UI/UX Designer**

Based on my comprehensive analysis of the LocalTranscribe codebase, here are all the features, options, workflows, and user selections that need to be implemented in a modern GUI:

---

### **1. MAIN DASHBOARD / HOME SCREEN**

**Core Elements:**
- Welcome message with brief description
- File drop zone for audio files
- "Browse Files" button (interactive file browser functionality)
- Recent files list
- Quick start guide
- Status indicators for system readiness

---

### **2. FILE SELECTION & BROWSER SCREEN**

**Interactive File Browser Features:**
- Folder navigation with arrow keys simulation
- Visual file icons: 📁 folders, 🎵 audio files, 🎬 video files
- File size display for media files
- "Go up" navigation to parent directories
- Cancel option at any time
- Multi-select capability
- File type filtering (audio/video formats)
- Search functionality within file browser

---

### **3. AUDIO ANALYSIS SCREEN (v3.1.1)**

**Pre-processing Analysis:**
- Audio duration detection
- Quality level assessment (excellent, high, medium, low, poor)
- SNR (Signal-to-Noise Ratio) calculation
- Speech/silence ratio detection
- Spectral analysis (centroid, rolloff, bandwidth)
- Clipping detection and peak analysis
- Rough speaker count estimation
- Parameter recommendations display
- Audio waveform visualization

---

### **4. PROCESSING CONFIGURATION SCREEN**

**Model Selection:**
- Whisper model size selector: tiny, base, small, medium, large
- Implementation preference: MLX (Apple Silicon), Faster-Whisper, Original
- Quality vs Speed preference: Quick, Balanced, High Quality

**Speaker Configuration:**
- Number of speakers input (with auto-detect option)
- Min/Max speakers range sliders
- Skip diarization checkbox

**Language Settings:**
- Auto-detect language (default)
- Specific language selection dropdown
- Language confidence display

---

### **5. ADVANCED PROCESSING OPTIONS SCREEN**

**Phase 1: Segment Processing Controls:**
- Enable/disable segment post-processing (default: ON)
- Min segment duration slider (0.1s - 1.0s, default: 0.3s)
- Merge gap threshold slider (0.1s - 3.0s, default: 1.0s)
- Min speaker turn duration slider (0.5s - 5.0s, default: 2.0s)
- Temporal smoothing window slider (0.5s - 5.0s, default: 2.0s)

**Phase 1: Speaker Mapping Controls:**
- Enable/disable speaker regions (default: ON)
- Temporal consistency weight (0.0 - 1.0, default: 0.3)
- Duration weight slider (0.0 - 1.0, default: 0.4)
- Overlap weight slider (0.0 - 1.0, default: 0.3)

---

### **6. QUALITY ASSURANCE SCREEN**

**Phase 2: Quality Gates Configuration:**
- Enable/disable quality assessment (default: ON)
- Diarization thresholds:
  - Max micro-segment ratio slider (0-100%, default: 15%)
  - Min avg segment duration (0.5s - 10s, default: 2.0s)
 - Max speaker switches per minute (1-20, default: 8)
- Transcription thresholds:
  - Min avg confidence slider (0.0 - 1.0, default: 0.7)
  - Max no-speech probability (0.0 - 1.0, default: 0.3)
- Combination thresholds:
 - Min speaker mapping confidence (0.0 - 1.0, default: 0.6)
  - Max ambiguous segments ratio (0-100%, default: 10%)

---

### **7. PROOFREADING CONFIGURATION SCREEN**

**Enhanced Proofreading Options:**
- Enable/disable proofreading (default: OFF)
- Proofreading level: Minimal, Standard, Thorough, Custom
- Domain dictionaries selection:
  - Military terms (75+ terms)
  - Technical/IT terms (60+ terms)
  - Business terms (40+ terms)
  - Medical terms (30+ terms)
  - Common acronyms (30+ terms)
  - Named entities (25+ terms)

**Acronym Expansion:**
- Enable/disable acronym expansion (default: OFF)
- Expansion format: Parenthetical, Replacement, Footnote
- First occurrence only vs. all occurrences

**Context-Aware Features (v3.1.1):**
- Enable/disable context matching
- SpaCy model selection: en_core_web_sm, en_core_web_md, en_core_web_lg
- Auto-download model option
- Context confidence threshold (0.0 - 1.0, default: 0.7)
- Context window size (1-10 tokens, default: 5)

---

### **8. OUTPUT CONFIGURATION SCREEN**

**Output Settings:**
- Output directory selection
- Output format checkboxes: TXT, JSON, SRT, Markdown
- Include confidence scores toggle
- Save markdown toggle
- Include quality report toggle
- Create backup files toggle
- Force overwrite toggle

---

### **9. HUGGINGFACE TOKEN MANAGEMENT SCREEN**

**Token Setup Flow:**
- Token input field with validation
- Token format validation (hf_ prefix check)
- License agreement links display
- Auto-save to .env file
- "Skip for now" option
- "Continue without diarization" option
- Token validation feedback
- Error handling with suggestions

---

### **10. SPEAKER LABELING SCREEN**

**Label Management:**
- Speaker ID to name mapping table
- Editable text fields for each speaker
- Import labels from JSON file
- Export labels to JSON file
- Auto-detect speakers from transcript
- Save labels for future use
- Bulk edit capabilities

---

### **11. BATCH PROCESSING SCREEN**

**Multi-file Processing:**
- File list with individual settings
- Global settings override option
- Worker count selection (1-8, auto-detect)
- Progress tracking per file
- Individual file retry option
- Batch summary statistics

---

### **12. PROGRESS & MONITORING SCREEN**

**Real-time Progress:**
- Stage-by-stage progress indicators
- MLX-Whisper: Audio duration + estimated completion time
- Faster-Whisper: Live progress bar with segment updates
- Processing time tracking
- Memory usage monitoring
- Current stage display
- Cancel processing option

**Quality Monitoring:**
- Live quality metrics display
- Issue detection alerts
- Performance statistics
- Resource utilization

---

### **13. RESULTS & OUTPUT SCREEN**

**Results Display:**
- Generated file list with download options
- Transcript preview with speaker colors
- Quality report summary
- Processing statistics
- Error logs (if any)
- Share/export options
- Open in default application

**Transcript Viewing:**
- Speaker-colored text display
- Timestamp navigation
- Search within transcript
- Copy/paste functionality
- Export options

---

### **14. SETTINGS & CONFIGURATION SCREEN**

**Global Settings:**
- Default model preferences
- Output directory defaults
- Quality threshold presets
- UI theme selection
- Language preferences
- Auto-update settings
- Cache management
- Advanced debugging options

---

### **15. SYSTEM HEALTH & DIAGNOSTICS SCREEN**

**Doctor Command Interface:**
- System compatibility check
- Dependency status
- Model availability
- Device detection (Apple Silicon, CUDA, etc.)
- Memory and storage checks
- Performance benchmarks
- Troubleshooting suggestions

---

### **16. MODEL MANAGEMENT SCREEN**

**NLP Model Management:**
- SpaCy installation status
- Available models list with sizes
- Download model options
- Model size information
- Installation progress
- Context-aware feature status
- Dependency verification

---

### **17. WORKFLOW SEQUENCES**

**Primary User Journeys:**
1. **Quick Start**: File → Auto-config → Process → Results
2. **Guided Setup**: File → Wizard → Configure → Process → Results  
3. **Advanced Mode**: File → Full Config → Process → Monitor → Results
4. **Batch Processing**: Multiple files → Global settings → Process → Monitor
5. **Post-Processing**: Results → Speaker labels → Proofreading → Export

**Error Recovery Paths:**
- Invalid file handling
- Missing dependencies
- Token validation failures
- Processing errors
- Quality gate failures
- System resource issues

---

### **18. VISUAL DESIGN REQUIREMENTS**

**UI Components Needed:**
- File upload/drop zones
- Progress bars and spinners
- Toggle switches for boolean options
- Sliders for numeric ranges
- Dropdown selectors
- Modal dialogs for confirmation
- Tabbed interfaces for settings
- Data tables for speaker mapping
- Text editors for custom rules
- Preview panes for results
- Notification system
- Status indicators
- Search and filter controls

**Responsive Design:**
- Desktop-first approach
- Multi-window support
- Drag-and-drop functionality
- Keyboard navigation
- Accessibility compliance

This comprehensive list covers all the features, options, and workflows from the CLI version that need to be translated into a modern, intuitive GUI interface for LocalTranscribe. 