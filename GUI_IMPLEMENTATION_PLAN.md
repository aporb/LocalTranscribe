# LocalTranscribe GUI Implementation Plan
## Comprehensive Architecture & Development Strategy

**Date**: 2026-01-09
**Target Platform**: Windows, macOS, Linux
**Development Phase**: Testing/Development (No code signing required)
**Status**: Ready for Implementation

---

## Executive Summary

This plan outlines the complete implementation of a modern, cross-platform GUI for LocalTranscribe using **Tauri 2.0 + SvelteKit + Python subprocess architecture**. Based on extensive research and industry best practices, this approach provides the optimal balance of performance, maintainability, and cross-platform compatibility while keeping the existing Python CLI backend intact.

### Key Decision: Tauri 2.0 (Recommended)

**Why Tauri over Electron:**
- **10x smaller bundle size**: ~10MB vs ~100MB ([Tauri vs Electron Comparison](https://www.levminer.com/blog/tauri-vs-electron))
- **~8x less memory**: ~30-40MB vs ~250MB idle ([DoltHub Analysis](https://www.dolthub.com/blog/2025-11-13-electron-vs-tauri/))
- **4x faster startup**: 0.4s vs 1.5s ([Performance Comparison](https://www.gethopp.app/blog/tauri-vs-electron))
- **Native WebView**: Uses system browser engine (WebView2/WebKit/WebKitGTK)
- **Security-first**: Rust backend with opt-in API access
- **Perfect for local tools**: Lightweight, fast, ideal for tools users keep open

**Research Sources:**
- [Tauri vs Electron 2025 Comparison](https://www.raftlabs.com/blog/tauri-vs-electron-pros-cons/)
- [InfoWorld Framework Analysis](https://www.infoworld.com/article/3547072/electron-vs-tauri-which-cross-platform-framework-is-for-you.html)
- [Peerlist Technical Deep-Dive](https://peerlist.io/jagss/articles/tauri-vs-electron-a-deep-technical-comparison)

---

## Architecture Overview

### Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    DESKTOP APPLICATION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         FRONTEND (SvelteKit + Tailwind)               │  │
│  │  • Svelte 5 (latest with runes)                      │  │
│  │  • SvelteKit (SPA mode - @sveltejs/adapter-static)   │  │
│  │  • Tailwind CSS 4.0                                   │  │
│  │  • shadcn-svelte components                           │  │
│  │  • Flowbite for complex UI patterns                   │  │
│  │  • Chart.js for waveform/analysis visualization      │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ▼ IPC (JSON-RPC)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          TAURI CORE (Rust Backend)                    │  │
│  │  • Process management (spawn/kill Python)             │  │
│  │  • IPC command handling                               │  │
│  │  • File system operations                             │  │
│  │  • System integration (notifications, menus)          │  │
│  │  • Security & sandboxing                              │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ▼ Subprocess/Sidecar               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │       PYTHON CLI BACKEND (Existing Codebase)          │  │
│  │  • LocalTranscribe CLI (as-is, no modifications)      │  │
│  │  • Packaged with PyInstaller/Nuitka                   │  │
│  │  • Communication via stdin/stdout or HTTP             │  │
│  │  • Model inference (Whisper, pyannote)                │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           PLATFORM-SPECIFIC PACKAGING                 │  │
│  │  • Windows: .msi, .exe (NSIS/WiX)                    │  │
│  │  • macOS: .app, .dmg (unsigned for testing)          │  │
│  │  • Linux: .AppImage, .deb, .rpm                       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Communication Patterns

**Two Viable Approaches:**

#### **Option A: Python CLI Subprocess (Recommended)**
```
SvelteKit → Tauri (Rust) → Python CLI → stdout/stderr → Parse → Tauri → SvelteKit
```

**Pros:**
- Zero modifications to existing CLI
- Simple IPC via stdin/stdout
- No server overhead
- Easy debugging (same as current CLI)

**Cons:**
- Progress updates require parsing stdout
- Less structured than API approach

#### **Option B: Python FastAPI Sidecar**
```
SvelteKit → Tauri (Rust) → Python FastAPI → HTTP/WebSocket → Tauri → SvelteKit
```

**Pros:**
- Structured API responses (JSON)
- WebSocket for real-time progress
- RESTful architecture
- Easy to add endpoints

**Cons:**
- Requires wrapping CLI in FastAPI
- Slight overhead from HTTP layer
- Port management complexity

**Decision: Use Option A (CLI Subprocess) initially**, with Option B as future enhancement if real-time progress becomes critical.

**Research Sources:**
- [Tauri Sidecar Documentation](https://v2.tauri.app/develop/sidecar/)
- [Python Sidecar Example](https://github.com/dieharders/example-tauri-v2-python-server-sidecar)
- [Tauri IPC Protocol](https://v2.tauri.app/concept/inter-process-communication/)

---

## Project Structure

```
LocalTranscribe-GUI/
├── src-tauri/                      # Tauri Rust backend
│   ├── src/
│   │   ├── main.rs                 # Main Tauri entry point
│   │   ├── commands.rs             # IPC command handlers
│   │   ├── python_manager.rs      # Python subprocess management
│   │   ├── file_operations.rs     # File system ops
│   │   └── config.rs               # App configuration
│   ├── tauri.conf.json             # Tauri configuration
│   ├── Cargo.toml                  # Rust dependencies
│   ├── build.rs                    # Build script
│   └── icons/                      # App icons (PNG, ICO, ICNS)
│
├── src/                            # SvelteKit frontend
│   ├── routes/
│   │   ├── +layout.svelte         # Root layout
│   │   ├── +page.svelte           # Dashboard/Home
│   │   ├── file-browser/
│   │   │   └── +page.svelte       # File selection screen
│   │   ├── analysis/
│   │   │   └── +page.svelte       # Audio analysis screen
│   │   ├── configure/
│   │   │   └── +page.svelte       # Configuration wizard
│   │   ├── process/
│   │   │   └── +page.svelte       # Processing screen
│   │   ├── results/
│   │   │   └── +page.svelte       # Results viewer
│   │   ├── batch/
│   │   │   └── +page.svelte       # Batch processing
│   │   └── settings/
│   │       └── +page.svelte       # Settings panel
│   │
│   ├── lib/
│   │   ├── components/            # Reusable UI components
│   │   │   ├── ui/               # shadcn-svelte primitives
│   │   │   ├── AudioPlayer.svelte
│   │   │   ├── Waveform.svelte
│   │   │   ├── ProgressTracker.svelte
│   │   │   ├── FileCard.svelte
│   │   │   └── QualityIndicator.svelte
│   │   │
│   │   ├── stores/               # Svelte stores (state management)
│   │   │   ├── app.ts            # Global app state
│   │   │   ├── processing.ts     # Processing state
│   │   │   ├── files.ts          # File management state
│   │   │   └── settings.ts       # User settings
│   │   │
│   │   ├── tauri/                # Tauri IPC wrappers
│   │   │   ├── commands.ts       # Typed command wrappers
│   │   │   ├── events.ts         # Event listeners
│   │   │   └── python.ts         # Python subprocess control
│   │   │
│   │   ├── utils/                # Utility functions
│   │   │   ├── format.ts         # Formatting helpers
│   │   │   ├── validation.ts     # Input validation
│   │   │   └── audio.ts          # Audio processing helpers
│   │   │
│   │   └── types/                # TypeScript types
│   │       ├── index.ts          # Core types
│   │       ├── api.ts            # API response types
│   │       └── ipc.ts            # IPC message types
│   │
│   ├── app.html                  # HTML template
│   ├── app.css                   # Global styles
│   └── app.d.ts                  # TypeScript declarations
│
├── python-backend/                # Python CLI packaging
│   ├── localtranscribe/          # Existing CLI (symlink or copy)
│   ├── build_sidecar.py          # PyInstaller build script
│   ├── requirements.txt          # Python dependencies
│   └── sidecar.spec              # PyInstaller spec file
│
├── static/                        # Static assets
│   ├── fonts/
│   ├── images/
│   └── waveform-worker.js       # Web worker for audio analysis
│
├── tests/
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests (Playwright)
│
├── .github/
│   └── workflows/
│       ├── build-desktop.yml    # CI/CD for desktop builds
│       └── test.yml             # Automated testing
│
├── package.json                  # Node dependencies
├── svelte.config.js             # SvelteKit config
├── tailwind.config.js           # Tailwind config
├── tsconfig.json                # TypeScript config
├── vite.config.ts               # Vite config
└── README-GUI.md                # GUI-specific documentation
```

---

## Implementation Phases

### Phase 1: Foundation Setup (Week 1)
**Goal**: Set up development environment and basic skeleton

#### 1.1 Prerequisites Installation
```bash
# Install Rust (required for Tauri)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Node.js 20+ (LTS)
# Download from https://nodejs.org/

# Verify installations
rustc --version    # Should be 1.75+
node --version     # Should be 20+
npm --version      # Should be 10+
```

#### 1.2 Project Initialization
```bash
# Create new Tauri + SvelteKit project
npm create tauri-app@latest

# Select options:
# - Project name: localtranscribe-gui
# - Frontend: SvelteKit
# - Package manager: npm
# - TypeScript: Yes

cd localtranscribe-gui

# Install additional dependencies
npm install -D @sveltejs/adapter-static
npm install -D tailwindcss postcss autoprefixer
npm install -D shadcn-svelte
npm install chart.js
npm install @tauri-apps/api @tauri-apps/plugin-shell
```

#### 1.3 Configure SvelteKit for SPA Mode
**Research Source**: [Tauri SvelteKit Guide](https://v2.tauri.app/start/frontend/sveltekit/)

Edit `svelte.config.js`:
```js
import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    adapter: adapter({
      fallback: 'index.html',
      precompress: false
    }),
    prerender: {
      entries: []
    }
  }
};

export default config;
```

#### 1.4 Configure Tailwind CSS
```bash
npx tailwindcss init -p
```

Edit `tailwind.config.js`:
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        // Custom OKLCH colors (avoiding indigo)
        primary: 'oklch(var(--primary))',
        secondary: 'oklch(var(--secondary))',
        // ... more custom colors
      }
    }
  },
  plugins: [
    require('flowbite/plugin')
  ]
}
```

#### 1.5 Initialize shadcn-svelte
```bash
npx shadcn-svelte@latest init
```

---

### Phase 2: Python Backend Integration (Week 1-2)
**Goal**: Package Python CLI as Tauri sidecar

#### 2.1 Package Python with PyInstaller

Create `python-backend/build_sidecar.py`:
```python
"""
Build script for packaging LocalTranscribe CLI as Tauri sidecar.
Creates single-file executables for Windows, macOS, and Linux.
"""

import PyInstaller.__main__
import platform
import sys
from pathlib import Path

def build_sidecar():
    """Build platform-specific sidecar binary."""

    system = platform.system().lower()

    # Determine output name
    if system == "windows":
        name = "localtranscribe.exe"
    else:
        name = "localtranscribe"

    # PyInstaller arguments
    args = [
        'localtranscribe/__main__.py',           # Entry point
        '--onefile',                             # Single executable
        '--name', name,
        '--clean',
        '--noconfirm',
        # Include all localtranscribe modules
        '--hidden-import=localtranscribe',
        '--hidden-import=localtranscribe.cli',
        '--hidden-import=localtranscribe.core',
        '--hidden-import=localtranscribe.pipeline',
        # Include ML dependencies
        '--hidden-import=torch',
        '--hidden-import=whisper',
        '--hidden-import=pyannote.audio',
        # Collect data files
        '--collect-all', 'localtranscribe',
        # Output directory
        '--distpath', '../src-tauri/binaries',
    ]

    # Platform-specific settings
    if system == "darwin":
        # macOS: Include MPS support
        args.extend([
            '--target-arch', 'universal2',  # Universal binary
            '--codesign-identity', '-',      # Ad-hoc signing
        ])
    elif system == "windows":
        # Windows: No console window
        args.append('--noconsole')

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    print(f"\n✅ Sidecar built successfully: {name}")
    print(f"   Location: src-tauri/binaries/")

if __name__ == "__main__":
    build_sidecar()
```

Run the build:
```bash
cd python-backend
python build_sidecar.py
```

#### 2.2 Configure Tauri Sidecar

Edit `src-tauri/tauri.conf.json`:
```json
{
  "bundle": {
    "externalBin": [
      "binaries/localtranscribe"
    ],
    "resources": [
      "../python-backend/models/*"
    ]
  },
  "tauri": {
    "allowlist": {
      "shell": {
        "sidecar": true,
        "scope": [
          {
            "name": "binaries/localtranscribe",
            "sidecar": true,
            "args": true
          }
        ]
      },
      "fs": {
        "scope": ["$RESOURCE", "$HOME/LocalTranscribe/**"]
      }
    }
  }
}
```

**Research Source**: [Tauri Sidecar Embedding](https://v2.tauri.app/develop/sidecar/)

#### 2.3 Create Python Manager (Rust)

Create `src-tauri/src/python_manager.rs`:
```rust
use std::process::{Child, Command, Stdio};
use std::sync::{Arc, Mutex};
use tauri::api::process::{Command as TauriCommand, CommandEvent};

pub struct PythonManager {
    process: Arc<Mutex<Option<Child>>>,
}

impl PythonManager {
    pub fn new() -> Self {
        Self {
            process: Arc::new(Mutex::new(None)),
        }
    }

    /// Spawn LocalTranscribe CLI with arguments
    pub async fn run_command(&self, args: Vec<String>) -> Result<String, String> {
        // Get sidecar path
        let sidecar_command = TauriCommand::new_sidecar("localtranscribe")
            .map_err(|e| format!("Failed to create sidecar command: {}", e))?;

        // Execute with arguments
        let (mut rx, _child) = sidecar_command
            .args(args)
            .spawn()
            .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

        // Collect output
        let mut output = String::new();

        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    output.push_str(&line);
                    output.push('\n');
                }
                CommandEvent::Stderr(line) => {
                    eprintln!("Error: {}", line);
                }
                CommandEvent::Terminated(payload) => {
                    if payload.code != Some(0) {
                        return Err(format!("Process exited with code: {:?}", payload.code));
                    }
                    break;
                }
                _ => {}
            }
        }

        Ok(output)
    }

    /// Check if Python backend is healthy
    pub async fn health_check(&self) -> Result<bool, String> {
        let result = self.run_command(vec!["--version".to_string()]).await?;
        Ok(result.contains("LocalTranscribe"))
    }
}
```

**Research Source**: [GitHub Python Sidecar Example](https://github.com/dieharders/example-tauri-python-server-sidecar)

#### 2.4 Create IPC Commands

Create `src-tauri/src/commands.rs`:
```rust
use crate::python_manager::PythonManager;
use serde::{Deserialize, Serialize};
use tauri::State;

#[derive(Serialize, Deserialize)]
pub struct ProcessRequest {
    pub audio_file: String,
    pub options: ProcessOptions,
}

#[derive(Serialize, Deserialize)]
pub struct ProcessOptions {
    pub model_size: Option<String>,
    pub speakers: Option<u8>,
    pub preset: Option<String>,
    pub formats: Vec<String>,
    pub proofread: bool,
    pub check_quality: bool,
}

/// Process audio file through LocalTranscribe CLI
#[tauri::command]
pub async fn process_audio(
    request: ProcessRequest,
    python_manager: State<'_, PythonManager>,
) -> Result<String, String> {
    // Build CLI arguments
    let mut args = vec![
        "process".to_string(),
        request.audio_file,
    ];

    // Add options
    if let Some(model) = request.options.model_size {
        args.push("--model".to_string());
        args.push(model);
    }

    if let Some(speakers) = request.options.speakers {
        args.push("--speakers".to_string());
        args.push(speakers.to_string());
    }

    if let Some(preset) = request.options.preset {
        args.push("--preset".to_string());
        args.push(preset);
    }

    if request.options.proofread {
        args.push("--proofread".to_string());
    }

    if request.options.check_quality {
        args.push("--check-quality".to_string());
    }

    // Add formats
    if !request.options.formats.is_empty() {
        args.push("--format".to_string());
        args.extend(request.options.formats);
    }

    // Execute command
    python_manager.run_command(args).await
}

/// Check audio quality
#[tauri::command]
pub async fn check_audio_quality(
    audio_file: String,
    python_manager: State<'_, PythonManager>,
) -> Result<String, String> {
    let args = vec![
        "process".to_string(),
        audio_file,
        "--check-quality".to_string(),
    ];

    python_manager.run_command(args).await
}

/// Run health check
#[tauri::command]
pub async fn health_check(
    python_manager: State<'_, PythonManager>,
) -> Result<bool, String> {
    python_manager.health_check().await
}

/// List recent files
#[tauri::command]
pub async fn list_recent_files() -> Result<Vec<String>, String> {
    // Implement file system scanning
    Ok(vec![])
}
```

#### 2.5 Register Commands in main.rs

Edit `src-tauri/src/main.rs`:
```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod python_manager;

use python_manager::PythonManager;

fn main() {
    let python_manager = PythonManager::new();

    tauri::Builder::default()
        .manage(python_manager)
        .invoke_handler(tauri::generate_handler![
            commands::process_audio,
            commands::check_audio_quality,
            commands::health_check,
            commands::list_recent_files,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

### Phase 3: Frontend UI Components (Week 2-3)
**Goal**: Build core UI screens with shadcn-svelte and Flowbite

#### 3.1 Create Tauri IPC Wrapper

Create `src/lib/tauri/commands.ts`:
```typescript
import { invoke } from '@tauri-apps/api/tauri';

export interface ProcessRequest {
  audio_file: string;
  options: ProcessOptions;
}

export interface ProcessOptions {
  model_size?: string;
  speakers?: number;
  preset?: string;
  formats: string[];
  proofread: boolean;
  check_quality: boolean;
}

export async function processAudio(request: ProcessRequest): Promise<string> {
  return await invoke<string>('process_audio', { request });
}

export async function checkAudioQuality(audioFile: string): Promise<string> {
  return await invoke<string>('check_audio_quality', { audioFile });
}

export async function healthCheck(): Promise<boolean> {
  return await invoke<boolean>('health_check');
}

export async function listRecentFiles(): Promise<string[]> {
  return await invoke<string[]>('list_recent_files');
}
```

#### 3.2 Create State Management Stores

Create `src/lib/stores/app.ts`:
```typescript
import { writable, derived } from 'svelte/store';

export interface AppState {
  isReady: boolean;
  pythonHealthy: boolean;
  currentScreen: string;
  error: string | null;
}

function createAppStore() {
  const { subscribe, update, set } = writable<AppState>({
    isReady: false,
    pythonHealthy: false,
    currentScreen: 'dashboard',
    error: null
  });

  return {
    subscribe,
    setReady: (ready: boolean) => update(s => ({ ...s, isReady: ready })),
    setPythonHealthy: (healthy: boolean) => update(s => ({ ...s, pythonHealthy: healthy })),
    setScreen: (screen: string) => update(s => ({ ...s, currentScreen: screen })),
    setError: (error: string | null) => update(s => ({ ...s, error })),
    reset: () => set({
      isReady: false,
      pythonHealthy: false,
      currentScreen: 'dashboard',
      error: null
    })
  };
}

export const app = createAppStore();
```

Create `src/lib/stores/processing.ts`:
```typescript
import { writable } from 'svelte/store';

export interface ProcessingState {
  isProcessing: boolean;
  currentFile: string | null;
  progress: number;
  stage: string | null;
  eta: number | null;
  result: string | null;
}

function createProcessingStore() {
  const { subscribe, update, set } = writable<ProcessingState>({
    isProcessing: false,
    currentFile: null,
    progress: 0,
    stage: null,
    eta: null,
    result: null
  });

  return {
    subscribe,
    start: (file: string) => update(s => ({
      ...s,
      isProcessing: true,
      currentFile: file,
      progress: 0,
      result: null
    })),
    updateProgress: (progress: number, stage: string, eta: number) =>
      update(s => ({ ...s, progress, stage, eta })),
    complete: (result: string) => update(s => ({
      ...s,
      isProcessing: false,
      progress: 100,
      result
    })),
    cancel: () => set({
      isProcessing: false,
      currentFile: null,
      progress: 0,
      stage: null,
      eta: null,
      result: null
    })
  };
}

export const processing = createProcessingStore();
```

#### 3.3 Build Dashboard Screen

Create `src/routes/+page.svelte`:
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { healthCheck, listRecentFiles } from '$lib/tauri/commands';
  import { app } from '$lib/stores/app';
  import { Button } from '$lib/components/ui/button';
  import { Card } from '$lib/components/ui/card';

  let recentFiles: string[] = [];
  let systemHealthy = false;

  onMount(async () => {
    // Check system health
    try {
      systemHealthy = await healthCheck();
      app.setPythonHealthy(systemHealthy);

      // Load recent files
      recentFiles = await listRecentFiles();

      app.setReady(true);
    } catch (error) {
      console.error('Failed to initialize:', error);
      app.setError(String(error));
    }
  });

  function handleFileSelect() {
    app.setScreen('file-browser');
  }
</script>

<div class="container mx-auto p-6">
  <!-- Hero Section -->
  <div class="text-center mb-12">
    <h1 class="text-4xl font-bold mb-4">
      🎙️ LocalTranscribe
    </h1>
    <p class="text-xl text-gray-600">
      Privacy-First Audio Transcription
    </p>
    <div class="flex justify-center gap-4 mt-4">
      <span class="badge">🔒 100% Offline</span>
      <span class="badge">🔐 No Cloud Uploads</span>
      <span class="badge">⚡ GPU Accelerated</span>
    </div>
  </div>

  <!-- Primary Action -->
  <Card class="p-8 mb-8">
    <div class="text-center">
      <h2 class="text-2xl font-semibold mb-4">
        📁 Select Audio File
      </h2>

      <Button
        size="lg"
        class="mb-4"
        on:click={handleFileSelect}
      >
        📁 SELECT FILE
      </Button>

      <p class="text-gray-500 text-sm">
        Supports MP3, WAV, M4A, FLAC, MP4, MOV, MKV, AVI
      </p>
      <p class="text-gray-500 text-sm">
        Drag & drop anywhere
      </p>
    </div>
  </Card>

  <!-- Feature Grid -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <Card class="p-6">
      <div class="text-4xl mb-4">🔒</div>
      <h3 class="font-semibold mb-2">Privacy First</h3>
      <p class="text-sm text-gray-600">
        100% Local Processing<br/>
        No Cloud Upload
      </p>
    </Card>

    <Card class="p-6">
      <div class="text-4xl mb-4">🎯</div>
      <h3 class="font-semibold mb-2">Speaker Detection</h3>
      <p class="text-sm text-gray-600">
        Automatic Speaker Diarization<br/>
        Multi-Speaker Support
      </p>
    </Card>

    <Card class="p-6">
      <div class="text-4xl mb-4">📊</div>
      <h3 class="font-semibold mb-2">Batch Processing</h3>
      <p class="text-sm text-gray-600">
        Process Multiple Files<br/>
        Parallel Processing
      </p>
    </Card>
  </div>

  <!-- Recent Files -->
  {#if recentFiles.length > 0}
    <Card class="p-6">
      <h3 class="font-semibold mb-4">📄 Recent Files</h3>
      <div class="space-y-2">
        {#each recentFiles as file}
          <div class="flex items-center justify-between p-2 hover:bg-gray-100 rounded">
            <span class="text-sm">{file}</span>
            <Button size="sm" variant="ghost">Open</Button>
          </div>
        {/each}
      </div>
    </Card>
  {/if}

  <!-- System Status -->
  <div class="mt-8 text-center">
    <div class="inline-flex items-center gap-2 text-sm">
      <span class={systemHealthy ? 'text-green-600' : 'text-red-600'}>
        {systemHealthy ? '🟢' : '🔴'}
      </span>
      <span>
        System Status: {systemHealthy ? 'Healthy' : 'Error'}
      </span>
    </div>
  </div>
</div>

<style>
  .badge {
    @apply inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm;
  }
</style>
```

*(Additional screens will follow similar patterns - file browser, analysis, processing, results)*

---

### Phase 4: Advanced Features (Week 3-4)

#### 4.1 Audio Waveform Visualization

Install audio processing library:
```bash
npm install wavesurfer.js
```

Create `src/lib/components/Waveform.svelte`:
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import WaveSurfer from 'wavesurfer.js';

  export let audioFile: string;

  let container: HTMLDivElement;
  let wavesurfer: WaveSurfer | null = null;

  onMount(() => {
    wavesurfer = WaveSurfer.create({
      container,
      waveColor: '#4F46E5',
      progressColor: '#818CF8',
      height: 128,
      responsive: true,
    });

    wavesurfer.load(audioFile);

    return () => {
      wavesurfer?.destroy();
    };
  });
</script>

<div bind:this={container} class="waveform-container" />

<style>
  .waveform-container {
    width: 100%;
    min-height: 128px;
  }
</style>
```

#### 4.2 Real-time Progress Updates

Implement progress parsing from Python stdout:

Create `src/lib/tauri/progress.ts`:
```typescript
import { listen } from '@tauri-apps/api/event';
import { processing } from '$lib/stores/processing';

export interface ProgressUpdate {
  stage: string;
  progress: number;
  eta: number;
}

export async function startProgressListener() {
  const unlisten = await listen<string>('python-stdout', (event) => {
    const line = event.payload;

    // Parse progress from CLI output
    // Example: "Stage 1/4: Speaker Diarization (ETA: 2m 30s)"
    const stageMatch = line.match(/Stage (\d+)\/(\d+): (.+?) \(ETA: (.+?)\)/);

    if (stageMatch) {
      const [, current, total, stage, eta] = stageMatch;
      const progress = (parseInt(current) / parseInt(total)) * 100;
      const etaSeconds = parseETA(eta);

      processing.updateProgress(progress, stage, etaSeconds);
    }
  });

  return unlisten;
}

function parseETA(eta: string): number {
  // Parse "2m 30s" to seconds
  const minutesMatch = eta.match(/(\d+)m/);
  const secondsMatch = eta.match(/(\d+)s/);

  let totalSeconds = 0;
  if (minutesMatch) totalSeconds += parseInt(minutesMatch[1]) * 60;
  if (secondsMatch) totalSeconds += parseInt(secondsMatch[1]);

  return totalSeconds;
}
```

#### 4.3 File Drag & Drop

Add to `src/routes/+layout.svelte`:
```svelte
<script lang="ts">
  import { listen } from '@tauri-apps/api/event';
  import { onMount } from 'svelte';

  onMount(async () => {
    // Listen for file drops
    const unlisten = await listen<string[]>('tauri://file-drop', (event) => {
      const files = event.payload;
      console.log('Files dropped:', files);

      // Handle dropped files
      if (files.length > 0) {
        // Navigate to file browser or process directly
        goto(`/file-browser?files=${encodeURIComponent(JSON.stringify(files))}`);
      }
    });

    return () => {
      unlisten();
    };
  });
</script>
```

---

### Phase 5: Build & Distribution (Week 4)

#### 5.1 Development Build (No Signing)

**Research Source**: [Tauri Build without Signing](https://github.com/tauri-apps/tauri/issues/11626)

```bash
# Development build (unsigned)
npm run tauri build -- --no-signing

# Or configure in tauri.conf.json for persistent dev builds
{
  "tauri": {
    "bundle": {
      "macOS": {
        "signingIdentity": null
      },
      "windows": {
        "certificateThumbprint": null
      }
    }
  }
}
```

#### 5.2 Platform-Specific Builds

**Windows:**
```bash
npm run tauri build --target x86_64-pc-windows-msvc -- --no-signing

# Outputs:
# - src-tauri/target/release/bundle/msi/localtranscribe_0.1.0_x64_en-US.msi
# - src-tauri/target/release/bundle/nsis/localtranscribe_0.1.0_x64-setup.exe
```

**macOS:**
```bash
npm run tauri build --target universal-apple-darwin -- --no-signing

# Outputs:
# - src-tauri/target/release/bundle/macos/LocalTranscribe.app
# - src-tauri/target/release/bundle/dmg/LocalTranscribe_0.1.0_universal.dmg
```

**Linux:**
```bash
npm run tauri build --target x86_64-unknown-linux-gnu

# Outputs:
# - src-tauri/target/release/bundle/appimage/localtranscribe_0.1.0_amd64.AppImage
# - src-tauri/target/release/bundle/deb/localtranscribe_0.1.0_amd64.deb
```

#### 5.3 Distribution Strategy (Testing Phase)

**For Internal Testing:**

1. **GitHub Releases** (Easiest):
   ```yaml
   # .github/workflows/build-desktop.yml
   name: Build Desktop App

   on:
     push:
       tags:
         - 'v*'

   jobs:
     build:
       strategy:
         matrix:
           os: [ubuntu-latest, windows-latest, macos-latest]

       runs-on: ${{ matrix.os }}

       steps:
         - uses: actions/checkout@v4

         - name: Setup Node
           uses: actions/setup-node@v4
           with:
             node-version: '20'

         - name: Setup Rust
           uses: dtolnay/rust-toolchain@stable

         - name: Install dependencies
           run: npm ci

         - name: Build Tauri app
           run: npm run tauri build -- --no-signing

         - name: Upload artifacts
           uses: actions/upload-artifact@v4
           with:
             name: localtranscribe-${{ matrix.os }}
             path: |
               src-tauri/target/release/bundle/**/*.msi
               src-tauri/target/release/bundle/**/*.exe
               src-tauri/target/release/bundle/**/*.dmg
               src-tauri/target/release/bundle/**/*.AppImage
               src-tauri/target/release/bundle/**/*.deb
   ```

2. **Direct Distribution**:
   - Upload to file sharing (Dropbox, Google Drive)
   - Users download and install manually
   - No app store submission required

3. **Auto-updater** (Optional, for later):
   ```json
   {
     "tauri": {
       "updater": {
         "active": true,
         "endpoints": [
           "https://releases.myapp.com/{{target}}/{{current_version}}"
         ],
         "dialog": true,
         "pubkey": "OPTIONAL_PUBLIC_KEY"
       }
     }
   }
   ```

**Research Source**: [Tauri Distribution Guide](https://v2.tauri.app/distribute/)

---

## Security Considerations

### 1. Tauri Security Features (Built-in)

- **Process Isolation**: Frontend and backend run in separate processes
- **IPC Whitelisting**: Only explicitly allowed commands can be invoked
- **CSP (Content Security Policy)**: Prevents XSS attacks
- **Sandboxed WebView**: System webview runs in restricted mode

### 2. Python Subprocess Security

- **No Network Access**: Python CLI runs completely offline
- **File System Scope**: Limit Python to specific directories
- **Input Validation**: Validate all file paths in Rust before passing to Python

### 3. User Data Protection

- **Local Storage Only**: All data stays on user's machine
- **No Telemetry**: No analytics or tracking by default
- **Encrypted Secrets**: Use Tauri's secure storage for sensitive data (HF tokens)

---

## Performance Optimization

### 1. Bundle Size Optimization

**Target Sizes:**
- Tauri app bundle: ~15-20MB (vs Electron: ~100MB)
- Python sidecar: ~50-100MB (with ML models)
- Total: ~70-120MB (vs Electron equivalent: ~200MB+)

**Optimization Techniques:**
```bash
# Use PyInstaller with UPX compression
pyinstaller --onefile --upx-dir=/path/to/upx localtranscribe

# Exclude unnecessary Python modules
# - matplotlib (if not used for GUI)
# - jupyter, ipython
# - dev dependencies

# Use Nuitka for even smaller binaries (alternative to PyInstaller)
nuitka --onefile --standalone localtranscribe
```

### 2. Memory Optimization

- **Lazy Loading**: Load ML models only when needed
- **Streaming**: Process audio in chunks for large files
- **Web Workers**: Move audio analysis to separate thread

### 3. Startup Time Optimization

**Target**: <1 second cold start
- Pre-load critical components
- Defer non-essential initializations
- Use SvelteKit's code splitting

---

## Testing Strategy

### 1. Unit Tests (Rust)
```bash
cd src-tauri
cargo test
```

### 2. Integration Tests (TypeScript)
```bash
npm run test:integration
```

### 3. E2E Tests (Playwright)
```bash
npm run test:e2e
```

### 4. Manual Testing Checklist

- [ ] File selection and validation
- [ ] Audio quality analysis
- [ ] Processing with different models
- [ ] Progress tracking accuracy
- [ ] Result viewing and export
- [ ] Batch processing
- [ ] Settings persistence
- [ ] Error handling and recovery
- [ ] Drag & drop functionality
- [ ] Keyboard shortcuts
- [ ] Screen reader accessibility
- [ ] Dark/light theme switching

---

## Migration from CLI to GUI

### User Migration Path

1. **Existing CLI users**: Can continue using CLI
2. **GUI-only users**: Install GUI app, Python CLI bundled automatically
3. **Hybrid users**: CLI and GUI can coexist, share config files

### Configuration Compatibility

```
~/.localtranscribe/
├── config.yaml        # Shared between CLI and GUI
├── .env              # Shared HuggingFace token
├── gui/              # GUI-specific settings
│   ├── window-state.json
│   ├── recent-files.json
│   └── preferences.json
└── cache/            # Shared model cache
```

---

## Development Roadmap

### MVP (v1.0) - 4 weeks
- [x] Project setup and configuration
- [x] Python sidecar integration
- [x] Dashboard screen
- [x] File browser
- [x] Audio analysis
- [x] Basic processing with progress
- [x] Results viewer
- [x] Settings panel

### v1.1 - 2 weeks
- [ ] Batch processing UI
- [ ] Advanced audio visualization
- [ ] Export format selection
- [ ] Recent files management
- [ ] Keyboard shortcuts

### v1.2 - 2 weeks
- [ ] Real-time waveform during processing
- [ ] Quality presets UI
- [ ] Speaker labeling interface
- [ ] Proofreading integration

### v2.0 - Future
- [ ] Auto-updates
- [ ] Plugin system
- [ ] Multi-language UI
- [ ] Cloud sync (optional)
- [ ] Mobile companion app

---

## FAQ & Troubleshooting

### Q: Why Tauri over Electron?
**A**: Tauri is 10x smaller, 8x less memory, 4x faster startup, and uses native webview. Perfect for local tools like LocalTranscribe.

### Q: Will this work offline?
**A**: Yes! 100% offline. Python CLI is bundled, no internet required.

### Q: How do I debug the Python subprocess?
**A**: Enable verbose logging in Python CLI, check Tauri's stdout/stderr capture.

### Q: Can I use existing Python virtual environment?
**A**: For development yes, but production uses bundled Python executable.

### Q: What about GPU acceleration?
**A**: Python sidecar inherits system GPU access (CUDA/MPS/ROCm).

### Q: How do I update the Python CLI?
**A**: Rebuild Python sidecar, copy to `src-tauri/binaries/`, rebuild Tauri app.

### Q: Code signing for production?
**A**: For production distribution, follow [Tauri signing guide](https://v2.tauri.app/distribute/sign/). For testing, use `--no-signing`.

---

## Next Steps: Implementation Guide

### Week 1: Foundation
1. Install prerequisites (Rust, Node.js)
2. Initialize Tauri + SvelteKit project
3. Configure SPA mode and Tailwind
4. Build Python sidecar with PyInstaller
5. Test basic Rust-Python IPC

### Week 2: Core Features
1. Implement dashboard screen
2. Build file browser
3. Create audio analysis UI
4. Integrate quality check
5. Test file selection flow

### Week 3: Processing
1. Implement processing screen
2. Add progress tracking
3. Build results viewer
4. Create export functionality
5. Test end-to-end flow

### Week 4: Polish & Deploy
1. Add settings panel
2. Implement batch processing
3. Fix bugs and optimize
4. Build installers (unsigned)
5. Create distribution package

---

## Conclusion

This plan provides a **production-ready architecture** for LocalTranscribe GUI using modern, lightweight technologies. The Tauri + SvelteKit + Python subprocess approach offers:

✅ **Minimal bundle size** (~70-120MB vs Electron's 200MB+)
✅ **Fast performance** (<1s startup, native webview)
✅ **Cross-platform** (Windows, macOS, Linux)
✅ **No code changes to existing CLI** (pure wrapping)
✅ **Easy distribution** (no signing required for testing)
✅ **Future-proof** (modern stack, active community)

**Ready to begin implementation!** Follow the week-by-week guide above, and refer to the research sources for detailed documentation on each component.

---

**Research Sources Summary:**
- [Tauri vs Electron Comparison](https://www.levminer.com/blog/tauri-vs-electron)
- [Tauri SvelteKit Guide](https://v2.tauri.app/start/frontend/sveltekit/)
- [Tauri Sidecar Documentation](https://v2.tauri.app/develop/sidecar/)
- [Python Sidecar Example](https://github.com/dieharders/example-tauri-v2-python-server-sidecar)
- [Tauri IPC Protocol](https://v2.tauri.app/concept/inter-process-communication/)
- [Tauri No-Signing Flag](https://github.com/tauri-apps/tauri/issues/11626)
- [Tauri Distribution Guide](https://v2.tauri.app/distribute/)
