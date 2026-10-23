<!--
	Underline tabs for page navigation (design system → Tabs & navigation): module sections,
	company sections. To switch views inside one page, use the segmented Tabs from $lib/components/ui/tabs.

	<NavTabs label="Accounting" items={[{ href: '/accounting/companies', label: 'Companies', active: true }]} />
-->
<script lang="ts">
	import type { Component } from 'svelte';
	import { cn } from '$lib/utils/shadcn.js';

	type Item = {
		href: string;
		label: string;
		active?: boolean;
		icon?: Component;
		/** small count shown after the label */
		count?: number | null;
	};

	let {
		items,
		label = undefined,
		onreorder = undefined,
		class: className = ''
	}: {
		items: Item[];
		label?: string;
		/** makes the tabs draggable; called with the old and new index */
		onreorder?: (from: number, to: number) => void;
		class?: string;
	} = $props();

	let dragIdx = $state<number | null>(null);
	let overIdx = $state<number | null>(null);

	const drop = (e: DragEvent, idx: number) => {
		e.preventDefault();
		if (dragIdx !== null && dragIdx !== idx) onreorder?.(dragIdx, idx);
		dragIdx = overIdx = null;
	};
</script>

<nav
	aria-label={label}
	class={cn(
		'flex gap-5 overflow-x-auto border-b border-border [scrollbar-width:none] [&::-webkit-scrollbar]:hidden',
		className
	)}
>
	{#each items as item, idx (item.href)}
		<a
			href={item.href}
			aria-current={item.active ? 'page' : undefined}
			draggable={onreorder ? 'true' : undefined}
			ondragstart={onreorder
				? (e) => {
						dragIdx = idx;
						e.dataTransfer?.setData('text/plain', String(idx));
						if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
					}
				: undefined}
			ondragover={onreorder
				? (e) => {
						e.preventDefault();
						overIdx = idx;
					}
				: undefined}
			ondrop={onreorder ? (e) => drop(e, idx) : undefined}
			ondragend={onreorder ? () => (dragIdx = overIdx = null) : undefined}
			class={cn(
				'-mb-px inline-flex items-center gap-1.5 border-b-2 border-transparent py-2.5 text-sm font-medium whitespace-nowrap text-muted-foreground transition-colors hover:text-foreground',
				'focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50',
				item.active && 'border-foreground text-foreground',
				onreorder && 'select-none',
				dragIdx === idx && 'opacity-40',
				overIdx === idx && dragIdx !== null && dragIdx !== idx && 'border-ring'
			)}
		>
			{#if item.icon}
				{@const Icon = item.icon}
				<Icon class="size-4" aria-hidden="true" />
			{/if}
			{item.label}
			{#if item.count !== undefined && item.count !== null}
				<span
					class="ml-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-secondary px-1.5 text-xs font-medium text-secondary-foreground tabular-nums"
					>{item.count}</span
				>
			{/if}
		</a>
	{/each}
</nav>
