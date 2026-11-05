<!--
	Picks a note (relation property) or a piece of Gnos3 data (entity property) from a search box.
	Notes come from the loaded vault; "Create …" makes a new note with the field's type.
-->
<script lang="ts">
	import { getContext, type Snippet } from 'svelte';
	import Plus from '@lucide/svelte/icons/plus';
	import FileText from '@lucide/svelte/icons/file-text';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { tree, normalizeTitle, typeOf, currentVault, chartColor } from '../vault';
	import { ENTITY_META, searchEntities, type EntityHit, type EntityType } from '../entities';

	const i18n: any = getContext('i18n');

	let {
		mode = 'note',
		noteType = null,
		entityType = null,
		exclude = [],
		onPick,
		onCreate = null,
		trigger
	}: {
		mode?: 'note' | 'entity';
		noteType?: string | null;
		entityType?: string | null;
		exclude?: string[];
		onPick: (value: any) => void;
		onCreate?: ((title: string) => Promise<{ id: string; title: string } | null>) | null;
		trigger: Snippet<[{ props: Record<string, unknown> }]>;
	} = $props();

	let open = $state(false);
	let query = $state('');
	let entityHits: EntityHit[] = $state([]);
	let searching = $state(false);
	let timer: ReturnType<typeof setTimeout> | null = null;

	const noteHits = $derived.by(() => {
		if (mode !== 'note') return [];
		const q = normalizeTitle(query);
		const notes = ($tree?.notes ?? []).filter((n) => !exclude.includes(n.id));
		const scored = notes
			.filter((n) => !q || normalizeTitle(n.title).includes(q))
			.sort((a, b) => {
				const at = noteType && a.type === noteType ? 0 : 1;
				const bt = noteType && b.type === noteType ? 0 : 1;
				return at - bt || b.updated_at - a.updated_at;
			});
		return scored.slice(0, 30);
	});

	const exact = $derived(
		mode === 'note' &&
			!!query.trim() &&
			noteHits.some((n) => normalizeTitle(n.title) === normalizeTitle(query))
	);

	$effect(() => {
		if (mode !== 'entity') return;
		const q = query;
		if (timer) clearTimeout(timer);
		if (q.trim().length < 2) {
			entityHits = [];
			return;
		}
		searching = true;
		timer = setTimeout(async () => {
			entityHits = await searchEntities(
				localStorage.token,
				q,
				entityType ? [entityType as EntityType] : undefined
			);
			searching = false;
		}, 200);
	});

	const pick = (value: any) => {
		onPick(value);
		open = false;
		query = '';
	};
</script>

<Popover.Root bind:open>
	<Popover.Trigger>
		{#snippet child({ props })}
			{@render trigger({ props })}
		{/snippet}
	</Popover.Trigger>
	<Popover.Content class="w-72 p-1" align="start">
		<div class="p-1">
			<Input
				bind:value={query}
				placeholder={mode === 'note' ? $i18n.t('Search notes') : $i18n.t('Search')}
				class="h-8"
				autofocus
			/>
		</div>
		<div class="max-h-64 overflow-y-auto">
			{#if mode === 'note'}
				{#each noteHits as note (note.id)}
					{@const t = typeOf($currentVault, note.type)}
					<button
						type="button"
						class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-accent"
						onclick={() => pick({ id: note.id, title: note.title })}
					>
						<FileText class="size-4 shrink-0" style="color: {t ? chartColor(t.color) : ''}" />
						<span class="min-w-0 flex-1 truncate">{note.title || $i18n.t('Untitled')}</span>
						{#if note.folder}
							<span class="max-w-24 truncate text-xs text-muted-foreground">{note.folder}</span>
						{/if}
					</button>
				{/each}
				{#if onCreate && query.trim() && !exact}
					<button
						type="button"
						class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm text-link hover:bg-accent"
						onclick={async () => {
							const created = await onCreate?.(query.trim());
							if (created) pick(created);
						}}
					>
						<Plus class="size-4 shrink-0" />
						<span class="truncate">{$i18n.t('Create “{{title}}”', { title: query.trim() })}</span>
					</button>
				{/if}
				{#if !noteHits.length && !query.trim()}
					<div class="px-2 py-1.5 text-sm text-muted-foreground">{$i18n.t('No notes yet')}</div>
				{/if}
			{:else}
				{#each entityHits as hit (hit.entity_type + hit.entity_id)}
					{@const Icon = ENTITY_META[hit.entity_type].icon}
					<button
						type="button"
						class="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-accent"
						onclick={() =>
							pick({ entity_type: hit.entity_type, entity_id: hit.entity_id, label: hit.label })}
					>
						<Icon class="size-4 shrink-0 text-muted-foreground" />
						<span class="min-w-0 flex-1">
							<span class="block truncate">{hit.label}</span>
							{#if hit.detail}<span class="block truncate text-xs text-muted-foreground"
									>{hit.detail}</span
								>{/if}
						</span>
					</button>
				{/each}
				{#if !entityHits.length}
					<div class="px-2 py-1.5 text-sm text-muted-foreground">
						{searching
							? $i18n.t('Searching…')
							: query.trim().length < 2
								? $i18n.t('Type at least 2 characters')
								: $i18n.t('No results')}
					</div>
				{/if}
			{/if}
		</div>
	</Popover.Content>
</Popover.Root>
