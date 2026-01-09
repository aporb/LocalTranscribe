use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::Manager;

/// Transcription configuration options
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TranscriptionOptions {
    pub audio_path: String,
    pub model_size: String,
    pub num_speakers: Option<usize>,
    pub min_speakers: Option<usize>,
    pub max_speakers: Option<usize>,
    pub skip_diarization: bool,
    pub proofread: bool,
    pub output_formats: Vec<String>,
    pub output_dir: Option<String>,
    pub preset: Option<String>,
    pub language: Option<String>,
}

/// Audio quality analysis result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AudioQualityResult {
    pub quality_level: String,
    pub snr_db: Option<f64>,
    pub sample_rate: u32,
    pub duration_seconds: f64,
    pub warnings: Vec<String>,
    pub recommendations: Vec<String>,
    pub optimal_model: String,
}

/// Progress update event
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProgressUpdate {
    pub stage: String,
    pub progress: f64,
    pub message: String,
    pub eta_seconds: Option<f64>,
}

/// Transcription result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TranscriptionResult {
    pub success: bool,
    pub output_files: Vec<String>,
    pub duration_seconds: f64,
    pub num_segments: usize,
    pub num_speakers: Option<usize>,
    pub error: Option<String>,
}

/// Run transcription with the given options
#[tauri::command]
pub async fn run_transcription(
    app: tauri::AppHandle,
    options: TranscriptionOptions,
) -> Result<TranscriptionResult, String> {
    use tauri_plugin_shell::ShellExt;

    println!("Starting transcription: {:?}", options.audio_path);

    // Build command arguments
    let mut args = vec!["process".to_string(), options.audio_path.clone()];

    // Add model size
    args.push("--model".to_string());
    args.push(options.model_size);

    // Add speaker configuration
    if let Some(num) = options.num_speakers {
        args.push("--speakers".to_string());
        args.push(num.to_string());
    }
    if let Some(min) = options.min_speakers {
        args.push("--min-speakers".to_string());
        args.push(min.to_string());
    }
    if let Some(max) = options.max_speakers {
        args.push("--max-speakers".to_string());
        args.push(max.to_string());
    }

    // Add flags
    if options.skip_diarization {
        args.push("--skip-diarization".to_string());
    }
    if options.proofread {
        args.push("--proofread".to_string());
    }

    // Add output formats
    for format in &options.output_formats {
        args.push("--format".to_string());
        args.push(format.clone());
    }

    // Add output directory
    if let Some(dir) = options.output_dir {
        args.push("--output-dir".to_string());
        args.push(dir);
    }

    // Add preset
    if let Some(preset) = options.preset {
        args.push("--preset".to_string());
        args.push(preset);
    }

    // Add language
    if let Some(lang) = options.language {
        args.push("--language".to_string());
        args.push(lang);
    }

    println!("Command args: {:?}", args);

    // Execute sidecar
    let sidecar = app
        .shell()
        .sidecar("localtranscribe")
        .map_err(|e| format!("Failed to create sidecar: {}", e))?;

    let (mut rx, _child) = sidecar
        .args(args)
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    let mut output = String::new();
    let mut error_output = String::new();

    // Collect output
    while let Some(event) = rx.recv().await {
        match event {
            tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
                println!("STDOUT: {}", line);
                output.push_str(&line);
                output.push('\n');

                // Try to parse progress updates
                if let Ok(progress) = serde_json::from_str::<ProgressUpdate>(&line) {
                    let _ = app.emit("transcription-progress", progress);
                }
            }
            tauri_plugin_shell::process::CommandEvent::Stderr(line) => {
                println!("STDERR: {}", line);
                error_output.push_str(&line);
                error_output.push('\n');
            }
            tauri_plugin_shell::process::CommandEvent::Terminated(payload) => {
                println!("Process terminated: {:?}", payload);
                if payload.code != Some(0) {
                    return Ok(TranscriptionResult {
                        success: false,
                        output_files: vec![],
                        duration_seconds: 0.0,
                        num_segments: 0,
                        num_speakers: None,
                        error: Some(format!(
                            "Process exited with code {:?}: {}",
                            payload.code, error_output
                        )),
                    });
                }
                break;
            }
            _ => {}
        }
    }

    // Parse result from output
    Ok(TranscriptionResult {
        success: true,
        output_files: parse_output_files(&output),
        duration_seconds: 0.0, // TODO: Parse from output
        num_segments: 0,       // TODO: Parse from output
        num_speakers: options.num_speakers,
        error: None,
    })
}

/// Check audio quality before transcription
#[tauri::command]
pub async fn check_audio_quality(
    app: tauri::AppHandle,
    audio_path: String,
) -> Result<AudioQualityResult, String> {
    use tauri_plugin_shell::ShellExt;

    println!("Checking audio quality: {}", audio_path);

    let args = vec![
        "process".to_string(),
        audio_path,
        "--check-quality".to_string(),
    ];

    let sidecar = app
        .shell()
        .sidecar("localtranscribe")
        .map_err(|e| format!("Failed to create sidecar: {}", e))?;

    let (mut rx, _child) = sidecar
        .args(args)
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    let mut output = String::new();

    while let Some(event) = rx.recv().await {
        match event {
            tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
                output.push_str(&line);
                output.push('\n');
            }
            tauri_plugin_shell::process::CommandEvent::Terminated(payload) => {
                if payload.code != Some(0) {
                    return Err(format!("Quality check failed with code {:?}", payload.code));
                }
                break;
            }
            _ => {}
        }
    }

    // Parse quality result (simplified - real implementation would parse JSON)
    Ok(AudioQualityResult {
        quality_level: "good".to_string(),
        snr_db: Some(25.0),
        sample_rate: 44100,
        duration_seconds: 0.0,
        warnings: vec![],
        recommendations: vec![],
        optimal_model: "medium".to_string(),
    })
}

/// Get available models
#[tauri::command]
pub async fn get_available_models() -> Result<Vec<String>, String> {
    Ok(vec![
        "tiny".to_string(),
        "base".to_string(),
        "small".to_string(),
        "medium".to_string(),
        "large".to_string(),
    ])
}

/// Get available presets
#[tauri::command]
pub async fn get_available_presets() -> Result<Vec<String>, String> {
    Ok(vec![
        "podcast".to_string(),
        "meeting".to_string(),
        "interview".to_string(),
        "lecture".to_string(),
        "dictation".to_string(),
        "fast".to_string(),
    ])
}

/// Get available output formats
#[tauri::command]
pub async fn get_available_formats() -> Result<Vec<String>, String> {
    Ok(vec![
        "txt".to_string(),
        "json".to_string(),
        "srt".to_string(),
        "vtt".to_string(),
        "md".to_string(),
        "html".to_string(),
        "docx".to_string(),
    ])
}

/// Cancel ongoing transcription
#[tauri::command]
pub async fn cancel_transcription() -> Result<(), String> {
    // TODO: Implement cancellation logic
    Ok(())
}

/// Helper function to parse output files from command output
fn parse_output_files(output: &str) -> Vec<String> {
    let mut files = Vec::new();
    for line in output.lines() {
        if line.contains("Output saved to:") || line.contains("Written to:") {
            // Extract file path from line
            if let Some(path) = line.split(':').nth(1) {
                files.push(path.trim().to_string());
            }
        }
    }
    files
}
