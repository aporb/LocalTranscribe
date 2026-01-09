<script lang="ts">
  import { onMount } from 'svelte';
  import { uiState, audioQualityState, configState } from '$lib/stores.svelte';
  import { checkAudioQuality, type QualityLevel } from '$lib/api';

  let checking = $state(false);
  let error = $state<string | null>(null);

  onMount(async () => {
    if (uiState.selectedFile) {
      await runQualityCheck();
    }
  });

  async function runQualityCheck() {
    if (!uiState.selectedFile) return;

    checking = true;
    error = null;
    audioQualityState.start();

    try {
      const result = await checkAudioQuality(uiState.selectedFile);
      audioQualityState.complete(result);

      // Auto-apply recommended model
      if (result.optimalModel) {
        configState.selectedModel = result.optimalModel as any;
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to analyze audio quality';
      audioQualityState.fail(error);
    } finally {
      checking = false;
    }
  }

  function getQualityColor(level: QualityLevel): string {
    switch (level) {
      case 'excellent':
        return 'from-green-500 to-emerald-500';
      case 'good':
        return 'from-blue-500 to-cyan-500';
      case 'fair':
        return 'from-yellow-500 to-orange-500';
      case 'poor':
        return 'from-red-500 to-pink-500';
    }
  }

  function getQualityText(level: QualityLevel): string {
    switch (level) {
      case 'excellent':
        return 'Excellent Quality';
      case 'good':
        return 'Good Quality';
      case 'fair':
        return 'Fair Quality';
      case 'poor':
        return 'Poor Quality';
    }
  }

  function getQualityPercent(level: QualityLevel): number {
    switch (level) {
      case 'excellent':
        return 95;
      case 'good':
        return 75;
      case 'fair':
        return 50;
      case 'poor':
        return 25;
    }
  }

  function proceedToConfig() {
    uiState.navigateTo('config');
  }

  function goBack() {
    uiState.navigateTo('file-select');
  }

  const quality = $derived(audioQualityState.result);
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-950">
  <!-- Header -->
  <header class="border-b border-slate-200/50 dark:border-slate-700/50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl">
    <div class="max-w-5xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <button
          onclick={goBack}
          class="flex items-center gap-2 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>

        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
          <span class="text-sm font-medium text-slate-900 dark:text-white">Quality Analysis</span>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-5xl mx-auto px-6 py-12">
    <!-- Progress Steps -->
    <div class="mb-12">
      <div class="flex items-center justify-center gap-4">
        <div class="flex items-center gap-2 opacity-60">
          <div class="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-semibold">
            ✓
          </div>
          <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Select File</span>
        </div>

        <div class="w-16 h-0.5 bg-indigo-600"></div>

        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-center text-sm font-semibold shadow-lg shadow-indigo-500/30">
            2
          </div>
          <span class="text-sm font-medium text-slate-900 dark:text-white">Quality Check</span>
        </div>

        <div class="w-16 h-0.5 bg-slate-200 dark:bg-slate-700"></div>

        <div class="flex items-center gap-2 opacity-40">
          <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400 flex items-center justify-center text-sm font-semibold">
            3
          </div>
          <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Configure</span>
        </div>

        <div class="w-16 h-0.5 bg-slate-200 dark:bg-slate-700"></div>

        <div class="flex items-center gap-2 opacity-40">
          <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400 flex items-center justify-center text-sm font-semibold">
            4
          </div>
          <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Process</span>
        </div>
      </div>
    </div>

    {#if checking}
      <!-- Loading State -->
      <div class="flex flex-col items-center justify-center py-20">
        <div class="w-32 h-32 rounded-full bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-400/20 dark:to-purple-400/20 flex items-center justify-center mb-6 animate-pulse">
          <svg class="w-16 h-16 text-indigo-600 dark:text-indigo-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        <h3 class="text-2xl font-semibold text-slate-900 dark:text-white mb-2">Analyzing Audio Quality...</h3>
        <p class="text-slate-600 dark:text-slate-400">This may take a few moments</p>
      </div>
    {:else if error}
      <!-- Error State -->
      <div class="bg-red-50/50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded-2xl p-8 text-center">
        <div class="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-red-900 dark:text-red-100 mb-2">Analysis Failed</h3>
        <p class="text-red-700 dark:text-red-300 mb-6">{error}</p>
        <button
          onclick={runQualityCheck}
          class="px-6 py-3 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold transition-colors">
          Try Again
        </button>
      </div>
    {:else if quality}
      <!-- Quality Results -->
      <div class="space-y-8">
        <!-- Quality Meter -->
        <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-3xl border border-slate-200/50 dark:border-slate-700/50 p-12">
          <div class="flex flex-col items-center">
            <!-- Circular Progress -->
            <div class="relative w-64 h-64 mb-8">
              <svg class="transform -rotate-90 w-64 h-64">
                <circle
                  cx="128"
                  cy="128"
                  r="120"
                  stroke="currentColor"
                  stroke-width="16"
                  fill="transparent"
                  class="text-slate-200 dark:text-slate-700"
                />
                <circle
                  cx="128"
                  cy="128"
                  r="120"
                  stroke="url(#gradient)"
                  stroke-width="16"
                  fill="transparent"
                  stroke-linecap="round"
                  class="transition-all duration-1000 ease-out"
                  style="stroke-dasharray: {2 * Math.PI * 120}; stroke-dashoffset: {2 * Math.PI * 120 * (1 - getQualityPercent(quality.qualityLevel) / 100)}"
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" class="stop-color-start" />
                    <stop offset="100%" class="stop-color-end" />
                  </linearGradient>
                </defs>
              </svg>

              <!-- Center Content -->
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <div class="w-20 h-20 rounded-full bg-gradient-to-br {getQualityColor(quality.qualityLevel)} flex items-center justify-center mb-3 shadow-xl">
                  <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p class="text-3xl font-bold text-slate-900 dark:text-white mb-1">{getQualityPercent(quality.qualityLevel)}%</p>
                <p class="text-sm font-medium text-slate-600 dark:text-slate-400">{getQualityText(quality.qualityLevel)}</p>
              </div>
            </div>

            <h3 class="text-2xl font-semibold text-slate-900 dark:text-white mb-2">{getQualityText(quality.qualityLevel)}</h3>
            <p class="text-slate-600 dark:text-slate-400 text-center max-w-md">
              {#if quality.qualityLevel === 'excellent'}
                Your audio has excellent quality for transcription. Expect highly accurate results.
              {:else if quality.qualityLevel === 'good'}
                Your audio has good quality. Transcription should work well with minor potential errors.
              {:else if quality.qualityLevel === 'fair'}
                Your audio has fair quality. Consider using a larger model for better accuracy.
              {:else}
                Your audio has poor quality. Results may be less accurate. Consider preprocessing or using the large model.
              {/if}
            </p>
          </div>
        </div>

        <!-- Metrics Grid -->
        <div class="grid md:grid-cols-3 gap-6">
          <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 rounded-lg bg-blue-500/10 dark:bg-blue-400/20 flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
              </div>
              <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Signal-to-Noise</span>
            </div>
            <p class="text-3xl font-bold text-slate-900 dark:text-white">
              {quality.snrDb ? `${quality.snrDb.toFixed(1)} dB` : 'N/A'}
            </p>
          </div>

          <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 rounded-lg bg-purple-500/10 dark:bg-purple-400/20 flex items-center justify-center">
                <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Sample Rate</span>
            </div>
            <p class="text-3xl font-bold text-slate-900 dark:text-white">{(quality.sampleRate / 1000).toFixed(1)} kHz</p>
          </div>

          <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 rounded-lg bg-green-500/10 dark:bg-green-400/20 flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Duration</span>
            </div>
            <p class="text-3xl font-bold text-slate-900 dark:text-white">
              {Math.floor(quality.durationSeconds / 60)}:{Math.floor(quality.durationSeconds % 60).toString().padStart(2, '0')}
            </p>
          </div>
        </div>

        <!-- Warnings -->
        {#if quality.warnings.length > 0}
          <div class="bg-yellow-50/50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800 rounded-2xl p-6">
            <div class="flex items-start gap-3 mb-4">
              <div class="w-10 h-10 rounded-lg bg-yellow-500/10 dark:bg-yellow-400/20 flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">Warnings</h4>
                <ul class="space-y-2">
                  {#each quality.warnings as warning}
                    <li class="flex items-start gap-2 text-sm text-yellow-800 dark:text-yellow-200">
                      <span class="text-yellow-500 mt-0.5">•</span>
                      <span>{warning}</span>
                    </li>
                  {/each}
                </ul>
              </div>
            </div>
          </div>
        {/if}

        <!-- Recommendations -->
        {#if quality.recommendations.length > 0}
          <div class="bg-blue-50/50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-2xl p-6">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-lg bg-blue-500/10 dark:bg-blue-400/20 flex items-center justify-center flex-shrink-0">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div class="flex-1">
                <h4 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">Recommendations</h4>
                <ul class="space-y-2">
                  {#each quality.recommendations as recommendation}
                    <li class="flex items-start gap-2 text-sm text-blue-800 dark:text-blue-200">
                      <span class="text-blue-500 mt-0.5">•</span>
                      <span>{recommendation}</span>
                    </li>
                  {/each}
                </ul>
                {#if quality.optimalModel}
                  <div class="mt-4 p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                    <p class="text-sm text-blue-900 dark:text-blue-100">
                      <strong>Suggested model:</strong> {quality.optimalModel} (automatically applied)
                    </p>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/if}

        <!-- Action Buttons -->
        <div class="flex items-center gap-4">
          <button
            onclick={goBack}
            class="px-6 py-3 rounded-xl bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white font-semibold transition-colors">
            Choose Different File
          </button>

          <button
            onclick={proceedToConfig}
            class="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 transition-all duration-300 hover:scale-105">
            Continue to Configuration
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>
    {/if}
  </main>
</div>

<style>
  .stop-color-start {
    stop-color: rgb(99, 102, 241);
  }
  .stop-color-end {
    stop-color: rgb(168, 85, 247);
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
