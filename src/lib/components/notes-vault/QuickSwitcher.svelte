<!--
	Ctrl/⌘ O: jump to a note by typing part of its title (or an alias, or its folder), create one
	with that title, search the text, open today's note or the graph.
-->
<script lang="ts">
	import { getContext, tick } from 'svelte';
	import Fuse from 'fuse.js';
	import FileText from '@lucide/svelte/icons/file-text';
	import Plus from '@lucide/svelte/icons/plus';
	import Search from '@lucide/svelte/icons/search';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Orbit from '@lucide/svelte/icons/orbit';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import { Kbd } from '$lib/components/ui/kbd/index.js';
	import {
		canWrite,
		chartColor,
		cleanTitle,
		currentVault,
		normalizeTitle,
		tree,
		typeOf
	} from './vault';
	import TypeIcon from './TypeIcon.svelte';

	const i18n: any = getContext('i18n');

	let {
		open = $bindable(false),
		onOpenNote,
		onCreate,
		onSearch,
		onDaily,
		onGraph
	}: {
		open?: boolean;
		onOpenNote: (id: string) => void;
		onCreate: (title: string) => void;
		onSearch: (query: string) => void;
		onDaily: () => void;
		onGraph: () => void;
	} = $props();

	let query = $state('');
	let selected = $state(0);
	let input: HTMLInputElement | null = $state(null);

	const fuse = $derived(
		new Fuse($tree?.notes ?? [], {
			keys: [
				{ name: 'title', weight: 3 },
				{ name: 'aliases', weight: 2 },
				{ name: 'folder', weight: 0.5 },
				{ name: 'tags', weight: 0.5 }
			],
			threshold: 0.4,
			ignoreLocation: true
		})
	);

	type Item = {
		key: string;
		label: string;
		detail?: string;
		kind: 'note' | 'action';
		icon?: any;
		run: () => void;
		note?: any;
	};

	const items: Item[] = $derived.by(() => {
		const q = query.trim();
		const notes = q
			? fuse.search(q, { limit: 30 }).map((r) => r.item)
			: [...($tree?.notes ?? [])].sort((a, b) => b.updated_at - a.updated_at).slice(0, 12);
		const out: Item[] = notes.map((n) => ({
			key: n.id,
			label: n.title || $i18n.t('Untitled'),
			detail: n.folder,
			kind: 'note',
			note: n,
			run: () => onOpenNote(n.id)
		}));
		const exact =
			(q && ($tree?.notes ?? []).some((n) => normalizeTitle(n.title) === normalizeTitle(q))) ||
			false;
		if (q && !exact && canWrite($currentVault)) {
			out.push({
				key: '__create',
				label: $i18n.t('Create “{{title}}”', { title: cleanTitle(q) }),
				kind: 'action',
				icon: Plus,
				run: () => onCreate(cleanTitle(q))
			});
		}
		if (q)
			out.push({
				key: '__search',
				label: $i18n.t('Search “{{query}}” in the text', { query: q }),
				kind: 'action',
				icon: Search,
				run: () => onSearch(q)
			});
		if (!q) {
			if (canWrite($currentVault))
				out.push({
					key: '__daily',
					label: $i18n.t("Today's note"),
					kind: 'action',
					icon: CalendarDays,
					run: onDaily
				});
			out.push({
				key: '__graph',
				label: $i18n.t('Graph view'),
				kind: 'action',
				icon: Orbit,
				run: onGraph
			});
		}
		return out;
	});

	$effect(() => {
		items;
		selected = 0;
	});

	$effect(() => {
		if (open) {
			query = '';
			tick().then(() => input?.focus());
		}
	});

	const run = (item: Item | undefined) => {
		if (!item) return;
		open = false;
		item.run();
	};

	const onKeydown = (e: KeyboardEvent) => {
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			selected = Math.min(items.length - 1, selected + 1);
			document.querySelector(`[data-qs-index="${selected}"]`)?.scrollIntoView({ block: 'nearest' });
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selected = Math.max(0, selected - 1);
			document.querySelector(`[data-qs-index="${selected}"]`)?.scrollIntoView({ block: 'nearest' });
		} else if (e.key === 'Enter') {
			e.preventDefault();
			run(items[selected]);
		}
	};
</script>

<Dialog.Root bind:open>
	<Dialog.Content
		class="top-[15%] translate-y-0 gap-0 overflow-hidden p-0 sm:max-w-xl"
		showCloseButton={false}
	>
		<Dialog.Title class="sr-only">{$i18n.t('Go to a note')}</Dialog.Title>
		<div class="flex items-center gap-2 border-b px-3">
			<Search class="size-4 shrink-0 text-muted-foreground" />
			<input
				bind:this={input}
				bind:value={query}
				onkeydown={onKeydown}
				class="h-12 w-full bg-transparent text-base outline-none placeholder:text-muted-foreground"
				placeholder={$i18n.t('Go to a note, or create one…')}
			/>
		</div>
		<div class="max-h-[50vh] overflow-y-auto p-1">
			{#each items as item, i (item.key)}
				{@const t = item.note ? typeOf($currentVault, item.note.type) : null}
				<button
					type="button"
					data-qs-index={i}
					class="flex w-full items-center gap-2.5 rounded-md px-2.5 py-2 text-left text-sm {i ===
					selected
						? 'bg-accent text-accent-foreground'
						: ''}"
					onmouseenter={() => (selected = i)}
					onclick={() => run(item)}
				>
					{#if item.kind === 'note'}
						{#if t}<TypeIcon
								icon={t.icon}
								class="size-4 shrink-0"
								style="color: {chartColor(t.color)}"
							/>{:else}<FileText class="size-4 shrink-0 text-muted-foreground" />{/if}
					{:else}
						<item.icon class="size-4 shrink-0 text-muted-foreground" />
					{/if}
					<span
						class="min-w-0 flex-1 truncate {item.kind === 'action' && item.key === '__create'
							? 'text-link'
							: ''}">{item.label}</span
					>
					{#if item.detail}<span class="max-w-40 shrink-0 truncate text-xs text-muted-foreground"
							>{item.detail}</span
						>{/if}
				</button>
			{:else}
				<p class="px-3 py-6 text-center text-sm text-muted-foreground">
					{$i18n.t('No notes yet.')}
				</p>
			{/each}
		</div>
		<div class="flex items-center gap-3 border-t px-3 py-2 text-xs text-muted-foreground">
			<span class="inline-flex items-center gap-1"
				><Kbd>↑</Kbd><Kbd>↓</Kbd>{$i18n.t('to move')}</span
			>
			<span class="inline-flex items-center gap-1"><Kbd>↵</Kbd>{$i18n.t('to open')}</span>
			<span class="inline-flex items-center gap-1"><Kbd>Esc</Kbd>{$i18n.t('to close')}</span>
		</div>
	</Dialog.Content>
</Dialog.Root>
