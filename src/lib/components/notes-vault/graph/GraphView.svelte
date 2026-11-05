<!--
	The vault's graph: every note, the [[links]] and relations between them, and (optionally) tags,
	notes not written yet and the Gnos3 data they point to. `mode="local"` shows the open note and
	its neighbours up to a chosen depth (the side panel); `mode="global"` the whole vault.
-->
<script lang="ts">
	import { getContext, onDestroy, onMount, untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import Maximize2 from '@lucide/svelte/icons/maximize-2';
	import Plus from '@lucide/svelte/icons/plus';
	import Minus from '@lucide/svelte/icons/minus';
	import LocateFixed from '@lucide/svelte/icons/locate-fixed';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';
	import Search from '@lucide/svelte/icons/search';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Switch } from '$lib/components/ui/switch/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as NativeSelect from '$lib/components/ui/native-select/index.js';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import { getVaultGraph, type GraphEdge, type GraphNode } from '$lib/apis/note-vaults';
	import { ForceGraph, type GLink, type GNode } from './forceGraph';
	import {
		chartColor,
		currentVault,
		linksVersion,
		noteTypes,
		prefs,
		typeName,
		typeOf
	} from '../vault';
	import { ENTITY_META, opensOutside } from '../entities';
	import TypeIcon from '../TypeIcon.svelte';

	const i18n: any = getContext('i18n');

	let {
		vaultId,
		mode = 'global',
		focusId = null,
		onOpenNote,
		onCreateNote,
		onTag = () => {}
	}: {
		vaultId: string;
		mode?: 'global' | 'local';
		focusId?: string | null;
		onOpenNote: (id: string) => void;
		onCreateNote: (title: string) => void;
		onTag?: (tag: string) => void;
	} = $props();

	type Settings = {
		showTags: boolean;
		showEntities: boolean;
		showGhosts: boolean;
		showOrphans: boolean;
		hideTemplates: boolean;
		colorBy: 'type' | 'folder';
		depth: number;
		linkDistance: number;
		repel: number;
		nodeSize: number;
		showArrows: boolean;
	};
	const DEFAULT_SETTINGS: Settings = {
		showTags: false,
		showEntities: true,
		showGhosts: true,
		showOrphans: true,
		hideTemplates: true,
		colorBy: 'type',
		depth: 1,
		linkDistance: 60,
		repel: 160,
		nodeSize: 1,
		showArrows: false
	};

	const SHOW_OPTIONS = [
		{ key: 'showTags', label: 'Tags' },
		{ key: 'showEntities', label: 'Gnos3 data' },
		{ key: 'showGhosts', label: 'Notes not created yet' },
		{ key: 'showOrphans', label: 'Notes without links' },
		{ key: 'hideTemplates', label: 'Hide templates' }
	];
	const FORCE_OPTIONS = [
		{ key: 'linkDistance', label: 'Link distance', min: 20, max: 200, step: 5 },
		{ key: 'repel', label: 'Repel', min: 20, max: 600, step: 10 },
		{ key: 'nodeSize', label: 'Node size', min: 0.5, max: 2.5, step: 0.1 }
	];

	let settings: Settings = $state({ ...DEFAULT_SETTINGS, ...prefs.get(`graph.${mode}`, {}) });
	let canvas = $state<HTMLCanvasElement | null>(null);
	let graph: ForceGraph | null = null;
	let data = $state<{ nodes: GraphNode[]; edges: GraphEdge[] } | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let filter = $state('');
	let hovered = $state<GNode | null>(null);
	let showControls = $state(false);

	const save = () => prefs.set(`graph.${mode}`, $state.snapshot(settings));

	const load = async () => {
		loading = !data;
		try {
			data = await getVaultGraph(localStorage.token, vaultId);
			error = null;
		} catch (e) {
			error = `${e}`;
		}
		loading = false;
	};

	const FOLDER_COLORS = [
		'chart-1',
		'chart-2',
		'chart-3',
		'chart-4',
		'chart-5',
		'chart-6',
		'chart-7',
		'chart-8'
	];
	const folderColor = (folder: string | undefined) => {
		const top = (folder ?? '').split('/')[0];
		if (!top) return null;
		let h = 0;
		for (const c of top) h = (h * 31 + c.charCodeAt(0)) >>> 0;
		return FOLDER_COLORS[h % FOLDER_COLORS.length];
	};

	const ENTITY_COLORS: Record<string, string> = {
		company: 'chart-2',
		invoice: 'chart-4',
		business_card: 'chart-1',
		document: 'chart-6',
		chat: 'chart-7'
	};

	const view = $derived.by(() => {
		if (!data) return { nodes: [] as GNode[], links: [] as GLink[] };
		const vault = $currentVault;
		const templates = vault?.settings?.templates_folder ?? '';
		let nodes: GraphNode[] = data.nodes.filter((n) => {
			if (n.kind === 'ghost') return settings.showGhosts;
			if (n.kind === 'entity') return settings.showEntities;
			if (n.kind === 'note' && settings.hideTemplates && templates)
				return !(n.folder === templates || n.folder?.startsWith(templates + '/'));
			return true;
		});
		let edges: GraphEdge[] = [...data.edges];
		if (settings.showTags) {
			const tagNodes = new Map<string, GraphNode>();
			for (const n of nodes) {
				for (const tag of n.tags ?? []) {
					const id = `tag:${tag.toLowerCase()}`;
					if (!tagNodes.has(id)) tagNodes.set(id, { id, kind: 'tag', title: `#${tag}` });
					edges.push({ source: n.id, target: id, kind: 'tag' });
				}
			}
			nodes = [...nodes, ...tagNodes.values()];
		}
		const ids = new Set(nodes.map((n) => n.id));
		edges = edges.filter((e) => ids.has(e.source) && ids.has(e.target));

		if (mode === 'local' && focusId) {
			const adjacent = new Map<string, Set<string>>();
			for (const e of edges) {
				if (!adjacent.has(e.source)) adjacent.set(e.source, new Set());
				if (!adjacent.has(e.target)) adjacent.set(e.target, new Set());
				adjacent.get(e.source)!.add(e.target);
				adjacent.get(e.target)!.add(e.source);
			}
			const keep = new Set([focusId]);
			let frontier = [focusId];
			for (let d = 0; d < settings.depth; d++) {
				const next: string[] = [];
				for (const id of frontier) {
					for (const other of adjacent.get(id) ?? []) {
						if (!keep.has(other)) {
							keep.add(other);
							next.push(other);
						}
					}
				}
				frontier = next;
			}
			nodes = nodes.filter((n) => keep.has(n.id));
			edges = edges.filter((e) => keep.has(e.source) && keep.has(e.target));
		} else if (!settings.showOrphans) {
			const linked = new Set(edges.flatMap((e) => [e.source, e.target]));
			nodes = nodes.filter((n) => linked.has(n.id));
		}

		const q = filter.trim().toLocaleLowerCase();
		if (q) {
			const match = new Set(
				nodes.filter((n) => n.title.toLocaleLowerCase().includes(q)).map((n) => n.id)
			);
			nodes = nodes.filter((n) => match.has(n.id));
			edges = edges.filter((e) => match.has(e.source) && match.has(e.target));
		}

		return {
			nodes: nodes.map((n) => ({
				id: n.id,
				kind: n.kind,
				title: n.title || $i18n.t('Untitled'),
				focus: n.id === focusId,
				color:
					n.kind === 'entity'
						? (ENTITY_COLORS[n.entity_type ?? ''] ?? null)
						: n.kind === 'note'
							? settings.colorBy === 'folder'
								? folderColor(n.folder)
								: (typeOf(vault, n.type)?.color ?? null)
							: null
			})) as GNode[],
			links: edges.map((e) => ({ source: e.source, target: e.target, kind: e.kind })) as GLink[]
		};
	});

	const nodeById = $derived(
		new Map<string, GraphNode>((data?.nodes ?? []).map((n) => [n.id, n] as [string, GraphNode]))
	);

	const open = (node: GNode, event: MouseEvent) => {
		const raw = nodeById.get(node.id);
		if (node.kind === 'note') onOpenNote(node.id);
		else if (node.kind === 'ghost') onCreateNote(node.title);
		else if (node.kind === 'tag') onTag(node.title.replace(/^#/, ''));
		else if (node.kind === 'entity' && raw?.href) {
			if (opensOutside(raw.entity_type ?? '') || event.metaKey || event.ctrlKey)
				window.open(raw.href, '_blank');
			else goto(raw.href);
		}
	};

	$effect(() => {
		const v = view;
		untrack(() => graph?.setData(v.nodes, v.links));
	});

	$effect(() => {
		const { linkDistance, repel, nodeSize, showArrows } = settings;
		untrack(() => graph?.setOptions({ linkDistance, repel, nodeSize, showArrows }));
	});

	// Reload when the vault changes or notes were saved / linked.
	let lastVersion = -1;
	let lastVault = '';
	$effect(() => {
		const version = $linksVersion;
		const vault = vaultId;
		untrack(() => {
			if (vault !== lastVault) {
				data = null;
				lastVault = vault;
				load();
			} else if (version !== lastVersion) {
				load();
			}
			lastVersion = version;
		});
	});

	$effect(() => {
		const id = focusId;
		if (mode === 'local' && id) untrack(() => setTimeout(() => graph?.zoomToFit(300), 400));
	});

	onMount(() => {
		if (!canvas) return;
		graph = new ForceGraph(canvas, {
			linkDistance: settings.linkDistance,
			repel: settings.repel,
			nodeSize: settings.nodeSize,
			showArrows: settings.showArrows,
			labelZoom: mode === 'local' ? 0.5 : 0.9,
			onOpen: open,
			onHover: (n) => (hovered = n)
		});
		graph.setData(view.nodes, view.links);
	});

	onDestroy(() => graph?.destroy());

	const hoveredRaw = $derived(hovered ? nodeById.get(hovered.id) : null);
	const usedTypes = $derived.by(() => {
		const keys = new Set((data?.nodes ?? []).map((n) => n.type).filter(Boolean));
		return noteTypes($currentVault).filter((t) => keys.has(t.key));
	});
	const counts = $derived({
		notes: view.nodes.filter((n) => n.kind === 'note').length,
		links: view.links.length
	});
</script>

<div class="relative h-full w-full overflow-hidden bg-background">
	<canvas bind:this={canvas} class="absolute inset-0 block"></canvas>

	{#if loading}
		<div class="absolute inset-0 flex items-center justify-center text-sm text-muted-foreground">
			{$i18n.t('Drawing the graph…')}
		</div>
	{:else if error}
		<div
			class="absolute inset-0 flex items-center justify-center p-6 text-center text-sm text-muted-foreground"
		>
			{$i18n.t('The graph could not be loaded.')}
		</div>
	{:else if data && view.nodes.length === 0}
		<div
			class="absolute inset-0 flex items-center justify-center p-6 text-center text-sm text-muted-foreground"
		>
			{mode === 'local'
				? $i18n.t('This note has no links yet. Type [[ to link it to another note.')
				: filter
					? $i18n.t('No note matches.')
					: $i18n.t('No notes yet.')}
		</div>
	{/if}

	<!-- Toolbar -->
	<div class="absolute top-2 left-2 flex items-center gap-1 {mode === 'local' ? '' : 'right-2'}">
		{#if mode === 'global'}
			<div class="relative w-56 max-w-[50vw]">
				<Search
					class="pointer-events-none absolute top-1/2 left-2.5 z-10 size-3.5 -translate-y-1/2 text-muted-foreground"
				/>
				<Input
					bind:value={filter}
					placeholder={$i18n.t('Filter by title')}
					class="h-8 bg-background/90 pl-8 backdrop-blur"
				/>
			</div>
			<span class="hidden px-2 text-xs text-muted-foreground tabular-nums sm:inline">
				{$i18n.t('{{notes}} notes · {{links}} links', counts)}
			</span>
		{:else}
			<NativeSelect.Root
				size="sm"
				class="w-28 bg-background/90"
				value={String(settings.depth)}
				onchange={(e) => {
					settings.depth = Number((e.currentTarget as HTMLSelectElement).value);
					save();
				}}
				aria-label={$i18n.t('Depth')}
			>
				{#each [1, 2, 3] as d}
					<NativeSelect.Option value={String(d)}
						>{$i18n.t('Depth {{n}}', { n: d })}</NativeSelect.Option
					>
				{/each}
			</NativeSelect.Root>
		{/if}
	</div>

	<div class="absolute top-2 right-2 flex items-center gap-1">
		<Popover.Root bind:open={showControls}>
			<Popover.Trigger>
				{#snippet child({ props })}
					<Button
						{...props}
						variant="outline"
						size="icon-sm"
						class="bg-background/90 backdrop-blur"
						aria-label={$i18n.t('Graph settings')}
					>
						<SlidersHorizontal />
					</Button>
				{/snippet}
			</Popover.Trigger>
			<Popover.Content align="end" class="w-72 space-y-3 text-sm">
				<div class="font-medium">{$i18n.t('Show')}</div>
				{#each SHOW_OPTIONS.filter((o) => mode === 'global' || o.key !== 'showOrphans') as { key, label: text }}
					<div class="flex items-center justify-between gap-2">
						<Label for="g-{mode}-{key}" class="font-normal">{$i18n.t(text)}</Label>
						<Switch
							id="g-{mode}-{key}"
							checked={settings[key as keyof Settings] as boolean}
							onCheckedChange={(v) => {
								(settings as any)[key] = v;
								save();
							}}
						/>
					</div>
				{/each}
				<div class="flex items-center justify-between gap-2">
					<Label class="font-normal">{$i18n.t('Colour by')}</Label>
					<NativeSelect.Root
						size="sm"
						class="w-32"
						value={settings.colorBy}
						onchange={(e) => {
							settings.colorBy = (e.currentTarget as HTMLSelectElement).value as 'type' | 'folder';
							save();
						}}
					>
						<NativeSelect.Option value="type">{$i18n.t('Type')}</NativeSelect.Option>
						<NativeSelect.Option value="folder">{$i18n.t('Folder')}</NativeSelect.Option>
					</NativeSelect.Root>
				</div>
				<div class="border-t pt-3 font-medium">{$i18n.t('Forces')}</div>
				{#each FORCE_OPTIONS as { key, label: text, min, max, step }}
					<label class="block space-y-1">
						<span class="text-xs text-muted-foreground">{$i18n.t(text as string)}</span>
						<input
							type="range"
							class="w-full accent-[var(--primary)]"
							min={min as number}
							max={max as number}
							step={step as number}
							value={settings[key as keyof Settings] as number}
							oninput={(e) => {
								(settings as any)[key] = Number((e.currentTarget as HTMLInputElement).value);
							}}
							onchange={save}
						/>
					</label>
				{/each}
				<div class="flex items-center justify-between gap-2">
					<Label for="g-{mode}-arrows" class="font-normal">{$i18n.t('Arrows')}</Label>
					<Switch
						id="g-{mode}-arrows"
						checked={settings.showArrows}
						onCheckedChange={(v) => {
							settings.showArrows = v;
							save();
						}}
					/>
				</div>
				<Button
					variant="outline"
					size="sm"
					class="w-full"
					onclick={() => {
						settings = { ...DEFAULT_SETTINGS };
						save();
					}}
				>
					{$i18n.t('Reset')}
				</Button>
			</Popover.Content>
		</Popover.Root>
	</div>

	<!-- Zoom -->
	<div class="absolute right-2 bottom-2 flex flex-col gap-1">
		<Tip content={$i18n.t('Zoom in')} side="left">
			<Button
				variant="outline"
				size="icon-sm"
				class="bg-background/90"
				onclick={() => graph?.zoomBy(1.3)}
				aria-label={$i18n.t('Zoom in')}><Plus /></Button
			>
		</Tip>
		<Tip content={$i18n.t('Zoom out')} side="left">
			<Button
				variant="outline"
				size="icon-sm"
				class="bg-background/90"
				onclick={() => graph?.zoomBy(1 / 1.3)}
				aria-label={$i18n.t('Zoom out')}><Minus /></Button
			>
		</Tip>
		<Tip content={$i18n.t('Fit to screen')} side="left">
			<Button
				variant="outline"
				size="icon-sm"
				class="bg-background/90"
				onclick={() => graph?.zoomToFit()}
				aria-label={$i18n.t('Fit to screen')}><Maximize2 /></Button
			>
		</Tip>
		{#if focusId}
			<Tip content={$i18n.t('Centre on this note')} side="left">
				<Button
					variant="outline"
					size="icon-sm"
					class="bg-background/90"
					onclick={() => graph?.centerOn(focusId!)}
					aria-label={$i18n.t('Centre on this note')}><LocateFixed /></Button
				>
			</Tip>
		{/if}
		<Tip content={$i18n.t('Refresh')} side="left">
			<Button
				variant="outline"
				size="icon-sm"
				class="bg-background/90"
				onclick={load}
				aria-label={$i18n.t('Refresh')}><RefreshCw /></Button
			>
		</Tip>
	</div>

	<!-- Legend + hover card -->
	<div
		class="pointer-events-none absolute bottom-2 left-2 flex max-w-[calc(100%-4rem)] flex-col gap-2"
	>
		{#if hoveredRaw}
			{@const t = typeOf($currentVault, hoveredRaw.type)}
			<div
				class="w-fit max-w-72 rounded-lg border bg-popover/95 px-3 py-2 text-xs shadow-sm backdrop-blur"
			>
				<div class="truncate text-sm font-medium text-foreground">
					{hoveredRaw.title || $i18n.t('Untitled')}
				</div>
				<div class="mt-0.5 text-muted-foreground">
					{#if hoveredRaw.kind === 'ghost'}
						{$i18n.t('Not created yet — click to create it')}
					{:else if hoveredRaw.kind === 'entity'}
						{$i18n.t(
							ENTITY_META[hoveredRaw.entity_type as keyof typeof ENTITY_META]?.label ?? 'Gnos3 data'
						)}
					{:else if hoveredRaw.kind === 'tag'}
						{$i18n.t('Tag')}
					{:else}
						{[t ? typeName(t, $i18n) : null, hoveredRaw.folder || null]
							.filter(Boolean)
							.join(' · ') || $i18n.t('Note')}
					{/if}
				</div>
			</div>
		{/if}
		{#if mode === 'global' && settings.colorBy === 'type' && usedTypes.length}
			<div
				class="flex w-fit flex-wrap gap-x-3 gap-y-1 rounded-lg border bg-background/90 px-2.5 py-1.5 text-xs text-muted-foreground backdrop-blur"
			>
				{#each usedTypes as t (t.key)}
					<span class="inline-flex items-center gap-1">
						<TypeIcon icon={t.icon} class="size-3" style="color: {chartColor(t.color)}" />{typeName(
							t,
							$i18n
						)}
					</span>
				{/each}
			</div>
		{/if}
	</div>
</div>
