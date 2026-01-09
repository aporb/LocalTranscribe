/**
 * LocalTranscribe API - TypeScript wrapper for Tauri commands
 * Provides type-safe access to backend transcription functionality
 */

import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';

// ============================================================================
// Type Definitions
// ============================================================================

export type ModelSize = 'tiny' | 'base' | 'small' | 'medium' | 'large';
export type Preset = 'podcast' | 'meeting' | 'interview' | 'lecture' | 'dictation' | 'fast';
export type OutputFormat = 'txt' | 'json' | 'srt' | 'vtt' | 'md' | 'html' | 'docx';
export type QualityLevel = 'excellent' | 'good' | 'fair' | 'poor';

export interface TranscriptionOptions {
  audioPath: string;
  modelSize: ModelSize;
  numSpeakers?: number;
  minSpeakers?: number;
  maxSpeakers?: number;
  skipDiarization: boolean;
  proofread: boolean;
  outputFormats: OutputFormat[];
  outputDir?: string;
  preset?: Preset;
  language?: string;
}

export interface AudioQualityResult {
  qualityLevel: QualityLevel;
  snrDb: number | null;
  sampleRate: number;
  durationSeconds: number;
  warnings: string[];
  recommendations: string[];
  optimalModel: ModelSize;
}

export interface ProgressUpdate {
  stage: string;
  progress: number; // 0.0 to 1.0
  message: string;
  etaSeconds: number | null;
}

export interface TranscriptionResult {
  success: boolean;
  outputFiles: string[];
  durationSeconds: number;
  numSegments: number;
  numSpeakers: number | null;
  error: string | null;
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Run transcription with the specified options
 */
export async function runTranscription(
  options: TranscriptionOptions
): Promise<TranscriptionResult> {
  try {
    const result = await invoke<TranscriptionResult>('run_transcription', {
      options,
    });
    return result;
  } catch (error) {
    throw new Error(`Transcription failed: ${error}`);
  }
}

/**
 * Analyze audio quality before transcription
 */
export async function checkAudioQuality(
  audioPath: string
): Promise<AudioQualityResult> {
  try {
    const result = await invoke<AudioQualityResult>('check_audio_quality', {
      audioPath,
    });
    return result;
  } catch (error) {
    throw new Error(`Quality check failed: ${error}`);
  }
}

/**
 * Get list of available Whisper models
 */
export async function getAvailableModels(): Promise<ModelSize[]> {
  try {
    return await invoke<ModelSize[]>('get_available_models');
  } catch (error) {
    throw new Error(`Failed to get models: ${error}`);
  }
}

/**
 * Get list of available presets
 */
export async function getAvailablePresets(): Promise<Preset[]> {
  try {
    return await invoke<Preset[]>('get_available_presets');
  } catch (error) {
    throw new Error(`Failed to get presets: ${error}`);
  }
}

/**
 * Get list of available output formats
 */
export async function getAvailableFormats(): Promise<OutputFormat[]> {
  try {
    return await invoke<OutputFormat[]>('get_available_formats');
  } catch (error) {
    throw new Error(`Failed to get formats: ${error}`);
  }
}

/**
 * Cancel ongoing transcription
 */
export async function cancelTranscription(): Promise<void> {
  try {
    await invoke('cancel_transcription');
  } catch (error) {
    throw new Error(`Failed to cancel: ${error}`);
  }
}

/**
 * Listen for transcription progress updates
 * Returns an unsubscribe function
 */
export async function onTranscriptionProgress(
  callback: (progress: ProgressUpdate) => void
): Promise<() => void> {
  const unlisten = await listen<ProgressUpdate>('transcription-progress', (event) => {
    callback(event.payload);
  });
  return unlisten;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Format duration in seconds to human-readable string
 */
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

/**
 * Get quality level color for UI display
 */
export function getQualityColor(level: QualityLevel): string {
  switch (level) {
    case 'excellent':
      return 'text-green-600 dark:text-green-400';
    case 'good':
      return 'text-blue-600 dark:text-blue-400';
    case 'fair':
      return 'text-yellow-600 dark:text-yellow-400';
    case 'poor':
      return 'text-red-600 dark:text-red-400';
  }
}

/**
 * Get model size description
 */
export function getModelDescription(model: ModelSize): string {
  const descriptions: Record<ModelSize, string> = {
    tiny: 'Fastest, lowest accuracy (~1GB RAM)',
    base: 'Fast, moderate accuracy (~1.5GB RAM)',
    small: 'Balanced speed/accuracy (~2GB RAM)',
    medium: 'High accuracy (~5GB RAM)',
    large: 'Highest accuracy (~10GB RAM)',
  };
  return descriptions[model];
}

/**
 * Get preset description
 */
export function getPresetDescription(preset: Preset): string {
  const descriptions: Record<Preset, string> = {
    podcast: 'Optimized for podcast/interview with 2 speakers',
    meeting: 'Multi-speaker meeting transcription',
    interview: 'One-on-one interview format',
    lecture: 'Single speaker lecture or presentation',
    dictation: 'Single speaker dictation with high accuracy',
    fast: 'Fast transcription without diarization',
  };
  return descriptions[preset];
}

/**
 * Get output format display name
 */
export function getFormatDisplayName(format: OutputFormat): string {
  const names: Record<OutputFormat, string> = {
    txt: 'Plain Text (.txt)',
    json: 'JSON (.json)',
    srt: 'SubRip Subtitle (.srt)',
    vtt: 'WebVTT Subtitle (.vtt)',
    md: 'Markdown (.md)',
    html: 'HTML Document (.html)',
    docx: 'Word Document (.docx)',
  };
  return names[format];
}
