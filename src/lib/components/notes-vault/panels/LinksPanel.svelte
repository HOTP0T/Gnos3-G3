<!--
	What links here (backlinks, with the sentence they are in), what this note links to, notes that
	name this one without linking it ("Link" turns that mention into a [[link]] in the other note),
	and the Gnos3 data it points to.
-->
<script lang="ts">
	import { getContext } from 'svelte';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import FileText from '@lucide/svelte/icons/file-text';
	import CircleDashed from '@lucide/svelte/icons/circle-dashed';
	import { toast } from 'svelte-sonner';
	import { Button } from '$lib/components/ui/button/index.js';
	import { getNoteLinks, setNoteMarkdown, type NoteLinks } from '$lib/apis/note-vaults';
	import { getNoteById } from '$lib/apis/notes';
	import { chartColor, currentVault, linksVersion, prefs, typeOf, canWrite } from '../vault';
	import { ENTITY_META, opensOutside } from '../entities';
	import { formatWikilink } from '../markdown';
	import { goto } from '$app/navigation';

	const i18n: any = getContext('i18n');

	let {
		noteId,
		noteTitle,
		onOpenNote,
		onCreateNote
	}: {
		noteId: string;
		noteTitle: string;
		onOpenNote: (id: string) => void;
		onCreateNote: (title: string) => void;
	} = $props();

	let links: NoteLinks | null = $state(null);
	let loading = $state(true);
	let open = $state(
		prefs.get('links.open', { backlinks: true, outgoing: true, unlinked: true, entities: true })
	);

	const load = async (id: string) => {
		loading = !links;
		try {
			links = await getNoteLinks(localStorage.token, id);
		} catch {
			links = null;
		}
		loading = false;
	};

	let timer: ReturnType<typeof setTimeout> | null = null;
	$effect(() => {
		const id = noteId;
		$linksVersion;
		if (timer) clearTimeout(timer);
		timer = setTimeout(() => load(id), 250);
	});

	const toggle = (key: keyof typeof open) => {
		open = { ...open, [key]: !open[key] };
		prefs.set('links.open', open);
	};

	const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

	/** Unlinked mention → [[link]], in the other note's Markdown (only for a note still in Markdown;
	 * a note saved by the editor is opened so the person links it there). */
	const linkMention = async (sourceId: string) => {
		const source = await getNoteById(localStorage.token, sourceId).catch(() => null);
		if (!source) return;
		const content = source.data?.content ?? {};
		if (content.json) {
			toast.info($i18n.t('Opened the note: select the name and type [[ to link it.'));
			onOpenNote(sourceId);
			return;
		}
		const md: string = content.md ?? '';
		const re = new RegExp(
			`(?<![\\p{L}\\p{N}_\\[])${escapeRe(noteTitle)}(?![\\p{L}\\p{N}_\\]])`,
			'iu'
		);
		const match = re.exec(md);
		if (!match) return;
		const replaced =
			md.slice(0, match.index) +
			formatWikilink(noteTitle, null, match[0] !== noteTitle ? match[0] : null) +
			md.slice(match.index + match[0].length);
		await setNoteMarkdown(localStorage.token, sourceId, replaced).catch((e: any) =>
			toast.error(`${e}`)
		);
		linksVersion.update((n) => n + 1);
	};

	/** A context line with its [[links]] shown as link text, the link to this note emphasised. */
	const segments = (line: string) => {
		const out: { text: string; link?: boolean; self?: boolean }[] = [];
		let last = 0;
		for (const m of line.matchAll(/\[\[([^\[\]]+?)\]\]/g)) {
			if ((m.index ?? 0) > last) out.push({ text: line.slice(last, m.index) });
			const inner = m[1];
			const [target, alias] = inner.split('|');
			const shown = alias ?? target.split('#')[0];
			out.push({
				text: shown,
				link: true,
				self: target.split('#')[0].trim().toLowerCase() === noteTitle.trim().toLowerCase()
			});
			last = (m.index ?? 0) + m[0].length;
		}
		if (last < line.length) out.push({ text: line.slice(last) });
		return out;
	};

	const mentionSegments = (line: string) => {
		const re = new RegExp(escapeRe(noteTitle), 'ig');
		const out: { text: string; self?: boolean }[] = [];
		let last = 0;
		for (const m of line.matchAll(re)) {
			if ((m.index ?? 0) > last) out.push({ text: line.slice(last, m.index) });
			out.push({ text: m[0], self: true });
			last = (m.index ?? 0) + m[0].length;
		}
		if (last < line.length) out.push({ text: line.slice(last) });
		return out;
	};
</script>

{#snippet header(key: keyof typeof open, label: string, count: number)}
	<button
		type="button"
		class="flex w-full items-center gap-1 px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground"
		onclick={() => toggle(key)}
	>
		<ChevronRight class="size-3.5 transition-transform {open[key] ? 'rotate-90' : ''}" />
		<span class="flex-1 text-left uppercase tracking-wide">{label}</span>
		<span class="tabular-nums">{count}</span>
	</button>
{/snippet}

{#snippet noteButton(note: { id: string; title: string; type: string | null; folder: string })}
	{@const t = typeOf($currentVault, note.type)}
	<button
		type="button"
		class="flex w-full min-w-0 items-center gap-1.5 text-left text-sm font-medium hover:text-link"
		onclick={() => onOpenNote(note.id)}
	>
		<FileText
			class="size-3.5 shrink-0 {t ? '' : 'text-muted-foreground'}"
			style={t ? `color: ${chartColor(t.color)}` : ''}
		/>
		<span class="truncate">{note.title || $i18n.t('Untitled')}</span>
		{#if note.folder}<span
				class="ml-auto shrink-0 truncate pl-2 text-xs font-normal text-muted-foreground"
				>{note.folder}</span
			>{/if}
	</button>
{/snippet}

<div class="h-full overflow-y-auto pb-6">
	{#if loading}
		<div class="p-4 text-sm text-muted-foreground">{$i18n.t('Loading…')}</div>
	{:else if !links}
		<div class="p-4 text-sm text-muted-foreground">
			{$i18n.t('Links are shown for notes in your vaults.')}
		</div>
	{:else}
		{@render header('backlinks', $i18n.t('Linked here'), links.backlinks.length)}
		{#if open.backlinks}
			<div class="space-y-1 px-3 pb-2">
				{#each links.backlinks as item (item.note.id)}
					<div class="rounded-lg border bg-card p-2.5">
						{@render noteButton(item.note)}
						{#each item.properties as prop}
							<div class="mt-1 text-xs text-muted-foreground">
								{$i18n.t('as “{{property}}”', { property: prop })}
							</div>
						{/each}
						{#each item.contexts as line}
							<p class="mt-1.5 line-clamp-3 text-xs leading-relaxed text-muted-foreground">
								{#each segments(line) as seg}
									{#if seg.link}<span
											class={seg.self ? 'rounded bg-primary/10 px-0.5 text-link' : 'text-link'}
											>{seg.text}</span
										>{:else}{seg.text}{/if}
								{/each}
							</p>
						{/each}
					</div>
				{:else}
					<p class="px-1 text-xs text-muted-foreground">{$i18n.t('No note links here yet.')}</p>
				{/each}
			</div>
		{/if}

		{@render header('unlinked', $i18n.t('Mentioned without a link'), links.unlinked.length)}
		{#if open.unlinked}
			<div class="space-y-1 px-3 pb-2">
				{#each links.unlinked as item (item.note.id)}
					<div class="rounded-lg border border-dashed p-2.5">
						<div class="flex items-center gap-2">
							<div class="min-w-0 flex-1">{@render noteButton(item.note)}</div>
							{#if canWrite($currentVault)}
								<Button variant="outline" size="xs" onclick={() => linkMention(item.note.id)}
									>{$i18n.t('Link')}</Button
								>
							{/if}
						</div>
						{#each item.contexts as line}
							<p class="mt-1.5 line-clamp-3 text-xs leading-relaxed text-muted-foreground">
								{#each mentionSegments(line) as seg}
									{#if seg.self}<mark class="rounded bg-warning/15 px-0.5 text-foreground"
											>{seg.text}</mark
										>{:else}{seg.text}{/if}
								{/each}
							</p>
						{/each}
					</div>
				{:else}
					<p class="px-1 text-xs text-muted-foreground">
						{$i18n.t('No other note names this one.')}
					</p>
				{/each}
			</div>
		{/if}

		{@render header('outgoing', $i18n.t('Links from this note'), links.outgoing.length)}
		{#if open.outgoing}
			<div class="space-y-0.5 px-3 pb-2">
				{#each links.outgoing as item, i (i)}
					<div class="flex items-center gap-2 rounded-md px-1 py-1 hover:bg-accent">
						{#if item.note}
							<div class="min-w-0 flex-1">{@render noteButton(item.note)}</div>
						{:else}
							<button
								type="button"
								class="flex min-w-0 flex-1 items-center gap-1.5 text-left text-sm text-muted-foreground hover:text-link"
								onclick={() => onCreateNote(item.title ?? '')}
								title={$i18n.t('Not created yet — click to create it')}
							>
								<CircleDashed class="size-3.5 shrink-0" />
								<span class="truncate">{item.title}</span>
							</button>
						{/if}
						{#if item.property}<span class="shrink-0 text-xs text-muted-foreground"
								>{item.property}</span
							>{/if}
					</div>
				{:else}
					<p class="px-1 text-xs text-muted-foreground">
						{$i18n.t('Type [[ in the note to link another note.')}
					</p>
				{/each}
			</div>
		{/if}

		{#if links.entities.length}
			{@render header('entities', $i18n.t('Gnos3 data'), links.entities.length)}
			{#if open.entities}
				<div class="space-y-0.5 px-3 pb-2">
					{#each links.entities as item, i (i)}
						{@const meta = ENTITY_META[item.entity_type as keyof typeof ENTITY_META]}
						<a
							href={item.href}
							target={opensOutside(item.entity_type) ? '_blank' : undefined}
							class="flex items-center gap-2 rounded-md px-1 py-1 text-sm hover:bg-accent"
							onclick={(e) => {
								if (!opensOutside(item.entity_type) && !e.metaKey && !e.ctrlKey) {
									e.preventDefault();
									goto(item.href);
								}
							}}
						>
							{#if meta}<meta.icon class="size-3.5 shrink-0 text-muted-foreground" />{/if}
							<span class="min-w-0 flex-1 truncate">{item.label ?? item.entity_id}</span>
							<span class="shrink-0 text-xs text-muted-foreground"
								>{item.property ?? $i18n.t(meta?.label ?? '')}</span
							>
						</a>
					{/each}
				</div>
			{/if}
		{/if}
	{/if}
</div>
