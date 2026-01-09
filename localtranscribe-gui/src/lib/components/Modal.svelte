<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    open: boolean;
    onClose: () => void;
    title?: string;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    children: Snippet;
  }

  let { open, onClose, title, size = 'md', children }: Props = $props();

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl',
  };

  function handleBackdropClick(e: MouseEvent) {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) {
      onClose();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true">
    <div
      class="relative w-full {sizeClasses[size]} bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200/50 dark:border-slate-700/50 animate-scale-in">
      <!-- Header -->
      {#if title}
        <div class="flex items-center justify-between p-6 border-b border-slate-200/50 dark:border-slate-700/50">
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">{title}</h2>
          <button
            onclick={onClose}
            class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
            <svg class="w-6 h-6 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      {:else}
        <!-- Close button without header -->
        <button
          onclick={onClose}
          class="absolute top-4 right-4 z-10 p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
          <svg class="w-6 h-6 text-slate-600 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      {/if}

      <!-- Content -->
      <div class="p-6 max-h-[80vh] overflow-y-auto">
        {@render children()}
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes fade-in {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes scale-in {
    from {
      transform: scale(0.95);
      opacity: 0;
    }
    to {
      transform: scale(1);
      opacity: 1;
    }
  }

  .animate-fade-in {
    animation: fade-in 0.2s ease-out;
  }

  .animate-scale-in {
    animation: scale-in 0.2s ease-out;
  }
</style>
