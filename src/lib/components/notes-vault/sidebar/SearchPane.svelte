<!-- Full-text search in the open vault: titles and text, with the passage that matched. -->
<script lang="ts">
	import { getContext } from 'svelte';
	import Search from '@lucide/svelte/icons/search';
	import { Input } from '$lib/components/ui/input/index.js';
	import { searchVault, type SearchHit } from '$lib/apis/note-vaults';
	import { currentVault } from '../vault';

	const i18n: any = getContext('i18n');

	let { onOpenNote, query = $bindable('') }: { onOpenNote: (id: string) => void; query?: string } =
		$props();

	let hits: SearchHit[] = $state([]);
	let searching = $state(false);
	let timer: ReturnType<typeof setTimeout> | null = null;

	$effect(() => {
		const q = query.trim();
		const vault = $currentVault?.id;
		if (timer) clearTimeout(timer);
		if (!q || !vault) {
			hits = [];
			return;
		}
		searching = true;
		timer = setTimeout(async () => {
			hits = await searchVault(localStorage.token, vault, q).catch(() => []);
			searching = false;
		}, 250);
	});

	const highlight = (text: string) => {
		const words = query
			.trim()
			.split(/\s+/)
			.filter(Boolean)
			.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
		if (!words.length) return [{ text, hit: false }];
		const re = new RegExp(`(${words.join('|')})`, 'gi');
		return text.split(re).map((part, i) => ({ text: part, hit: i % 2 === 1 }));
	};
</script>

<div class="flex h-full flex-col">
	<div class="relative px-2 pb-2">
		<Search
			class="pointer-events-none absolute top-1/2 left-4.5 z-10 size-3.5 -translate-y-[calc(50%+4px)] text-muted-foreground"
		/>
		<Input bind:value={query} placeholder={$i18n.t('Search in notes')} class="h-8 pl-8" autofocus />
	</div>
	<div class="min-h-0 flex-1 overflow-y-auto px-1 pb-6">
		{#if searching && !hits.length}
			<p class="px-2 py-2 text-sm text-muted-foreground">{$i18n.t('Searching…')}</p>
		{:else if query.trim() && !hits.length}
			<p class="px-2 py-2 text-sm text-muted-foreground">{$i18n.t('No note matches.')}</p>
		{/if}
		{#each hits as hit (hit.id)}
			<button
				type="button"
				class="block w-full rounded-md px-2 py-1.5 text-left hover:bg-sidebar-accent"
				onclick={() => onOpenNote(hit.id)}
			>
				<span class="block truncate text-sm font-medium">
					{#each highlight(hit.title || $i18n.t('Untitled')) as part}{#if part.hit}<mark
								class="rounded bg-warning/20 text-foreground">{part.text}</mark
							>{:else}{part.text}{/if}{/each}
				</span>
				{#if hit.folder}<span class="block truncate text-xs text-muted-foreground"
						>{hit.folder}</span
					>{/if}
				{#if hit.snippet}
					<span class="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
						{#each highlight(hit.snippet) as part}{#if part.hit}<mark
									class="rounded bg-warning/20 text-foreground">{part.text}</mark
								>{:else}{part.text}{/if}{/each}
					</span>
				{/if}
			</button>
		{/each}
	</div>
</div>
