<script lang="ts">
  import Modal from './Modal.svelte';

  interface Props {
    open: boolean;
    onClose: () => void;
  }

  let { open, onClose }: Props = $props();

  const features = [
    {
      icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z',
      title: '100% Private',
      description: 'All processing happens locally on your machine. Your audio never leaves your computer.',
    },
    {
      icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
      title: 'OpenAI Whisper',
      description: 'Powered by state-of-the-art Whisper AI for accurate transcription in multiple languages.',
    },
    {
      icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
      title: 'Speaker Diarization',
      description: 'Automatically identify and label different speakers in your audio recordings.',
    },
    {
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      title: 'Multiple Formats',
      description: 'Export to TXT, JSON, SRT, VTT, Markdown, HTML, and Word formats for any workflow.',
    },
  ];

  const techStack = [
    { name: 'Tauri', description: 'Lightweight desktop framework' },
    { name: 'SvelteKit', description: 'Modern web framework' },
    { name: 'Whisper', description: 'OpenAI speech recognition' },
    { name: 'PyAnnotate', description: 'Speaker diarization' },
    { name: 'Rust', description: 'Safe and fast backend' },
    { name: 'Python', description: 'AI/ML processing' },
  ];
</script>

<Modal {open} {onClose} title="About LocalTranscribe" size="lg">
  <div class="space-y-6">
    <!-- Hero Section -->
    <div class="text-center pb-6 border-b border-slate-200 dark:border-slate-700">
      <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-xl shadow-indigo-500/30">
        <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      </div>
      <h3 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">LocalTranscribe</h3>
      <p class="text-lg text-slate-600 dark:text-slate-400 mb-1">Version 3.1.2</p>
      <p class="text-sm text-slate-500 dark:text-slate-500">Privacy-First Audio Transcription</p>
    </div>

    <!-- Description -->
    <div class="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl p-6 border border-indigo-200/50 dark:border-indigo-800/50">
      <p class="text-slate-700 dark:text-slate-300 leading-relaxed">
        LocalTranscribe is a powerful, privacy-focused desktop application for transcribing audio files. Built with modern
        technologies and powered by OpenAI's Whisper, it provides professional-grade transcription that runs entirely on your
        local machine.
      </p>
    </div>

    <!-- Features -->
    <div>
      <h4 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Key Features</h4>
      <div class="grid md:grid-cols-2 gap-4">
        {#each features as feature}
          <div class="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-400/20 dark:to-purple-400/20 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={feature.icon} />
                </svg>
              </div>
              <div class="flex-1">
                <h5 class="font-semibold text-slate-900 dark:text-white mb-1">{feature.title}</h5>
                <p class="text-sm text-slate-600 dark:text-slate-400">{feature.description}</p>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Technology Stack -->
    <div>
      <h4 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Built With</h4>
      <div class="grid grid-cols-3 gap-3">
        {#each techStack as tech}
          <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-700/50 text-center">
            <div class="font-semibold text-slate-900 dark:text-white text-sm">{tech.name}</div>
            <div class="text-xs text-slate-500 dark:text-slate-400 mt-1">{tech.description}</div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Links -->
    <div class="pt-6 border-t border-slate-200 dark:border-slate-700">
      <div class="grid md:grid-cols-3 gap-3">
        <button
          class="flex items-center justify-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path
              d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
          </svg>
          GitHub
        </button>
        <button
          class="flex items-center justify-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Documentation
        </button>
        <button
          class="flex items-center justify-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Support
        </button>
      </div>
    </div>

    <!-- Copyright -->
    <div class="pt-6 border-t border-slate-200 dark:border-slate-700 text-center">
      <p class="text-sm text-slate-500 dark:text-slate-400">
        © 2024-2026 LocalTranscribe. Made with ❤️ for privacy.
      </p>
      <p class="text-xs text-slate-400 dark:text-slate-500 mt-2">
        Licensed under MIT License. Free and open source software.
      </p>
    </div>
  </div>
</Modal>
