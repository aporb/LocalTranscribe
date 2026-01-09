<script lang="ts">
  import { uiState, recentFilesState } from '$lib/stores.svelte';
  import { open } from '@tauri-apps/plugin-dialog';

  async function selectAudioFile() {
    try {
      const selected = await open({
        multiple: false,
        filters: [
          {
            name: 'Audio Files',
            extensions: ['mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac', 'wma'],
          },
        ],
      });

      if (selected) {
        const path = Array.isArray(selected) ? selected[0] : selected;
        uiState.selectFile(path);
      }
    } catch (error) {
      console.error('Failed to select file:', error);
    }
  }

  function formatDate(timestamp: number): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  function getFileName(path: string): string {
    return path.split('/').pop() || path.split('\\').pop() || path;
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-950">
  <!-- Header -->
  <header class="border-b border-slate-200/50 dark:border-slate-700/50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl">
    <div class="max-w-7xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-bold text-slate-900 dark:text-white">LocalTranscribe</h1>
            <p class="text-xs text-slate-500 dark:text-slate-400">Privacy-First Audio Transcription</p>
          </div>
        </div>

        <button
          onclick={() => uiState.toggleDarkMode()}
          class="p-2.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
          {#if uiState.darkMode}
            <svg class="w-5 h-5 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          {:else}
            <svg class="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          {/if}
        </button>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-6 py-12">
    <!-- Hero Section -->
    <div class="text-center mb-16">
      <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 text-sm font-medium mb-6">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
        </svg>
        100% Private • Offline • Secure
      </div>

      <h2 class="text-5xl font-bold text-slate-900 dark:text-white mb-4 bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-indigo-900 to-purple-900 dark:from-slate-100 dark:via-indigo-200 dark:to-purple-200">
        Professional Audio<br />Transcription
      </h2>

      <p class="text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto mb-12">
        Convert your audio files to text with AI-powered transcription,<br class="hidden sm:block" />
        speaker identification, and intelligent proofreading.
      </p>

      <!-- Primary CTA -->
      <button
        onclick={selectAudioFile}
        class="group relative inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold text-lg shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:shadow-indigo-500/40 transition-all duration-300 hover:scale-105">
        <svg class="w-6 h-6 group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        Select Audio File
      </button>

      <!-- Supported formats -->
      <div class="mt-6 flex items-center justify-center gap-3 flex-wrap">
        <span class="text-sm text-slate-500 dark:text-slate-400">Supports:</span>
        {#each ['MP3', 'WAV', 'M4A', 'FLAC', 'OGG'] as format}
          <span class="px-3 py-1 rounded-lg bg-white dark:bg-slate-800 text-xs font-medium text-slate-600 dark:text-slate-300 shadow-sm">
            {format}
          </span>
        {/each}
      </div>
    </div>

    <!-- Feature Cards -->
    <div class="grid md:grid-cols-3 gap-6 mb-16">
      <div class="group p-6 rounded-2xl bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50 hover:shadow-xl hover:shadow-indigo-500/10 transition-all duration-300 hover:-translate-y-1">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-blue-500/30">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Speaker Diarization</h3>
        <p class="text-slate-600 dark:text-slate-400 text-sm">Automatically identify and label different speakers in your audio with AI-powered voice recognition.</p>
      </div>

      <div class="group p-6 rounded-2xl bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50 hover:shadow-xl hover:shadow-purple-500/10 transition-all duration-300 hover:-translate-y-1">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-purple-500/30">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Multiple Formats</h3>
        <p class="text-slate-600 dark:text-slate-400 text-sm">Export to TXT, JSON, SRT, VTT, Markdown, HTML, and Word formats. Perfect for any workflow.</p>
      </div>

      <div class="group p-6 rounded-2xl bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50 hover:shadow-xl hover:shadow-green-500/10 transition-all duration-300 hover:-translate-y-1">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-green-500/30">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Smart Proofreading</h3>
        <p class="text-slate-600 dark:text-slate-400 text-sm">Context-aware corrections for acronyms, industry terms, and common transcription errors.</p>
      </div>
    </div>

    <!-- Recent Files -->
    {#if recentFilesState.files.length > 0}
      <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200/50 dark:border-slate-700/50">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Recent Transcriptions</h3>
        </div>
        <div class="divide-y divide-slate-200/50 dark:divide-slate-700/50">
          {#each recentFilesState.files as file}
            <button
              class="w-full px-6 py-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left group">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4 flex-1 min-w-0">
                  <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-400/20 dark:to-purple-400/20 flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-slate-900 dark:text-white truncate">{getFileName(file.path)}</p>
                    <p class="text-sm text-slate-500 dark:text-slate-400">{formatDate(file.timestamp)}</p>
                  </div>
                </div>
                <svg class="w-5 h-5 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          {/each}
        </div>
      </div>
    {/if}
  </main>

  <!-- Footer -->
  <footer class="border-t border-slate-200/50 dark:border-slate-700/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-xl mt-auto">
    <div class="max-w-7xl mx-auto px-6 py-6">
      <div class="flex items-center justify-between text-sm">
        <p class="text-slate-600 dark:text-slate-400">
          LocalTranscribe v3.1.2 • Made with ❤️ for privacy
        </p>
        <div class="flex items-center gap-6">
          <button class="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            Documentation
          </button>
          <button
            onclick={() => uiState.settingsModalOpen = true}
            class="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            Settings
          </button>
          <button
            onclick={() => uiState.aboutModalOpen = true}
            class="text-slate-600 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
            About
          </button>
        </div>
      </div>
    </div>
  </footer>
</div>
