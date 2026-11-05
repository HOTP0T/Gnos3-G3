<!-- The vault's tags (nested tags under their parent: project/alpha); choosing one lists its notes. -->
<script lang="ts">
	import { getContext } from 'svelte';
	import Hash from '@lucide/svelte/icons/hash';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import FileText from '@lucide/svelte/icons/file-text';
	import { allTags, tree } from '../vault';

	const i18n: any = getContext('i18n');

	let {
		selected = $bindable(null),
		onOpenNote
	}: { selected?: string | null; onOpenNote: (id: string) => void } = $props();

	const hasTag = (tags: string[], tag: string) =>
		tags.some(
			(t) =>
				t.toLowerCase() === tag.toLowerCase() || t.toLowerCase().startsWith(tag.toLowerCase() + '/')
		);

	const notes = $derived(
		selected
			? ($tree?.notes ?? [])
					.filter((n) => hasTag(n.tags ?? [], selected!))
					.sort((a, b) => b.updated_at - a.updated_at)
			: []
	);
</script>

<div class="h-full overflow-y-auto px-1 pb-6">
	{#if selected}
		<button
			type="button"
			class="mb-1 flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-sidebar-accent hover:text-foreground"
			onclick={() => (selected = null)}
		>
			<ArrowLeft class="size-3.5" />{$i18n.t('All tags')}
		</button>
		<div class="px-2 pb-2 text-sm font-medium text-link">
			#{selected} <span class="font-normal text-muted-foreground">· {notes.length}</span>
		</div>
		{#each notes as note (note.id)}
			<button
				type="button"
				class="flex w-full items-center gap-1.5 rounded-md px-2 py-1.5 text-left text-sm hover:bg-sidebar-accent"
				onclick={() => onOpenNote(note.id)}
			>
				<FileText class="size-4 shrink-0 text-muted-foreground" />
				<span class="truncate">{note.title || $i18n.t('Untitled')}</span>
			</button>
		{/each}
	{:else}
		{#each $allTags as { tag, count } (tag)}
			{@const depth = tag.split('/').length - 1}
			<button
				type="button"
				class="flex w-full items-center gap-1.5 rounded-md py-1.5 pr-2 text-left text-sm hover:bg-sidebar-accent"
				style="padding-left: {0.5 + depth * 0.85}rem"
				onclick={() => (selected = tag)}
			>
				<Hash class="size-3.5 shrink-0 text-muted-foreground" />
				<span class="min-w-0 flex-1 truncate">{tag.split('/').pop()}</span>
				<span class="text-xs text-muted-foreground tabular-nums">{count}</span>
			</button>
		{:else}
			<p class="px-2 py-2 text-sm text-muted-foreground">
				{$i18n.t('No tags yet. Write #tag in a note, or add tags in its properties.')}
			</p>
		{/each}
	{/if}
</div>
