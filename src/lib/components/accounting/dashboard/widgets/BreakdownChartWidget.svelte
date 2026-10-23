<script lang="ts">
	// Expense or revenue breakdown by account (donut), from /reports/profit-loss.
	// Uses leaf accounts (is_parent === false) to avoid double-counting rollups. At most eight
	// slices: the seven largest accounts in palette order, the rest folded into "Other" (neutral).
	import { onMount, getContext } from 'svelte';
	import ChartPie from '@lucide/svelte/icons/chart-pie';
	import { theme } from '$lib/stores';
	import { getProfitLoss } from '$lib/apis/accounting';
	import EChart from '../EChart.svelte';
	import WidgetState from '../WidgetState.svelte';
	import {
		chartTheme,
		pageIsDark,
		tooltipStyle,
		legendStyle,
		tooltipHtml,
		donutLayout,
		OTHER_LIMIT
	} from '../palette';
	import { fmtNumber } from '../format';

	export let companyId: number;
	export let options: { kind?: 'expenses' | 'revenue'; range?: 'ytd' | 'mtd' } = {};

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	$: t = chartTheme(pageIsDark($theme));

	let rows: { name: string; value: number; other?: boolean }[] = [];
	let currency = '';
	let loading = true;
	let error = false;

	$: kind = options?.kind ?? 'expenses';
	$: range = options?.range ?? 'ytd';

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const now = new Date();
			const y = now.getFullYear();
			const m = String(now.getMonth() + 1).padStart(2, '0');
			const d = String(now.getDate()).padStart(2, '0');
			const date_to = `${y}-${m}-${d}`;
			const date_from = range === 'mtd' ? `${y}-${m}-01` : `${y}-01-01`;
			const pl = await getProfitLoss({ company_id: companyId, date_from, date_to });
			currency = pl?.currency ?? '';
			const items = (kind === 'revenue' ? pl?.revenue : pl?.expenses) ?? [];
			const leaves = items
				.filter((a: any) => !a.is_parent)
				.map((a: any) => ({
					name: a.account_name || a.account_code,
					value: Math.abs(parseFloat(String(a.amount ?? 0)))
				}))
				.filter((a: any) => a.value > 0)
				.sort((a: any, b: any) => b.value - a.value);
			// Never a ninth colour: past eight slices the tail folds into "Other".
			if (leaves.length > OTHER_LIMIT) {
				const top = leaves.slice(0, OTHER_LIMIT - 1);
				const other = leaves.slice(OTHER_LIMIT - 1).reduce((s: number, a: any) => s + a.value, 0);
				rows = [...top, { name: T('Other'), value: other, other: true }];
			} else {
				rows = leaves;
			}
		} catch {
			rows = [];
			error = true;
		}
		loading = false;
	}

	$: total = rows.reduce((s, r) => s + r.value, 0);
	$: money = (v: number) => `${fmtNumber(v)} ${currency}`.trim();

	const layout = donutLayout(['50%', '76%']);
	$: option = {
		baseOption: {
			tooltip: {
				trigger: 'item',
				...tooltipStyle(t),
				formatter: (p: any) =>
					tooltipHtml(t, '', [
						{
							color: p.color,
							name: `${p.name} · ${total ? Math.round((p.value / total) * 100) : 0}%`,
							value: money(p.value)
						}
					])
			},
			legend: {
				...legendStyle(t),
				type: 'scroll',
				orient: 'vertical',
				right: 0,
				top: 'middle',
				itemGap: 8,
				pageTextStyle: { color: t.muted },
				pageIconColor: t.muted,
				pageIconInactiveColor: t.grid,
				formatter: layout.legendFormatter
			},
			series: [
				{
					type: 'pie',
					...layout.wide,
					avoidLabelOverlap: true,
					// 2px surface gap between slices
					itemStyle: { borderColor: t.surface, borderWidth: 2 },
					label: { show: false },
					data: rows.map((r, i) => ({
						name: r.name,
						value: r.value,
						itemStyle: { color: r.other ? t.other : t.series[i] }
					}))
				}
			]
		},
		media: [layout.narrow]
	};
	$: label = `${T(kind === 'revenue' ? 'Revenue' : 'Expenses')}: ${rows
		.slice(0, 3)
		.map((r) => `${r.name} ${money(r.value)}`)
		.join(', ')}`;
</script>

{#if loading}
	<WidgetState state="loading" />
{:else if error}
	<WidgetState state="error" onretry={load} />
{:else if rows.length === 0}
	<WidgetState state="empty" icon={ChartPie} message={T('No data')} />
{:else}
	<EChart {option} {label} />
{/if}
