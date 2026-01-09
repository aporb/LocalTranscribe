# LocalTranscribe GUI - Phase 1 Foundation Complete

**Date:** 2026-01-09
**Status:** Phase 1 of 4 Complete
**Next Steps:** Python Sidecar & Backend Integration (Phase 2)

---

## ✅ Phase 1: Foundation Setup (COMPLETE)

### 1.1 Prerequisites Installed ✅
- **Rust**: 1.91.1 (compatible with Tauri 2.0)
- **Node.js**: v22.21.1 (meets >= 20 requirement)
- **pnpm**: 10.25.0
- **PyInstaller**: 6.17.0 (for Python sidecar)

### 1.2 Project Structure Created ✅

```
LocalTranscribe/
├── localtranscribe/              # Python CLI (existing)
│   ├── cli/
│   ├── core/
│   ├── pipeline/
│   ├── formats/                  # Including new DOCX & HTML formats
│   └── utils/                    # Including audio quality analysis
│
└── localtranscribe-gui/          # NEW: Tauri + SvelteKit GUI
    ├── src/                      # SvelteKit frontend
    │   ├── app.css               # Tailwind CSS styles
    │   ├── app.html
    │   └── routes/
    │       ├── +layout.svelte    # Root layout with CSS import
    │       ├── +layout.ts
    │       └── +page.svelte      # Home page
    │
    ├── src-tauri/                # Rust backend
    │   ├── Cargo.toml
    │   ├── tauri.conf.json
    │   └── src/
    │       └── main.rs
    │
    ├── static/                   # Static assets
    ├── package.json              # Dependencies
    ├── svelte.config.js          # SPA mode configured
    ├── tailwind.config.js        # Tailwind configuration
    ├── postcss.config.js         # PostCSS with Tailwind
    ├── vite.config.js
    └── tsconfig.json
```

### 1.3 Configuration Complete ✅

**SvelteKit SPA Mode** (`svelte.config.js`):
```javascript
import adapter from "@sveltejs/adapter-static";

const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      fallback: "index.html",  // SPA mode for Tauri
    }),
  },
};
```

**Tailwind CSS** (`src/app.css`):
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Dependencies Installed**:
- Tauri 2.0 API & CLI
- SvelteKit 2.49.4 with static adapter
- Svelte 5.46.1
- Tailwind CSS 4.1.18
- PostCSS & Autoprefixer

### 1.4 Key Architecture Decisions ✅

1. **Tauri 2.0 over Electron**: 10x smaller bundle, 8x less memory, 4x faster startup
2. **SvelteKit in SPA mode**: Static export for Tauri compatibility
3. **Python as Sidecar**: Existing CLI remains unchanged, bundled with PyInstaller
4. **IPC Communication**: JSON-RPC between Rust and frontend
5. **No Code Signing**: Using `--no-signing` flag for development builds

---

## 🚧 Phase 2: Python Backend Integration (NEXT)

### 2.1 Python Sidecar with PyInstaller

**Create build script** (`scripts/build_sidecar.py`):
```python
#!/usr/bin/env python3
"""Build LocalTranscribe Python sidecar for Tauri."""

import PyInstaller.__main__
import sys
import platform

# Determine platform-specific binary name
system = platform.system().lower()
if system == "windows":
    binary_name = "localtranscribe.exe"
elif system == "darwin":
    binary_name = "localtranscribe-macos"
else:
    binary_name = "localtranscribe-linux"

PyInstaller.__main__.run([
    'localtranscribe/cli/main.py',
    '--name', binary_name,
    '--onefile',
    '--console',
    '--collect-all', 'localtranscribe',
    '--collect-all', 'torch',
    '--collect-all', 'pyannote',
    '--hidden-import', 'sklearn.utils._cython_blas',
    '--hidden-import', 'sklearn.neighbors.typedefs',
    '--hidden-import', 'sklearn.neighbors.quad_tree',
    '--hidden-import', 'sklearn.tree._utils',
    '--distpath', './src-tauri/binaries',
])
```

**Run build**:
```bash
cd /home/user/LocalTranscribe
python scripts/build_sidecar.py
```

### 2.2 Tauri Configuration for Sidecar

**Update** `src-tauri/tauri.conf.json`:
```json
{
  "bundle": {
    "externalBin": [
      "binaries/localtranscribe-linux",
      "binaries/localtranscribe-macos",
      "binaries/localtranscribe.exe"
    ]
  },
  "build": {
    "beforeBuildCommand": "pnpm build",
    "beforeDevCommand": "pnpm dev",
    "devUrl": "http://localhost:5173"
  }
}
```

### 2.3 Rust IPC Commands

**Create** `src-tauri/src/python_manager.rs`:
```rust
use std::process::{Command, Stdio};
use tauri::Manager;
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TranscriptionOptions {
    pub audio_path: String,
    pub model_size: String,
    pub num_speakers: Option<usize>,
    pub skip_diarization: bool,
    pub proofread: bool,
    pub output_formats: Vec<String>,
}

#[tauri::command]
pub async fn run_transcription(options: TranscriptionOptions) -> Result<String, String> {
    // Build command args
    let mut args = vec![
        "process".to_string(),
        options.audio_path,
        "--model".to_string(),
        options.model_size,
    ];

    if let Some(speakers) = options.num_speakers {
        args.push("--speakers".to_string());
        args.push(speakers.to_string());
    }

    if options.skip_diarization {
        args.push("--skip-diarization".to_string());
    }

    if options.proofread {
        args.push("--proofread".to_string());
    }

    for format in options.output_formats {
        args.push("--format".to_string());
        args.push(format);
    }

    // Execute sidecar
    let sidecar_command = tauri::api::process::Command::new_sidecar("localtranscribe")
        .map_err(|e| format!("Failed to create sidecar: {}", e))?;

    let (mut rx, _child) = sidecar_command
        .args(args)
        .spawn()
        .map_err(|e| format!("Failed to spawn: {}", e))?;

    let mut output = String::new();
    while let Some(event) = rx.recv().await {
        match event {
            tauri::api::process::CommandEvent::Stdout(line) => {
                output.push_str(&line);
                output.push('\n');
            }
            tauri::api::process::CommandEvent::Terminated(payload) => {
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

#[tauri::command]
pub async fn check_audio_quality(audio_path: String) -> Result<String, String> {
    let args = vec![
        "process".to_string(),
        audio_path,
        "--check-quality".to_string(),
    ];

    let sidecar_command = tauri::api::process::Command::new_sidecar("localtranscribe")
        .map_err(|e| format!("Failed to create sidecar: {}", e))?;

    let (mut rx, _child) = sidecar_command
        .args(args)
        .spawn()
        .map_err(|e| format!("Failed to spawn: {}", e))?;

    let mut output = String::new();
    while let Some(event) = rx.recv().await {
        match event {
            tauri::api::process::CommandEvent::Stdout(line) => {
                output.push_str(&line);
            }
            tauri::api::process::CommandEvent::Terminated(_) => break,
            _ => {}
        }
    }

    Ok(output)
}
```

**Register commands in** `src-tauri/src/main.rs`:
```rust
mod python_manager;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            python_manager::run_transcription,
            python_manager::check_audio_quality,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 2.4 Frontend Integration

**Create** `src/lib/api.ts`:
```typescript
import { invoke } from '@tauri-apps/api/core';

export interface TranscriptionOptions {
  audioPath: string;
  modelSize: 'tiny' | 'base' | 'small' | 'medium' | 'large';
  numSpeakers?: number;
  skipDiarization: boolean;
  proofread: boolean;
  outputFormats: string[];
}

export interface AudioQualityResult {
  qualityLevel: 'excellent' | 'good' | 'fair' | 'poor';
  snrDb: number;
  sampleRate: number;
  durationSeconds: number;
  warnings: string[];
  recommendations: string[];
  optimalModel: string;
}

export async function runTranscription(
  options: TranscriptionOptions
): Promise<string> {
  return await invoke('run_transcription', { options });
}

export async function checkAudioQuality(
  audioPath: string
): Promise<AudioQualityResult> {
  const result = await invoke('check_audio_quality', { audioPath });
  return JSON.parse(result as string);
}
```

---

## 📋 Phase 3: Frontend UI Components (TODO)

### 3.1 Main Dashboard
- Welcome screen
- Recent transcriptions list
- Quick start button
- Settings access

### 3.2 File Browser
- Audio file selector with drag-and-drop
- File type validation (mp3, wav, m4a, etc.)
- File info preview (duration, size)
- Multiple file selection for batch

### 3.3 Audio Quality Analysis Screen
- SNR visualization
- Quality level indicator
- Model recommendations
- Warnings and suggestions

### 3.4 Configuration Screen
- Model size selector
- Speaker diarization settings
- Output format checkboxes
- Proofreading options
- Advanced settings

### 3.5 Processing Screen
- Real-time progress tracking
- Stage indicators (validation → diarization → transcription)
- ETA calculation
- Cancel button

### 3.6 Results Viewer
- Transcript display with speaker labels
- Export options (TXT, JSON, SRT, VTT, MD, HTML, DOCX)
- Copy to clipboard
- Open output folder

---

## 🚀 Phase 4: Build & Distribution (TODO)

### 4.1 Platform-Specific Builds

**Linux**:
```bash
cd localtranscribe-gui
pnpm tauri build --no-signing
```

**macOS**:
```bash
pnpm tauri build --target universal-apple-darwin --no-signing
```

**Windows**:
```bash
pnpm tauri build --target x86_64-pc-windows-msvc --no-signing
```

### 4.2 Output Artifacts

- **Linux**: `.AppImage`, `.deb`
- **macOS**: `.dmg`, `.app`
- **Windows**: `.exe`, `.msi`

### 4.3 Distribution

For testing/development (no code signing required):
1. Build with `--no-signing` flag
2. Distribute via GitHub Releases
3. Users install with unsigned app warnings (expected for dev builds)

For production (future):
1. Obtain code signing certificates
2. Sign builds for each platform
3. Notarize macOS builds
4. Distribute via official channels

---

## 📦 Dependencies Summary

### Python (LocalTranscribe CLI)
- PyTorch 2.0+
- pyannote.audio 3.0+
- Whisper (faster-whisper, MLX, or original)
- Typer, Rich, Questionary (CLI framework)
- PyInstaller 6.17.0 (for sidecar)

### Rust (Tauri Backend)
- tauri 2.0
- tauri-plugin-dialog
- tauri-plugin-fs
- serde, serde_json

### TypeScript/Frontend (SvelteKit)
- SvelteKit 2.49.4
- Svelte 5.46.1
- @tauri-apps/api 2.9.1
- Tailwind CSS 4.1.18
- (TODO: shadcn-svelte or Flowbite for components)

---

## 🔧 Development Commands

### Start Development Server
```bash
cd localtranscribe-gui
pnpm tauri dev
```

### Build for Production
```bash
pnpm tauri build --no-signing
```

### Run Python CLI Directly
```bash
cd /home/user/LocalTranscribe
python -m localtranscribe.cli.main process <audio-file>
```

---

## 📝 Next Immediate Steps

1. **Create Python sidecar build script** (scripts/build_sidecar.py)
2. **Build Python executable** with PyInstaller
3. **Add Rust IPC commands** to src-tauri/src/python_manager.rs
4. **Update Tauri configuration** for sidecar binary
5. **Create TypeScript API wrapper** (src/lib/api.ts)
6. **Test basic IPC communication** between frontend and Python sidecar
7. **Begin UI component development** (Phase 3)

---

## ⚠️ Known Issues / Notes

1. **Linux Dependencies**: Tauri requires:
   - `libwebkit2gtk-4.1-dev`
   - `libgtk-3-dev`
   - `libayatana-appindicator3-dev`
   - `librsvg2-dev`

   Install on Ubuntu/Debian:
   ```bash
   sudo apt-get install libwebkit2gtk-4.1-dev libgtk-3-dev \
                        libayatana-appindicator3-dev librsvg2-dev
   ```

2. **Python Sidecar Size**: The bundled Python executable will be large (100-200MB) due to PyTorch and ML models. This is expected.

3. **First Run Setup**: Users will still need to configure HuggingFace token on first run (can be prompted via GUI).

4. **Model Downloads**: First transcription will download Whisper models (~1-5GB depending on size). Need to add download progress tracking in GUI.

---

## 📚 References

- [Tauri Documentation](https://v2.tauri.app/)
- [SvelteKit Documentation](https://svelte.dev/docs/kit)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [GUI Implementation Plan](./GUI_IMPLEMENTATION_PLAN.md)
- [Complete Implementation Summary](./COMPLETE_IMPLEMENTATION_SUMMARY.md)

---

**Status**: Foundation complete. Ready for Phase 2 (Backend Integration).
**Estimated Time for Phase 2**: 4-6 hours
**Estimated Time for Phase 3**: 8-12 hours
**Estimated Time for Phase 4**: 2-4 hours

**Total Estimated Remaining**: 14-22 hours to complete GUI
