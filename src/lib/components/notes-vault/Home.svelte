<!-- The vault's front page when no note is open: what to do next, recent and pinned notes. -->
<script lang="ts">
	import { getContext } from 'svelte';
	import FilePlus from '@lucide/svelte/icons/file-plus';
	import CalendarDays from '@lucide/svelte/icons/calendar-days';
	import Orbit from '@lucide/svelte/icons/orbit';
	import Search from '@lucide/svelte/icons/search';
	import Pin from '@lucide/svelte/icons/pin';
	import FileText from '@lucide/svelte/icons/file-text';
	import Link2 from '@lucide/svelte/icons/link-2';
	import Hash from '@lucide/svelte/icons/hash';
	import AtSign from '@lucide/svelte/icons/at-sign';
	import Slash from '@lucide/svelte/icons/slash';
	import Users from '@lucide/svelte/icons/users';
	import Lock from '@lucide/svelte/icons/lock';
	import { Kbd } from '$lib/components/ui/kbd/index.js';
	import { canWrite, chartColor, currentVault, tree, typeOf, vaultName, allTags } from './vault';
	import TypeIcon from './TypeIcon.svelte';
	import dayjs from '$lib/dayjs';

	const i18n: any = getContext('i18n');

	let {
		onOpenNote,
		onNewNote,
		onDaily,
		onGraph,
		onSwitcher
	}: {
		onOpenNote: (id: string) => void;
		onNewNote: () => void;
		onDaily: () => void;
		onGraph: () => void;
		onSwitcher: () => void;
	} = $props();

	const notes = $derived($tree?.notes ?? []);
	const recent = $derived([...notes].sort((a, b) => b.updated_at - a.updated_at).slice(0, 8));
	const pinned = $derived(notes.filter((n) => n.is_pinned).slice(0, 8));
	const links = $derived(notes.reduce((s, n) => s + n.links_out, 0));
	const mod =
		typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.platform) ? '⌘' : 'Ctrl';

	const actions = $derived([
		...(canWrite($currentVault)
			? [{ icon: FilePlus, label: 'New note', run: onNewNote, keys: ['Alt', 'N'] }]
			: []),
		...(canWrite($currentVault)
			? [{ icon: CalendarDays, label: "Today's note", run: onDaily, keys: [] as string[] }]
			: []),
		{ icon: Search, label: 'Go to a note', run: onSwitcher, keys: [mod, 'O'] },
		{ icon: Orbit, label: 'Graph view', run: onGraph, keys: [mod, 'Shift', 'G'] }
	]);
</script>

{#snippet noteRow(note: any)}
	{@const t = typeOf($currentVault, note.type)}
	<button
		type="button"
		class="flex w-full items-center gap-2.5 rounded-md px-2 py-1.5 text-left text-sm hover:bg-accent"
		onclick={() => onOpenNote(note.id)}
	>
		{#if t}<TypeIcon
				icon={t.icon}
				class="size-4 shrink-0"
				style="color: {chartColor(t.color)}"
			/>{:else}<FileText class="size-4 shrink-0 text-muted-foreground" />{/if}
		<span class="min-w-0 flex-1 truncate">{note.title || $i18n.t('Untitled')}</span>
		<span class="shrink-0 text-xs text-muted-foreground"
			>{dayjs(note.updated_at / 1e6).fromNow()}</span
		>
	</button>
{/snippet}

<div class="h-full overflow-y-auto">
	<div class="mx-auto max-w-3xl px-6 py-10">
		<div class="flex items-center gap-2 text-sm text-muted-foreground">
			{#if $currentVault?.kind === 'shared'}<Users class="size-4" />{$i18n.t(
					'Shared vault'
				)}{:else}<Lock class="size-4" />{$i18n.t('Personal vault')}{/if}
		</div>
		<h1 class="mt-1 text-3xl font-semibold tracking-tight">{vaultName($currentVault, $i18n)}</h1>
		{#if $currentVault?.description}<p class="mt-1 text-muted-foreground">
				{$currentVault.description}
			</p>{/if}
		<p class="mt-2 text-sm text-muted-foreground tabular-nums">
			{$i18n.t('{{notes}} notes · {{links}} links · {{tags}} tags', {
				notes: notes.length,
				links,
				tags: $allTags.length
			})}
		</p>

		<div class="mt-6 grid gap-2 sm:grid-cols-2">
			{#each actions as action (action.label)}
				<button
					type="button"
					class="flex items-center gap-3 rounded-lg border bg-card p-3 text-left text-sm transition-colors hover:bg-accent"
					onclick={action.run}
				>
					<action.icon class="size-5 text-link" />
					<span class="flex-1 font-medium">{$i18n.t(action.label)}</span>
					{#if action.keys.length}<span class="hidden gap-1 sm:flex"
							>{#each action.keys as k}<Kbd>{k}</Kbd>{/each}</span
						>{/if}
				</button>
			{/each}
		</div>

		{#if pinned.length}
			<h2 class="mt-8 mb-2 flex items-center gap-1.5 text-sm font-medium text-muted-foreground">
				<Pin class="size-4" />{$i18n.t('Pinned')}
			</h2>
			{#each pinned as note (note.id)}{@render noteRow(note)}{/each}
		{/if}

		{#if recent.length}
			<h2 class="mt-8 mb-2 text-sm font-medium text-muted-foreground">
				{$i18n.t('Recently edited')}
			</h2>
			{#each recent as note (note.id)}{@render noteRow(note)}{/each}
		{:else if $tree}
			<div
				class="mt-8 rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground"
			>
				{$i18n.t(
					'This vault is empty. Create a note, or import an Obsidian / Tolaria vault from the vault settings.'
				)}
			</div>
		{/if}

		<h2 class="mt-10 mb-3 text-sm font-medium text-muted-foreground">{$i18n.t('While writing')}</h2>
		<div class="grid gap-3 text-sm sm:grid-cols-2">
			<div class="flex gap-3">
				<Link2 class="mt-0.5 size-4 shrink-0 text-link" /><span
					><Kbd>[[</Kbd>
					{$i18n.t('links another note; a title that does not exist yet creates it.')}</span
				>
			</div>
			<div class="flex gap-3">
				<AtSign class="mt-0.5 size-4 shrink-0 text-link" /><span
					><Kbd>@</Kbd>
					{$i18n.t('links a company, an invoice, a business card, a document or a chat.')}</span
				>
			</div>
			<div class="flex gap-3">
				<Hash class="mt-0.5 size-4 shrink-0 text-link" /><span
					><Kbd>#</Kbd> {$i18n.t('adds a tag (#project/alpha nests it under #project).')}</span
				>
			</div>
			<div class="flex gap-3">
				<Slash class="mt-0.5 size-4 shrink-0 text-link" /><span
					><Kbd>/</Kbd> {$i18n.t('inserts headings, lists, tasks, tables or a template.')}</span
				>
			</div>
		</div>
	</div>
</div>
