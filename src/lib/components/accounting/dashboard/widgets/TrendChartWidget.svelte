<script lang="ts">
	// Revenue vs Expenses (grouped bars) or Net Income (line) over N months.
	// Backed by the /reports/monthly-series endpoint. Revenue is always aqua (chart-3), expenses
	// orange (chart-2), net blue (chart-1); the latest bar carries its value.
	import { onMount, getContext } from 'svelte';
	import ChartColumn from '@lucide/svelte/icons/chart-column';
	import { theme } from '$lib/stores';
	import { getMonthlySeries, type MonthlySeriesPoint } from '$lib/apis/accounting';
	import EChart from '../EChart.svelte';
	import WidgetState from '../WidgetState.svelte';
	import { chartTheme, pageIsDark, tooltipStyle, legendStyle, tooltipHtml } from '../palette';
	import { fmtCompact, fmtNumber } from '../format';

	export let companyId: number;
	export let options: { mode?: 'revenue_expenses' | 'net_income'; months?: number } = {};

	const i18n: any = getContext('i18n');
	const T = (k: string) => ($i18n?.t ? $i18n.t(k) : k);
	$: t = chartTheme(pageIsDark($theme));

	let points: MonthlySeriesPoint[] = [];
	let currency = '';
	let loading = true;
	let error = false;

	$: mode = options?.mode ?? 'revenue_expenses';
	$: months = options?.months ?? 12;

	onMount(load);
	async function load() {
		loading = true;
		error = false;
		try {
			const res = await getMonthlySeries({ company_id: companyId, months });
			points = res.points ?? [];
			currency = res.currency ?? '';
		} catch {
			error = true;
		}
		loading = false;
	}

	$: labels = points.map((p) => p.period);
	$: hasData = points.some((p) => p.revenue || p.expenses || p.net_income);
	$: last = points.length - 1;

	$: revenueName = T('Revenue');
	$: expensesName = T('Expenses');
	$: netName = T('Net Income');
	$: option = buildOption(t, mode, points, labels, currency);
	$: label =
		mode === 'net_income'
			? `${netName}, ${labels[0] ?? ''} – ${labels[last] ?? ''}`
			: `${revenueName} / ${expensesName}, ${labels[0] ?? ''} – ${labels[last] ?? ''}`;

	// The latest bar / point carries its value (design system: a value on the latest bar).
	const lastLabel = (t: any) => ({
		show: true,
		position: 'top',
		distance: 4,
		color: t.primary,
		fontSize: 11,
		fontWeight: 500,
		formatter: (p: any) => (p.value ? fmtCompact(p.value) : '')
	});

	function buildOption(
		t: any,
		mode: string,
		pts: MonthlySeriesPoint[],
		labels: string[],
		cur: string
	) {
		const money = (v: number) => `${fmtNumber(v)} ${cur}`.trim();
		const base = {
			grid: {
				left: 6,
				right: 8,
				top: mode === 'net_income' ? 20 : 40,
				bottom: 0,
				containLabel: true
			},
			tooltip: {
				trigger: 'axis',
				axisPointer: { type: 'shadow', shadowStyle: { color: t.band, opacity: 0.8 } },
				...tooltipStyle(t),
				formatter: (params: any[]) =>
					tooltipHtml(
						t,
						params[0]?.axisValueLabel ?? '',
						params.map((p) => ({ color: p.color, name: p.seriesName, value: money(p.value) }))
					)
			},
			xAxis: {
				type: 'category',
				data: labels,
				axisLine: { show: false },
				axisTick: { show: false },
				axisLabel: { color: t.muted, fontSize: 11 }
			},
			yAxis: {
				type: 'value',
				splitNumber: 3,
				splitLine: { lineStyle: { color: t.grid } },
				axisLabel: { color: t.muted, fontSize: 11, formatter: (v: number) => fmtCompact(v) }
			}
		};
		if (mode === 'net_income') {
			return {
				...base,
				series: [
					{
						name: netName,
						type: 'line',
						smooth: true,
						symbolSize: 8,
						data: pts.map((p, i) => ({
							value: +p.net_income.toFixed(2),
							...(i === pts.length - 1 ? { label: lastLabel(t) } : {})
						})),
						lineStyle: { color: t.net, width: 2 },
						itemStyle: { color: t.net, borderColor: t.surface, borderWidth: 2 },
						areaStyle: { color: t.net, opacity: t.isDark ? 0.12 : 0.08 }
					}
				]
			};
		}
		const bar = (name: string, color: string, key: 'revenue' | 'expenses') => ({
			name,
			type: 'bar',
			barMaxWidth: 24,
			barGap: '10%',
			itemStyle: { color },
			data: pts.map((p, i) => {
				const value = +p[key].toFixed(2);
				// 4px rounding on the data end, which is the bottom for a negative bar
				const negative = value < 0;
				return {
					value,
					itemStyle: { borderRadius: negative ? [0, 0, 4, 4] : [4, 4, 0, 0] },
					...(i === pts.length - 1
						? { label: { ...lastLabel(t), position: negative ? 'bottom' : 'top' } }
						: {})
				};
			})
		});
		return {
			...base,
			legend: { ...legendStyle(t), data: [revenueName, expensesName], top: 0, left: 0 },
			series: [bar(revenueName, t.revenue, 'revenue'), bar(expensesName, t.expenses, 'expenses')]
		};
	}
</script>

{#if loading}
	<WidgetState state="loading" />
{:else if error}
	<WidgetState state="error" onretry={load} />
{:else if !hasData}
	<WidgetState state="empty" icon={ChartColumn} message={T('No data')} />
{:else}
	<EChart {option} {label} />
{/if}
