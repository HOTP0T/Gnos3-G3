<!--
	The pop-up list under the caret for [[ links, @ Gnos3 data, # tags and / commands
	(mounted by suggestionPopup.svelte.ts). Arrow keys move, Enter or Tab picks, Escape closes.
-->
<script lang="ts">
	import { getContext, tick } from 'svelte';
	import type { SuggestItem } from './suggestionPopup.svelte';

	const i18n: any = getContext('i18n');

	let {
		items = [],
		loading = false,
		emptyText = '',
		onSelect = (_item: SuggestItem) => {}
	}: {
		items?: SuggestItem[];
		loading?: boolean;
		emptyText?: string;
		onSelect?: (item: SuggestItem) => void;
	} = $props();

	let selected = $state(0);
	let list: HTMLDivElement | null = $state(null);

	$effect(() => {
		// New results: back to the first one.
		items;
		selected = 0;
	});

	const scrollIntoView = async () => {
		await tick();
		list?.querySelector(`[data-index="${selected}"]`)?.scrollIntoView({ block: 'nearest' });
	};

	export function onKeyDown(event: KeyboardEvent): boolean {
		if (!items.length) return false;
		if (event.key === 'ArrowDown') {
			selected = (selected + 1) % items.length;
			scrollIntoView();
			return true;
		}
		if (event.key === 'ArrowUp') {
			selected = (selected - 1 + items.length) % items.length;
			scrollIntoView();
			return true;
		}
		if (event.key === 'Enter' || event.key === 'Tab') {
			const item = items[selected];
			if (item) onSelect(item);
			return true;
		}
		return false;
	}

	const groupStart = (index: number) =>
		!!items[index]?.group && items[index]?.group !== items[index - 1]?.group;
</script>

<div
	bind:this={list}
	class="max-h-80 w-80 max-w-[calc(100vw-2rem)] overflow-y-auto rounded-lg border bg-popover p-1 text-popover-foreground shadow-lg"
	role="listbox"
>
	{#if items.length === 0}
		<div class="px-2 py-1.5 text-sm text-muted-foreground">
			{loading ? $i18n.t('Searching…') : emptyText || $i18n.t('No results')}
		</div>
	{:else}
		{#each items as item, index (item.key)}
			{#if groupStart(index)}
				<div
					class="px-2 pt-2 pb-1 text-[11px] font-medium tracking-wide text-muted-foreground uppercase first:pt-1"
				>
					{item.group}
				</div>
			{/if}
			<button
				type="button"
				data-index={index}
				role="option"
				aria-selected={index === selected}
				class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm outline-none {index ===
				selected
					? 'bg-accent text-accent-foreground'
					: ''}"
				onmouseenter={() => (selected = index)}
				onmousedown={(e) => {
					e.preventDefault();
					onSelect(item);
				}}
			>
				{#if item.icon}
					{@const Icon = item.icon}
					<Icon
						class="size-4 shrink-0 {item.color ? '' : 'text-muted-foreground'}"
						style={item.color ? `color: ${item.color}` : ''}
					/>
				{/if}
				<span class="min-w-0 flex-1">
					<span class="block truncate {item.create ? 'text-link' : ''}">{item.label}</span>
					{#if item.detail}
						<span class="block truncate text-xs text-muted-foreground">{item.detail}</span>
					{/if}
				</span>
				{#if item.hint}
					<span class="shrink-0 text-xs text-muted-foreground">{item.hint}</span>
				{/if}
			</button>
		{/each}
	{/if}
</div>
