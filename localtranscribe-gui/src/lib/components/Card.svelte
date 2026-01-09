<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    variant?: 'default' | 'gradient' | 'glass';
    padding?: 'sm' | 'md' | 'lg';
    hover?: boolean;
    children: Snippet;
  }

  let { variant = 'default', padding = 'md', hover = false, children }: Props = $props();

  const variantClasses = {
    default: 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700',
    gradient: 'bg-gradient-to-br from-indigo-500 to-purple-500 text-white shadow-xl shadow-indigo-500/30',
    glass: 'bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50',
  };

  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const hoverClasses = hover
    ? 'hover:shadow-xl hover:-translate-y-1 transition-all duration-300'
    : '';

  const classes = `rounded-2xl ${variantClasses[variant]} ${paddingClasses[padding]} ${hoverClasses}`;
</script>

<div class={classes}>
  {@render children()}
</div>
