<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import {
		getAPAging,
		getARAging,
		exportAPAging,
		exportARAging,
		getTransactionInvoices,
		setTransactionInvoices,
		getUnmatchedBankLines,
		matchBankStatement,
		type AgingParams
	} from '$lib/apis/accounting';
	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';
	import InvoiceSelector from '$lib/components/accounting/InvoiceSelector.svelte';
	import type { Writable } from 'svelte/store';
	import { convertAmount } from '$lib/utils/currency';
	import ReportAmount from '$lib/components/accounting/ReportAmount.svelte';

	import Download from '@lucide/svelte/icons/download';
	import Search from '@lucide/svelte/icons/search';
	import ArrowUp from '@lucide/svelte/icons/arrow-up';
	import ArrowDown from '@lucide/svelte/icons/arrow-down';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';
	import ArrowLeftRight from '@lucide/svelte/icons/arrow-left-right';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';
	import Inbox from '@lucide/svelte/icons/inbox';

	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import Tip from '$lib/components/gnos3-ui/Tip.svelte';
	import StatusBadge, { STATUS_MAP } from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import { cn } from '$lib/utils/shadcn.js';

	const i18n: any = getContext('i18n');
	export let companyId: number;
	export let reportType: 'ap' | 'ar' = 'ap';

	let loading = false;
	let loadError = '';
	let exporting = false;
	let rawData: any = null;
	let asOf = new Date().toISOString().slice(0, 10);

	// Display-currency conversion (company-wide selector). Aging is in base currency;
	// scale the summary buckets + per-row balances by the base→display rate as of `asOf`.
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrency = getContext<Writable<string>>('companyCurrency');
	$: baseCcy = rawData?.currency || $companyCurrency || 'EUR';
	$: converting = !!($displayCurrency && baseCcy && $displayCurrency !== baseCcy);
	$: fx =
		converting && rawData
			? convertAmount(1, baseCcy, $displayCurrency, $exchangeRates ?? [], asOf)
			: null;
	$: factor = converting ? (fx?.hasRate ? fx.rate : null) : 1;
	$: noRate = converting && !fx?.hasRate;
	$: displayCcy = converting ? $displayCurrency : baseCcy;
	$: fxProps = { factor, converting, displayCcy, baseCcy, zeroText: '—' };
	$: data = rawData;

	// Filters
	let q = '';
	let bucket = '';
	let minBalance: number | null = null;
	let maxBalance: number | null = null;
	// Sort
	let sortBy: 'name' | 'balance' | 'days' | 'bucket' = 'balance';
	let sortDir: 'asc' | 'desc' = 'desc';

	// Drill-down modal (shownRow keeps the content while the dialog animates out)
	let modalRow: any = null;
	let shownRow: any = null;
	$: if (modalRow) shownRow = modalRow;

	// Invoice linking (from the drill-down, for journal items)
	let showInvoiceSelector = false;
	let linkTargetItem: any = null;
	let linking = false;

	const openLinkPicker = (item: any) => {
		linkTargetItem = item;
		showInvoiceSelector = true;
	};

	const handleLinkSelect = async (e: CustomEvent) => {
		const invoice = e.detail;
		if (!linkTargetItem?.transaction_id || !invoice?.id) return;
		linking = true;
		try {
			const existing = (linkTargetItem.linked_invoices ?? []).map((li: any) => li.invoice_id);
			const next = Array.from(new Set([...existing, invoice.id]));
			await setTransactionInvoices(linkTargetItem.transaction_id, next);
			toast.success($i18n.t('Invoice linked'));
			await refreshModal();
		} catch (err) {
			toast.error(`${err}`);
		}
		linking = false;
	};

	const unlinkInvoice = async (item: any, invoiceId: number) => {
		linking = true;
		try {
			const next = (item.linked_invoices ?? [])
				.map((li: any) => li.invoice_id)
				.filter((id: number) => id !== invoiceId);
			await setTransactionInvoices(item.transaction_id, next);
			toast.success($i18n.t('Invoice unlinked'));
			await refreshModal();
		} catch (err) {
			toast.error(`${err}`);
		}
		linking = false;
	};

	// After a link/match change, reload the report and re-point the open modal at the fresh row.
	const refreshModal = async () => {
		const party = modalRow?.vendor_or_customer;
		await load();
		if (party && data?.rows) {
			modalRow = data.rows.find((r: any) => r.vendor_or_customer === party) ?? null;
		}
	};

	// Reconcile a journal item to a bank statement line (closes it in the aging).
	let reconcileItem: any = null;
	let bankCandidates: any[] = [];
	let loadingCandidates = false;

	const openReconcile = async (item: any) => {
		reconcileItem = reconcileItem?.transaction_id === item.transaction_id ? null : item;
		bankCandidates = [];
		if (!reconcileItem) return;
		loadingCandidates = true;
		try {
			// Prefer exact-amount lines; the match endpoint requires the amounts to balance.
			bankCandidates = await getUnmatchedBankLines(companyId, {
				amount: Number(item.balance),
				tolerance: 0.01,
				limit: 25
			});
		} catch (err) {
			toast.error(`${err}`);
		}
		loadingCandidates = false;
	};

	const doReconcile = async (line: any) => {
		if (!reconcileItem?.transaction_id) return;
		linking = true;
		try {
			await matchBankStatement(line.id, reconcileItem.transaction_id);
			toast.success($i18n.t('Reconciled to bank line'));
			reconcileItem = null;
			bankCandidates = [];
			await refreshModal();
		} catch (err) {
			toast.error(`${err}`);
		}
		linking = false;
	};

	const entityLabel = reportType === 'ap' ? 'Vendor' : 'Customer';
	const title = reportType === 'ap' ? 'Accounts Payable Aging' : 'Accounts Receivable Aging';

	const buildParams = (): AgingParams => ({
		company_id: companyId,
		as_of: asOf,
		q: q || undefined,
		bucket: bucket || undefined,
		min_balance: minBalance ?? undefined,
		max_balance: maxBalance ?? undefined,
		sort_by: sortBy,
		sort_dir: sortDir
	});

	const load = async () => {
		loading = true;
		loadError = '';
		try {
			const fn = reportType === 'ap' ? getAPAging : getARAging;
			rawData = await fn(buildParams());
		} catch (err) {
			loadError = `${err}`;
			toast.error(`${err}`);
		}
		loading = false;
	};

	const doExport = async () => {
		exporting = true;
		try {
			await (reportType === 'ap' ? exportAPAging : exportARAging)(buildParams());
		} catch (err) {
			toast.error(`${err}`);
		}
		exporting = false;
	};

	// Reload when sort or the select/number filters change (only if we've loaded once).
	const reloadIfLoaded = () => {
		if (data) load();
	};

	// Debounced reload for the free-text search.
	let qTimer: any;
	const onSearchInput = () => {
		clearTimeout(qTimer);
		qTimer = setTimeout(() => {
			if (data) load();
		}, 350);
	};

	const setSort = (col: 'name' | 'balance' | 'days' | 'bucket') => {
		if (sortBy === col) {
			sortDir = sortDir === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = col;
			sortDir = col === 'name' ? 'asc' : 'desc';
		}
		reloadIfLoaded();
	};

	const ariaSort = (col: string) =>
		sortBy === col ? (sortDir === 'asc' ? 'ascending' : 'descending') : undefined;

	const clearFilters = () => {
		q = '';
		bucket = '';
		minBalance = null;
		maxBalance = null;
		reloadIfLoaded();
	};

	const toggleBucket = (b: string) => {
		bucket = bucket === b ? '' : b;
		reloadIfLoaded();
	};

	$: hasFilters = q || bucket || minBalance != null || maxBalance != null;

	const fmt = (v: any): string => {
		const n = typeof v === 'string' ? parseFloat(v) : (v ?? 0);
		if (n === 0) return '—';
		return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	};

	// Aging bucket → badge (icon + word, never colour alone): the design system's status map.
	const BUCKET_BADGE = STATUS_MAP.aging;
	const bucketTone = (b: string) => {
		const spec = BUCKET_BADGE[b];
		if (!spec) return '';
		if (spec.tone === 'success') return 'text-success';
		return spec.variant === 'warning'
			? 'text-warning'
			: spec.variant === 'danger'
				? 'text-destructive'
				: '';
	};

	// The drill-down dialog stays open (and lets the invoice picker take focus) while the picker is
	// up. The picker closes itself on the same Escape / outside click before our handler runs, so
	// whether it was open is noted when the event starts (window, capture phase).
	let pickerOpenAtEventStart = false;
	const notePicker = () => (pickerOpenAtEventStart = showInvoiceSelector);
	const keepOpenWhilePicking = (e: Event) => {
		if (showInvoiceSelector || pickerOpenAtEventStart) e.preventDefault();
	};

	// Dense report table: 13px, 6px row padding, 12px at the outer edges (design system → Reports).
	const TABLE =
		'text-[13px] [&_td]:py-1.5 [&_td:first-child]:pl-3 [&_th:first-child]:pl-3 [&_td:last-child]:pr-3 [&_th:last-child]:pr-3';
	const SORT_BTN =
		'-mx-1 inline-flex items-center gap-1 rounded-sm px-1 hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none';
</script>

{#snippet bucketBadge(b: string)}
	{#if BUCKET_BADGE[b]}
		<StatusBadge kind="aging" status={b} class="tabular-nums" />
	{:else}
		<span class="text-muted-foreground">{b ?? '—'}</span>
	{/if}
{/snippet}

{#snippet sortHead(col: 'name' | 'balance' | 'days' | 'bucket', label: string, cls: string)}
	<Table.Head class={cls} aria-sort={ariaSort(col)}>
		<button type="button" class={SORT_BTN} onclick={() => setSort(col)}>
			{label}
			{#if sortBy === col}
				{#if sortDir === 'asc'}<ArrowUp class="size-3.5 text-muted-foreground" />{:else}<ArrowDown
						class="size-3.5 text-muted-foreground"
					/>{/if}
			{/if}
		</button>
	</Table.Head>
{/snippet}

<div class="flex min-w-0 flex-col gap-4">
	<!-- Controls -->
	<div class="flex flex-wrap items-end gap-2">
		<div class="grid gap-1.5">
			<Label for="aging-as-of-{reportType}">{$i18n.t('As of')}</Label>
			<Input
				id="aging-as-of-{reportType}"
				type="date"
				class="h-8 w-40"
				bind:value={asOf}
				onchange={reloadIfLoaded}
			/>
		</div>
		<div class="grid min-w-[10rem] grow gap-1.5 sm:max-w-72">
			<Label for="aging-q-{reportType}">{$i18n.t('Search')} {$i18n.t(entityLabel)}</Label>
			<div class="relative">
				<Search
					class="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground"
				/>
				<Input
					id="aging-q-{reportType}"
					type="search"
					class="h-8 pl-8"
					placeholder={$i18n.t('Name contains…')}
					bind:value={q}
					oninput={onSearchInput}
				/>
			</div>
		</div>
		<div class="grid gap-1.5">
			<Label for="aging-min-{reportType}">{$i18n.t('Min balance')}</Label>
			<Input
				id="aging-min-{reportType}"
				type="number"
				class="h-8 w-28 text-right tabular-nums"
				bind:value={minBalance}
				onchange={reloadIfLoaded}
			/>
		</div>
		<div class="grid gap-1.5">
			<Label for="aging-max-{reportType}">{$i18n.t('Max balance')}</Label>
			<Input
				id="aging-max-{reportType}"
				type="number"
				class="h-8 w-28 text-right tabular-nums"
				bind:value={maxBalance}
				onchange={reloadIfLoaded}
			/>
		</div>
		<Button size="sm" disabled={loading} onclick={load}>
			{#if loading}<Spinner />{/if}
			{$i18n.t('Generate', { context: 'gnos3' })}
		</Button>
		{#if data}
			<Button variant="outline" size="sm" onclick={doExport} disabled={exporting}>
				{#if exporting}<Spinner />{:else}<Download />{/if}
				{$i18n.t('Export Excel')}
			</Button>
		{/if}
		{#if hasFilters}
			<Button variant="ghost" size="sm" onclick={clearFilters}>
				<X />
				{$i18n.t('Clear filters')}
			</Button>
		{/if}
	</div>

	{#if loading}
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(10rem,100%),1fr))] gap-4">
			{#each Array(5) as _}
				<Skeleton class="h-[74px] rounded-xl" />
			{/each}
		</div>
		<div class="flex flex-col gap-2 rounded-md border p-3">
			{#each Array(6) as _}
				<Skeleton class="h-6 w-full" />
			{/each}
		</div>
	{:else if loadError}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load the report.')}</Alert.Title>
			<Alert.Description>{loadError}</Alert.Description>
			<Alert.Action>
				<Button variant="outline" size="sm" onclick={load}>{$i18n.t('Retry')}</Button>
			</Alert.Action>
		</Alert.Root>
	{:else if data}
		{#if displayCcy}
			<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
				<span>{$i18n.t('Currency')}: {displayCcy}</span>
				{#if noRate}
					<span class="inline-flex items-center gap-1 text-foreground">
						<TriangleAlert class="size-4 text-warning" />
						({$i18n.t('no rate for')}
						{$displayCurrency}, {$i18n.t('showing')}
						{baseCcy})
					</span>
				{/if}
			</div>
		{/if}
		<!-- Summary cards (click to filter by bucket) -->
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(10rem,100%),1fr))] gap-4">
			{#each [{ k: 'current', label: $i18n.t('Current'), val: data.summary.current }, { k: '31-60', label: '31–60', val: data.summary.days_31_60 }, { k: '61-90', label: '61–90', val: data.summary.days_61_90 }, { k: '90+', label: '90+', val: data.summary.over_90 }] as card}
				{@const spec = BUCKET_BADGE[card.k]}
				<button
					type="button"
					aria-pressed={bucket === card.k}
					title={$i18n.t('Filter by this bucket')}
					onclick={() => toggleBucket(card.k)}
					class={cn(
						'flex min-w-0 flex-col gap-1 rounded-xl border bg-card px-4 py-3 text-left shadow-sm transition-colors hover:bg-accent/40 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none',
						bucket === card.k && 'border-ring ring-[3px] ring-ring/30'
					)}
				>
					<span class="flex items-center gap-1.5 text-sm text-muted-foreground">
						{#if spec.icon}
							<spec.icon class={cn('size-4', bucketTone(card.k))} aria-hidden="true" />
						{/if}
						{card.label}
					</span>
					<span class="text-lg leading-7 font-semibold tabular-nums"
						><ReportAmount value={card.val} {...fxProps} /></span
					>
				</button>
			{/each}
			<div class="flex min-w-0 flex-col gap-1 rounded-xl border bg-muted/50 px-4 py-3">
				<span class="text-sm text-muted-foreground">{$i18n.t('Total')}</span>
				<span class="text-lg leading-7 font-semibold tabular-nums"
					><ReportAmount value={data.summary.total} {...fxProps} /></span
				>
			</div>
		</div>

		{#if data.rows.length === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><Inbox /></Empty.Media>
					<Empty.Title>{$i18n.t('No outstanding balances')}</Empty.Title>
					{#if hasFilters}
						<Empty.Description
							>{$i18n.t('Clear the filters to see every balance.')}</Empty.Description
						>
					{/if}
				</Empty.Header>
				{#if hasFilters}
					<Empty.Content>
						<Button variant="outline" size="sm" onclick={clearFilters}
							>{$i18n.t('Clear filters')}</Button
						>
					</Empty.Content>
				{/if}
			</Empty.Root>
		{:else}
			<div class="overflow-hidden rounded-md border">
				<Table.Root class={TABLE}>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							{@render sortHead('name', $i18n.t(entityLabel), '')}
							<Table.Head class="text-right">{$i18n.t('Items')}</Table.Head>
							<Table.Head class="min-w-28 text-right">{$i18n.t('Original')}</Table.Head>
							<Table.Head class="min-w-28 text-right">{$i18n.t('Paid')}</Table.Head>
							{@render sortHead('balance', $i18n.t('Balance'), 'min-w-28 text-right')}
							{@render sortHead('days', $i18n.t('Days'), 'text-right')}
							{@render sortHead('bucket', $i18n.t('Bucket'), '')}
							<Table.Head class="w-16"><span class="sr-only">{$i18n.t('View')}</span></Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each data.rows as row}
							<Table.Row
								class="cursor-pointer"
								tabindex={0}
								onclick={() => (modalRow = row)}
								onkeydown={(e: KeyboardEvent) => {
									if (e.key === 'Enter' || e.key === ' ') {
										e.preventDefault();
										modalRow = row;
									}
								}}
							>
								<Table.Cell class="max-w-[220px] truncate font-medium"
									>{row.vendor_or_customer}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums">{row.item_count}</Table.Cell>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.original_amount} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums"
									><ReportAmount value={row.paid_amount} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right font-medium tabular-nums"
									><ReportAmount value={row.balance} {...fxProps} /></Table.Cell
								>
								<Table.Cell class="text-right tabular-nums">{row.days_outstanding}</Table.Cell>
								<Table.Cell>{@render bucketBadge(row.bucket)}</Table.Cell>
								<Table.Cell class="text-right">
									<span class="inline-flex items-center gap-0.5 text-link"
										>{$i18n.t('View')}<ChevronRight class="size-3.5" aria-hidden="true" /></span
									>
								</Table.Cell>
							</Table.Row>
						{/each}
					</Table.Body>
					<Table.Footer>
						<Table.Row class="hover:bg-transparent">
							<Table.Cell colspan={4}>{$i18n.t('Total')}</Table.Cell>
							<Table.Cell class="text-right tabular-nums"
								><ReportAmount value={data.summary.total} {...fxProps} /></Table.Cell
							>
							<Table.Cell colspan={3}></Table.Cell>
						</Table.Row>
					</Table.Footer>
				</Table.Root>
			</div>
		{/if}
	{:else}
		<Empty.Root class="border border-dashed">
			<Empty.Header>
				<Empty.Media variant="icon"><FileSpreadsheet /></Empty.Media>
				<Empty.Title>{$i18n.t(title)}</Empty.Title>
				<Empty.Description>{$i18n.t('Choose a date, then Generate.')}</Empty.Description>
			</Empty.Header>
		</Empty.Root>
	{/if}
</div>

<svelte:window on:keydown|capture={notePicker} on:pointerdown|capture={notePicker} />

<!-- Drill-down: the open items of one vendor / customer -->
<Dialog.Root
	open={!!modalRow}
	onOpenChange={(v) => {
		if (!v) modalRow = null;
	}}
>
	<Dialog.Content
		class="max-h-[90vh] overflow-y-auto sm:max-w-3xl"
		trapFocus={!showInvoiceSelector}
		onInteractOutside={keepOpenWhilePicking}
		onEscapeKeydown={keepOpenWhilePicking}
	>
		{#if shownRow}
			<Dialog.Header>
				<p class="text-xs text-muted-foreground">{$i18n.t(title)}</p>
				<Dialog.Title>{shownRow.vendor_or_customer}</Dialog.Title>
				<Dialog.Description>
					{shownRow.item_count}
					{$i18n.t('open items')} · {$i18n.t('Balance')}
					<span class="font-medium text-foreground tabular-nums">{fmt(shownRow.balance)}</span>
				</Dialog.Description>
			</Dialog.Header>
			<div class="min-w-0 overflow-hidden rounded-md border">
				<Table.Root class={TABLE}>
					<Table.Header class="bg-muted/50">
						<Table.Row class="hover:bg-transparent">
							<Table.Head>{$i18n.t('Type')}</Table.Head>
							<Table.Head>{$i18n.t('Reference')}</Table.Head>
							<Table.Head>{$i18n.t('Date')}</Table.Head>
							<Table.Head>{$i18n.t('Due')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Original')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Paid')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Balance')}</Table.Head>
							<Table.Head class="text-right">{$i18n.t('Days')}</Table.Head>
							<Table.Head>{$i18n.t('Bucket')}</Table.Head>
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each shownRow.items as it}
							<Table.Row>
								<Table.Cell>
									{#if it.is_invoice}
										<Badge variant="outline">{$i18n.t('Invoice')}</Badge>
									{:else}
										<Badge variant="secondary">{$i18n.t('Journal')}</Badge>
									{/if}
								</Table.Cell>
								<Table.Cell class="max-w-[240px] font-mono text-[13px] whitespace-normal">
									{#if it.is_invoice && it.k4mi_document_id}
										<K4miDocLink docId={it.k4mi_document_id} title={$i18n.t('Open in K4mi')}
											>{it.reference ?? '—'}</K4miDocLink
										>
									{:else}
										<div class="truncate">{it.reference ?? '—'}</div>
										<!-- Journal item: show + manage linked invoices -->
										<div class="mt-1 flex flex-wrap items-center gap-1 font-sans">
											{#each it.linked_invoices ?? [] as li}
												<Badge variant="outline" class="gap-1 pr-0.5 font-normal">
													<K4miDocLink docId={li.k4mi_document_id} title={$i18n.t('Open in K4mi')}
														>{li.invoice_number ?? `#${li.invoice_id}`}</K4miDocLink
													>
													<Tip content={$i18n.t('Unlink')}>
														<button
															type="button"
															class="inline-flex size-4 items-center justify-center rounded-sm text-muted-foreground hover:bg-accent hover:text-destructive focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none disabled:opacity-50"
															aria-label={$i18n.t('Unlink')}
															disabled={linking}
															onclick={(e) => {
																e.stopPropagation();
																unlinkInvoice(it, li.invoice_id);
															}}><X class="size-3" /></button
														>
													</Tip>
												</Badge>
											{/each}
											<Button
												variant="outline"
												size="xs"
												class="h-6 border-dashed"
												disabled={linking}
												onclick={(e) => {
													e.stopPropagation();
													openLinkPicker(it);
												}}><Plus />{$i18n.t('Link invoice')}</Button
											>
											{#if it.transaction_id}
												<Button
													variant="outline"
													size="xs"
													class="h-6 border-dashed"
													aria-expanded={reconcileItem?.transaction_id === it.transaction_id}
													disabled={linking}
													onclick={(e) => {
														e.stopPropagation();
														openReconcile(it);
													}}><ArrowLeftRight />{$i18n.t('Reconcile')}</Button
												>
											{/if}
										</div>
									{/if}
								</Table.Cell>
								<Table.Cell class="tabular-nums">{it.invoice_date ?? '—'}</Table.Cell>
								<Table.Cell class="tabular-nums">{it.due_date ?? '—'}</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(it.original_amount)}</Table.Cell>
								<Table.Cell class="text-right tabular-nums">{fmt(it.paid_amount)}</Table.Cell>
								<Table.Cell class="text-right font-medium tabular-nums"
									>{fmt(it.balance)}</Table.Cell
								>
								<Table.Cell class="text-right tabular-nums">{it.days_outstanding}</Table.Cell>
								<Table.Cell>{@render bucketBadge(it.bucket)}</Table.Cell>
							</Table.Row>
							{#if reconcileItem && reconcileItem.transaction_id === it.transaction_id}
								<Table.Row class="bg-muted/50 hover:bg-muted/50">
									<Table.Cell colspan={9} class="whitespace-normal">
										<div class="mb-2 text-sm font-medium">
											{$i18n.t('Match to an unmatched bank line')}
											<span class="text-muted-foreground tabular-nums">({fmt(it.balance)})</span>
										</div>
										{#if loadingCandidates}
											<div class="flex items-center gap-2 text-muted-foreground">
												<Spinner />
												{$i18n.t('Loading…')}
											</div>
										{:else if bankCandidates.length === 0}
											<p class="text-sm text-muted-foreground">
												{$i18n.t('No matching unmatched bank lines found for this amount.')}
											</p>
										{:else}
											<div class="flex flex-col gap-1">
												{#each bankCandidates as line}
													<button
														type="button"
														class="flex w-full items-center justify-between gap-3 rounded-md border bg-card px-3 py-2 text-left transition-colors hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none disabled:opacity-50"
														disabled={linking}
														onclick={(e) => {
															e.stopPropagation();
															doReconcile(line);
														}}
													>
														<div class="min-w-0">
															<div class="truncate">
																{line.description ?? line.reference ?? `#${line.id}`}
															</div>
															<div
																class="flex flex-wrap items-center gap-x-1.5 text-xs text-muted-foreground tabular-nums"
															>
																{line.transaction_date ?? ''} · {line.bank_account_name ?? ''} ·
																<StatusBadge kind="bank" status={line.match_status} bare />
															</div>
														</div>
														<div class="font-medium whitespace-nowrap tabular-nums">
															{fmt(line.amount)}
														</div>
													</button>
												{/each}
											</div>
										{/if}
									</Table.Cell>
								</Table.Row>
							{/if}
						{/each}
					</Table.Body>
				</Table.Root>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>

<!-- The invoice picker opens as its own dialog on top of the drill-down -->
<InvoiceSelector bind:show={showInvoiceSelector} on:select={handleLinkSelect} />
