<script lang="ts">
	import { onMount, onDestroy, setContext, getContext, tick } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import 'gridstack/dist/gridstack.min.css';

	import {
		getBalanceSheet,
		getProfitLoss,
		getCompanyStats,
		getDashboardLayout,
		saveDashboardLayout,
		type DashboardLayout
	} from '$lib/apis/accounting';
	import SlidersHorizontal from '@lucide/svelte/icons/sliders-horizontal';
	import Plus from '@lucide/svelte/icons/plus';
	import RotateCcw from '@lucide/svelte/icons/rotate-ccw';
	import Check from '@lucide/svelte/icons/check';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import WidgetCard from './WidgetCard.svelte';
	import { createCommonData, COMMON_DATA_CTX } from './store';
	import {
		WIDGETS,
		WIDGET_BY_TYPE,
		defaultLayout,
		type LayoutItem,
		type WidgetCategory
	} from './registry';

	export let companyId: number;

	const i18n: any = getContext('i18n');
	// The context is a store of i18next: read it with $ (i18n.t does not exist on the store).
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);

	// ── Shared common-data store (KPI tiles + alerts read from this) ──
	const common = createCommonData();
	setContext(COMMON_DATA_CTX, common);

	let loading = true;
	let editing = false;
	let dirty = false;
	let saving = false;
	let showCatalog = false;

	let layout: LayoutItem[] = [];
	let els: Record<string, HTMLElement> = {};
	let gridEl: HTMLDivElement;
	let grid: any = null;
	let GridStackCls: any = null;
	let idSeq = 1;

	const categories: WidgetCategory[] = ['KPI', 'Charts', 'Lists', 'Panels'];
	$: catalogByCat = categories.map((c) => ({
		cat: c,
		items: WIDGETS.filter((w) => w.category === c)
	}));

	function newId() {
		return `w${Date.now().toString(36)}${idSeq++}`;
	}

	// Svelte action: set gridstack's hyphenated attributes ONCE, on mount, and
	// never again. This is critical — if these attributes were bound reactively
	// (e.g. an interpolated attr or a spread), Svelte would re-write gs-w/gs-h on
	// every array change and fight gridstack, resizing untouched widgets. gridstack
	// owns positioning after init; Svelte must not touch it.
	function gsItem(node: HTMLElement, params: { item: LayoutItem; def: any }) {
		const { item, def } = params;
		node.setAttribute('gs-id', String(item.id));
		node.setAttribute('gs-x', String(item.x));
		node.setAttribute('gs-y', String(item.y));
		node.setAttribute('gs-w', String(item.w));
		node.setAttribute('gs-h', String(item.h));
		node.setAttribute('gs-min-w', String(def?.minW ?? 2));
		node.setAttribute('gs-min-h', String(def?.minH ?? 2));
		// No `update` handler on purpose: attributes are never re-applied.
		return {};
	}

	// ── Load common data + saved layout ──
	onMount(async () => {
		await Promise.all([loadCommon(), loadLayout()]);
		loading = false;
		await tick();
		await initGrid();
	});

	async function loadCommon() {
		try {
			const now = new Date();
			const monthStart = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
			const monthEnd = dayjs(now).format('YYYY-MM-DD');
			const [stats, balanceSheet, profitLoss] = await Promise.all([
				getCompanyStats(companyId).catch(() => ({})),
				getBalanceSheet({ company_id: companyId }).catch(() => null),
				getProfitLoss({ date_from: monthStart, date_to: monthEnd, company_id: companyId }).catch(
					() => null
				)
			]);
			common.set({ loading: false, stats, balanceSheet, profitLoss });
		} catch {
			common.set({ loading: false, stats: {}, balanceSheet: null, profitLoss: null });
		}
	}

	async function loadLayout() {
		try {
			const res = await getDashboardLayout(companyId);
			const saved = res?.layout as DashboardLayout | undefined;
			if (saved && Array.isArray((saved as any).widgets) && (saved as any).widgets.length) {
				layout = (saved as any).widgets
					.filter((w: any) => WIDGET_BY_TYPE[w.type])
					.map((w: any) => ({
						id: w.id || newId(),
						type: w.type,
						x: w.x ?? 0,
						y: w.y ?? 0,
						w: w.w ?? WIDGET_BY_TYPE[w.type].w,
						h: w.h ?? WIDGET_BY_TYPE[w.type].h,
						options: w.options
					}));
				return;
			}
		} catch {
			// fall through to default
		}
		layout = defaultLayout();
	}

	// ── Gridstack ──
	async function initGrid() {
		if (grid) return;
		const mod = await import('gridstack');
		GridStackCls = mod.GridStack;
		grid = GridStackCls.init(
			{
				column: 12,
				// 64px rows and 8px margins: 16px between cards (design system → Layout), and a
				// 2-row KPI tile fits its label, figure and one footer line.
				cellHeight: 64,
				margin: 8,
				// float:true — widgets stay exactly where the user puts them; moving
				// or resizing one never reflows/compacts the others. Only widgets the
				// dragged item directly collides with get pushed.
				float: true,
				// Start read-only. Edit mode flips this + enables move/resize.
				// No `handle` — the whole item drags, and the corner/edge resize
				// handles coexist (they stop propagation), so both gestures work.
				staticGrid: true,
				resizable: { handles: 'se' },
				columnOpts: { breakpoints: [{ w: 768, c: 1 }], breakpointForWindow: true }
			},
			gridEl
		);

		// Only flag dirty. Never write positions back into the reactive `layout`
		// array here — that would re-render items and disturb gridstack. Positions
		// are read straight from gridstack at save time.
		grid.on('change', () => {
			if (editing) dirty = true;
		});
	}

	// ── Edit mode ──
	function enterEdit() {
		editing = true;
		showCatalog = true;
		// setStatic(false) alone does not reliably re-enable per-widget drag/resize
		// across gridstack versions — call the explicit enablers too.
		if (grid) {
			grid.setStatic(false);
			grid.enableMove(true);
			grid.enableResize(true);
		}
	}

	async function exitEdit() {
		editing = false;
		showCatalog = false;
		if (grid) {
			grid.enableMove(false);
			grid.enableResize(false);
			grid.setStatic(true);
		}
		if (dirty) await persist();
	}

	async function persist() {
		saving = true;
		try {
			// Read live positions straight from gridstack, and merge in each
			// widget's type/options (which gridstack doesn't track) by id.
			const meta: Record<string, LayoutItem> = {};
			for (const it of layout) meta[it.id] = it;
			const nodes = (grid ? (grid.save(false) as any[]) : []).filter((n) => n.id != null);
			const payload: DashboardLayout = {
				version: 1,
				widgets: nodes
					.map((n) => {
						const it = meta[String(n.id)];
						return {
							id: String(n.id),
							type: it?.type,
							x: n.x ?? 0,
							y: n.y ?? 0,
							w: n.w ?? 1,
							h: n.h ?? 1,
							...(it?.options ? { options: it.options } : {})
						};
					})
					.filter((w) => w.type)
			};
			await saveDashboardLayout(companyId, payload);
			dirty = false;
			toast.success(T('Dashboard saved'));
		} catch (err) {
			toast.error(`${err}`);
		}
		saving = false;
	}

	// ── Add / remove widgets ──
	async function addWidget(type: string) {
		const def = WIDGET_BY_TYPE[type];
		if (!def || !grid) return;
		const nodes = grid.save(false) as any[];
		const maxY = nodes.reduce((m, n) => Math.max(m, (n.y ?? 0) + (n.h ?? 1)), 0);
		const item: LayoutItem = {
			id: newId(),
			type,
			x: 0,
			y: maxY,
			w: def.w,
			h: def.h,
			options: def.options
		};
		layout = [...layout, item];
		dirty = true;
		await tick();
		const el = els[item.id];
		if (el) {
			grid.makeWidget(el);
			el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
		}
	}

	function removeWidget(item: LayoutItem) {
		const el = els[item.id];
		if (grid && el) grid.removeWidget(el, false);
		layout = layout.filter((it) => it.id !== item.id);
		dirty = true;
	}

	async function resetDefault() {
		if (!grid) return;
		// remove all current widgets from gridstack, then swap layout
		for (const it of layout) {
			const el = els[it.id];
			if (el) grid.removeWidget(el, false);
		}
		// Fresh ids so Svelte creates brand-new nodes (the mount-once action re-runs
		// and re-applies the default positions/sizes).
		layout = defaultLayout().map((d) => ({ ...d, id: newId() }));
		dirty = true;
		await tick();
		for (const it of layout) {
			const el = els[it.id];
			if (el) grid.makeWidget(el);
		}
	}

	onDestroy(() => {
		if (grid) {
			try {
				grid.destroy(false);
			} catch {}
			grid = null;
		}
	});
</script>

<div class="flex flex-col gap-4">
	<!-- Toolbar -->
	<div class="flex flex-wrap items-center justify-between gap-2">
		<p class="text-sm text-muted-foreground">
			{#if editing}
				{T('Drag to move, resize from the corner, or add widgets below.')}
			{/if}
		</p>
		<div class="flex items-center gap-2">
			{#if editing}
				<Button variant="outline" size="sm" onclick={resetDefault}>
					<RotateCcw />{T('Reset to default')}
				</Button>
				<Button size="sm" onclick={exitEdit} disabled={saving}>
					{#if saving}<Spinner />{:else}<Check />{/if}
					{T('Done')}
				</Button>
			{:else}
				<Button variant="outline" size="sm" onclick={enterEdit} disabled={loading}>
					<SlidersHorizontal />{T('Configure')}
				</Button>
			{/if}
		</div>
	</div>

	<!-- Catalog (edit mode) -->
	{#if editing && showCatalog}
		<Card.Root size="sm" class="border-dashed shadow-none">
			<Card.Header>
				<Card.Title>{T('Add widgets')}</Card.Title>
			</Card.Header>
			<Card.Content class="flex flex-col gap-3">
				{#each catalogByCat as group}
					{#if group.items.length}
						<div class="flex flex-col gap-1.5">
							<div class="text-sm font-medium text-muted-foreground">{T(group.cat)}</div>
							<div class="flex flex-wrap gap-1.5">
								{#each group.items as w}
									<Tip content={T(w.description)}>
										<Button variant="outline" size="xs" onclick={() => addWidget(w.type)}>
											<Plus />{T(w.title)}
										</Button>
									</Tip>
								{/each}
							</div>
						</div>
					{/if}
				{/each}
			</Card.Content>
		</Card.Root>
	{/if}

	{#if loading}
		<div class="flex flex-col gap-4" aria-busy="true">
			<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
				{#each Array(4) as _}<Skeleton class="h-28 rounded-xl" />{/each}
			</div>
			<div class="grid grid-cols-1 gap-4 md:grid-cols-[2fr_1fr]">
				<Skeleton class="h-72 rounded-xl" />
				<Skeleton class="h-72 rounded-xl" />
			</div>
		</div>
	{/if}

	<!-- Grid. NB: use class: directives (classList-based) — never an interpolated
	     class="" attribute here, which would rewrite className on every `editing`
	     change and clobber the classes gridstack adds to this element. The -m-2 cancels
	     gridstack's outer 8px margin so the cards line up with the page edges. -->
	<div
		class="grid-stack -m-2"
		bind:this={gridEl}
		class:is-editing={editing}
		class:invisible={loading}
	>
		{#each layout as item (item.id)}
			{@const def = WIDGET_BY_TYPE[item.type]}
			<div class="grid-stack-item" use:gsItem={{ item, def }} bind:this={els[item.id]}>
				<div class="grid-stack-item-content">
					{#if def}
						<WidgetCard
							title={def.bare ? '' : T(def.title)}
							href={def.link ? def.link(companyId) : null}
							linkLabel={def.linkLabel ? T(def.linkLabel) : ''}
							padded={!def.flush}
							on:remove={() => removeWidget(item)}
						>
							<svelte:component
								this={def.component}
								{companyId}
								options={item.options ?? def.options ?? {}}
							/>
						</WidgetCard>
					{/if}
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	/* Let widget cards fill the gridstack item content box. */
	:global(.grid-stack-item-content) {
		inset: 0;
		overflow: visible;
	}
	/* Edit-only chrome is hidden unless the grid is editing. */
	:global(.grid-stack:not(.is-editing) .wcard-remove),
	:global(.grid-stack:not(.is-editing) .wcard-handle) {
		display: none;
	}
	/* Edit-mode affordances: draggable cursor, no text selection, dashed outline. */
	.grid-stack.is-editing :global(.grid-stack-item) {
		cursor: grab;
	}
	.grid-stack.is-editing :global(.grid-stack-item .grid-stack-item-content) {
		cursor: grab;
		user-select: none;
		-webkit-user-select: none;
	}
	.grid-stack.is-editing :global(.grid-stack-item.ui-draggable-dragging),
	.grid-stack.is-editing :global(.grid-stack-item.ui-draggable-dragging .grid-stack-item-content) {
		cursor: grabbing;
	}
	.grid-stack.is-editing :global(.wcard) {
		border-style: dashed;
		border-color: color-mix(in oklab, var(--ring) 55%, var(--border));
		box-shadow: none;
	}
	/* Links inside widgets would navigate on drop; they come back when editing ends. */
	.grid-stack.is-editing :global(.wcard-link) {
		display: none;
	}
	/* the remove button takes the top-right corner */
	.grid-stack.is-editing :global(.wcard-corner) {
		visibility: hidden;
	}
	.grid-stack.is-editing :global(.wcard a) {
		pointer-events: none;
	}
	/* Resize handles — visible only while editing, with a grabbable hit area. */
	.grid-stack.is-editing :global(.ui-resizable-handle) {
		opacity: 1;
		display: block;
	}
	.grid-stack.is-editing :global(.ui-resizable-se) {
		z-index: 21;
		/* inside the card's corner: gridstack's 8px margin + 3px */
		width: 18px;
		height: 18px;
		right: 11px;
		bottom: 11px;
		background-image: none;
		/* gridstack rotates its own arrow icon; this corner mark must stay upright */
		transform: none;
		border-right: 2px solid var(--ring);
		border-bottom: 2px solid var(--ring);
		border-bottom-right-radius: 6px;
		cursor: se-resize;
	}
	/* Placeholder shown while dragging. */
	:global(.grid-stack .grid-stack-placeholder > .placeholder-content) {
		border: 1px dashed var(--ring);
		border-radius: 0.875rem;
		background: color-mix(in oklab, var(--ring) 6%, transparent);
	}
</style>
