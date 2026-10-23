<script lang="ts">
	// Generic KPI tile (design system → Cards & KPIs: label, a 28px tabular figure, an optional
	// badge at the top right, one footer line). `metric` (from the widget's registry options)
	// selects which number to show; the value is read from the shared common-data store so all
	// KPI tiles share a single batch of API calls. Figures are plain ink: what needs attention
	// carries a badge with a word, never a coloured number.
	import { getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import ArrowRight from '@lucide/svelte/icons/arrow-right';
	import { Badge, type BadgeVariant } from '$lib/components/ui/badge/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { COMMON_DATA_CTX, type CommonData } from '../store';
	import { money, fmtNumber } from '../format';

	export let companyId: number;
	export let options: { metric?: string } = {};

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	const common = getContext<Writable<CommonData>>(COMMON_DATA_CTX);
	const displayCurrency = getContext<Writable<string>>('displayCurrency');
	const exchangeRates = getContext<Writable<any[]>>('exchangeRates');
	const companyCurrencyCtx = getContext<Writable<string>>('companyCurrency');

	$: nativeCurrency = ($companyCurrencyCtx as any) || 'EUR';

	type Kind = 'money' | 'count' | 'ratio';
	interface Metric {
		label: string;
		kind: Kind;
		value: (d: CommonData) => number;
		/** footer line (already formatted) */
		sub?: (d: CommonData) => string | null;
		/** badge when the figure needs attention */
		badge?: (v: number) => { variant: BadgeVariant; label: string } | null;
		/** the page where it is dealt with (a link while not configuring) */
		href?: (id: number) => string;
	}

	const METRICS: Record<string, Metric> = {
		assets: {
			label: 'Total Assets',
			kind: 'money',
			value: (d) => d.balanceSheet?.total_assets ?? 0
		},
		liabilities: {
			label: 'Total Liabilities',
			kind: 'money',
			value: (d) => d.balanceSheet?.total_liabilities ?? 0
		},
		net_income: {
			label: 'Net Income (Current Month)',
			kind: 'money',
			value: (d) => d.profitLoss?.net_income ?? 0
		},
		cash: { label: 'Cash Position', kind: 'money', value: (d) => d.stats?.cash_position ?? 0 },
		ar: { label: 'Accounts Receivable', kind: 'money', value: (d) => d.stats?.outstanding_ar ?? 0 },
		ap: { label: 'Accounts Payable', kind: 'money', value: (d) => d.stats?.outstanding_ap ?? 0 },
		overdue: {
			label: 'Overdue Invoices',
			kind: 'count',
			value: (d) => d.stats?.overdue_invoices ?? 0,
			sub: (d) =>
				(d.stats?.overdue_invoices ?? 0) > 0
					? `${fmtNumber(d.stats?.overdue_amount ?? 0)} ${nativeCurrency}`
					: null,
			badge: (v) => (v > 0 ? { variant: 'danger', label: T('Overdue') } : null),
			href: (id) => `/accounting/company/${id}/invoices`
		},
		drafts: {
			label: 'Draft Entries',
			kind: 'count',
			value: (d) => d.stats?.draft_count ?? 0,
			badge: (v) => (v > 0 ? { variant: 'warning', label: T('Review') } : null),
			href: (id) => `/accounting/company/${id}/entries`
		},
		unmatched: {
			label: 'Unmatched Bank Lines',
			kind: 'count',
			value: (d) => d.stats?.unmatched_bank_lines ?? 0,
			badge: (v) => (v > 0 ? { variant: 'warning', label: T('Reconcile') } : null),
			href: (id) => `/accounting/company/${id}/bank`
		},
		current_ratio: {
			label: 'Assets / Liabilities',
			kind: 'ratio',
			value: (d) => {
				const l = d.balanceSheet?.total_liabilities ?? 0;
				return l ? (d.balanceSheet?.total_assets ?? 0) / l : 0;
			},
			badge: (v) => (v > 0 && v < 1 ? { variant: 'warning', label: T('Below 1') } : null)
		}
	};

	$: metric = METRICS[options?.metric ?? 'cash'] ?? METRICS.cash;
	$: loading = $common.loading;
	$: rawValue = metric.value($common);
	$: badge = metric.badge ? metric.badge(rawValue) : null;
	$: subText = metric.sub ? metric.sub($common) : null;
	$: href = metric.href ? metric.href(companyId) : null;
	$: mv =
		metric.kind === 'money'
			? money(rawValue, nativeCurrency, $displayCurrency, $exchangeRates ?? [])
			: null;
	$: converted = !!mv && mv.converting && mv.hasRate;
</script>

<svelte:element
	this={href ? 'a' : 'div'}
	{href}
	class="flex h-full flex-col justify-between gap-1 p-4 {href
		? 'rounded-xl transition-colors hover:bg-accent/40 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none'
		: ''}"
>
	<div class="flex items-start justify-between gap-2">
		<span class="min-w-0 truncate text-sm text-muted-foreground">{T(metric.label)}</span>
		{#if badge && !loading}<Badge variant={badge.variant} class="wcard-corner -my-0.5"
				>{badge.label}</Badge
			>{/if}
	</div>
	{#if loading}
		<div class="flex flex-col gap-1.5">
			<Skeleton class="h-7 w-2/3" />
			<Skeleton class="h-3.5 w-1/3" />
		</div>
	{:else}
		<div class="min-w-0">
			<div
				class="truncate text-[28px] leading-8 font-semibold tracking-[-0.01em] whitespace-nowrap tabular-nums"
			>
				{#if metric.kind === 'money' && mv}
					{converted ? mv.display : mv.original}
					<span class="text-sm font-normal tracking-normal text-muted-foreground"
						>{converted ? $displayCurrency : nativeCurrency}</span
					>
				{:else if metric.kind === 'ratio'}
					{rawValue ? rawValue.toFixed(2) : '—'}
				{:else}
					{rawValue}
				{/if}
			</div>
			<div
				class="flex h-4 items-center gap-1 truncate text-[13px] leading-4 text-muted-foreground tabular-nums"
			>
				{#if converted && mv}
					{mv.original} {nativeCurrency}
				{:else if subText}
					{subText}
				{/if}
				{#if href}<ArrowRight
						class="wcard-corner ml-auto size-3.5 shrink-0"
						aria-hidden="true"
					/>{/if}
			</div>
		</div>
	{/if}
</svelte:element>
