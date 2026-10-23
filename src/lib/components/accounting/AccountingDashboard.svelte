<script lang="ts">
	import { onMount, onDestroy, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import {
		getBalanceSheet,
		getProfitLoss,
		getTransactions,
		getPeriods,
		getCompanyStats,
		getAccountingAiStatus
	} from '$lib/apis/accounting';
	import { theme } from '$lib/stores';
	import { convertAmount, convertRowAmount } from '$lib/utils/currency';

	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import Circle from '@lucide/svelte/icons/circle';
	import Lock from '@lucide/svelte/icons/lock';
	import Plus from '@lucide/svelte/icons/plus';
	import Wallet from '@lucide/svelte/icons/wallet';
	import ChartColumn from '@lucide/svelte/icons/chart-column';

	import * as Card from '$lib/components/ui/card/index.js';
	import * as Table from '$lib/components/ui/table/index.js';
	import * as Empty from '$lib/components/ui/empty/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import KpiCard from '$lib/components/gnos3-ui/KpiCard.svelte';
	import StatusBadge from '$lib/components/gnos3-ui/StatusBadge.svelte';
	import AuditTrail from '$lib/components/accounting/AuditTrail.svelte';
	import { chartTheme, pageIsDark } from '$lib/components/accounting/dashboard/palette';

	// NB: not mounted anywhere since the configurable dashboard (dashboard/ConfigurableDashboard)
	// replaced it; kept in step with the design system in case it is used again.

	const i18n: any = getContext('i18n');
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrencyCtx = getContext<Writable<string>>('companyCurrency');

	export let companyId: number;

	$: isDark = pageIsDark($theme);
	$: ct = chartTheme(isDark);

	let loading = true;

	// Stats
	let totalAssets = 0;
	let totalLiabilities = 0;
	let netIncome = 0;
	let draftCount = 0;

	// KPIs from company stats
	let cashPosition = 0;
	let outstandingAP = 0;
	let outstandingAR = 0;
	let unmatchedBankLines = 0;
	let overdueInvoices = 0;
	let overdueAmount = 0;

	// Chart data
	let monthlyRevenueExpenses: Array<{
		period: string;
		revenue: number;
		expenses: number;
	}> = [];

	// Recent transactions
	let recentTransactions: any[] = [];

	// Periods
	let currentPeriod: any = null;

	// Accounting AI status
	let aiStatus: { enabled: boolean; available: boolean; model: string | null } | null = null;

	// Chart instances
	let revenueExpenseCanvas: HTMLCanvasElement;
	let revenueExpenseChart: any = null;
	let Chart: any = null;

	const loadData = async () => {
		loading = true;
		try {
			const now = new Date();
			const monthStart = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
			const monthEnd = dayjs(now).format('YYYY-MM-DD');

			const [balanceSheet, profitLoss, transactions, periods, stats] = await Promise.all([
				getBalanceSheet({ company_id: companyId }),
				getProfitLoss({ date_from: monthStart, date_to: monthEnd, company_id: companyId }),
				getTransactions({ limit: 10, company_id: companyId }),
				getPeriods({ company_id: companyId }),
				getCompanyStats(companyId).catch(() => ({}))
			]);

			totalAssets = balanceSheet?.total_assets ?? 0;
			totalLiabilities = balanceSheet?.total_liabilities ?? 0;
			netIncome = profitLoss?.net_income ?? 0;

			// KPIs
			cashPosition = stats?.cash_position ?? 0;
			outstandingAP = stats?.outstanding_ap ?? 0;
			outstandingAR = stats?.outstanding_ar ?? 0;
			unmatchedBankLines = stats?.unmatched_bank_lines ?? 0;
			overdueInvoices = stats?.overdue_invoices ?? 0;
			overdueAmount = stats?.overdue_amount ?? 0;
			draftCount = stats?.draft_count ?? 0;

			// Recent transactions
			const txList = Array.isArray(transactions)
				? transactions
				: (transactions?.transactions ?? transactions?.items ?? []);
			recentTransactions = txList.slice(0, 10);

			// Build monthly revenue vs expenses data from the last 6 months
			const monthlyMap: Record<string, { revenue: number; expenses: number }> = {};
			for (let i = 5; i >= 0; i--) {
				const d = dayjs().subtract(i, 'month');
				const key = d.format('YYYY-MM');
				monthlyMap[key] = { revenue: 0, expenses: 0 };
			}

			// Fetch P&L for last 6 months
			const sixMonthsAgo = dayjs().subtract(5, 'month').startOf('month').format('YYYY-MM-DD');
			try {
				const fullPL = await getProfitLoss({
					date_from: sixMonthsAgo,
					date_to: monthEnd,
					company_id: companyId
				});
				if (fullPL?.revenue) {
					for (const item of fullPL.revenue) {
						const key = item.period ?? item.month;
						if (key && monthlyMap[key]) {
							monthlyMap[key].revenue += parseFloat(String(item.amount ?? item.balance ?? 0));
						}
					}
				}
				if (fullPL?.expenses) {
					for (const item of fullPL.expenses) {
						const key = item.period ?? item.month;
						if (key && monthlyMap[key]) {
							monthlyMap[key].expenses += Math.abs(
								parseFloat(String(item.amount ?? item.balance ?? 0))
							);
						}
					}
				}
			} catch {
				// If detailed P&L fails, use summary values for current month only
				const currentKey = dayjs().format('YYYY-MM');
				if (monthlyMap[currentKey]) {
					monthlyMap[currentKey].revenue = parseFloat(String(profitLoss?.total_revenue ?? 0));
					monthlyMap[currentKey].expenses = Math.abs(
						parseFloat(String(profitLoss?.total_expenses ?? 0))
					);
				}
			}

			monthlyRevenueExpenses = Object.entries(monthlyMap).map(([period, vals]) => ({
				period,
				revenue: vals.revenue,
				expenses: vals.expenses
			}));

			// Periods
			const periodList = Array.isArray(periods) ? periods : (periods?.items ?? []);
			currentPeriod = periodList.find((p: any) => !p.is_closed) ?? periodList[0] ?? null;
		} catch (err) {
			toast.error(`${err}`);
		}
		loading = false;
	};

	const createCharts = async () => {
		if (!Chart) {
			const module = await import('chart.js/auto');
			Chart = module.default;
		}

		// Monthly revenue vs expenses bar chart
		if (revenueExpenseCanvas && monthlyRevenueExpenses.length) {
			if (revenueExpenseChart) revenueExpenseChart.destroy();

			const t = ct;
			const fmt = (v: number) =>
				`${Number(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${nativeCurrency}`;
			revenueExpenseChart = new Chart(revenueExpenseCanvas, {
				type: 'bar',
				data: {
					labels: monthlyRevenueExpenses.map((d) => d.period),
					datasets: [
						{
							label: $i18n.t('Revenue'),
							data: monthlyRevenueExpenses.map((d) => d.revenue),
							backgroundColor: t.revenue,
							borderRadius: 4,
							barPercentage: 0.7,
							categoryPercentage: 0.8
						},
						{
							label: $i18n.t('Expenses'),
							data: monthlyRevenueExpenses.map((d) => d.expenses),
							backgroundColor: t.expenses,
							borderRadius: 4,
							barPercentage: 0.7,
							categoryPercentage: 0.8
						}
					]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: {
						legend: {
							display: true,
							position: 'top',
							align: 'start',
							labels: {
								color: t.secondary,
								font: { size: 12 },
								boxWidth: 10,
								boxHeight: 10,
								padding: 12
							}
						},
						tooltip: {
							backgroundColor: t.background,
							titleColor: t.primary,
							bodyColor: t.secondary,
							borderColor: t.grid,
							borderWidth: 1,
							padding: 8,
							callbacks: {
								label: (ctx: any) => `${ctx.dataset.label}: ${fmt(ctx.raw)}`
							}
						}
					},
					scales: {
						x: {
							grid: { display: false },
							ticks: { color: t.muted, font: { size: 11 } },
							border: { display: false }
						},
						y: {
							grid: { color: t.grid, drawTicks: false },
							ticks: {
								color: t.muted,
								font: { size: 11 },
								padding: 8,
								callback: (value: number) => value.toLocaleString()
							},
							border: { display: false }
						}
					},
					animation: { duration: 400, easing: 'easeOutQuart' }
				}
			});
		}
	};

	$: if (!loading && revenueExpenseCanvas && isDark !== undefined) {
		createCharts();
	}

	onMount(() => {
		loadData();
		// Load AI status (non-blocking)
		getAccountingAiStatus()
			.then((s) => (aiStatus = s))
			.catch(() => (aiStatus = { enabled: false, available: false, model: null }));
	});

	onDestroy(() => {
		if (revenueExpenseChart) {
			revenueExpenseChart.destroy();
			revenueExpenseChart = null;
		}
	});

	// ─── Currency conversion ────────────────────────────────────────────────────
	$: nativeCurrency = $companyCurrencyCtx || 'EUR';

	// Try to get native currency from company data when loaded
	const _trySetNativeCurrency = (currency: string) => {
		if (currency) nativeCurrency = currency;
	};

	function cvt(
		amount: any,
		date?: string
	): { display: string; original: string; hasRate: boolean } {
		const num = typeof amount === 'string' ? parseFloat(amount) : (amount ?? 0);
		if (!num || !$displayCurrency || $displayCurrency === nativeCurrency) {
			return { display: '', original: '', hasRate: true };
		}
		const result = convertAmount(num, nativeCurrency, $displayCurrency, $exchangeRates ?? [], date);
		return {
			display: result.hasRate
				? result.converted.toLocaleString(undefined, {
						minimumFractionDigits: 2,
						maximumFractionDigits: 2
					})
				: '',
			original: num.toLocaleString(undefined, {
				minimumFractionDigits: 2,
				maximumFractionDigits: 2
			}),
			hasRate: result.hasRate
		};
	}

	$: isConverting = $displayCurrency && $displayCurrency !== nativeCurrency;

	// A KPI figure as text: converted to the display currency when one is chosen and a rate exists.
	const kpiValue = (value: number, _display?: string): string => {
		if (isConverting) {
			const c = cvt(value);
			if (c.hasRate) return `${c.display} ${$displayCurrency}`;
		}
		return formatCurrency(value);
	};
	const kpiOriginal = (value: number, _display?: string): string => {
		if (!isConverting) return '';
		const c = cvt(value);
		return c.hasRate ? `${c.original} ${nativeCurrency}` : '';
	};

	const formatCurrency = (value: number | string): string => {
		const num = typeof value === 'string' ? parseFloat(value) : value;
		const cur = nativeCurrency || 'EUR';
		return `${num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${cur}`;
	};
</script>

{#if loading}
	<div class="flex flex-col gap-4" aria-busy="true">
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			{#each Array(4) as _}<Skeleton class="h-[118px] rounded-xl" />{/each}
		</div>
		<Skeleton class="h-64 rounded-xl" />
	</div>
{:else}
	<div class="flex flex-col gap-4">
		<!-- AI Status Indicator -->
		{#if aiStatus?.enabled}
			<div class="flex items-center gap-2 text-sm text-muted-foreground">
				{#if aiStatus.available}
					<CircleCheck class="size-4 text-success" aria-hidden="true" />
				{:else}
					<Circle class="size-4" aria-hidden="true" />
				{/if}
				<span>
					{$i18n.t('Accounting AI')}
					{aiStatus.available ? $i18n.t('Online') : $i18n.t('Offline')}
					{#if aiStatus.model && aiStatus.available}({aiStatus.model}){/if}
				</span>
			</div>
		{/if}

		<!-- KPIs: plain figures; what needs attention carries a badge with a word -->
		<div class="grid grid-cols-[repeat(auto-fit,minmax(min(12.5rem,100%),1fr))] gap-4">
			{#each [{ label: 'Total Assets', v: totalAssets }, { label: 'Total Liabilities', v: totalLiabilities }, { label: 'Net Income (Current Month)', v: netIncome }] as k}
				<KpiCard label={$i18n.t(k.label)} value={kpiValue(k.v, $displayCurrency)}>
					{#snippet footer()}
						{#if kpiOriginal(k.v, $displayCurrency)}<span class="tabular-nums"
								>{kpiOriginal(k.v, $displayCurrency)}</span
							>{/if}
					{/snippet}
				</KpiCard>
			{/each}
			<KpiCard
				label={$i18n.t('Draft Entries')}
				value={draftCount}
				href="/accounting/company/{companyId}/entries"
			>
				{#snippet action()}
					{#if draftCount > 0}<Badge variant="warning">{$i18n.t('Pending', { context: 'gnos3' })}</Badge>{/if}
				{/snippet}
			</KpiCard>
			<KpiCard label={$i18n.t('Cash Position')} value={formatCurrency(cashPosition)} />
			<KpiCard label={$i18n.t('Accounts Receivable')} value={formatCurrency(outstandingAR)} />
			<KpiCard label={$i18n.t('Accounts Payable')} value={formatCurrency(outstandingAP)} />
			<KpiCard
				label={$i18n.t('Overdue Invoices')}
				value={overdueInvoices}
				href="/accounting/company/{companyId}/invoices"
			>
				{#snippet footer()}
					{#if overdueInvoices > 0}<span class="tabular-nums">{formatCurrency(overdueAmount)}</span
						>{/if}
				{/snippet}
			</KpiCard>
		</div>

		<div class="grid grid-cols-1 gap-4 lg:grid-cols-[2fr_1fr]">
			<!-- Revenue vs Expenses (revenue aqua, expenses orange) -->
			<Card.Root>
				<Card.Header>
					<Card.Title>{$i18n.t('Monthly Revenue vs Expenses')}</Card.Title>
				</Card.Header>
				<Card.Content>
					{#if monthlyRevenueExpenses.length === 0}
						<Empty.Root class="p-6">
							<Empty.Header>
								<Empty.Media variant="icon"><ChartColumn /></Empty.Media>
								<Empty.Title>{$i18n.t('No data')}</Empty.Title>
							</Empty.Header>
						</Empty.Root>
					{:else}
						<div class="h-56">
							<canvas
								bind:this={revenueExpenseCanvas}
								role="img"
								aria-label={$i18n.t('Monthly Revenue vs Expenses')}
							></canvas>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			<div class="flex flex-col gap-4">
				<!-- Alerts -->
				{#if draftCount > 0 || unmatchedBankLines > 0 || overdueInvoices > 0}
					<Card.Root size="sm">
						<Card.Header><Card.Title>{$i18n.t('Alerts')}</Card.Title></Card.Header>
						<Card.Content>
							<ul class="divide-y">
								{#if draftCount > 0}
									<li class="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
										<TriangleAlert class="size-4 shrink-0 text-warning" aria-hidden="true" />
										<span class="min-w-0 flex-1 font-medium"
											>{draftCount} {$i18n.t('draft entries awaiting review')}</span
										>
										<Button
											variant="outline"
											size="xs"
											href="/accounting/company/{companyId}/entries">{$i18n.t('View')}</Button
										>
									</li>
								{/if}
								{#if unmatchedBankLines > 0}
									<li class="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
										<TriangleAlert class="size-4 shrink-0 text-warning" aria-hidden="true" />
										<span class="min-w-0 flex-1 font-medium"
											>{unmatchedBankLines} {$i18n.t('unmatched bank lines')}</span
										>
										<Button variant="outline" size="xs" href="/accounting/company/{companyId}/bank"
											>{$i18n.t('Reconcile')}</Button
										>
									</li>
								{/if}
								{#if overdueInvoices > 0}
									<li class="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
										<CircleAlert class="size-4 shrink-0 text-destructive" aria-hidden="true" />
										<span class="min-w-0 flex-1 font-medium"
											>{overdueInvoices} {$i18n.t('overdue invoices')}</span
										>
										<Button
											variant="outline"
											size="xs"
											href="/accounting/company/{companyId}/invoices">{$i18n.t('View')}</Button
										>
									</li>
								{/if}
							</ul>
						</Card.Content>
					</Card.Root>
				{/if}

				<!-- Quick Actions -->
				<Card.Root size="sm">
					<Card.Header><Card.Title>{$i18n.t('Quick Actions')}</Card.Title></Card.Header>
					<Card.Content
						class="grid grid-cols-[repeat(auto-fill,minmax(min(10rem,100%),1fr))] gap-2"
					>
						<Button
							variant="outline"
							size="sm"
							class="justify-start"
							href="/accounting/company/{companyId}/entries"
						>
							<Plus />{$i18n.t('New Journal Entry')}
						</Button>
						<Button
							variant="outline"
							size="sm"
							class="justify-start"
							href="/accounting/company/{companyId}/payments"
						>
							<Wallet />{$i18n.t('Record Payment')}
						</Button>
					</Card.Content>
				</Card.Root>

				<!-- Accounting Period Summary -->
				{#if currentPeriod}
					<Card.Root size="sm">
						<Card.Header>
							<Card.Title>{$i18n.t('Current Accounting Period')}</Card.Title>
						</Card.Header>
						<Card.Content class="flex flex-col gap-1">
							<div class="flex flex-wrap items-center gap-2">
								<span class="font-medium">
									{currentPeriod.name ??
										currentPeriod.label ??
										`${currentPeriod.start_date} - ${currentPeriod.end_date}`}
								</span>
								<Badge variant="status">
									{#if !currentPeriod.is_closed}
										<Circle class="text-success" aria-hidden="true" />{$i18n.t('Open')}
									{:else}
										<Lock aria-hidden="true" />{$i18n.t('Closed')}
									{/if}
								</Badge>
							</div>
							{#if currentPeriod.start_date && currentPeriod.end_date}
								<span class="text-sm text-muted-foreground tabular-nums">
									{dayjs(currentPeriod.start_date).format('YYYY-MM-DD')} — {dayjs(
										currentPeriod.end_date
									).format('YYYY-MM-DD')}
								</span>
							{/if}
						</Card.Content>
					</Card.Root>
				{/if}
			</div>
		</div>

		<div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
			<!-- Recent Transactions -->
			{#if recentTransactions.length > 0}
				<Card.Root class="gap-0 pb-0">
					<Card.Header class="pb-4">
						<Card.Title>{$i18n.t('Recent Transactions')}</Card.Title>
						<Card.Action>
							<Button variant="link" size="sm" href="/accounting/company/{companyId}/entries"
								>{$i18n.t('View All')}</Button
							>
						</Card.Action>
					</Card.Header>
					<div class="border-t">
						<Table.Root class="text-[13px]">
							<Table.Header class="bg-muted/50">
								<Table.Row class="hover:bg-transparent">
									<Table.Head class="pl-6">{$i18n.t('Date')}</Table.Head>
									<Table.Head>{$i18n.t('Type')}</Table.Head>
									<Table.Head>{$i18n.t('Description')}</Table.Head>
									<Table.Head class="text-right">{$i18n.t('Total')}</Table.Head>
									<Table.Head class="pr-6">{$i18n.t('Status')}</Table.Head>
								</Table.Row>
							</Table.Header>
							<Table.Body>
								{#each recentTransactions as transaction}
									{@const c = convertRowAmount(
										transaction.total ?? transaction.amount ?? 0,
										transaction.currency,
										$displayCurrency,
										nativeCurrency,
										$exchangeRates ?? [],
										transaction.transaction_date,
										transaction.exchange_rate
									)}
									<Table.Row
										class="cursor-pointer"
										tabindex={0}
										onclick={() =>
											goto(`/accounting/company/${companyId}/entries?id=${transaction.id}`)}
										onkeydown={(e: KeyboardEvent) => {
											if (e.key === 'Enter')
												goto(`/accounting/company/${companyId}/entries?id=${transaction.id}`);
										}}
									>
										<Table.Cell class="pl-6 tabular-nums">
											{transaction.transaction_date
												? dayjs(transaction.transaction_date).format('YYYY-MM-DD')
												: '—'}
										</Table.Cell>
										<Table.Cell>
											<Badge variant="outline" class="font-normal"
												>{(transaction.transaction_type ?? '—').replace(/_/g, ' ')}</Badge
											>
										</Table.Cell>
										<Table.Cell class="max-w-[200px] truncate">
											{transaction.description ?? transaction.memo ?? '—'}
										</Table.Cell>
										<Table.Cell class="text-right tabular-nums">
											{#if c.converting && c.hasRate}
												{c.display} <span class="text-xs text-muted-foreground">{c.to}</span>
											{:else if c.converting}
												{c.original} <span class="text-xs text-muted-foreground">{c.from}</span>
												<TriangleAlert
													class="inline size-3.5 text-warning"
													aria-label={$i18n.t('No exchange rate available')}
												/>
											{:else}
												{c.original} <span class="text-xs text-muted-foreground">{c.from}</span>
											{/if}
										</Table.Cell>
										<Table.Cell class="pr-6">
											<StatusBadge kind="entry" status={transaction.status ?? 'draft'} />
										</Table.Cell>
									</Table.Row>
								{/each}
							</Table.Body>
						</Table.Root>
					</div>
				</Card.Root>
			{/if}

			<!-- Activity / Audit Trail -->
			<Card.Root>
				<Card.Header><Card.Title>{$i18n.t('Recent Activity')}</Card.Title></Card.Header>
				<Card.Content><AuditTrail {companyId} limit={10} /></Card.Content>
			</Card.Root>
		</div>
	</div>
{/if}
