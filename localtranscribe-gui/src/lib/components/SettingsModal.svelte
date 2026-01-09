<script lang="ts">
  import Modal from './Modal.svelte';
  import { uiState, configState } from '../stores.svelte';

  interface Props {
    open: boolean;
    onClose: () => void;
  }

  let { open, onClose }: Props = $props();

  let tempDarkMode = $state(uiState.darkMode);
  let tempSelectedModel = $state(configState.selectedModel);
  let tempProofread = $state(configState.proofread);

  function saveSettings() {
    if (tempDarkMode !== uiState.darkMode) {
      uiState.toggleDarkMode();
    }
    configState.selectedModel = tempSelectedModel;
    configState.proofread = tempProofread;
    onClose();
  }

  function resetSettings() {
    tempDarkMode = false;
    tempSelectedModel = 'medium';
    tempProofread = true;
  }
</script>

<Modal {open} {onClose} title="Settings" size="lg">
  <div class="space-y-6">
    <!-- Appearance -->
    <div>
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Appearance</h3>
      <div class="space-y-3">
        <label class="flex items-center justify-between p-4 rounded-xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/50 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </div>
            <div>
              <div class="font-medium text-slate-900 dark:text-white">Dark Mode</div>
              <div class="text-sm text-slate-600 dark:text-slate-400">Use dark color scheme</div>
            </div>
          </div>
          <input
            type="checkbox"
            bind:checked={tempDarkMode}
            class="w-5 h-5 rounded border-slate-300 dark:border-slate-600 text-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-0" />
        </label>
      </div>
    </div>

    <!-- Default Model -->
    <div>
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Default Transcription Settings</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Default Whisper Model</label>
          <select
            bind:value={tempSelectedModel}
            class="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="tiny">Tiny - Fastest, lowest accuracy (~1GB RAM)</option>
            <option value="base">Base - Fast, moderate accuracy (~1.5GB RAM)</option>
            <option value="small">Small - Balanced speed/accuracy (~2GB RAM)</option>
            <option value="medium">Medium - High accuracy (~5GB RAM)</option>
            <option value="large">Large - Highest accuracy (~10GB RAM)</option>
          </select>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">This can be changed for each transcription</p>
        </div>

        <label class="flex items-center justify-between p-4 rounded-xl border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/50 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <div class="font-medium text-slate-900 dark:text-white">Enable Proofreading by Default</div>
              <div class="text-sm text-slate-600 dark:text-slate-400">Fix common transcription errors with AI</div>
            </div>
          </div>
          <input
            type="checkbox"
            bind:checked={tempProofread}
            class="w-5 h-5 rounded border-slate-300 dark:border-slate-600 text-indigo-600 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-0" />
        </label>
      </div>
    </div>

    <!-- Advanced -->
    <div>
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Advanced</h3>
      <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-700/50">
        <div class="flex items-start gap-3">
          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm text-slate-700 dark:text-slate-300">
            <p class="font-medium mb-1">Model Storage Location</p>
            <p class="text-slate-600 dark:text-slate-400">Whisper models are automatically downloaded and cached in your system's default cache directory. First-time use of each model will require a download.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
      <button
        onclick={resetSettings}
        class="px-6 py-3 rounded-xl border border-slate-300 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors">
        Reset to Defaults
      </button>
      <button
        onclick={onClose}
        class="px-6 py-3 rounded-xl bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white font-medium transition-colors">
        Cancel
      </button>
      <button
        onclick={saveSettings}
        class="flex-1 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold shadow-lg shadow-indigo-500/30 transition-all">
        Save Changes
      </button>
    </div>
  </div>
</Modal>
