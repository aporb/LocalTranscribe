<script lang="ts">
  import { uiState, configState, transcriptionState } from '$lib/stores.svelte';
  import { runTranscription, onTranscriptionProgress, getModelDescription, getPresetDescription, type ModelSize, type Preset, type OutputFormat } from '$lib/api';
  import { open } from '@tauri-apps/plugin-dialog';

  let error = $state<string | null>(null);
  let progressUnlisten: (() => void) | null = null;

  function selectPreset(preset: Preset) {
    configState.applyPreset(preset);
  }

  function toggleFormat(format: OutputFormat) {
    const index = configState.selectedFormats.indexOf(format);
    if (index >= 0) {
      configState.selectedFormats.splice(index, 1);
    } else {
      configState.selectedFormats.push(format);
    }
  }

  async function selectOutputDirectory() {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
      });
      if (selected) {
        const path = Array.isArray(selected) ? selected[0] : selected;
        configState.outputDir = path;
      }
    } catch (error) {
      console.error('Failed to select directory:', error);
    }
  }

  async function startTranscription() {
    if (!uiState.selectedFile) {
      error = 'No file selected';
      return;
    }

    if (configState.selectedFormats.length === 0) {
      error = 'Please select at least one output format';
      return;
    }

    error = null;
    transcriptionState.start(uiState.selectedFile);
    uiState.navigateTo('processing');

    try {
      // Listen for progress updates
      progressUnlisten = await onTranscriptionProgress((progress) => {
        transcriptionState.updateProgress(progress);
      });

      // Run transcription
      const options = configState.toTranscriptionOptions(uiState.selectedFile);
      const result = await runTranscription(options);

      transcriptionState.complete(result);
      uiState.navigateTo('results');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Transcription failed';
      transcriptionState.fail(errorMsg);
    } finally {
      if (progressUnlisten) {
        progressUnlisten();
        progressUnlisten = null;
      }
    }
  }

  function getFormatIcon(format: OutputFormat): string {
    const icons: Record<OutputFormat, string> = {
      txt: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      json: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4',
      srt: 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z',
      vtt: 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z',
      md: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
      html: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4',
      docx: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    };
    return icons[format];
  }

  function getFormatName(format: OutputFormat): string {
    const names: Record<OutputFormat, string> = {
      txt: 'Plain Text',
      json: 'JSON',
      srt: 'SRT Subtitle',
      vtt: 'WebVTT',
      md: 'Markdown',
      html: 'HTML',
      docx: 'Word Doc',
    };
    return names[format];
  }

  function getFileName(path: string): string {
    return path.split('/').pop() || path.split('\\').pop() || path;
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-950">
  <!-- Header -->
  <header class="border-b border-slate-200/50 dark:border-slate-700/50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl sticky top-0 z-10">
    <div class="max-w-7xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button
            onclick={() => uiState.navigateTo('quality-check')}
            class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
            <svg class="w-5 h-5 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <h1 class="text-xl font-bold text-slate-900 dark:text-white">Configuration</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400">Customize your transcription settings</p>
          </div>
        </div>

        <!-- Progress Steps -->
        <div class="hidden md:flex items-center gap-2">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span class="text-xs text-slate-600 dark:text-slate-400">Select</span>
          </div>
          <div class="w-8 h-0.5 bg-green-500"></div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span class="text-xs text-slate-600 dark:text-slate-400">Quality</span>
          </div>
          <div class="w-8 h-0.5 bg-indigo-500"></div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center">
              <span class="text-xs font-semibold text-white">3</span>
            </div>
            <span class="text-xs font-medium text-slate-900 dark:text-white">Configure</span>
          </div>
          <div class="w-8 h-0.5 bg-slate-300 dark:bg-slate-600"></div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center">
              <span class="text-xs font-semibold text-slate-600 dark:text-slate-400">4</span>
            </div>
            <span class="text-xs text-slate-600 dark:text-slate-400">Process</span>
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-6 py-8">
    <div class="grid lg:grid-cols-3 gap-8">
      <!-- Left Column - Settings -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Model Selection -->
        <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Whisper Model</h2>
              <p class="text-sm text-slate-600 dark:text-slate-400">Choose accuracy vs speed tradeoff</p>
            </div>
          </div>

          <div class="grid grid-cols-5 gap-3">
            {#each configState.availableModels as model}
              <button
                onclick={() => configState.selectedModel = model}
                class="group relative p-4 rounded-xl border-2 transition-all duration-300 hover:scale-105 {configState.selectedModel === model
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 shadow-lg shadow-indigo-500/20'
                  : 'border-slate-200 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 hover:border-indigo-300'}">
                <div class="text-center">
                  <div class="text-sm font-semibold text-slate-900 dark:text-white mb-1 capitalize">{model}</div>
                  <div class="text-xs text-slate-600 dark:text-slate-400">
                    {#if model === 'tiny'}~1GB{/if}
                    {#if model === 'base'}~1.5GB{/if}
                    {#if model === 'small'}~2GB{/if}
                    {#if model === 'medium'}~5GB{/if}
                    {#if model === 'large'}~10GB{/if}
                  </div>
                </div>
                {#if configState.selectedModel === model}
                  <div class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center shadow-lg">
                    <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                {/if}
              </button>
            {/each}
          </div>

          <div class="mt-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-700/50">
            <p class="text-sm text-slate-700 dark:text-slate-300">{getModelDescription(configState.selectedModel)}</p>
          </div>
        </div>

        <!-- Presets -->
        <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Quick Presets</h2>
              <p class="text-sm text-slate-600 dark:text-slate-400">Optimized settings for common use cases</p>
            </div>
          </div>

          <div class="grid md:grid-cols-3 gap-3">
            {#each configState.availablePresets as preset}
              <button
                onclick={() => selectPreset(preset)}
                class="group p-4 rounded-xl border-2 transition-all duration-300 hover:scale-105 text-left {configState.selectedPreset === preset
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 shadow-lg shadow-indigo-500/20'
                  : 'border-slate-200 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 hover:border-indigo-300'}">
                <div class="font-semibold text-slate-900 dark:text-white mb-1 capitalize">{preset}</div>
                <div class="text-xs text-slate-600 dark:text-slate-400">{getPresetDescription(preset)}</div>
              </button>
            {/each}
          </div>
        </div>

        <!-- Speaker Settings -->
        <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-green-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Speaker Diarization</h2>
              <p class="text-sm text-slate-600 dark:text-slate-400">Identify and label different speakers</p>
            </div>
          </div>

          <div class="space-y-4">
            <label class="flex items-center gap-3 cursor-pointer group">
              <input
                type="checkbox"
                bind:checked={configState.skipDiarization}
                class="w-5 h-5 rounded border-slate-300 dark:border-slate-600 text-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-0" />
              <span class="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">Skip speaker identification (faster)</span>
            </label>

            {#if !configState.skipDiarization}
              <div class="space-y-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-700/50">
                <div>
                  <label class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Number of Speakers</span>
                    <span class="text-sm font-semibold text-indigo-600 dark:text-indigo-400">{configState.numSpeakers || 'Auto'}</span>
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={configState.numSpeakers || 0}
                    oninput={(e) => configState.numSpeakers = e.currentTarget.value === '0' ? undefined : parseInt(e.currentTarget.value)}
                    class="w-full h-2 rounded-lg appearance-none bg-slate-200 dark:bg-slate-700 accent-indigo-600" />
                  <div class="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-1">
                    <span>Auto</span>
                    <span>10</span>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="flex items-center justify-between mb-2">
                      <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Min Speakers</span>
                      <span class="text-sm font-semibold text-indigo-600 dark:text-indigo-400">{configState.minSpeakers || 'None'}</span>
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="5"
                      value={configState.minSpeakers || 0}
                      oninput={(e) => configState.minSpeakers = e.currentTarget.value === '0' ? undefined : parseInt(e.currentTarget.value)}
                      class="w-full h-2 rounded-lg appearance-none bg-slate-200 dark:bg-slate-700 accent-indigo-600" />
                  </div>
                  <div>
                    <label class="flex items-center justify-between mb-2">
                      <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Max Speakers</span>
                      <span class="text-sm font-semibold text-indigo-600 dark:text-indigo-400">{configState.maxSpeakers || 'None'}</span>
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="20"
                      value={configState.maxSpeakers || 0}
                      oninput={(e) => configState.maxSpeakers = e.currentTarget.value === '0' ? undefined : parseInt(e.currentTarget.value)}
                      class="w-full h-2 rounded-lg appearance-none bg-slate-200 dark:bg-slate-700 accent-indigo-600" />
                  </div>
                </div>
              </div>
            {/if}
          </div>
        </div>

        <!-- Processing Options -->
        <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-lg shadow-orange-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Processing Options</h2>
              <p class="text-sm text-slate-600 dark:text-slate-400">Advanced transcription settings</p>
            </div>
          </div>

          <div class="space-y-4">
            <label class="flex items-center gap-3 cursor-pointer group">
              <input
                type="checkbox"
                bind:checked={configState.proofread}
                class="w-5 h-5 rounded border-slate-300 dark:border-slate-600 text-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-0" />
              <div class="flex-1">
                <div class="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">Enable AI Proofreading</div>
                <div class="text-xs text-slate-500 dark:text-slate-400">Fix common transcription errors and improve readability</div>
              </div>
            </label>

            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Language (Optional)</label>
              <input
                type="text"
                bind:value={configState.language}
                placeholder="Auto-detect"
                class="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">e.g., "en" for English, "es" for Spanish</p>
            </div>
          </div>
        </div>

        <!-- Output Formats -->
        <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center shadow-lg shadow-pink-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Output Formats</h2>
              <p class="text-sm text-slate-600 dark:text-slate-400">Select one or more export formats</p>
            </div>
          </div>

          <div class="grid md:grid-cols-4 gap-3">
            {#each configState.availableFormats as format}
              <button
                onclick={() => toggleFormat(format)}
                class="group p-3 rounded-xl border-2 transition-all duration-300 hover:scale-105 {configState.selectedFormats.includes(format)
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30 shadow-lg shadow-indigo-500/20'
                  : 'border-slate-200 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 hover:border-indigo-300'}">
                <div class="flex flex-col items-center text-center gap-2">
                  <svg class="w-8 h-8 {configState.selectedFormats.includes(format) ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400 dark:text-slate-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getFormatIcon(format)} />
                  </svg>
                  <span class="text-sm font-semibold text-slate-900 dark:text-white uppercase">{format}</span>
                  <span class="text-xs text-slate-600 dark:text-slate-400">{getFormatName(format)}</span>
                </div>
                {#if configState.selectedFormats.includes(format)}
                  <div class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center shadow-lg">
                    <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                {/if}
              </button>
            {/each}
          </div>

          {#if configState.selectedFormats.length === 0}
            <div class="mt-4 p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
              <p class="text-sm text-yellow-800 dark:text-yellow-200">⚠️ Please select at least one output format</p>
            </div>
          {/if}
        </div>

        <!-- Output Directory -->
        <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg shadow-cyan-500/30">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Output Directory</h2>
              <p class="text-sm text-slate-600 dark:text-slate-400">Where to save the transcription files</p>
            </div>
          </div>

          <button
            onclick={selectOutputDirectory}
            class="w-full p-4 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 hover:border-indigo-400 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20 transition-all duration-300 text-left group">
            {#if configState.outputDir}
              <div class="flex items-center gap-3">
                <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-slate-900 dark:text-white truncate">{configState.outputDir}</div>
                  <div class="text-xs text-slate-500 dark:text-slate-400">Click to change</div>
                </div>
              </div>
            {:else}
              <div class="flex items-center justify-center gap-2 text-slate-600 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <span class="text-sm font-medium">Same as audio file (default)</span>
              </div>
            {/if}
          </button>
        </div>
      </div>

      <!-- Right Column - Summary & Action -->
      <div class="space-y-6">
        <!-- Selected File Info -->
        {#if uiState.selectedFile}
          <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 sticky top-24">
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">Selected File</h3>
            <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-700/50">
              <div class="flex items-start gap-3 mb-4">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-400/20 dark:to-purple-400/20 flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-slate-900 dark:text-white text-sm break-words">{getFileName(uiState.selectedFile)}</div>
                  <div class="text-xs text-slate-500 dark:text-slate-400 mt-1 break-all">{uiState.selectedFile}</div>
                </div>
              </div>
            </div>

            <div class="mt-6 space-y-3">
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600 dark:text-slate-400">Model:</span>
                <span class="font-semibold text-slate-900 dark:text-white capitalize">{configState.selectedModel}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600 dark:text-slate-400">Preset:</span>
                <span class="font-semibold text-slate-900 dark:text-white capitalize">{configState.selectedPreset || 'Custom'}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600 dark:text-slate-400">Speakers:</span>
                <span class="font-semibold text-slate-900 dark:text-white">
                  {configState.skipDiarization ? 'Disabled' : configState.numSpeakers || 'Auto'}
                </span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600 dark:text-slate-400">Proofreading:</span>
                <span class="font-semibold {configState.proofread ? 'text-green-600 dark:text-green-400' : 'text-slate-500 dark:text-slate-400'}">
                  {configState.proofread ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600 dark:text-slate-400">Formats:</span>
                <span class="font-semibold text-slate-900 dark:text-white">{configState.selectedFormats.length}</span>
              </div>
            </div>

            {#if error}
              <div class="mt-6 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <p class="text-sm text-red-800 dark:text-red-200">{error}</p>
              </div>
            {/if}

            <button
              onclick={startTranscription}
              disabled={configState.selectedFormats.length === 0}
              class="mt-6 w-full group relative inline-flex items-center justify-center gap-3 px-6 py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:shadow-indigo-500/40 transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100">
              <svg class="w-5 h-5 group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Start Transcription
            </button>
          </div>
        {/if}
      </div>
    </div>
  </main>
</div>

<style>
  /* Custom range slider styling */
  input[type='range']::-webkit-slider-thumb {
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #6366f1;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
  }

  input[type='range']::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #6366f1;
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
  }

  input[type='range']::-webkit-slider-thumb:hover {
    background: #4f46e5;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.6);
  }

  input[type='range']::-moz-range-thumb:hover {
    background: #4f46e5;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.6);
  }
</style>
