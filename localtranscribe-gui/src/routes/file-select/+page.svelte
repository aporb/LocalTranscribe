<script lang="ts">
  import { uiState } from '$lib/stores.svelte';
  import { open } from '@tauri-apps/plugin-dialog';

  let dragActive = $state(false);
  let selectedFile = $state<{
    path: string;
    name: string;
    size: number;
    sizeFormatted: string;
  } | null>(null);

  async function handleFileSelect() {
    try {
      const selected = await open({
        multiple: false,
        filters: [
          {
            name: 'Audio Files',
            extensions: ['mp3', 'wav', 'm4a', 'flac', 'ogg', 'aac', 'wma', 'opus'],
          },
        ],
      });

      if (selected) {
        const path = Array.isArray(selected) ? selected[0] : selected;
        processFile(path);
      }
    } catch (error) {
      console.error('Failed to select file:', error);
    }
  }

  function processFile(path: string) {
    const name = path.split('/').pop() || path.split('\\').pop() || path;

    // In a real implementation, we'd get the actual file size
    // For now, we'll use a placeholder
    const size = 0;
    const sizeFormatted = formatFileSize(size);

    selectedFile = { path, name, size, sizeFormatted };
  }

  function formatFileSize(bytes: number): string {
    if (bytes === 0) return 'Unknown size';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  function handleDragEnter(e: DragEvent) {
    e.preventDefault();
    dragActive = true;
  }

  function handleDragLeave(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
  }

  async function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragActive = false;

    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      // For Tauri, we need to handle file paths differently
      // The file will have a path property in desktop mode
      if ('path' in file && typeof file.path === 'string') {
        processFile(file.path);
      }
    }
  }

  function proceedToQualityCheck() {
    if (selectedFile) {
      uiState.selectFile(selectedFile.path);
    }
  }

  function clearSelection() {
    selectedFile = null;
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-950">
  <!-- Header -->
  <header class="border-b border-slate-200/50 dark:border-slate-700/50 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl">
    <div class="max-w-5xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <button
          onclick={() => uiState.navigateTo('home')}
          class="flex items-center gap-2 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </button>

        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <span class="text-sm font-medium text-slate-900 dark:text-white">Select Audio File</span>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-5xl mx-auto px-6 py-12">
    <!-- Progress Steps -->
    <div class="mb-12">
      <div class="flex items-center justify-center gap-4">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white flex items-center justify-center text-sm font-semibold shadow-lg shadow-indigo-500/30">
            1
          </div>
          <span class="text-sm font-medium text-slate-900 dark:text-white">Select File</span>
        </div>

        <div class="w-16 h-0.5 bg-slate-200 dark:bg-slate-700"></div>

        <div class="flex items-center gap-2 opacity-40">
          <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400 flex items-center justify-center text-sm font-semibold">
            2
          </div>
          <span class="text-sm font-medium text-slate-600 dark:text-slate-400">Quality Check</span>
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

    <!-- Drag and Drop Zone -->
    <div
      class="relative mb-8"
      ondragenter={handleDragEnter}
      ondragleave={handleDragLeave}
      ondragover={handleDragOver}
      ondrop={handleDrop}
    >
      <div
        class="border-2 border-dashed rounded-3xl p-16 text-center transition-all duration-300 {dragActive
          ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-900/20 scale-102'
          : 'border-slate-300 dark:border-slate-600 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm hover:border-indigo-400 dark:hover:border-indigo-500'}"
      >
        <div class="flex flex-col items-center gap-6">
          <!-- Icon -->
          <div class="relative">
            <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-400/20 dark:to-purple-400/20 flex items-center justify-center {dragActive ? 'animate-bounce' : ''}">
              <svg class="w-12 h-12 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            {#if dragActive}
              <div class="absolute inset-0 rounded-2xl bg-indigo-500/20 animate-ping"></div>
            {/if}
          </div>

          <!-- Text -->
          <div>
            <h3 class="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
              {dragActive ? 'Drop your audio file here' : 'Drag & drop your audio file'}
            </h3>
            <p class="text-slate-600 dark:text-slate-300">
              or click the button below to browse
            </p>
          </div>

          <!-- Browse Button -->
          <button
            onclick={handleFileSelect}
            class="group relative inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold text-lg shadow-xl shadow-indigo-500/30 hover:shadow-2xl hover:shadow-indigo-500/40 transition-all duration-300 hover:scale-105">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            Browse Files
          </button>

          <!-- Supported Formats -->
          <div class="flex items-center gap-3 flex-wrap justify-center">
            <span class="text-xs text-slate-500 dark:text-slate-400">Supported:</span>
            {#each ['MP3', 'WAV', 'M4A', 'FLAC', 'OGG', 'AAC', 'WMA'] as format}
              <span class="px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-700 text-xs font-medium text-slate-600 dark:text-slate-300">
                {format}
              </span>
            {/each}
          </div>
        </div>
      </div>
    </div>

    <!-- Selected File Card -->
    {#if selectedFile}
      <div class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm rounded-2xl border border-slate-200/50 dark:border-slate-700/50 p-6 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Selected File</h3>
          <button
            onclick={clearSelection}
            class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <svg class="w-5 h-5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-indigo-500/30">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>

          <div class="flex-1 min-w-0">
            <p class="font-medium text-slate-900 dark:text-white truncate mb-1">{selectedFile.name}</p>
            <div class="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
              <span>{selectedFile.sizeFormatted}</span>
              <span>•</span>
              <span class="truncate">{selectedFile.path}</span>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-3 mt-6">
          <button
            onclick={proceedToQualityCheck}
            class="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40 transition-all duration-300 hover:scale-105">
            Continue to Quality Check
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>
    {/if}

    <!-- Tips Section -->
    <div class="grid md:grid-cols-3 gap-6">
      <div class="p-6 rounded-2xl bg-blue-50/50 dark:bg-blue-900/10 border border-blue-200/50 dark:border-blue-800/50">
        <div class="w-10 h-10 rounded-lg bg-blue-500/10 dark:bg-blue-400/20 flex items-center justify-center mb-3">
          <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h4 class="font-semibold text-slate-900 dark:text-white mb-2">Best Quality</h4>
        <p class="text-sm text-slate-600 dark:text-slate-400">Use uncompressed formats like WAV or FLAC for best transcription accuracy.</p>
      </div>

      <div class="p-6 rounded-2xl bg-purple-50/50 dark:bg-purple-900/10 border border-purple-200/50 dark:border-purple-800/50">
        <div class="w-10 h-10 rounded-lg bg-purple-500/10 dark:bg-purple-400/20 flex items-center justify-center mb-3">
          <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h4 class="font-semibold text-slate-900 dark:text-white mb-2">File Size</h4>
        <p class="text-sm text-slate-600 dark:text-slate-400">Files under 5GB recommended. Larger files may take longer to process.</p>
      </div>

      <div class="p-6 rounded-2xl bg-green-50/50 dark:bg-green-900/10 border border-green-200/50 dark:border-green-800/50">
        <div class="w-10 h-10 rounded-lg bg-green-500/10 dark:bg-green-400/20 flex items-center justify-center mb-3">
          <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h4 class="font-semibold text-slate-900 dark:text-white mb-2">Privacy First</h4>
        <p class="text-sm text-slate-600 dark:text-slate-400">Your files stay on your device. Nothing is uploaded to the cloud.</p>
      </div>
    </div>
  </main>
</div>
