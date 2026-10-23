<!--
	Segmented tabs whose segments are links (design system → Tabs & navigation): switching views
	of the same data, e.g. Dashboard / Table. For in-page state use $lib/components/ui/tabs instead.
-->
<script lang="ts">
	import { cn } from '$lib/utils/shadcn.js';

	let {
		items,
		label = undefined,
		class: className = ''
	}: {
		items: { href: string; label: string; active?: boolean }[];
		label?: string;
		class?: string;
	} = $props();
</script>

<div
	role="navigation"
	aria-label={label}
	class={cn(
		'inline-flex h-9 w-fit max-w-full items-center overflow-x-auto rounded-lg bg-muted p-[3px] text-muted-foreground [scrollbar-width:none]',
		className
	)}
>
	{#each items as item (item.href)}
		<a
			href={item.href}
			aria-current={item.active ? 'page' : undefined}
			class={cn(
				'inline-flex h-full flex-[1_0_auto] items-center justify-center gap-1.5 rounded-md border border-transparent px-2 py-1 text-sm font-medium whitespace-nowrap transition-[color,box-shadow]',
				'text-foreground/70 hover:text-foreground dark:text-muted-foreground dark:hover:text-foreground',
				'focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50',
				item.active &&
					'bg-background text-foreground shadow-sm dark:border-input dark:bg-input/30 dark:text-foreground'
			)}>{item.label}</a
		>
	{/each}
</div>
