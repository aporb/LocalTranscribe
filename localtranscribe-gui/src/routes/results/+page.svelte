<script lang="ts">
  import { onMount } from 'svelte';
  import { uiState, transcriptionState, recentFilesState } from '$lib/stores.svelte';
  import { open } from '@tauri-apps/plugin-shell';

  const result = $derived(transcriptionState.result);
  const currentFile = $derived(transcriptionState.currentFile);

  let showConfetti = $state(false);

  onMount(() => {
    // Add to recent files
    if (currentFile && result) {
      recentFilesState.addFile(currentFile, result);
    }

    // Show confetti animation
    showConfetti = true;
    setTimeout(() => {
      showConfetti = false;
    }, 3000);
  });

  function formatDuration(seconds: number): string {
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

  function getFileName(path: string): string {
    return path.split('/').pop() || path.split('\\').pop() || path;
  }

  function getFileExtension(path: string): string {
    const parts = path.split('.');
    return parts.length > 1 ? parts[parts.length - 1].toUpperCase() : 'FILE';
  }

  function getFileIcon(extension: string): string {
    const icons: Record<string, string> = {
      'TXT': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      'JSON': 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4',
      'SRT': 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z',
      'VTT': 'M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z',
      'MD': 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
      'HTML': 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4',
      'DOCX': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    };
    return icons[extension] || icons['TXT'];
  }

  function getFileColor(extension: string): string {
    const colors: Record<string, string> = {
      'TXT': 'from-blue-500 to-cyan-500',
      'JSON': 'from-purple-500 to-pink-500',
      'SRT': 'from-green-500 to-emerald-500',
      'VTT': 'from-teal-500 to-cyan-500',
      'MD': 'from-orange-500 to-red-500',
      'HTML': 'from-yellow-500 to-orange-500',
      'DOCX': 'from-indigo-500 to-purple-500',
    };
    return colors[extension] || colors['TXT'];
  }

  async function openFile(path: string) {
    try {
      await open(path);
    } catch (error) {
      console.error('Failed to open file:', error);
    }
  }

  async function revealInFolder(path: string) {
    try {
      // Get directory from file path
      const parts = path.split('/');
      parts.pop();
      const dir = parts.join('/');
      await open(dir);
    } catch (error) {
      console.error('Failed to reveal file:', error);
    }
  }

  function startNew() {
    transcriptionState.reset();
    uiState.selectedFile = null;
    uiState.navigateTo('home');
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-950">
  <!-- Confetti Animation -->
  {#if showConfetti}
    <div class="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {#each Array(50) as _, i}
        <div
          class="absolute w-2 h-2 rounded-full animate-confetti"
          style="left: {Math.random() * 100}%;
                 top: -10px;
                 background: {['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6'][i % 6]};
                 animation-delay: {Math.random() * 1}s;
                 animation-duration: {2 + Math.random() * 2}s;">
        </div>
      {/each}
    </div>
  {/if}

  <!-- Header -->
  <header class="border-b border-slate-200/50 dark:border-slate-700/50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl sticky top-0 z-10">
    <div class="max-w-7xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-green-500/30">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold text-slate-900 dark:text-white">Transcription Complete!</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400">Your files are ready</p>
          </div>
        </div>

        <button
          onclick={startNew}
          class="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-medium text-sm transition-all hover:scale-105 shadow-lg shadow-indigo-500/30">
          New Transcription
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-6 py-12">
    {#if result}
      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Left Column - Files & Statistics -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Success Message -->
          <div class="bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl p-8 text-white shadow-2xl shadow-green-500/30">
            <div class="flex items-center gap-4 mb-4">
              <div class="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="flex-1">
                <h2 class="text-2xl font-bold mb-1">Success!</h2>
                <p class="text-green-100">Your audio has been transcribed successfully</p>
              </div>
            </div>

            <!-- Statistics Grid -->
            <div class="grid grid-cols-3 gap-4 mt-6">
              <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div class="text-3xl font-bold mb-1">{result.numSegments}</div>
                <div class="text-sm text-green-100">Segments</div>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div class="text-3xl font-bold mb-1">{result.numSpeakers || 'N/A'}</div>
                <div class="text-sm text-green-100">Speakers</div>
              </div>
              <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div class="text-3xl font-bold mb-1">{formatDuration(result.durationSeconds)}</div>
                <div class="text-sm text-green-100">Duration</div>
              </div>
            </div>
          </div>

          <!-- Output Files -->
          <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
            <div class="flex items-center gap-3 mb-6">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Output Files</h2>
                <p class="text-sm text-slate-600 dark:text-slate-400">{result.outputFiles.length} file{result.outputFiles.length !== 1 ? 's' : ''} generated</p>
              </div>
            </div>

            <div class="space-y-3">
              {#each result.outputFiles as file}
                {@const ext = getFileExtension(file)}
                <div class="group p-4 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 hover:-translate-y-0.5">
                  <div class="flex items-center gap-4">
                    <!-- File Icon -->
                    <div class="w-12 h-12 rounded-lg bg-gradient-to-br {getFileColor(ext)} flex items-center justify-center shadow-lg flex-shrink-0">
                      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getFileIcon(ext)} />
                      </svg>
                    </div>

                    <!-- File Info -->
                    <div class="flex-1 min-w-0">
                      <div class="font-medium text-slate-900 dark:text-white truncate">{getFileName(file)}</div>
                      <div class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        <span class="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 font-medium">{ext}</span>
                      </div>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-2 flex-shrink-0">
                      <button
                        onclick={() => openFile(file)}
                        class="p-2 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 hover:bg-indigo-200 dark:hover:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 transition-colors"
                        title="Open file">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </button>
                      <button
                        onclick={() => revealInFolder(file)}
                        class="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-600 dark:text-slate-400 transition-colors"
                        title="Show in folder">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          </div>

          <!-- Source File Info -->
          {#if currentFile}
            <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Source Audio</h3>
                  <p class="text-sm text-slate-600 dark:text-slate-400">Original file that was transcribed</p>
                </div>
              </div>

              <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-700/50">
                <div class="font-medium text-slate-900 dark:text-white mb-1">{getFileName(currentFile)}</div>
                <div class="text-xs text-slate-500 dark:text-slate-400 break-all">{currentFile}</div>
              </div>
            </div>
          {/if}
        </div>

        <!-- Right Column - Actions & Info -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 sticky top-24">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Quick Actions</h3>

            <div class="space-y-3">
              <button
                onclick={startNew}
                class="w-full group flex items-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500 hover:shadow-lg hover:shadow-indigo-500/10 transition-all duration-300 hover:-translate-y-0.5">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div class="flex-1 text-left">
                  <div class="font-medium text-slate-900 dark:text-white">New Transcription</div>
                  <div class="text-xs text-slate-600 dark:text-slate-400">Start transcribing another file</div>
                </div>
                <svg class="w-5 h-5 text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <button
                onclick={() => uiState.navigateTo('home')}
                class="w-full group flex items-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/10 transition-all duration-300 hover:-translate-y-0.5">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </div>
                <div class="flex-1 text-left">
                  <div class="font-medium text-slate-900 dark:text-white">Back to Home</div>
                  <div class="text-xs text-slate-600 dark:text-slate-400">Return to main screen</div>
                </div>
                <svg class="w-5 h-5 text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              {#if result.outputFiles.length > 0}
                <button
                  onclick={() => revealInFolder(result.outputFiles[0])}
                  class="w-full group flex items-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 hover:border-green-400 dark:hover:border-green-500 hover:shadow-lg hover:shadow-green-500/10 transition-all duration-300 hover:-translate-y-0.5">
                  <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 text-left">
                    <div class="font-medium text-slate-900 dark:text-white">Open Folder</div>
                    <div class="text-xs text-slate-600 dark:text-slate-400">View all output files</div>
                  </div>
                  <svg class="w-5 h-5 text-slate-400 group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              {/if}
            </div>
          </div>

          <!-- Share Feedback -->
          <div class="bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl p-6 text-white shadow-xl shadow-indigo-500/30">
            <div class="flex items-center gap-3 mb-3">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
              </svg>
              <h3 class="text-lg font-semibold">Enjoying LocalTranscribe?</h3>
            </div>
            <p class="text-indigo-100 text-sm mb-4">
              Your transcription was successful! Help us improve by sharing your feedback or reporting issues on GitHub.
            </p>
            <button class="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white font-medium text-sm transition-colors">
              Share Feedback
            </button>
          </div>
        </div>
      </div>
    {:else}
      <!-- No Results State -->
      <div class="text-center py-16">
        <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-slate-400 to-slate-500 flex items-center justify-center shadow-2xl">
          <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">No Results Available</h2>
        <p class="text-slate-600 dark:text-slate-400 mb-6">Start a new transcription to see results here.</p>

        <button
          onclick={startNew}
          class="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold transition-all hover:scale-105">
          Start Transcribing
        </button>
      </div>
    {/if}
  </main>
</div>

<style>
  @keyframes confetti {
    0% {
      transform: translateY(-10px) rotate(0deg);
      opacity: 1;
    }
    100% {
      transform: translateY(100vh) rotate(720deg);
      opacity: 0;
    }
  }

  .animate-confetti {
    animation: confetti linear forwards;
  }
</style>
