# LocalTranscribe GUI Implementation Prompt

## Project Overview

LocalTranscribe is a privacy-first desktop application for audio transcription with speaker diarization, entirely offline and running locally on user machines. The application transforms audio recordings into detailed transcripts showing who said what and when, with advanced features including:

- Complete privacy (100% offline processing)
- Speaker diarization with automatic speaker detection
- Interactive file browser with arrow-key navigation
- Guided wizard for new users
- Quality gates system with actionable recommendations
- Enhanced proofreading with domain dictionaries and acronym expansion
- Context-aware NLP features using spaCy
- Batch processing capabilities
- Real-time progress tracking with time estimates
- Interactive speaker labeling

The GUI should maintain all existing CLI functionality while providing an intuitive, visually appealing user experience with modern desktop application patterns, real-time progress monitoring, and comprehensive workflow management.

## Architecture Requirements

### Frontend Stack
- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS with shadcn-svelte components
- **State Management**: Svelte stores for reactive state management and Tauri state management for shared backend data
- **Build Tool**: Vite for fast development and optimized builds
- **SSR**: Disabled (`ssr: false`) for Tauri compatibility

### Backend Stack
- **Framework**: Tauri v2.x with Rust
- **Runtime**: WRY webview runtime
- **Architecture**: Command-based IPC with proper error handling and progress channels
- **State Management**: Tauri state management with Mutex-wrapped shared data
- **File System**: Tauri plugin-fs with proper capability scopes

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
│   │   ├── +layout.svelte # Disable SSR: export const ssr = false
│   │   ├── index.svelte   # Main dashboard
│   │   ├── process/+page.svelte
│   │   ├── settings/+page.svelte
│   │   ├── results/+page.svelte
│   │   ├── wizard/+page.svelte
│   │   ├── quality/+page.svelte
│   │   ├── proofreading/+page.svelte
│   │   └── batch/+page.svelte
│   └── app.d.ts
├── src-tauri/
│   ├── src/
│   │   ├── lib.rs        # Plugin initialization
│   │   ├── main.rs       # App entry point
│   │   ├── commands/     # Tauri command handlers
│   │   ├── models/       # Data structures
│   │   ├── services/     # Business logic
│   │   └── state/        # Application state management
│   ├── Cargo.toml
│   └── tauri.conf.json
├── package.json
├── svelte.config.js
└── vite.config.js
```

## Core Features Implementation

### 1. Main Dashboard Window & Wizard Flow

**Rust Implementation:**
```rust
use tauri::{AppHandle, Manager, WebviewWindowBuilder, WebviewUrl};
use std::sync::Mutex;
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize, Default)]
struct AppState {
    current_file: Option<String>,
    processing_status: ProcessingStatus,
    progress: f64,
    current_stage: String,
}

#[derive(Clone, Serialize, Deserialize)]
enum ProcessingStatus {
    Idle,
    Processing,
    Completed,
    Failed,
}

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

#[tauri::command]
async fn start_wizard_flow(app: AppHandle) -> Result<(), String> {
    // Initialize wizard flow with file browser
    app.emit_to("main", "wizard-start", ()).map_err(|e| e.to_string())?;
    Ok(())
}
```

**Svelte Component (Main Dashboard):**
```svelte
<script>
  import { invoke } from '@tauri-apps/api/core';
  import { listen } from '@tauri-apps/api/event';
  import { onMount } from 'svelte';
  import { derived, writable } from 'svelte/store';
  
  // Reactive state using Svelte stores
  let isProcessing = $state(false);
  let progress = $state(0);
  let currentStage = $state('');
  let selectedFile = $state(null);
  
  // State store for global app state
  const appState = writable({
    currentFile: null,
    processingStatus: 'idle',
    progress: 0,
    currentStage: ''
  });
  
  $: derived(appState, $state => $state.currentFile);
  
  onMount(async () => {
    // Listen for processing progress updates
    const unlistenProgress = await listen('processing-progress', (event) => {
      const { progress, stage } = event.payload;
      appState.update(state => ({
        ...state,
        progress,
        currentStage: stage,
        processingStatus: 'processing'
      }));
    });
    
    // Listen for processing completion
    const unlistenComplete = await listen('processing-complete', (event) => {
      appState.update(state => ({
        ...state,
        processingStatus: 'completed',
        currentStage: 'Complete'
      }));
      isProcessing = false;
    });
    
    return () => {
      unlistenProgress();
      unlistenComplete();
    };
  });
  
  async function startProcessing() {
    if (!selectedFile) return;
    
    isProcessing = true;
    await invoke('start_transcription', { 
      filePath: selectedFile,
      config: getProcessingConfig()
    });
  }
  
  async function browseFiles() {
    const result = await invoke('browse_audio_files');
    if (result) {
      selectedFile = result;
      appState.update(state => ({ ...state, currentFile: result }));
    }
  }
</script>

<div class="flex flex-col h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-white shadow-sm border-b sticky top-0 z-10">
    <div class="px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <h1 class="text-2xl font-bold text-gray-900">LocalTranscribe</h1>
        {#if $appState.currentFile}
          <span class="text-sm text-gray-500 truncate max-w-xs">
            {path.basename($appState.currentFile)}
          </span>
        {/if}
      </div>
      <div class="flex items-center space-x-2">
        <button 
          class="px-3 py-1 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700"
          on:click={browseFiles}
        >
          Browse Files
        </button>
      </div>
    </div>
  </header>
  
  <!-- Main Content -->
  <main class="flex-1 p-6 overflow-auto">
    {#if $appState.processingStatus === 'processing'}
      <div class="max-w-2xl mx-auto">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-4">Processing Audio</h2>
          <div class="space-y-4">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style="width: {$appState.progress}%"
              ></div>
            </div>
            <div class="flex justify-between text-sm">
              <span>{$appState.progress.toFixed(0)}%</span>
              <span class="text-gray-600">{$appState.currentStage}</span>
            </div>
            
            {#if $appState.currentStage.includes('transcription')}
              <div class="mt-4 p-3 bg-blue-50 rounded-md">
                <p class="text-sm text-blue-800">
                  Estimated completion: Calculating...
                </p>
              </div>
            {/if}
          </div>
          
          <div class="mt-4 flex justify-end">
            <button 
              class="px-4 py-2 text-sm rounded-md bg-red-600 text-white hover:bg-red-700"
              on:click={() => invoke('cancel_processing')}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    {:else if $appState.currentFile}
      <!-- Configuration and processing options -->
      <div class="max-w-4xl mx-auto space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-4">Audio Analysis</h2>
          <AudioAnalysis :filePath={$appState.currentFile} />
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold mb-4">Processing Configuration</h2>
          <ProcessingConfig />
        </div>
        
        <div class="flex justify-end space-x-3">
          <button 
            class="px-4 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
            on:click={() => { selectedFile = null; appState.update(s => ({ ...s, currentFile: null })); }}
          >
            Change File
          </button>
          <button 
            class="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700"
            on:click={startProcessing}
          >
            Start Processing
          </button>
        </div>
      </div>
    {:else}
      <!-- Welcome screen -->
      <div class="max-w-2xl mx-auto text-center py-12">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-4">
            Privacy-First Audio Transcription
          </h1>
          <p class="text-gray-600 mb-8">
            Transform audio recordings into detailed transcripts showing who said what and when. 
            All processing happens locally on your machine.
          </p>
        </div>
        
        <div class="space-y-4">
          <button 
            class="px-6 py-3 text-lg rounded-lg bg-blue-600 text-white hover:bg-blue-700 w-full max-w-sm"
            on:click={browseFiles}
          >
            Select Audio File
          </button>
          
          <p class="text-sm text-gray-500">
            Supports MP3, WAV, M4A, FLAC, MP4, MOV, and more
          </p>
        </div>
        
        <div class="mt-12 grid grid-cols-2 gap-6">
          <div class="bg-white rounded-lg p-4 shadow">
            <div class="text-2xl mb-2">🔒</div>
            <h3 class="font-semibold mb-1">100% Private</h3>
            <p class="text-sm text-gray-600">All processing on your machine</p>
          </div>
          <div class="bg-white rounded-lg p-4 shadow">
            <div class="text-2xl mb-2">🎯</div>
            <h3 class="font-semibold mb-1">Speaker Detection</h3>
            <p class="text-sm text-gray-600">Automatic speaker identification</p>
          </div>
        </div>
      </div>
    {/if}
  </main>
</div>
```

### 2. Interactive File Browser & Audio Analysis
```rust
use tauri::api::dialog::blocking::FileDialogBuilder;
use std::path::PathBuf;
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize)]
struct AudioFileInfo {
    path: String,
    name: String,
    extension: String,
    size: u64,
    duration: Option<f64>,
    sample_rate: Option<u32>,
    channels: Option<u16>,
}

#[tauri::command]
fn browse_audio_files(
    initial_dir: Option<String>
) -> Result<Vec<AudioFileInfo>, String> {
    let mut dialog = FileDialogBuilder::new();
    
    // Add multiple file filters
    dialog = dialog
        .add_filter("Audio", &["mp3", "wav", "m4a", "flac", "aac", "ogg"])
        .add_filter("Video", &["mp4", "mov", "avi", "mkv", "wmv"])
        .add_filter("All", &["*"]);
    
    if let Some(dir) = initial_dir {
        dialog = dialog.set_directory(dir);
    }
    
    let selected_files = dialog.pick_files();
    
    match selected_files {
        Some(files) => {
            let mut results = Vec::new();
            for file_path in files {
                let info = analyze_audio_file(&file_path)?;
                results.push(info);
            }
            Ok(results)
        }
        None => Ok(vec![]), // User cancelled
    }
}

#[tauri::command]
fn analyze_audio_file(path: String) -> Result<AudioFileInfo, String> {
    let path_buf = PathBuf::from(path);
    let metadata = std::fs::metadata(&path_buf)
        .map_err(|e| format!("Failed to read file metadata: {}", e))?;
    
    // Use existing LocalTranscribe audio analysis
    let analysis_result = run_audio_analysis(path_buf.clone())
        .map_err(|e| format!("Audio analysis failed: {}", e))?;
    
    Ok(AudioFileInfo {
        path: path_buf.to_string_lossy().to_string(),
        name: path_buf.file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string(),
        extension: path_buf.extension()
            .unwrap_or_default()
            .to_string_lossy()
            .to_string(),
        size: metadata.len(),
        duration: Some(analysis_result.duration),
        sample_rate: analysis_result.sample_rate,
        channels: analysis_result.channels,
    })
}
```

### 3. Processing Configuration with Advanced Options
```rust
use serde::{Deserialize, Serialize};
use std::sync::Mutex;

#[derive(Clone, Serialize, Deserialize, Default)]
pub struct ProcessingConfig {
    // Basic settings
    pub model_size: String,
    pub implementation: String,
    pub language: Option<String>,
    
    // Speaker settings
    pub num_speakers: Option<u32>,
    pub min_speakers: Option<u32>,
    pub max_speakers: Option<u32>,
    pub skip_diarization: bool,
    
    // Phase 1: Segment processing (v3.1+)
    pub enable_segment_processing: bool,
    pub min_segment_duration: f64,
    pub merge_gap_threshold: f64,
    pub min_speaker_turn: f64,
    pub smoothing_window: f64,
    
    // Phase 1: Speaker mapping
    pub use_speaker_regions: bool,
    pub temporal_consistency_weight: f64,
    pub duration_weight: f64,
    pub overlap_weight: f64,
    
    // Phase 2: Quality gates
    pub enable_quality_gates: bool,
    pub enable_audio_analysis: bool,
    
    // Phase 2: Proofreading enhancements
    pub enable_proofreading: bool,
    pub proofreading_level: String,
    pub proofreading_domains: Vec<String>,
    pub enable_acronym_expansion: bool,
    pub acronym_format: String,
    pub enable_context_matching: bool,
    pub spacy_model: String,
    pub context_confidence_threshold: f64,
    pub context_window_size: u32,
    
    // Output settings
    pub output_formats: Vec<String>,
    pub include_confidence: bool,
    pub include_quality_report: bool,
    pub create_backup: bool,
    pub force_overwrite: bool,
    
    // HuggingFace token
    pub hf_token: Option<String>,
    
    // Batch processing (if applicable)
    pub max_workers: usize,
    pub skip_existing: bool,
}

#[tauri::command]
fn get_default_config(app: AppHandle) -> Result<ProcessingConfig, String> {
    let state: tauri::State<Mutex<ProcessingConfig>> = app.state();
    let state_guard = state.lock().map_err(|e| e.to_string())?;
    Ok((*state_guard).clone())
}

#[tauri::command]
fn save_config(config: ProcessingConfig, app: AppHandle) -> Result<(), String> {
    let state: tauri::State<Mutex<ProcessingConfig>> = app.state();
    let mut state_guard = state.lock().map_err(|e| e.to_string())?;
    *state_guard = config;
    Ok(())
}
```

### 4. Pipeline Execution with Progress Tracking
```rust
use tauri::{ipc::Channel, AppHandle, Emitter, EventTarget};
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize)]
pub struct ProcessingProgress {
    pub stage: String,
    pub progress: f64,
    pub message: String,
    pub elapsed_time: f64,
    pub remaining_time: Option<f64>,
    pub details: Option<ProgressDetails>,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct ProgressDetails {
    pub current_file: Option<String>,
    pub files_processed: u32,
    pub total_files: u32,
    pub current_stage: String,
    pub estimated_completion: Option<f64>,
    pub memory_usage: Option<f64>,
    pub gpu_usage: Option<f64>,
}

#[tauri::command]
async fn start_transcription(
    config: ProcessingConfig,
    file_path: String,
    progress_channel: Channel<ProcessingProgress>,
    app: AppHandle,
) -> Result<(), String> {
    use localtranscribe::pipeline::PipelineOrchestrator;
    
    let mut orchestrator = PipelineOrchestrator::new(
        PathBuf::from(&file_path),
        PathBuf::from("./output"),
        config.model_size,
        config.num_speakers,
        config.min_speakers,
        config.max_speakers,
        config.language,
        config.implementation,
        config.skip_diarization,
        vec!["txt", "json", "md"],
        config.hf_token,
        None,
        config.force_overwrite,
        false,
        config.create_backup,
        false,
        // Phase 1: Segment processing
        config.enable_segment_processing,
        None, // Use defaults
        config.use_speaker_regions,
        config.temporal_consistency_weight,
        config.duration_weight,
        config.overlap_weight,
        // Phase 2: Quality/Proofreading
        config.enable_audio_analysis,
        config.enable_quality_gates,
        None, // Quality report path
        Some(config.proofreading_domains),
        config.enable_acronym_expansion,
    );

    // Enable advanced features
    orchestrator.enable_proofreading = config.enable_proofreading;
    orchestrator.proofreading_level = config.proofreading_level;
    
    // Spawn processing in background with progress channel
    tauri::async_runtime::spawn(async move {
        let mut progress_receiver = orchestrator.run_with_progress();
        
        while let Some(progress) = progress_receiver.recv().await {
            let _ = progress_channel.send(ProcessingProgress {
                stage: progress.stage,
                progress: progress.progress,
                message: progress.message,
                elapsed_time: progress.elapsed_time,
                remaining_time: progress.estimated_remaining,
                details: Some(ProgressDetails {
                    current_file: Some(file_path.clone()),
                    files_processed: 1,
                    total_files: 1,
                    current_stage: progress.stage,
                    estimated_completion: progress.estimated_remaining,
                    memory_usage: progress.memory_usage,
                    gpu_usage: progress.gpu_usage,
                }),
            });
        }
        
        // Emit completion event
        let _ = app.emit("processing-complete", {});
    });
    
    Ok(())
}
```

### 5. Quality Assessment & Proofreading Integration
```rust
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize)]
pub struct QualityReport {
    pub overall_score: f64,
    pub passed: bool,
    pub diarization_score: f64,
    pub transcription_score: f64,
    pub combination_score: f64,
    pub issues: Vec<QualityIssue>,
    pub metrics: QualityMetrics,
    pub recommendations: Vec<String>,
    pub audio_analysis: Option<AudioAnalysisResult>,
}

#[tauri::command]
fn get_quality_report(file_path: String) -> Result<QualityReport, String> {
    use localtranscribe::quality::QualityGate;
    use localtranscribe::audio::AudioAnalyzer;
    
    let gate = QualityGate::new();
    let analyzer = AudioAnalyzer::new();
    
    // Analyze audio quality
    let audio_result = analyzer.analyze(PathBuf::from(&file_path))
        .map_err(|e| format!("Audio analysis failed: {}", e))?;
    
    // Assess diarization quality
    let dia_assessment = gate.assess_diarization_quality_from_file(&file_path)
        .map_err(|e| format!("Quality assessment failed: {}", e))?;
    
    Ok(QualityReport {
        overall_score: dia_assessment.overall_score,
        passed: dia_assessment.passed,
        diarization_score: dia_assessment.overall_score,
        transcription_score: 0.8, // Placeholder
        combination_score: 0.85,  // Placeholder
        issues: dia_assessment.issues,
        metrics: dia_assessment.metrics,
        recommendations: dia_assessment.recommendations,
        audio_analysis: Some(audio_result.into()),
    })
}

#[tauri::command]
fn get_domain_dictionaries() -> Result<std::collections::HashMap<String, Vec<String>>, String> {
    use localtranscribe::proofreading::{get_all_domain_terms, get_domains_list};
    
    let mut domains = std::collections::HashMap::new();
    let available_domains = get_domains_list();
    
    for domain in available_domains {
        let terms = get_all_domain_terms(&domain);
        domains.insert(domain, terms);
    }
    
    Ok(domains)
}

#[tauri::command]
fn get_nlp_models_status() -> Result<Vec<NLPModelInfo>, String> {
    use localtranscribe::proofreading::model_manager::check_spacy_model;
    
    let models = vec![
        NLPModelInfo {
            name: "en_core_web_sm".to_string(),
            display_name: "English (Small)".to_string(),
            size: "15MB".to_string(),
            installed: check_spacy_model("en_core_web_sm"),
            available: true,
            version: "3.7.0".to_string(),
        },
        NLPModelInfo {
            name: "en_core_web_md".to_string(),
            display_name: "English (Medium)".to_string(),
            size: "43MB".to_string(),
            installed: check_spacy_model("en_core_web_md"),
            available: true,
            version: "3.7.0".to_string(),
        },
        NLPModelInfo {
            name: "en_core_web_lg".to_string(),
            display_name: "English (Large)".to_string(),
            size: "741MB".to_string(),
            installed: check_spacy_model("en_core_web_lg"),
            available: true,
            version: "3.7.0".to_string(),
        },
    ];
    
    Ok(models)
}

#[derive(Clone, Serialize, Deserialize)]
pub struct NLPModelInfo {
    pub name: String,
    pub display_name: String,
    pub size: String,
    pub installed: bool,
    pub available: bool,
    pub version: String,
}
```

### 6. Tauri Configuration with Capabilities
**svelte.config.js:**
```javascript
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      fallback: 'index.html',
      ssr: false  // Disable SSR for Tauri compatibility
    })
  }
};

export default config;
```

**tauri.conf.json:**
```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "build": {
    "beforeDevCommand": "pnpm dev",
    "beforeBuildCommand": "pnpm build",
    "devUrl": "http://localhost:1420",
    "frontendDist": "../build"
  },
  "app": {
    "windows": [
      {
        "label": "main",
        "title": "LocalTranscribe",
        "width": 1200,
        "height": 800,
        "minWidth": 800,
        "minHeight": 600,
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
      "scope": [
        "$APPDATA/**",
        "$APPDATA/output/**",
        "$HOME/**/*",
        "$DOCUMENT/**/*",
        "$DESKTOP/**/*",
        "$DOWNLOAD/**/*"
      ]
    }
  }
}
```

**capabilities/default.json:**
```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability",
  "description": "Main application capability",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:allow-read-file",
    "fs:allow-write-file",
    "fs:allow-read-dir",
    "fs:allow-copy-file",
    "fs:allow-create-dir",
    "fs:default",
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [
        { "path": "$APPDATA/**/*" },
        { "path": "$HOME/**/*" },
        { "path": "$DOCUMENT/**/*" },
        { "path": "$DESKTOP/**/*" },
        { "path": "$DOWNLOAD/**/*" }
      ]
    },
    {
      "identifier": "fs:allow-write-file",
      "allow": [
        { "path": "$APPDATA/**/*" },
        { "path": "$HOME/**/*" },
        { "path": "$DOCUMENT/**/*" },
        { "path": "$DESKTOP/**/*" },
        { "path": "$DOWNLOAD/**/*" }
      ]
    }
  ]
}
```

## Advanced Features Implementation

### Batch Processing
```rust
#[derive(Clone, Serialize, Deserialize)]
pub struct BatchProcessingConfig {
    pub files: Vec<String>,
    pub base_config: ProcessingConfig,
    pub max_workers: usize,
    pub skip_existing: bool,
    pub recursive: bool,
}

#[tauri::command]
async fn start_batch_processing(
    config: BatchProcessingConfig,
    progress_channel: Channel<BatchProgress>,
    app: AppHandle,
) -> Result<(), String> {
    use localtranscribe::batch::BatchProcessor;
    
    let processor = BatchProcessor::new(
        Some(config.files),
        PathBuf::from("./output"),
        config.base_config.model_size,
        config.base_config.num_speakers,
        config.base_config.min_speakers,
        config.base_config.max_speakers,
        config.base_config.language,
        config.base_config.implementation,
        config.base_config.skip_diarization,
        vec!["txt", "json", "md"],
        config.max_workers,
        config.skip_existing,
        config.recursive,
        config.base_config.hf_token,
        false, // verbose
    );

    tauri::async_runtime::spawn(async move {
        let mut progress_receiver = processor.process_batch_with_progress();
        
        while let Some(progress) = progress_receiver.recv().await {
            let _ = progress_channel.send(progress);
        }
        
        let _ = app.emit("batch-complete", {});
    });
    
    Ok(())
}

#[derive(Clone, Serialize, Deserialize)]
pub struct BatchProgress {
    pub file_index: usize,
    pub total_files: usize,
    pub current_file: String,
    pub file_progress: f64,
    pub overall_progress: f64,
    pub status: String,
    pub details: Option<String>,
}
```

### Model Management (v3.1.1+)
```rust
#[tauri::command]
async fn check_nlp_models() -> Result<Vec<NLPModelInfo>, String> {
    use localtranscribe::proofreading::model_manager::check_spacy_model;
    
    let models = vec![
        NLPModelInfo {
            name: "en_core_web_sm".to_string(),
            display_name: "English (Small)".to_string(),
            size: "15MB".to_string(),
            installed: check_spacy_model("en_core_web_sm"),
            available: true,
            version: "3.7.0".to_string(),
        },
        NLPModelInfo {
            name: "en_core_web_md".to_string(),
            display_name: "English (Medium)".to_string(),
            size: "43MB".to_string(),
            installed: check_spacy_model("en_core_web_md"),
            available: true,
            version: "3.7.0".to_string(),
        },
        NLPModelInfo {
            name: "en_core_web_lg".to_string(),
            display_name: "English (Large)".to_string(),
            size: "741MB".to_string(),
            installed: check_spacy_model("en_core_web_lg"),
            available: true,
            version: "3.7.0".to_string(),
        },
    ];
    
    Ok(models)
}

#[tauri::command]
async fn download_nlp_model(model_name: String) -> Result<(), String> {
    use localtranscribe::proofreading::model_manager::ensure_spacy_model;
    
    let (nlp, ready) = ensure_spacy_model(&model_name, true, false)
        .map_err(|e| format!("Failed to download model: {}", e))?;
    
    if !ready {
        return Err("Model download failed".to_string());
    }
    
    Ok(())
}
```

### System Health & Doctor Command
```rust
#[derive(Clone, Serialize, Deserialize)]
pub struct HealthCheckResult {
    pub overall_status: String,
    pub python_version: Option<String>,
    pub platform: Option<String>,
    pub dependencies: Vec<DependencyStatus>,
    pub gpu_available: bool,
    pub memory_available: u64,
    pub ffmpeg_available: bool,
    pub huggingface_token: bool,
    pub recommendations: Vec<String>,
}

#[derive(Clone, Serialize, Deserialize)]
pub struct DependencyStatus {
    pub name: String,
    pub available: bool,
    pub version: Option<String>,
    pub required: bool,
}

#[tauri::command]
async fn run_health_check() -> Result<HealthCheckResult, String> {
    use localtranscribe::health::doctor::run_health_check;
    
    let result = run_health_check(false) // verbose = false
        .map_err(|e| format!("Health check failed: {}", e))?;
    
    Ok(result.into())
}
```

## Security & Permissions
- Implement Tauri's capability system for fine-grained permissions
- Secure file system access with scoped permissions
- Validate all user inputs and file paths
- Implement proper error handling and sanitization
- Use Rust's type system for memory safety
- Implement secure HuggingFace token management

## UI/UX Guidelines
- Follow modern desktop application patterns
- Implement responsive design for different screen sizes
- Use appropriate loading states and progress indicators
- Provide clear error messages and recovery options
- Implement keyboard shortcuts for power users
- Support dark/light mode preferences
- Provide intuitive workflow with guided setup for new users
- Implement undo/redo functionality where appropriate

## Development Workflow
1. Set up Tauri development environment with Rust and node.js
2. Configure SvelteKit with adapter-static and SSR disabled
3. Create Tauri command handlers with proper state management
4. Implement file system access with capability scopes
5. Build reusable Svelte components with proper state management
6. Integrate existing LocalTranscribe functionality
7. Implement progress tracking with channels
8. Test cross-platform compatibility
9. Optimize performance and bundle size

## Key User Flows
1. **New User Wizard**: File browser → Audio analysis → Auto-config → Process
2. **Quick Processing**: Drop file → Auto-process → View results
3. **Advanced Mode**: File → Full configuration → Advanced options → Process
4. **Batch Processing**: Multiple files → Common settings → Process
5. **Post-processing**: Results → Speaker labeling → Proofreading → Export
6. **Quality Review**: Results → Quality assessment → Recommendations → Re-process
7. **Model Management**: Settings → NLP models → Download/install → Configure

This comprehensive prompt provides the foundation for building a modern, feature-complete LocalTranscribe GUI that maintains all existing functionality while providing an enhanced user experience with proper error handling, security, and performance optimization.