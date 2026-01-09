<script lang="ts">
  import { onDestroy } from 'svelte';
  import { uiState, transcriptionState } from '$lib/stores.svelte';
  import { cancelTranscription } from '$lib/api';

  let showCancelConfirm = $state(false);
  let cancelling = $state(false);

  const progress = $derived(transcriptionState.progress);
  const currentFile = $derived(transcriptionState.currentFile);
  const error = $derived(transcriptionState.error);

  // Stage icons and colors
  function getStageIcon(stage: string): string {
    const icons: Record<string, string> = {
      'loading': 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
      'transcribing': 'M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z',
      'diarization': 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
      'proofreading': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      'exporting': 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4',
      'complete': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    };
    return icons[stage.toLowerCase()] || icons['transcribing'];
  }

  function getStageColor(stage: string): string {
    const colors: Record<string, string> = {
      'loading': 'from-blue-500 to-cyan-500',
      'transcribing': 'from-indigo-500 to-purple-500',
      'diarization': 'from-green-500 to-emerald-500',
      'proofreading': 'from-yellow-500 to-orange-500',
      'exporting': 'from-pink-500 to-rose-500',
      'complete': 'from-green-500 to-emerald-500',
    };
    return colors[stage.toLowerCase()] || colors['transcribing'];
  }

  function formatETA(seconds: number | null): string {
    if (seconds === null || seconds <= 0) return 'Calculating...';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `~${hours}h ${minutes}m remaining`;
    } else if (minutes > 0) {
      return `~${minutes}m ${secs}s remaining`;
    } else {
      return `~${secs}s remaining`;
    }
  }

  function getFileName(path: string): string {
    return path.split('/').pop() || path.split('\\').pop() || path;
  }

  async function handleCancel() {
    if (!showCancelConfirm) {
      showCancelConfirm = true;
      return;
    }

    cancelling = true;
    try {
      await cancelTranscription();
      transcriptionState.fail('Transcription cancelled by user');
      uiState.navigateTo('config');
    } catch (err) {
      console.error('Failed to cancel:', err);
    } finally {
      cancelling = false;
      showCancelConfirm = false;
    }
  }

  function dismissCancelConfirm() {
    showCancelConfirm = false;
  }

  // Redirect if no transcription is in progress
  onDestroy(() => {
    if (!transcriptionState.isTranscribing && !transcriptionState.result && !error) {
      uiState.navigateTo('home');
    }
  });
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-950 flex items-center justify-center p-6">
  <div class="w-full max-w-2xl">
    <!-- Main Processing Card -->
    <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl border border-slate-200/50 dark:border-slate-700/50 shadow-2xl p-8">
      {#if error}
        <!-- Error State -->
        <div class="text-center">
          <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center shadow-2xl shadow-red-500/30">
            <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>

          <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">Transcription Failed</h2>
          <p class="text-slate-600 dark:text-slate-400 mb-6">{error}</p>

          <div class="flex gap-3 justify-center">
            <button
              onclick={() => uiState.navigateTo('config')}
              class="px-6 py-3 rounded-xl bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white font-medium transition-colors">
              Back to Configuration
            </button>
            <button
              onclick={() => uiState.navigateTo('home')}
              class="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-medium transition-all">
              Start Over
            </button>
          </div>
        </div>
      {:else}
        <!-- Processing State -->
        <div class="text-center">
          <!-- Animated Circular Progress -->
          <div class="relative w-48 h-48 mx-auto mb-8">
            <!-- Background circle -->
            <svg class="transform -rotate-90 w-48 h-48">
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="currentColor"
                stroke-width="8"
                fill="transparent"
                class="text-slate-200 dark:text-slate-700" />

              <!-- Progress circle -->
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="url(#gradient)"
                stroke-width="8"
                fill="transparent"
                stroke-linecap="round"
                style="stroke-dasharray: {2 * Math.PI * 88}; stroke-dashoffset: {2 * Math.PI * 88 * (1 - (progress?.progress || 0))}"
                class="transition-all duration-500 ease-out" />

              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" class="text-indigo-500" style="stop-color: currentColor" />
                  <stop offset="100%" class="text-purple-500" style="stop-color: currentColor" />
                </linearGradient>
              </defs>
            </svg>

            <!-- Center content -->
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br {progress ? getStageColor(progress.stage) : 'from-indigo-500 to-purple-500'} flex items-center justify-center shadow-xl mb-2 animate-pulse">
                <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={progress ? getStageIcon(progress.stage) : getStageIcon('transcribing')} />
                </svg>
              </div>
              <div class="text-3xl font-bold text-slate-900 dark:text-white">
                {Math.round((progress?.progress || 0) * 100)}%
              </div>
            </div>
          </div>

          <!-- Status Information -->
          <div class="space-y-4 mb-8">
            <div>
              <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-1">
                {progress?.stage || 'Processing'}
              </h2>
              <p class="text-slate-600 dark:text-slate-400">
                {progress?.message || 'Preparing transcription...'}
              </p>
            </div>

            {#if progress?.etaSeconds !== null && progress?.etaSeconds !== undefined}
              <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 text-sm font-medium">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {formatETA(progress.etaSeconds)}
              </div>
            {/if}
          </div>

          <!-- File Info -->
          {#if currentFile}
            <div class="mb-8 p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-700/50">
              <div class="flex items-center gap-3 justify-center">
                <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                </svg>
                <span class="text-sm font-medium text-slate-700 dark:text-slate-300">{getFileName(currentFile)}</span>
              </div>
            </div>
          {/if}

          <!-- Progress Stages -->
          <div class="mb-8 flex justify-center gap-2">
            {#each ['Loading', 'Transcribing', 'Diarization', 'Proofreading', 'Exporting'] as stage, index}
              {@const currentStage = progress?.stage?.toLowerCase() || ''}
              {@const stageKey = stage.toLowerCase()}
              {@const isActive = currentStage.includes(stageKey)}
              {@const isPast = progress && progress.progress > (index / 5)}

              <div class="flex flex-col items-center gap-1">
                <div class="w-2 h-2 rounded-full transition-all duration-300 {isPast || isActive ? 'bg-indigo-500 dark:bg-indigo-400' : 'bg-slate-300 dark:bg-slate-600'} {isActive ? 'scale-150' : ''}"></div>
                <span class="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">{stage}</span>
              </div>
            {/each}
          </div>

          <!-- Cancel Button -->
          {#if !showCancelConfirm}
            <button
              onclick={handleCancel}
              class="px-6 py-3 rounded-xl border-2 border-slate-300 dark:border-slate-600 hover:border-red-400 dark:hover:border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 text-slate-700 dark:text-slate-300 hover:text-red-600 dark:hover:text-red-400 font-medium transition-all duration-300">
              Cancel Transcription
            </button>
          {:else}
            <div class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
              <p class="text-sm text-red-800 dark:text-red-200 mb-3">Are you sure you want to cancel?</p>
              <div class="flex gap-3 justify-center">
                <button
                  onclick={dismissCancelConfirm}
                  disabled={cancelling}
                  class="px-4 py-2 rounded-lg bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors disabled:opacity-50">
                  No, Continue
                </button>
                <button
                  onclick={handleCancel}
                  disabled={cancelling}
                  class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium transition-colors disabled:opacity-50 flex items-center gap-2">
                  {#if cancelling}
                    <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Cancelling...
                  {:else}
                    Yes, Cancel
                  {/if}
                </button>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Tips Card -->
    {#if !error && transcriptionState.isTranscribing}
      <div class="mt-6 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
        <div class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/10 to-cyan-500/10 dark:from-blue-400/20 dark:to-cyan-400/20 flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1">
            <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-2">Processing Tip</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">
              Transcription time depends on your audio length and selected model. Larger models provide better accuracy but take longer to process. You can safely close this window and return later - the transcription will continue in the background.
            </p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }

  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
</style>
