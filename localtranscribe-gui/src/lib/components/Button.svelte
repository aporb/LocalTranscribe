<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    loading?: boolean;
    fullWidth?: boolean;
    onclick?: () => void;
    children: Snippet;
  }

  let {
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    fullWidth = false,
    onclick,
    children,
  }: Props = $props();

  const variantClasses = {
    primary:
      'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/40',
    secondary:
      'bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white',
    danger:
      'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40',
    ghost:
      'border-2 border-slate-300 dark:border-slate-600 hover:border-indigo-400 dark:hover:border-indigo-500 bg-white/50 dark:bg-slate-800/50 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/20 text-slate-700 dark:text-slate-300',
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const baseClasses =
    'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100';

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${fullWidth ? 'w-full' : ''}`;
</script>

<button {onclick} {disabled} class={classes} disabled={disabled || loading}>
  {#if loading}
    <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  {/if}
  {@render children()}
</button>

<style>
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>
