/**
 * Application State Management using Svelte 5 Runes
 * Modern reactive state with the new $state rune system
 */

import type {
  TranscriptionOptions,
  TranscriptionResult,
  AudioQualityResult,
  ProgressUpdate,
  ModelSize,
  Preset,
  OutputFormat,
} from './api';

// ============================================================================
// Transcription State
// ============================================================================

class TranscriptionState {
  isTranscribing = $state(false);
  currentFile = $state<string | null>(null);
  progress = $state<ProgressUpdate | null>(null);
  result = $state<TranscriptionResult | null>(null);
  error = $state<string | null>(null);

  reset() {
    this.isTranscribing = false;
    this.currentFile = null;
    this.progress = null;
    this.result = null;
    this.error = null;
  }

  start(file: string) {
    this.reset();
    this.isTranscribing = true;
    this.currentFile = file;
  }

  updateProgress(progress: ProgressUpdate) {
    this.progress = progress;
  }

  complete(result: TranscriptionResult) {
    this.isTranscribing = false;
    this.result = result;
  }

  fail(error: string) {
    this.isTranscribing = false;
    this.error = error;
  }
}

export const transcriptionState = new TranscriptionState();

// ============================================================================
// Configuration State
// ============================================================================

class ConfigState {
  // Model settings
  selectedModel = $state<ModelSize>('medium');
  selectedPreset = $state<Preset | null>(null);

  // Speaker settings
  numSpeakers = $state<number | undefined>(undefined);
  minSpeakers = $state<number | undefined>(undefined);
  maxSpeakers = $state<number | undefined>(undefined);
  skipDiarization = $state(false);

  // Processing options
  proofread = $state(true);
  language = $state<string | undefined>(undefined);

  // Output settings
  selectedFormats = $state<OutputFormat[]>(['txt', 'json', 'srt']);
  outputDir = $state<string | undefined>(undefined);

  // Available options
  availableModels = $state<ModelSize[]>([
    'tiny',
    'base',
    'small',
    'medium',
    'large',
  ]);
  availablePresets = $state<Preset[]>([
    'podcast',
    'meeting',
    'interview',
    'lecture',
    'dictation',
    'fast',
  ]);
  availableFormats = $state<OutputFormat[]>([
    'txt',
    'json',
    'srt',
    'vtt',
    'md',
    'html',
    'docx',
  ]);

  toTranscriptionOptions(audioPath: string): TranscriptionOptions {
    return {
      audioPath,
      modelSize: this.selectedModel,
      numSpeakers: this.numSpeakers,
      minSpeakers: this.minSpeakers,
      maxSpeakers: this.maxSpeakers,
      skipDiarization: this.skipDiarization,
      proofread: this.proofread,
      outputFormats: this.selectedFormats,
      outputDir: this.outputDir,
      preset: this.selectedPreset || undefined,
      language: this.language,
    };
  }

  applyPreset(preset: Preset) {
    this.selectedPreset = preset;

    switch (preset) {
      case 'podcast':
        this.numSpeakers = 2;
        this.skipDiarization = false;
        this.proofread = true;
        this.selectedFormats = ['md', 'json', 'srt'];
        this.selectedModel = 'medium';
        break;
      case 'meeting':
        this.numSpeakers = undefined;
        this.minSpeakers = 2;
        this.maxSpeakers = 10;
        this.skipDiarization = false;
        this.proofread = true;
        this.selectedFormats = ['txt', 'docx'];
        this.selectedModel = 'medium';
        break;
      case 'interview':
        this.numSpeakers = 2;
        this.skipDiarization = false;
        this.proofread = true;
        this.selectedFormats = ['txt', 'json'];
        this.selectedModel = 'medium';
        break;
      case 'lecture':
        this.numSpeakers = 1;
        this.skipDiarization = true;
        this.proofread = true;
        this.selectedFormats = ['txt', 'md'];
        this.selectedModel = 'medium';
        break;
      case 'dictation':
        this.numSpeakers = 1;
        this.skipDiarization = true;
        this.proofread = true;
        this.selectedFormats = ['txt', 'docx'];
        this.selectedModel = 'large';
        break;
      case 'fast':
        this.numSpeakers = undefined;
        this.skipDiarization = true;
        this.proofread = false;
        this.selectedFormats = ['txt'];
        this.selectedModel = 'base';
        break;
    }
  }
}

export const configState = new ConfigState();

// ============================================================================
// Audio Quality State
// ============================================================================

class AudioQualityState {
  isChecking = $state(false);
  result = $state<AudioQualityResult | null>(null);
  error = $state<string | null>(null);

  reset() {
    this.isChecking = false;
    this.result = null;
    this.error = null;
  }

  start() {
    this.reset();
    this.isChecking = true;
  }

  complete(result: AudioQualityResult) {
    this.isChecking = false;
    this.result = result;
  }

  fail(error: string) {
    this.isChecking = false;
    this.error = error;
  }
}

export const audioQualityState = new AudioQualityState();

// ============================================================================
// UI State
// ============================================================================

class UIState {
  // Theme
  darkMode = $state(false);

  // Current view/screen
  currentView = $state<
    | 'home'
    | 'file-select'
    | 'quality-check'
    | 'config'
    | 'processing'
    | 'results'
  >('home');

  // Selected file
  selectedFile = $state<string | null>(null);

  // Modal states
  settingsModalOpen = $state(false);
  aboutModalOpen = $state(false);

  // Sidebar state
  sidebarCollapsed = $state(false);

  navigateTo(
    view:
      | 'home'
      | 'file-select'
      | 'quality-check'
      | 'config'
      | 'processing'
      | 'results'
  ) {
    this.currentView = view;
  }

  selectFile(file: string) {
    this.selectedFile = file;
    this.navigateTo('quality-check');
  }

  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    if (typeof document !== 'undefined') {
      if (this.darkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  }
}

export const uiState = new UIState();

// ============================================================================
// Recent Files State
// ============================================================================

interface RecentFile {
  path: string;
  timestamp: number;
  result?: TranscriptionResult;
}

class RecentFilesState {
  files = $state<RecentFile[]>([]);

  addFile(path: string, result?: TranscriptionResult) {
    const existing = this.files.findIndex((f) => f.path === path);
    if (existing >= 0) {
      this.files.splice(existing, 1);
    }

    this.files.unshift({
      path,
      timestamp: Date.now(),
      result,
    });

    // Keep only last 10
    if (this.files.length > 10) {
      this.files = this.files.slice(0, 10);
    }

    // TODO: Persist to localStorage
  }

  clear() {
    this.files = [];
  }
}

export const recentFilesState = new RecentFilesState();
