<script lang="ts">
	import { onMount, onDestroy, getContext, tick } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import ChevronRight from '@lucide/svelte/icons/chevron-right';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import Receipt from '@lucide/svelte/icons/receipt';

	import {
		getInvoices,
		getVendors,
		getSpendingSummary,
		getNeedsReview,
		getProcessingInvoices,
		getInvoiceStats
	} from '$lib/apis/invoices';

	import K4miDocLink from '$lib/components/common/K4miDocLink.svelte';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Alert from '$lib/components/ui/alert/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import KpiCard from '$lib/components/gnos3-ui/KpiCard.svelte';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';

	const i18n: any = getContext('i18n');

	let loading = true;
	let loadError = '';

	// Stats
	let totalInvoices = 0;
	let needsReviewCount = 0;
	let vendorCount = 0;

	// Chart data
	let monthlyData: Array<{ period: string; total_amount: number; invoice_count: number }> = [];
	let vendorData: Array<{ period: string; total_amount: number; invoice_count: number }> = [];

	// Needs review list
	let reviewInvoices: any[] = [];

	// Processing invoices
	let processingCount = 0;
	let processingInvoices: any[] = [];

	// Background refresh: a cheap /stats heartbeat runs for as long as the page is
	// mounted, so an invoice uploaded to K4mi *after* the dashboard was opened
	// still shows up as "processing" without a manual reload.
	const POLL_INTERVAL_MS = 5000;
	let refreshInterval: ReturnType<typeof setInterval> | null = null;
	let polling = false;

	// Chart instance (monthly spending; vendors are plain bars)
	let monthlyCanvas: HTMLCanvasElement;
	let monthlyChart: any = null;
	let Chart: any = null;
	let themeObserver: MutationObserver | null = null;

	const num = (v: any) => {
		const n = parseFloat(String(v));
		return isFinite(n) ? n : 0;
	};
	const fmtAmount = (v: any) =>
		num(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	const fmtCompact = (v: any) =>
		new Intl.NumberFormat(undefined, { notation: 'compact', maximumFractionDigits: 1 }).format(
			num(v)
		);

	const loadData = async ({ silent = false } = {}) => {
		if (!silent) {
			loading = true;
			loadError = '';
		}
		try {
			const [stats, vendors, monthly, byVendor, review, processing] = await Promise.all([
				getInvoiceStats(localStorage.token),
				getVendors(localStorage.token),
				getSpendingSummary(localStorage.token, { period: 'monthly' }),
				getSpendingSummary(localStorage.token, { period: 'by_vendor' }),
				getNeedsReview(localStorage.token),
				getProcessingInvoices(localStorage.token)
			]);

			vendorCount = vendors?.length ?? 0;
			totalInvoices = stats?.total ?? 0;
			needsReviewCount = review?.length ?? 0;
			reviewInvoices = (review ?? []).slice(0, 10);

			processingCount = stats?.processing ?? 0;
			processingInvoices = (processing?.invoices ?? []).slice(0, 10);

			const nextMonthly = monthly ?? [];
			const chartsChanged = JSON.stringify(nextMonthly) !== JSON.stringify(monthlyData);
			monthlyData = nextMonthly;
			vendorData = byVendor ?? [];

			// A silent reload keeps the page on screen; the reactive block below only
			// rebuilds the chart on the initial (non-silent) load, so redraw here
			// when the spending data actually moved.
			if (silent && chartsChanged) {
				createCharts();
			}
		} catch (err) {
			if (!silent) {
				loadError = `${err}`;
				toast.error(`${err}`);
			}
		}
		if (!silent) loading = false;
	};

	const pollStats = async () => {
		if (polling || loading) return;
		polling = true;
		try {
			const stats = await getInvoiceStats(localStorage.token);
			if (!stats) return;
			const remoteProcessing = stats.processing ?? 0;
			const remoteTotal = stats.total ?? 0;
			// Reload while anything is in flight (the processing list changes as
			// extractions finish), and once more when the counts settle.
			if (
				remoteProcessing > 0 ||
				remoteProcessing !== processingCount ||
				remoteTotal !== totalInvoices
			) {
				await loadData({ silent: true });
			}
		} catch {
			// transient — next tick retries
		} finally {
			polling = false;
		}
	};

	// Chart colours come from the theme tokens, read when the chart is (re)built.
	const cssVar = (name: string, fallback: string) =>
		getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;

	const createCharts = async () => {
		if (!Chart) {
			const module = await import('chart.js/auto');
			Chart = module.default;
		}
		await tick();

		if (!monthlyCanvas || !monthlyData.length) return;
		if (monthlyChart) monthlyChart.destroy();

		const bar = cssVar('--chart-1', '#2a78d6');
		const muted = cssVar('--muted-foreground', '#6b7280');
		const grid = cssVar('--border', '#e5e7eb');
		const popover = cssVar('--popover', '#ffffff');
		const popoverFg = cssVar('--popover-foreground', '#111827');
		const family = getComputedStyle(document.body).fontFamily || 'sans-serif';

		monthlyChart = new Chart(monthlyCanvas, {
			type: 'bar',
			data: {
				labels: monthlyData.map((d) => d.period),
				datasets: [
					{
						label: $i18n.t('Monthly Spending'),
						data: monthlyData.map((d) => num(d.total_amount)),
						backgroundColor: bar,
						hoverBackgroundColor: bar,
						borderRadius: 4,
						borderSkipped: 'start',
						maxBarThickness: 28,
						barPercentage: 0.8,
						categoryPercentage: 0.8
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { display: false },
					tooltip: {
						backgroundColor: popover,
						titleColor: popoverFg,
						bodyColor: popoverFg,
						borderColor: grid,
						borderWidth: 1,
						cornerRadius: 8,
						padding: 8,
						displayColors: false,
						titleFont: { family, size: 12, weight: '500' },
						bodyFont: { family, size: 12 },
						callbacks: {
							label: (ctx: any) => fmtAmount(ctx.raw)
						}
					}
				},
				scales: {
					x: {
						grid: { display: false },
						ticks: { color: muted, font: { family, size: 11 } },
						border: { color: grid }
					},
					y: {
						grid: { color: grid, drawTicks: false },
						ticks: {
							color: muted,
							font: { family, size: 11 },
							padding: 8,
							maxTicksLimit: 5,
							callback: (value: number) => fmtCompact(value)
						},
						border: { display: false }
					}
				},
				animation: { duration: 400, easing: 'easeOutQuart' }
			}
		});
	};

	$: if (!loading && monthlyCanvas) {
		createCharts();
	}

	// Spending by vendor: top five and the rest, largest first.
	$: vendorSorted = [...vendorData].sort((a, b) => num(b.total_amount) - num(a.total_amount));
	$: vendorTop = vendorSorted.slice(0, 5);
	$: vendorRest = vendorSorted.slice(5);
	$: vendorOther = vendorRest.reduce((s, d) => s + num(d.total_amount), 0);
	$: vendorMax = Math.max(1, ...vendorTop.map((d) => num(d.total_amount)), vendorOther);

	const openVendor = (invoice: any) =>
		goto(`/invoices/data?vendor=${encodeURIComponent(invoice.vendor_name)}`);

	onMount(() => {
		loadData();
		refreshInterval = setInterval(pollStats, POLL_INTERVAL_MS);
		// Rebuild the chart when the theme flips (the <html> class changes).
		themeObserver = new MutationObserver(() => {
			if (monthlyChart) createCharts();
		});
		themeObserver.observe(document.documentElement, {
			attributes: true,
			attributeFilter: ['class']
		});
	});

	onDestroy(() => {
		themeObserver?.disconnect();
		if (refreshInterval) {
			clearInterval(refreshInterval);
			refreshInterval = null;
		}
		if (monthlyChart) {
			monthlyChart.destroy();
			monthlyChart = null;
		}
	});
</script>

<div class="flex flex-col gap-4">
	<div class="flex items-center justify-between gap-2">
		<h1 class="text-2xl font-semibold tracking-tight">{$i18n.t('Invoices')}</h1>
		<Button variant="outline" size="sm" onclick={() => loadData()} disabled={loading}>
			{#if loading}<Spinner />{:else}<RefreshCw />{/if}
			{$i18n.t('Refresh')}
		</Button>
	</div>

	{#if loadError && !loading}
		<Alert.Root variant="destructive">
			<CircleAlert />
			<Alert.Title>{$i18n.t('Could not load the dashboard.')}</Alert.Title>
			<Alert.Description>
				<p>{loadError}</p>
				<Button variant="outline" size="sm" class="mt-2" onclick={() => loadData()}>
					<RefreshCw />{$i18n.t('Retry')}
				</Button>
			</Alert.Description>
		</Alert.Root>
	{/if}

	{#if loading}
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			{#each Array(4) as _}<Skeleton class="h-[104px] rounded-xl" />{/each}
		</div>
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(20rem,100%),1fr))] gap-4">
			<Skeleton class="h-72 rounded-xl" />
			<Skeleton class="h-72 rounded-xl" />
		</div>
	{:else if !loadError}
		{#if processingCount > 0}
			<Alert.Root>
				<LoaderCircle class="animate-spin motion-reduce:animate-none" />
				<Alert.Title>
					{processingCount}
					{processingCount === 1
						? $i18n.t('invoice is currently being processed')
						: $i18n.t('invoices are currently being processed')}
				</Alert.Title>
				<Alert.Description>{$i18n.t('This page will update automatically.')}</Alert.Description>
			</Alert.Root>
		{/if}

		<!-- KPI cards -->
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			<KpiCard label={$i18n.t('Total Invoices')} value={totalInvoices.toLocaleString()} />
			<KpiCard label={$i18n.t('Processing')} value={processingCount.toLocaleString()}>
				{#snippet action()}
					{#if processingCount > 0}
						<LoaderCircle
							class="size-4 animate-spin text-muted-foreground motion-reduce:animate-none"
							aria-hidden="true"
						/>
					{/if}
				{/snippet}
			</KpiCard>
			<KpiCard
				label={$i18n.t('Needs Attention')}
				value={needsReviewCount.toLocaleString()}
				href="/invoices/data?needs_review=true"
			>
				{#snippet action()}
					{#if needsReviewCount > 0}<Badge variant="warning">{$i18n.t('Review')}</Badge>{/if}
				{/snippet}
				{#snippet footer()}
					<span class="inline-flex items-center gap-1 text-link"
						>{$i18n.t('Open the review list')}<ArrowRight class="size-3.5" /></span
					>
				{/snippet}
			</KpiCard>
			<KpiCard label={$i18n.t('Vendors')} value={vendorCount.toLocaleString()} />
		</div>

		{#if totalInvoices === 0}
			<Empty.Root class="border border-dashed">
				<Empty.Header>
					<Empty.Media variant="icon"><Receipt /></Empty.Media>
					<Empty.Title>{$i18n.t('No invoices yet.')}</Empty.Title>
					<Empty.Description>
						{$i18n.t('Tag a K4mi document with')} <code>invoice</code>
						{$i18n.t('to get started.')}
					</Empty.Description>
				</Empty.Header>
			</Empty.Root>
		{:else}
			<!-- Charts -->
			<div class="grid grid-cols-[repeat(auto-fit,minmax(min(20rem,100%),1fr))] gap-4">
				<Card.Root>
					<Card.Header>
						<Card.Title>{$i18n.t('Monthly Spending')}</Card.Title>
						<Card.Description>{$i18n.t('Invoice totals per month')}</Card.Description>
					</Card.Header>
					<Card.Content>
						{#if monthlyData.length === 0}
							<div class="flex h-56 items-center justify-center text-sm text-muted-foreground">
								{$i18n.t('No data')}
							</div>
						{:else}
							<div class="h-56" role="img" aria-label={$i18n.t('Monthly Spending')}>
								<canvas bind:this={monthlyCanvas}></canvas>
							</div>
						{/if}
					</Card.Content>
					{#if monthlyData.length > 0}
						<Card.Footer>
							<Collapsible.Root class="w-full">
								<Collapsible.Trigger
									class="group inline-flex items-center gap-1.5 rounded-sm text-sm font-medium text-muted-foreground hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
								>
									<ChevronRight
										class="size-4 transition-transform group-data-[state=open]:rotate-90 motion-reduce:transition-none"
									/>
									{$i18n.t('Data table')}
								</Collapsible.Trigger>
								<Collapsible.Content>
									<div class="mt-3 max-h-64 overflow-y-auto rounded-md border">
										<Table.Root>
											<Table.Header class="bg-muted/50">
												<Table.Row class="hover:bg-transparent">
													<Table.Head>{$i18n.t('Month')}</Table.Head>
													<Table.Head class="text-right">{$i18n.t('Invoices')}</Table.Head>
													<Table.Head class="text-right">{$i18n.t('Total')}</Table.Head>
												</Table.Row>
											</Table.Header>
											<Table.Body>
												{#each monthlyData as d}
													<Table.Row>
														<Table.Cell class="tabular-nums">{d.period}</Table.Cell>
														<Table.Cell class="text-right tabular-nums"
															>{d.invoice_count ?? '—'}</Table.Cell
														>
														<Table.Cell class="text-right tabular-nums"
															>{fmtAmount(d.total_amount)}</Table.Cell
														>
													</Table.Row>
												{/each}
											</Table.Body>
										</Table.Root>
									</div>
								</Collapsible.Content>
							</Collapsible.Root>
						</Card.Footer>
					{/if}
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title>{$i18n.t('Spending by Vendor')}</Card.Title>
						<Card.Description>{$i18n.t('Top 5 and the rest')}</Card.Description>
					</Card.Header>
					<Card.Content>
						{#if vendorData.length === 0}
							<div class="flex h-56 items-center justify-center text-sm text-muted-foreground">
								{$i18n.t('No data')}
							</div>
						{:else}
							<ul class="grid gap-2.5">
								{#each vendorTop as d}
									<li
										class="grid grid-cols-[minmax(6rem,9rem)_1fr_auto] items-center gap-3 text-[13px]"
										title="{d.period}: {fmtAmount(d.total_amount)}"
									>
										<span class="truncate">{d.period}</span>
										<div class="h-5">
											<div
												class="h-full min-w-0.5 rounded-r bg-chart-1"
												style="width: {(num(d.total_amount) / vendorMax) * 100}%"
											></div>
										</div>
										<span class="text-right tabular-nums">{fmtCompact(d.total_amount)}</span>
									</li>
								{/each}
								{#if vendorRest.length > 0}
									<li
										class="grid grid-cols-[minmax(6rem,9rem)_1fr_auto] items-center gap-3 text-[13px] text-muted-foreground"
										title="{$i18n.t('Other')} ({vendorRest.length}): {fmtAmount(vendorOther)}"
									>
										<span class="truncate">{$i18n.t('Other')} ({vendorRest.length})</span>
										<div class="h-5">
											<div
												class="h-full min-w-0.5 rounded-r bg-muted-foreground/45"
												style="width: {(vendorOther / vendorMax) * 100}%"
											></div>
										</div>
										<span class="text-right tabular-nums">{fmtCompact(vendorOther)}</span>
									</li>
								{/if}
							</ul>
						{/if}
					</Card.Content>
				</Card.Root>
			</div>

			<!-- Needs review -->
			{#if reviewInvoices.length > 0}
				<Card.Root>
					<Card.Header>
						<Card.Title>{$i18n.t('Invoices Needing Review')}</Card.Title>
						<Card.Description>{$i18n.t('Low confidence or flagged in K4mi')}</Card.Description>
						<Card.Action>
							<Button variant="ghost" size="sm" href="/invoices/data?needs_review=true">
								{$i18n.t('View All')}<ArrowRight />
							</Button>
						</Card.Action>
					</Card.Header>
					<Card.Content>
						<div class="overflow-hidden rounded-md border">
							<Table.Root>
								<Table.Header class="bg-muted/50">
									<Table.Row class="hover:bg-transparent">
										<Table.Head>{$i18n.t('Vendor')}</Table.Head>
										<Table.Head>{$i18n.t('Invoice #')}</Table.Head>
										<Table.Head>{$i18n.t('Date')}</Table.Head>
										<Table.Head class="text-right">{$i18n.t('Total')}</Table.Head>
										<Table.Head>{$i18n.t('Confidence')}</Table.Head>
										<Table.Head>{$i18n.t('K4mi')}</Table.Head>
									</Table.Row>
								</Table.Header>
								<Table.Body>
									{#each reviewInvoices as invoice}
										<Table.Row
											class="cursor-pointer"
											tabindex={0}
											onclick={() => openVendor(invoice)}
											onkeydown={(e: KeyboardEvent) => {
												if (e.key === 'Enter') openVendor(invoice);
											}}
										>
											<Table.Cell class="max-w-[16rem] truncate font-medium">
												{invoice.vendor_name ?? '—'}
											</Table.Cell>
											<Table.Cell class="font-mono text-[13px]">
												{#if invoice.invoice_number}{invoice.invoice_number}{:else}<span
														class="text-muted-foreground">—</span
													>{/if}
											</Table.Cell>
											<Table.Cell class="tabular-nums">
												{#if invoice.invoice_date}{dayjs(invoice.invoice_date).format(
														'YYYY-MM-DD'
													)}{:else}<span class="text-muted-foreground">—</span>{/if}
											</Table.Cell>
											<Table.Cell class="text-right tabular-nums">
												{#if invoice.total_amount !== null && invoice.total_amount !== undefined}
													{invoice.currency ? `${invoice.currency} ` : ''}{fmtAmount(
														invoice.total_amount
													)}
												{:else}
													<span class="text-muted-foreground">—</span>
												{/if}
											</Table.Cell>
											<Table.Cell>
												{#if invoice.confidence_score !== null && invoice.confidence_score !== undefined}
													<StatusBadge kind="confidence" status={invoice.confidence_score} />
												{:else}
													<span class="text-muted-foreground">—</span>
												{/if}
											</Table.Cell>
											<Table.Cell>
												<K4miDocLink
													docId={invoice.k4mi_document_id}
													extraClass="font-mono text-[13px] text-link underline-offset-4 hover:underline"
													stopPropagation
												>
													#{invoice.k4mi_document_id}
												</K4miDocLink>
											</Table.Cell>
										</Table.Row>
									{/each}
								</Table.Body>
							</Table.Root>
						</div>
					</Card.Content>
				</Card.Root>
			{/if}
		{/if}
	{/if}
</div>
